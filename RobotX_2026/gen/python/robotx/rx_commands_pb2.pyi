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

class RxCommand(_message.Message):
    __slots__ = ("team_id", "seq", "sent_at", "vehicle_id", "run_start", "assistance_request", "keep_out_zone", "all_clear", "moving_object_alert", "readiness_confirm")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SENT_AT_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_START_FIELD_NUMBER: _ClassVar[int]
    ASSISTANCE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    KEEP_OUT_ZONE_FIELD_NUMBER: _ClassVar[int]
    ALL_CLEAR_FIELD_NUMBER: _ClassVar[int]
    MOVING_OBJECT_ALERT_FIELD_NUMBER: _ClassVar[int]
    READINESS_CONFIRM_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    seq: int
    sent_at: _timestamp_pb2.Timestamp
    vehicle_id: str
    run_start: RunStart
    assistance_request: AssistanceRequest
    keep_out_zone: KeepOutZone
    all_clear: AllClear
    moving_object_alert: MovingObjectAlert
    readiness_confirm: ReadinessConfirm
    def __init__(self, team_id: _Optional[str] = ..., seq: _Optional[int] = ..., sent_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., vehicle_id: _Optional[str] = ..., run_start: _Optional[_Union[RunStart, _Mapping]] = ..., assistance_request: _Optional[_Union[AssistanceRequest, _Mapping]] = ..., keep_out_zone: _Optional[_Union[KeepOutZone, _Mapping]] = ..., all_clear: _Optional[_Union[AllClear, _Mapping]] = ..., moving_object_alert: _Optional[_Union[MovingObjectAlert, _Mapping]] = ..., readiness_confirm: _Optional[_Union[ReadinessConfirm, _Mapping]] = ...) -> None: ...

class RunStart(_message.Message):
    __slots__ = ("declaration_seq", "run_id")
    DECLARATION_SEQ_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    declaration_seq: int
    run_id: int
    def __init__(self, declaration_seq: _Optional[int] = ..., run_id: _Optional[int] = ...) -> None: ...

class AssistanceRequest(_message.Message):
    __slots__ = ("position", "vehicle_type")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    position: _common_pb2.LatLng
    vehicle_type: _rx_common_pb2.VehicleType
    def __init__(self, position: _Optional[_Union[_common_pb2.LatLng, _Mapping]] = ..., vehicle_type: _Optional[_Union[_rx_common_pb2.VehicleType, str]] = ...) -> None: ...

class ReadinessConfirm(_message.Message):
    __slots__ = ("report_seq", "vehicle_id")
    REPORT_SEQ_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_ID_FIELD_NUMBER: _ClassVar[int]
    report_seq: int
    vehicle_id: str
    def __init__(self, report_seq: _Optional[int] = ..., vehicle_id: _Optional[str] = ...) -> None: ...

class KeepOutZone(_message.Message):
    __slots__ = ("center", "radius_m", "vehicle_type")
    CENTER_FIELD_NUMBER: _ClassVar[int]
    RADIUS_M_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    center: _common_pb2.LatLng
    radius_m: float
    vehicle_type: _rx_common_pb2.VehicleType
    def __init__(self, center: _Optional[_Union[_common_pb2.LatLng, _Mapping]] = ..., radius_m: _Optional[float] = ..., vehicle_type: _Optional[_Union[_rx_common_pb2.VehicleType, str]] = ...) -> None: ...

class AllClear(_message.Message):
    __slots__ = ("vehicle_type",)
    VEHICLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    vehicle_type: _rx_common_pb2.VehicleType
    def __init__(self, vehicle_type: _Optional[_Union[_rx_common_pb2.VehicleType, str]] = ...) -> None: ...

class MovingObjectAlert(_message.Message):
    __slots__ = ("position", "heading_deg", "speed_mps", "affected_vehicle_types")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    HEADING_DEG_FIELD_NUMBER: _ClassVar[int]
    SPEED_MPS_FIELD_NUMBER: _ClassVar[int]
    AFFECTED_VEHICLE_TYPES_FIELD_NUMBER: _ClassVar[int]
    position: _common_pb2.LatLng
    heading_deg: float
    speed_mps: float
    affected_vehicle_types: _containers.RepeatedScalarFieldContainer[_rx_common_pb2.VehicleType]
    def __init__(self, position: _Optional[_Union[_common_pb2.LatLng, _Mapping]] = ..., heading_deg: _Optional[float] = ..., speed_mps: _Optional[float] = ..., affected_vehicle_types: _Optional[_Iterable[_Union[_rx_common_pb2.VehicleType, str]]] = ...) -> None: ...
