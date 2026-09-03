#!/usr/bin/env python3
"""Subscribes to all RobotX MQTT topics and logs decoded protobuf messages.

Every message is logged to both the console and a timestamped file under
LOG_DIR (default /app/logs, mounted to ./logs on the host)
"""

import logging
import math
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

# The course RxCourse publishes: Course Alpha's boundary and Garuda's
# Transit A beside it (MyDroneFleets, 2026-10-22), each a closed ring of
# (lat, lng). The competition's own may differ: read them from RxCourse
# rather than copying these.
COURSE_ALPHA = [
    (1.2809652, 103.8548424),
    (1.2808457, 103.8550331),
    (1.2810752, 103.8551770),
    (1.2811947, 103.8549863),
    (1.2809652, 103.8548424),
]
TRANSIT_A = [
    (1.281294119, 103.855048646),
    (1.281174598, 103.855239379),
    (1.2810752, 103.8551770),
    (1.2811947, 103.8549863),
    (1.281294119, 103.855048646),
]
# A declared UAV geofence's ceiling must be above 0 and at most this
# (meters above the WGS84 ellipsoid).
MAX_UAV_ALTITUDE_HAE_M = float(os.environ.get("MAX_UAV_ALTITUDE_HAE_M", "50"))
# How far outside the course and transit area a geofence point may lie
# (rounding between surveys), and how finely its edges are checked.
GEOFENCE_TOLERANCE_M = 1.0
EDGE_STEP_M = 0.5


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


# ── UAV geofence check (as RoboCommand does it) ──────────────────────────


def _xy(p, origin):
    """(lat, lng) as local east/north meters around origin."""
    r = 6371000.0
    return (
        math.radians(p[1] - origin[1]) * r * math.cos(math.radians(origin[0])),
        math.radians(p[0] - origin[0]) * r,
    )


def _inside(p, ring) -> bool:
    x, y = p
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def _outside_by(p, ring) -> float:
    """0 inside the ring, else meters to its nearest edge."""
    if _inside(p, ring):
        return 0.0
    best = math.inf
    for (ax, ay), (bx, by) in zip(ring, ring[1:]):
        dx, dy = bx - ax, by - ay
        t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy)))
    return best


def geofence_problems(decl: rx_requests_pb2.RunDeclaration) -> list:
    """Why RoboCommand would refuse this UAV geofence (empty: it's fine).
    Every point along its edges must lie within the course or the transit
    area (to within GEOFENCE_TOLERANCE_M), and its ceiling must be above 0
    and at most MAX_UAV_ALTITUDE_HAE_M."""
    fence = [(p.latitude, p.longitude) for p in decl.uav_geofence]
    problems = []
    if len(fence) < 4:
        problems.append(f"uav_geofence has {len(fence)} point(s), needs at least 4")
    elif fence[0] != fence[-1]:
        problems.append("uav_geofence isn't closed: its first and last points must be the same")
    else:
        origin = COURSE_ALPHA[0]
        areas = [[_xy(p, origin) for p in ring] for ring in (COURSE_ALPHA, TRANSIT_A)]
        pts = [_xy(p, origin) for p in fence]
        worst, where = 0.0, None
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            steps = max(1, math.ceil(math.dist(a, b) / EDGE_STEP_M))
            for k in range(steps + 1):
                q = (a[0] + (b[0] - a[0]) * k / steps, a[1] + (b[1] - a[1]) * k / steps)
                out = min(_outside_by(q, area) for area in areas)
                if out > worst:
                    worst = out
                    where = f"point {i + 1}" if k == 0 else f"point {i + 2}" if k == steps else f"edge {i + 1}-{i + 2}"
        if worst > GEOFENCE_TOLERANCE_M:
            problems.append(f"uav_geofence leaves the course and transit area by {worst:.1f} m at {where}")
    ceiling = decl.uav_geofence_max_altitude_hae_m
    if not 0 < ceiling <= MAX_UAV_ALTITUDE_HAE_M:
        problems.append(
            f"uav_geofence_max_altitude_hae_m is {ceiling:g}: it must be above 0 and at most {MAX_UAV_ALTITUDE_HAE_M:g}"
        )
    return problems


def handle_run_declaration(msg: rx_requests_pb2.RxRequest) -> None:
    decl = msg.run_declaration
    # As RoboCommand: only a declaration with a UAV is checked.
    if any(vid.startswith("UAV") for vid in decl.vehicle_ids):
        problems = geofence_problems(decl)
        if problems:
            # RoboCommand sends nothing back for a refused declaration: the
            # run just never starts. Fix it and send a new RunDeclaration.
            raise ValueError(f"RunDeclaration for {msg.team_id} refused: " + "; ".join(problems))
        log.info(f"[geofence] {msg.team_id}: UAV geofence and ceiling OK")
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
        corners=[common_pb2.LatLng(latitude=lat, longitude=lng) for lat, lng in COURSE_ALPHA],
        sent_at=_now_ts(),
        uav_transit_area=[common_pb2.LatLng(latitude=lat, longitude=lng) for lat, lng in TRANSIT_A],
    )
    client.publish(f"{TOPIC_ROOT}/course", course.SerializeToString(), retain=True)
    log.info(f"Published RxCourse (retained) → {TOPIC_ROOT}/course")

    client.loop_forever()


if __name__ == "__main__":
    main()
