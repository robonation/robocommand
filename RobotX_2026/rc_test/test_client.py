#!/usr/bin/env python3
"""Publish test RobotX protobuf messages to the MQTT broker.

One-shot mode — single command, connects, publishes, disconnects:
  docker compose run --rm rc-test python test_client.py <command> [options]

Interactive mode — persistent connection, issue multiple commands in a row:
  docker compose run --rm rc-test python test_client.py
  robotx> heartbeat --vehicle USV1 --state auto
  robotx> run-start --declaration-seq 1 --run-id 42
  robotx> exit

Run against the exposed broker from the host (requires local deps):
  BROKER_HOST=localhost python rc_test/test_client.py [command]

Commands:
  heartbeat           Send an RxReport/Heartbeat from a vehicle
  run-declaration     Send an RxRequest/RunDeclaration (team pre-run)
  run-start           Send an RxCommand/RunStart (simulates RC starting the run)
  pipeline-survey     Send an RxReport/PipelineSurveyReport (Task 2)
  resource-delivery   Send an RxReport/ResourceDeliveryRequest (Task 2/3 Adv/Disruptive)
  docking             Send an RxReport/DockingReport (Task 3)
  firefighting        Send an RxReport/FirefightingReport (Task 3)
  incident-ack        Send an RxReport/IncidentAck (Task 4)
  readiness-report    Send an RxReport/ReadinessReport (Task 4)
  assistance-request  Send an RxCommand/AssistanceRequest (simulates RC Task 4)
  keep-out-zone       Send an RxCommand/KeepOutZone (Task 4 Advanced)
  all-clear           Send an RxCommand/AllClear (Task 4 Advanced)
  moving-object-alert Send an RxCommand/MovingObjectAlert (Task 4 Disruptive)
  readiness-confirm   Send an RxCommand/ReadinessConfirm (Task 4)
  receive-course      Receive and decode the retained RxCourse from the broker
"""

import argparse
import os
import queue
import shlex
import sys
import paho.mqtt.client as mqtt
from google.protobuf.timestamp_pb2 import Timestamp

import common_pb2
from robotx import rx_reports_pb2, rx_commands_pb2, rx_requests_pb2, rx_common_pb2, rx_course_pb2

TOPIC_ROOT = "robocommand/robotx"

_seq = 0


def next_seq() -> int:
    global _seq
    _seq += 1
    return _seq


def now_ts() -> Timestamp:
    ts = Timestamp()
    ts.GetCurrentTime()
    return ts


def make_client(broker_host: str, broker_port: int) -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(broker_host, broker_port)
    return client


def publish(client: mqtt.Client, topic: str, msg, retain: bool = False) -> None:
    client.publish(topic, msg.SerializeToString(), retain=retain)
    suffix = " [retained]" if retain else ""
    print(f"Published {type(msg).__name__} → {topic}{suffix}")


TIER_MAP = {
    "unknown": common_pb2.TIER_UNKNOWN,
    "none": common_pb2.TIER_NONE,
    "core": common_pb2.TIER_CORE,
    "advanced": common_pb2.TIER_ADVANCED,
    "disruptive": common_pb2.TIER_DISRUPTIVE,
}

STATE_MAP = {
    "unknown": common_pb2.STATE_UNKNOWN,
    "killed": common_pb2.STATE_KILLED,
    "manual": common_pb2.STATE_MANUAL,
    "auto": common_pb2.STATE_AUTO,
}

TYPE_MAP = {
    "unknown": rx_common_pb2.TYPE_UNKNOWN,
    "usv": rx_common_pb2.TYPE_USV,
    "uuv": rx_common_pb2.TYPE_UUV,
    "uav": rx_common_pb2.TYPE_UAV,
}

COLOR_MAP = {
    "unknown": rx_common_pb2.COLOR_UNKNOWN,
    "red": rx_common_pb2.COLOR_RED,
    "green": rx_common_pb2.COLOR_GREEN,
    "blue": rx_common_pb2.COLOR_BLUE,
    "any": rx_common_pb2.COLOR_ANY,
}

TASK_MAP = {
    "unknown": rx_common_pb2.TASK_UNKNOWN,
    "none": rx_common_pb2.TASK_NONE,
    "safe-passage": rx_common_pb2.TASK_SAFE_PASSAGE,
    "infra-survey-repair": rx_common_pb2.TASK_INFRA_SURVEY_REPAIR,
    "coordinated-logistics": rx_common_pb2.TASK_COORDINATED_LOGISTICS,
    "dynamic-incident": rx_common_pb2.TASK_DYNAMIC_INCIDENT,
}

SEGMENT_MAP = {
    "unknown": rx_common_pb2.PIPELINE_SEGMENT_UNKNOWN,
    "intact": rx_common_pb2.PIPELINE_SEGMENT_INTACT,
    "damaged": rx_common_pb2.PIPELINE_SEGMENT_DAMAGED,
}


def parse_tier(s: str) -> int:
    s = s.lower()
    if s not in TIER_MAP:
        raise argparse.ArgumentTypeError(f"must be one of: {', '.join(TIER_MAP)}")
    return TIER_MAP[s]


# --- subcommand handlers (all take the shared, already-connected client) ---

def cmd_heartbeat(args, client):
    report = rx_reports_pb2.RxReport(
        team_id=args.team,
        vehicle_id=args.vehicle,
        seq=next_seq(),
        sent_at=now_ts(),
        heartbeat=rx_reports_pb2.Heartbeat(
            state=STATE_MAP.get(args.state, common_pb2.STATE_UNKNOWN),
            position=common_pb2.LatLng(latitude=args.lat, longitude=args.lng),
            spd_mps=args.speed,
            heading_deg=args.heading,
            vehicle_type=TYPE_MAP.get(args.vehicle_type, rx_common_pb2.TYPE_UNKNOWN),
            uav_registration=args.registration,
        ),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/{args.vehicle}/report"
    publish(client, topic, report)


def cmd_run_declaration(args, client):
    if len(args.geofence_lats) != len(args.geofence_lngs):
        raise ValueError(f"--geofence-lats has {len(args.geofence_lats)} values and --geofence-lngs "
                         f"{len(args.geofence_lngs)}: give one longitude per latitude")
    geofence = [
        common_pb2.LatLng(latitude=lat, longitude=lng)
        for lat, lng in zip(args.geofence_lats, args.geofence_lngs)
    ]
    request = rx_requests_pb2.RxRequest(
        team_id=args.team,
        seq=next_seq(),
        sent_at=now_ts(),
        run_declaration=rx_requests_pb2.RunDeclaration(
            vehicle_ids=args.vehicles,
            task1_tier=parse_tier(args.task1),
            task2_tier=parse_tier(args.task2),
            task3_tier=parse_tier(args.task3),
            task4_tier=parse_tier(args.task4),
            uav_geofence=geofence,
            uav_geofence_max_altitude_hae_m=args.geofence_max_altitude_hae,
            uav_pilot_callsign=args.uav_pilot_callsign,
        ),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/request"
    publish(client, topic, request)


def cmd_run_start(args, client):
    command = rx_commands_pb2.RxCommand(
        team_id=args.team,
        seq=next_seq(),
        sent_at=now_ts(),
        run_start=rx_commands_pb2.RunStart(
            declaration_seq=args.declaration_seq,
            run_id=args.run_id,
        ),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/command"
    publish(client, topic, command)


def cmd_assistance_request(args, client):
    command = rx_commands_pb2.RxCommand(
        team_id=args.team,
        seq=next_seq(),
        sent_at=now_ts(),
        assistance_request=rx_commands_pb2.AssistanceRequest(
            position=common_pb2.LatLng(latitude=args.lat, longitude=args.lng),
            vehicle_type=TYPE_MAP.get(args.vehicle_type, rx_common_pb2.TYPE_UNKNOWN),
        ),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/command"
    publish(client, topic, command)


def cmd_pipeline_survey(args, client):
    report = rx_reports_pb2.RxReport(
        team_id=args.team,
        vehicle_id=args.vehicle,
        seq=next_seq(),
        sent_at=now_ts(),
        pipeline_survey=rx_reports_pb2.PipelineSurveyReport(
            active_buoy_position=common_pb2.LatLng(latitude=args.lat, longitude=args.lng),
            segments=[SEGMENT_MAP.get(s, rx_common_pb2.PIPELINE_SEGMENT_UNKNOWN) for s in args.segments],
        ),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/{args.vehicle}/report"
    publish(client, topic, report)


def cmd_resource_delivery(args, client):
    report = rx_reports_pb2.RxReport(
        team_id=args.team,
        vehicle_id=args.vehicle,
        seq=next_seq(),
        sent_at=now_ts(),
        resource_delivery=rx_reports_pb2.ResourceDeliveryRequest(
            task=TASK_MAP.get(args.task, rx_common_pb2.TASK_UNKNOWN),
            resource_color=COLOR_MAP.get(args.resource_color, rx_common_pb2.COLOR_UNKNOWN),
            delivery_circle_color=COLOR_MAP.get(args.delivery_circle_color, rx_common_pb2.COLOR_UNKNOWN),
        ),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/{args.vehicle}/report"
    publish(client, topic, report)


def cmd_docking(args, client):
    report = rx_reports_pb2.RxReport(
        team_id=args.team,
        vehicle_id=args.vehicle,
        seq=next_seq(),
        sent_at=now_ts(),
        docking=rx_reports_pb2.DockingReport(bay_id=args.bay_id),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/{args.vehicle}/report"
    publish(client, topic, report)


def cmd_firefighting(args, client):
    report = rx_reports_pb2.RxReport(
        team_id=args.team,
        vehicle_id=args.vehicle,
        seq=next_seq(),
        sent_at=now_ts(),
        firefighting=rx_reports_pb2.FirefightingReport(window_id=args.window_id),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/{args.vehicle}/report"
    publish(client, topic, report)


def cmd_incident_ack(args, client):
    report = rx_reports_pb2.RxReport(
        team_id=args.team,
        vehicle_id=args.vehicle,
        seq=next_seq(),
        sent_at=now_ts(),
        incident_ack=rx_reports_pb2.IncidentAck(command_seq=args.command_seq),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/{args.vehicle}/report"
    publish(client, topic, report)


def cmd_readiness_report(args, client):
    report = rx_reports_pb2.RxReport(
        team_id=args.team,
        vehicle_id=args.vehicle,
        seq=next_seq(),
        sent_at=now_ts(),
        readiness=rx_reports_pb2.ReadinessReport(command_seq=args.command_seq),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/{args.vehicle}/report"
    publish(client, topic, report)


def cmd_keep_out_zone(args, client):
    command = rx_commands_pb2.RxCommand(
        team_id=args.team,
        seq=next_seq(),
        sent_at=now_ts(),
        keep_out_zone=rx_commands_pb2.KeepOutZone(
            center=common_pb2.LatLng(latitude=args.lat, longitude=args.lng),
            radius_m=args.radius_m,
            vehicle_type=TYPE_MAP.get(args.vehicle_type, rx_common_pb2.TYPE_UNKNOWN),
        ),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/command"
    publish(client, topic, command)


def cmd_all_clear(args, client):
    command = rx_commands_pb2.RxCommand(
        team_id=args.team,
        seq=next_seq(),
        sent_at=now_ts(),
        all_clear=rx_commands_pb2.AllClear(
            vehicle_type=TYPE_MAP.get(args.vehicle_type, rx_common_pb2.TYPE_UNKNOWN),
        ),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/command"
    publish(client, topic, command)


def cmd_moving_object_alert(args, client):
    command = rx_commands_pb2.RxCommand(
        team_id=args.team,
        seq=next_seq(),
        sent_at=now_ts(),
        moving_object_alert=rx_commands_pb2.MovingObjectAlert(
            position=common_pb2.LatLng(latitude=args.lat, longitude=args.lng),
            heading_deg=args.heading,
            speed_mps=args.speed,
            affected_vehicle_types=[TYPE_MAP.get(t, rx_common_pb2.TYPE_UNKNOWN) for t in args.affected_vehicle_types],
            keep_out_radius_m=args.keep_out_radius,
        ),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/command"
    publish(client, topic, command)


def cmd_readiness_confirm(args, client):
    command = rx_commands_pb2.RxCommand(
        team_id=args.team,
        seq=next_seq(),
        sent_at=now_ts(),
        readiness_confirm=rx_commands_pb2.ReadinessConfirm(
            report_seq=args.report_seq,
            vehicle_id=args.vehicle_id,
        ),
    )
    topic = f"{TOPIC_ROOT}/{args.team}/command"
    publish(client, topic, command)


def cmd_receive_course(args, client):
    topic = f"{TOPIC_ROOT}/course"
    received = queue.Queue()

    def on_message(_client, _userdata, msg):
        if msg.topic == topic:
            received.put(msg.payload)

    client.on_message = on_message
    client.subscribe(topic)
    try:
        payload = received.get(timeout=5)
    except queue.Empty:
        print("No course message received (timeout — is the server running?)", file=sys.stderr)
        return
    finally:
        client.unsubscribe(topic)
        client.on_message = None

    course = rx_course_pb2.RxCourse()
    course.ParseFromString(payload)
    print(f"[RxCourse] {topic}")
    print(course)


def add_commands(sub) -> None:
    # heartbeat
    p = sub.add_parser("heartbeat", help="RxReport/Heartbeat from a vehicle")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--vehicle", default="USV1")
    p.add_argument("--state", default="auto", choices=STATE_MAP)
    p.add_argument("--vehicle-type", default="usv", choices=TYPE_MAP)
    p.add_argument("--lat", type=float, default=1.2810202)
    p.add_argument("--lng", type=float, default=103.8550097)
    p.add_argument("--speed", type=float, default=0.0)
    p.add_argument("--heading", type=float, default=0.0)
    p.add_argument("--registration", default="", help="UAV: its CAAS registration number, e.g. 53551")
    p.set_defaults(func=cmd_heartbeat)

    # run-declaration
    p = sub.add_parser("run-declaration", help="RxRequest/RunDeclaration (pre-run team submission)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--vehicles", nargs="+", default=["USV1", "UUV1", "UAV1"])
    p.add_argument("--task1", default="unknown", metavar="TIER", help="Safe Passage")
    p.add_argument("--task2", default="unknown", metavar="TIER", help="Infrastructure Survey & Repair")
    p.add_argument("--task3", default="unknown", metavar="TIER", help="Coordinated Logistics")
    p.add_argument("--task4", default="unknown", metavar="TIER", help="Dynamic Incident Response")
    p.add_argument("--geofence-lats", nargs="+", type=float,
                   default=[1.2809652, 1.2808457, 1.2810752, 1.281174598, 1.281294119, 1.2811947, 1.2809652],
                   metavar="LAT", help="UAV geofence corner latitudes, closed ring "
                   "(first/last must match; same count as --geofence-lngs)")
    p.add_argument("--geofence-lngs", nargs="+", type=float,
                   default=[103.8548424, 103.8550331, 103.8551770, 103.855239379, 103.855048646, 103.8549863, 103.8548424],
                   metavar="LNG", help="UAV geofence corner longitudes, closed ring "
                   "(first/last must match; same count as --geofence-lats)")
    p.add_argument("--geofence-max-altitude-hae", type=float, default=40.0,
                   metavar="METERS", help="Max altitude of the UAV geofence, in meters HAE (at most 50)")
    p.add_argument("--uav-pilot-callsign", default="", help="UAV pilot's MyDroneFleets call sign for this run: first name + UAPL number")
    p.set_defaults(func=cmd_run_declaration)

    # run-start
    p = sub.add_parser("run-start", help="RxCommand/RunStart (simulates RC starting the run)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--declaration-seq", type=int, default=1)
    p.add_argument("--run-id", type=int, default=1)
    p.set_defaults(func=cmd_run_start)

    # assistance-request
    p = sub.add_parser("assistance-request", help="RxCommand/AssistanceRequest (simulates RC Task 4)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--lat", type=float, default=1.2810202)
    p.add_argument("--lng", type=float, default=103.8550097)
    p.add_argument("--vehicle-type", default="usv", choices=["usv", "uuv", "uav"])
    p.set_defaults(func=cmd_assistance_request)

    # pipeline-survey
    p = sub.add_parser("pipeline-survey", help="RxReport/PipelineSurveyReport (Task 2)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--vehicle", default="UUV1")
    p.add_argument("--lat", type=float, default=1.2810202)
    p.add_argument("--lng", type=float, default=103.8550097)
    p.add_argument("--segments", nargs="+", default=["intact", "damaged", "intact"], choices=SEGMENT_MAP,
                   metavar="STATUS", help="Segment statuses, ordered from the active buoy end")
    p.set_defaults(func=cmd_pipeline_survey)

    # resource-delivery
    p = sub.add_parser("resource-delivery", help="RxReport/ResourceDeliveryRequest (Task 2/3 Adv/Disruptive)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--vehicle", default="UAV1")
    p.add_argument("--task", default="infra-survey-repair", choices=TASK_MAP)
    p.add_argument("--resource-color", default="any", choices=COLOR_MAP)
    p.add_argument("--delivery-circle-color", default="red", choices=COLOR_MAP)
    p.set_defaults(func=cmd_resource_delivery)

    # docking
    p = sub.add_parser("docking", help="RxReport/DockingReport (Task 3)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--vehicle", default="USV1")
    p.add_argument("--bay-id", type=int, default=1)
    p.set_defaults(func=cmd_docking)

    # firefighting
    p = sub.add_parser("firefighting", help="RxReport/FirefightingReport (Task 3)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--vehicle", default="USV1")
    p.add_argument("--window-id", type=int, default=1)
    p.set_defaults(func=cmd_firefighting)

    # incident-ack
    p = sub.add_parser("incident-ack", help="RxReport/IncidentAck (Task 4)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--vehicle", default="USV1")
    p.add_argument("--command-seq", type=int, default=1)
    p.set_defaults(func=cmd_incident_ack)

    # readiness-report
    p = sub.add_parser("readiness-report", help="RxReport/ReadinessReport (Task 4)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--vehicle", default="USV1")
    p.add_argument("--command-seq", type=int, default=1)
    p.set_defaults(func=cmd_readiness_report)

    # keep-out-zone
    p = sub.add_parser("keep-out-zone", help="RxCommand/KeepOutZone (Task 4 Advanced)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--lat", type=float, default=1.2810202)
    p.add_argument("--lng", type=float, default=103.8550097)
    p.add_argument("--radius-m", type=float, default=15.0)
    p.add_argument("--vehicle-type", default="usv", choices=TYPE_MAP)
    p.set_defaults(func=cmd_keep_out_zone)

    # all-clear
    p = sub.add_parser("all-clear", help="RxCommand/AllClear (Task 4 Advanced)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--vehicle-type", default="usv", choices=TYPE_MAP)
    p.set_defaults(func=cmd_all_clear)

    # moving-object-alert
    p = sub.add_parser("moving-object-alert", help="RxCommand/MovingObjectAlert (Task 4 Disruptive)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--lat", type=float, default=1.2810202)
    p.add_argument("--lng", type=float, default=103.8550097)
    p.add_argument("--heading", type=float, default=0.0)
    p.add_argument("--speed", type=float, default=0.0)
    p.add_argument("--affected-vehicle-types", nargs="+", default=["usv"], choices=TYPE_MAP, metavar="TYPE")
    p.add_argument("--keep-out-radius", type=float, default=5.0, help="Keep-out radius around the object, in meters")
    p.set_defaults(func=cmd_moving_object_alert)

    # readiness-confirm
    p = sub.add_parser("readiness-confirm", help="RxCommand/ReadinessConfirm (Task 4, response to ReadinessReport)")
    p.add_argument("--team", default="RNRX")
    p.add_argument("--report-seq", type=int, default=1)
    p.add_argument("--vehicle-id", default="USV1", help="Vehicle whose ReadinessReport is being confirmed")
    p.set_defaults(func=cmd_readiness_confirm)

    # receive-course
    p = sub.add_parser("receive-course", help="Receive and decode the retained RxCourse from the broker")
    p.set_defaults(func=cmd_receive_course)


# --- interactive REPL ---

class ReplExit(Exception):
    """Raised in place of SystemExit so argparse errors/--help don't kill the REPL."""


class ReplArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            (sys.stderr if status else sys.stdout).write(message)
        raise ReplExit


def run_repl(client: mqtt.Client) -> None:
    parser = ReplArgumentParser(prog="", add_help=True)
    sub = parser.add_subparsers(dest="command")
    add_commands(sub)

    print("RobotX test client — interactive mode. Type a command, '<command> --help', or 'exit'.")
    try:
        while True:
            try:
                line = input("robotx> ").strip()
            except EOFError:
                print()
                break
            if not line:
                continue
            if line in ("exit", "quit"):
                break
            try:
                args = parser.parse_args(shlex.split(line))
            except ReplExit:
                continue
            if not args.command:
                continue
            try:
                args.func(args, client)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        print()
    finally:
        client.loop_stop()
        client.disconnect()
        print("Disconnected.")


# --- CLI ---

def main():
    default_host = os.environ.get("BROKER_HOST", "localhost")
    default_port = int(os.environ.get("BROKER_PORT", "1883"))

    parser = argparse.ArgumentParser(
        description="RobotX 2026 test message publisher",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--broker", default=default_host)
    parser.add_argument("--port", type=int, default=default_port)
    sub = parser.add_subparsers(dest="command")
    add_commands(sub)

    args = parser.parse_args()

    client = make_client(args.broker, args.port)
    client.loop_start()

    if args.command:
        try:
            args.func(args, client)
        except Exception as e:  # as in the REPL: the reason, not a traceback
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            client.loop_stop()
            client.disconnect()
        return

    run_repl(client)


if __name__ == "__main__":
    main()
