#!/usr/bin/env python3
"""Subscribes to all RobotX MQTT topics and logs decoded protobuf messages.

Every message is logged to both the console and a timestamped file under
LOG_DIR (default /app/logs, mounted to ./logs on the host)
"""

import logging
import os
import time
import paho.mqtt.client as mqtt
from google.protobuf.timestamp_pb2 import Timestamp

import common_pb2
from robotx import rx_reports_pb2, rx_commands_pb2, rx_requests_pb2, rx_course_pb2

def _now_ts() -> Timestamp:
    ts = Timestamp()
    ts.GetCurrentTime()
    return ts


BROKER_HOST = os.environ.get("BROKER_HOST", "localhost")
BROKER_PORT = int(os.environ.get("BROKER_PORT", "1883"))
TOPIC_ROOT = "robocommand/robotx"
LOG_DIR = os.environ.get("LOG_DIR", "/app/logs")


def setup_logger() -> logging.Logger:
    os.makedirs(LOG_DIR, exist_ok=True)
    # The container runs as root, so files land root-owned on the host's
    # bind-mounted ./logs — open up permissions so the host user can manage
    # (move, delete, attach to a submission) the logs without sudo.
    os.chmod(LOG_DIR, 0o777)
    log_path = os.path.join(LOG_DIR, f"robocommand_{time.strftime('%Y%m%d_%H%M%S')}.log")

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    os.chmod(log_path, 0o666)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger("robocommand")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.info(f"Logging this session to {log_path}")
    return logger


log = setup_logger()

# team_id -> {"seq": int, "vehicle_ids": set[str], "auto_vehicles": set[str], "started": bool}
run_declarations: dict = {}

_command_seq_by_team: dict = {}
_run_id_seq = 0


def next_command_seq(team_id: str) -> int:
    _command_seq_by_team[team_id] = _command_seq_by_team.get(team_id, 0) + 1
    return _command_seq_by_team[team_id]


def next_run_id() -> int:
    global _run_id_seq
    _run_id_seq += 1
    return _run_id_seq


def parse_message(topic: str, payload: bytes):
    parts = topic.split("/")
    msg_type = parts[-1]
    if msg_type == "report":
        msg = rx_reports_pb2.RxReport()
        msg.ParseFromString(payload)
        return "RxReport", msg
    if msg_type == "request":
        msg = rx_requests_pb2.RxRequest()
        msg.ParseFromString(payload)
        return "RxRequest", msg
    if msg_type == "command":
        msg = rx_commands_pb2.RxCommand()
        msg.ParseFromString(payload)
        return "RxCommand", msg
    if msg_type == "course":
        msg = rx_course_pb2.RxCourse()
        msg.ParseFromString(payload)
        return "RxCourse", msg
    return None, None


def on_connect(client, userdata, flags, reason_code, properties):
    log.info(f"Connected ({reason_code}), subscribing to {TOPIC_ROOT}/#")
    client.subscribe(f"{TOPIC_ROOT}/#")


def handle_run_declaration(msg: rx_requests_pb2.RxRequest) -> None:
    decl = msg.run_declaration
    if any(vid.startswith("UAV") for vid in decl.vehicle_ids) and len(decl.uav_geofence) < 4:
        raise ValueError(
            f"RunDeclaration for {msg.team_id} lists a UAV vehicle but uav_geofence "
            f"has only {len(decl.uav_geofence)} point(s) (min 4)"
        )
    run_declarations[msg.team_id] = {
        "seq": msg.seq,
        "vehicle_ids": set(decl.vehicle_ids),
        "auto_vehicles": set(),
        "started": False,
    }
    log.info(f"[auto-start] Tracking {msg.team_id} vehicles {sorted(decl.vehicle_ids)} — waiting for all to report AUTO")


def handle_heartbeat(client: mqtt.Client, report: rx_reports_pb2.RxReport) -> None:
    pending = run_declarations.get(report.team_id)
    if pending is None or pending["started"]:
        return
    if report.vehicle_id not in pending["vehicle_ids"]:
        return

    if report.heartbeat.state == common_pb2.STATE_AUTO:
        pending["auto_vehicles"].add(report.vehicle_id)
    else:
        pending["auto_vehicles"].discard(report.vehicle_id)

    if pending["auto_vehicles"] == pending["vehicle_ids"]:
        start_run(client, report.team_id, pending)


def start_run(client: mqtt.Client, team_id: str, pending: dict) -> None:
    pending["started"] = True
    run_id = next_run_id()
    command = rx_commands_pb2.RxCommand(
        team_id=team_id,
        seq=next_command_seq(team_id),
        sent_at=_now_ts(),
        run_start=rx_commands_pb2.RunStart(
            declaration_seq=pending["seq"],
            run_id=run_id,
        ),
    )
    topic = f"{TOPIC_ROOT}/{team_id}/command"
    client.publish(topic, command.SerializeToString())
    log.info(f"[auto-start] All declared vehicles autonomous for {team_id} — publishing RunStart "
             f"(declaration_seq={pending['seq']}, run_id={run_id}) → {topic}")


def on_message(client, userdata, msg):
    try:
        msg_type, parsed = parse_message(msg.topic, msg.payload)
        if parsed is None:
            log.warning(f"[UNKNOWN] {msg.topic}")
            return
        log.info(f"[{msg_type}] {msg.topic}\n{parsed}")

        if msg_type == "RxRequest" and parsed.WhichOneof("body") == "run_declaration":
            handle_run_declaration(parsed)
        elif msg_type == "RxReport" and parsed.WhichOneof("body") == "heartbeat":
            handle_heartbeat(client, parsed)
    except Exception as e:
        log.error(f"[ERROR] {msg.topic}: {e}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            log.info(f"Connecting to {BROKER_HOST}:{BROKER_PORT}...")
            client.connect(BROKER_HOST, BROKER_PORT)
            break
        except Exception as e:
            log.warning(f"Connection failed ({e}), retrying in 2s...")
            time.sleep(2)

    course = rx_course_pb2.RxCourse(
        course_id=os.environ.get("COURSE_ID", "ALPHA"),
        pinger_freq_hz=int(os.environ.get("PINGER_FREQ_HZ", "25000")),
        corners=[
            common_pb2.LatLng(latitude=1.280329,  longitude=103.8556869),
            common_pb2.LatLng(latitude=1.2804716, longitude=103.8554529),
            common_pb2.LatLng(latitude=1.2808993, longitude=103.8557337),
            common_pb2.LatLng(latitude=1.2807567, longitude=103.8559743),
            common_pb2.LatLng(latitude=1.280329,  longitude=103.8556869),
        ],
        sent_at=_now_ts(),
    )
    client.publish(f"{TOPIC_ROOT}/course", course.SerializeToString(), retain=True)
    log.info(f"Published RxCourse (retained) → {TOPIC_ROOT}/course")

    client.loop_forever()


if __name__ == "__main__":
    main()
