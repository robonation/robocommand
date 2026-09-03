# Changelog

All notable changes to the RobotX 2026 proto schema are documented here.

## 2026-10-23
- Add `RunDeclaration.uav_geofence_max_altitude_hae_m` (required with a UAV; at most the competition's maximum UAV altitude) and `uav_pilot_callsign` (the pilot's MyDroneFleets call sign).
- Add `Heartbeat.uav_registration`: a UAV's CAAS registration number.
- Add `RxCourse.uav_transit_area`: the area beyond the course boundary where a declared UAV geofence may also lie (takeoff, landing and the way to and from the course). Empty: the geofence must fit the course.
- `RxCourse` is republished whenever it changes, not only at startup.
- Add `MovingObjectAlert.keep_out_radius_m`: how far the affected vehicles must stay from the moving object (5 m by default).
- `RunStart` comment: sent once every declared vehicle is in `STATE_AUTO` and nothing holds the start (Garuda's clearance with a UAV; the course manager's approval).
- `test_client.py`: `--uav-pilot-callsign` (was `--pilot-name`), `--registration`, and `moving-object-alert --keep-out-radius`. The `course` command is gone: the course comes from the test server. `run-declaration`'s default geofence and positions are on the new course, with a 40 m ceiling, and it refuses geofence latitudes and longitudes of different counts.
- `test_server.py`: publishes Course Alpha's boundary and its UAV transit area (Transit A), and checks the geofence of a declaration with a UAV as RoboCommand does: closed, within the course or transit area, ceiling above 0 and at most 50 m HAE. A refused declaration is logged with the reason; nothing is sent back.

## 2026-08-06
- Initial publish of the RobotX 2026 proto schema and MQTT test tooling.
