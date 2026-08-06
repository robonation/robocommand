import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
import common_pb2 as _common_pb2
from robotx import rx_common_pb2 as _rx_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RxReport(_message.Message):
    __slots__ = ("team_id", "vehicle_id", "seq", "sent_at", "heartbeat", "safe_passage", "pipeline_survey", "resource_delivery", "docking", "firefighting", "incident_ack", "readiness")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SENT_AT_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    SAFE_PASSAGE_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_SURVEY_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_DELIVERY_FIELD_NUMBER: _ClassVar[int]
    DOCKING_FIELD_NUMBER: _ClassVar[int]
    FIREFIGHTING_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_ACK_FIELD_NUMBER: _ClassVar[int]
    READINESS_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    vehicle_id: str
    seq: int
    sent_at: _timestamp_pb2.Timestamp
    heartbeat: Heartbeat
    safe_passage: SafePassageReport
    pipeline_survey: PipelineSurveyReport
    resource_delivery: ResourceDeliveryRequest
    docking: DockingReport
    firefighting: FirefightingReport
    incident_ack: IncidentAck
    readiness: ReadinessReport
    def __init__(self, team_id: _Optional[str] = ..., vehicle_id: _Optional[str] = ..., seq: _Optional[int] = ..., sent_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., heartbeat: _Optional[_Union[Heartbeat, _Mapping]] = ..., safe_passage: _Optional[_Union[SafePassageReport, _Mapping]] = ..., pipeline_survey: _Optional[_Union[PipelineSurveyReport, _Mapping]] = ..., resource_delivery: _Optional[_Union[ResourceDeliveryRequest, _Mapping]] = ..., docking: _Optional[_Union[DockingReport, _Mapping]] = ..., firefighting: _Optional[_Union[FirefightingReport, _Mapping]] = ..., incident_ack: _Optional[_Union[IncidentAck, _Mapping]] = ..., readiness: _Optional[_Union[ReadinessReport, _Mapping]] = ...) -> None: ...

class Heartbeat(_message.Message):
    __slots__ = ("state", "position", "spd_mps", "heading_deg", "roll_deg", "pitch_deg", "altitude_hae_m", "depth_m", "current_task", "vehicle_type", "flight_phase")
    STATE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    SPD_MPS_FIELD_NUMBER: _ClassVar[int]
    HEADING_DEG_FIELD_NUMBER: _ClassVar[int]
    ROLL_DEG_FIELD_NUMBER: _ClassVar[int]
    PITCH_DEG_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_HAE_M_FIELD_NUMBER: _ClassVar[int]
    DEPTH_M_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TASK_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    FLIGHT_PHASE_FIELD_NUMBER: _ClassVar[int]
    state: _common_pb2.RobotState
    position: _common_pb2.LatLng
    spd_mps: float
    heading_deg: float
    roll_deg: float
    pitch_deg: float
    altitude_hae_m: float
    depth_m: float
    current_task: _rx_common_pb2.RxTask
    vehicle_type: _rx_common_pb2.VehicleType
    flight_phase: _rx_common_pb2.FlightPhase
    def __init__(self, state: _Optional[_Union[_common_pb2.RobotState, str]] = ..., position: _Optional[_Union[_common_pb2.LatLng, _Mapping]] = ..., spd_mps: _Optional[float] = ..., heading_deg: _Optional[float] = ..., roll_deg: _Optional[float] = ..., pitch_deg: _Optional[float] = ..., altitude_hae_m: _Optional[float] = ..., depth_m: _Optional[float] = ..., current_task: _Optional[_Union[_rx_common_pb2.RxTask, str]] = ..., vehicle_type: _Optional[_Union[_rx_common_pb2.VehicleType, str]] = ..., flight_phase: _Optional[_Union[_rx_common_pb2.FlightPhase, str]] = ...) -> None: ...

class BuoyDetection(_message.Message):
    __slots__ = ("position", "state")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    position: _common_pb2.LatLng
    state: _rx_common_pb2.BeaconState
    def __init__(self, position: _Optional[_Union[_common_pb2.LatLng, _Mapping]] = ..., state: _Optional[_Union[_rx_common_pb2.BeaconState, str]] = ...) -> None: ...

class SafePassageReport(_message.Message):
    __slots__ = ("entry_position", "exit_position", "buoys")
    ENTRY_POSITION_FIELD_NUMBER: _ClassVar[int]
    EXIT_POSITION_FIELD_NUMBER: _ClassVar[int]
    BUOYS_FIELD_NUMBER: _ClassVar[int]
    entry_position: _common_pb2.LatLng
    exit_position: _common_pb2.LatLng
    buoys: _containers.RepeatedCompositeFieldContainer[BuoyDetection]
    def __init__(self, entry_position: _Optional[_Union[_common_pb2.LatLng, _Mapping]] = ..., exit_position: _Optional[_Union[_common_pb2.LatLng, _Mapping]] = ..., buoys: _Optional[_Iterable[_Union[BuoyDetection, _Mapping]]] = ...) -> None: ...

class PipelineSurveyReport(_message.Message):
    __slots__ = ("active_buoy_position", "segments")
    ACTIVE_BUOY_POSITION_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    active_buoy_position: _common_pb2.LatLng
    segments: _containers.RepeatedScalarFieldContainer[_rx_common_pb2.PipelineSegmentStatus]
    def __init__(self, active_buoy_position: _Optional[_Union[_common_pb2.LatLng, _Mapping]] = ..., segments: _Optional[_Iterable[_Union[_rx_common_pb2.PipelineSegmentStatus, str]]] = ...) -> None: ...

class ResourceDeliveryRequest(_message.Message):
    __slots__ = ("task", "resource_color", "delivery_circle_color")
    TASK_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_COLOR_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_CIRCLE_COLOR_FIELD_NUMBER: _ClassVar[int]
    task: _rx_common_pb2.RxTask
    resource_color: _rx_common_pb2.Color
    delivery_circle_color: _rx_common_pb2.Color
    def __init__(self, task: _Optional[_Union[_rx_common_pb2.RxTask, str]] = ..., resource_color: _Optional[_Union[_rx_common_pb2.Color, str]] = ..., delivery_circle_color: _Optional[_Union[_rx_common_pb2.Color, str]] = ...) -> None: ...

class DockingReport(_message.Message):
    __slots__ = ("bay_id",)
    BAY_ID_FIELD_NUMBER: _ClassVar[int]
    bay_id: int
    def __init__(self, bay_id: _Optional[int] = ...) -> None: ...

class FirefightingReport(_message.Message):
    __slots__ = ("window_id",)
    WINDOW_ID_FIELD_NUMBER: _ClassVar[int]
    window_id: int
    def __init__(self, window_id: _Optional[int] = ...) -> None: ...

class IncidentAck(_message.Message):
    __slots__ = ("command_seq",)
    COMMAND_SEQ_FIELD_NUMBER: _ClassVar[int]
    command_seq: int
    def __init__(self, command_seq: _Optional[int] = ...) -> None: ...

class ReadinessReport(_message.Message):
    __slots__ = ("command_seq",)
    COMMAND_SEQ_FIELD_NUMBER: _ClassVar[int]
    command_seq: int
    def __init__(self, command_seq: _Optional[int] = ...) -> None: ...
