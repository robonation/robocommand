# RobotX 2026

Protobuf message schemas and test tooling for RobotX 2026 MQTT communication between a team's Operator Control Station (OCS) and RoboCommand. The OCS is the only team system that connects to the RoboCommand network — it publishes vehicle-attributed reports on behalf of its vehicles and routes RoboCommand information to those vehicles over the team's own internal communications, which are outside the scope of this schema. A vehicle-scoped topic segment or `vehicle_id` field identifies which vehicle a message is *about*; it does not mean that vehicle has its own connection to RoboCommand.

## Proto schema

| File | Package | Purpose |
|---|---|---|
| `common.proto` | `robocommand.common.v1` | Shared types: `LatLng`, `RobotState`, `TaskTier` |
| `robotx/rx_common.proto` | `robocommand.robotx.v1` | RobotX enums: `RxTask`, `VehicleType`, beacon/pipeline/resource types |
| `robotx/rx_reports.proto` | `robocommand.robotx.v1` | `RxReport` — OCS → RoboCommand, attributed to a vehicle (heartbeat, task reports) |
| `robotx/rx_requests.proto` | `robocommand.robotx.v1` | `RxRequest` — OCS → RoboCommand (pre-run `RunDeclaration`) |
| `robotx/rx_commands.proto` | `robocommand.robotx.v1` | `RxCommand` — RoboCommand → OCS, targeted to a vehicle type (`RunStart`, Task 4 commands) |
| `robotx/rx_course.proto` | `robocommand.robotx.v1` | `RxCourse` — retained course config published by RC on server start |

### MQTT topics

```
robocommand/robotx/course                          # RxCourse  (retained, RC → OCS)
robocommand/robotx/<team_id>/<vehicle_id>/report   # RxReport  (OCS → RC, attributed to <vehicle_id>)
robocommand/robotx/<team_id>/request               # RxRequest (OCS → RC)
robocommand/robotx/<team_id>/command               # RxCommand (RC → OCS)
```

### Task tiers

`TaskTier` is declared per-task in `RunDeclaration`. `TIER_UNKNOWN` is the proto zero default; use `TIER_NONE` to explicitly signal "not attempting."

### Versions

The checked-in `gen/` output was produced with `protoc`/protobuf runtime **v7.35.0**.

The broker runs **Eclipse Mosquitto 2.x** (`eclipse-mosquitto:2` in `docker-compose.yml`).

## Test environment

Runs a Mosquitto broker and a server that subscribes to all topics and logs decoded messages.

**Start:**
```bash
docker compose up --build
```

**Stop:**
```bash
docker compose down
```

### Session logs

Every server run writes a timestamped log (`robocommand_<YYYYMMDD>_<HHMMSS>.log`) to `./logs/` on the host, alongside the usual console output. Each entry is the decoded contents of one message that crossed the broker.

## Test publisher

`test_client.py` simulates a team's OCS — it publishes vehicle-attributed reports and team-level requests exactly as an OCS would, one command at a time.

Publish individual test messages against the running broker. Add `--rm` so one-shot containers don't pile up:

```bash
# Heartbeat attributed to a vehicle
docker compose run --rm rc-test python test_client.py heartbeat --vehicle USV1 --state auto

# Pre-run declaration (OCS → RC)
docker compose run --rm rc-test python test_client.py run-declaration \
  --vehicles USV1 UUV1 UAV1 \
  --task1 advanced --task2 core --task3 core --task4 none

# Run start signal (RC → OCS)
docker compose run --rm rc-test python test_client.py run-start \
  --declaration-seq 1 --run-id 42

# Task 4 assistance request (RC → OCS, targeted to a vehicle type)
docker compose run --rm rc-test python test_client.py assistance-request \
  --vehicle-type uuv --lat 21.31 --lng -157.89

# Course config — retained, survives broker restart (simulates RC server start)
docker compose run --rm rc-test python test_client.py course \
  --course-id RX2026-A --pinger-freq-hz 27000
```

All subcommands accept `--broker` and `--port` to target a different broker. Use `--help` on any subcommand for the full option list.

### Interactive mode

Running with no subcommand drops into a REPL on a single persistent MQTT connection — useful for driving a vehicle through several message types in a row without reconnecting each time:

```bash
docker compose run --rm rc-test python test_client.py
```
```
robotx> heartbeat --vehicle USV1 --state auto
Published RxReport → robocommand/robotx/RNRX/USV1/report
robotx> run-start --declaration-seq 1 --run-id 42
Published RxCommand → robocommand/robotx/RNRX/command
robotx> exit
Disconnected.
```

`<command> --help` works inside the REPL too. `exit`, `quit`, or Ctrl-D ends the session and disconnects.
