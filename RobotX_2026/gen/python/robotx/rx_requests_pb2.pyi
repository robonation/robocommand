import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RxRequest(_message.Message):
    __slots__ = ("team_id", "seq", "sent_at", "run_declaration")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SENT_AT_FIELD_NUMBER: _ClassVar[int]
    RUN_DECLARATION_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    seq: int
    sent_at: _timestamp_pb2.Timestamp
    run_declaration: RunDeclaration
    def __init__(self, team_id: _Optional[str] = ..., seq: _Optional[int] = ..., sent_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., run_declaration: _Optional[_Union[RunDeclaration, _Mapping]] = ...) -> None: ...

class RunDeclaration(_message.Message):
    __slots__ = ("vehicle_ids", "task1_tier", "task2_tier", "task3_tier", "task4_tier", "uav_geofence")
    VEHICLE_IDS_FIELD_NUMBER: _ClassVar[int]
    TASK1_TIER_FIELD_NUMBER: _ClassVar[int]
    TASK2_TIER_FIELD_NUMBER: _ClassVar[int]
    TASK3_TIER_FIELD_NUMBER: _ClassVar[int]
    TASK4_TIER_FIELD_NUMBER: _ClassVar[int]
    UAV_GEOFENCE_FIELD_NUMBER: _ClassVar[int]
    vehicle_ids: _containers.RepeatedScalarFieldContainer[str]
    task1_tier: _common_pb2.TaskTier
    task2_tier: _common_pb2.TaskTier
    task3_tier: _common_pb2.TaskTier
    task4_tier: _common_pb2.TaskTier
    uav_geofence: _containers.RepeatedCompositeFieldContainer[_common_pb2.LatLng]
    def __init__(self, vehicle_ids: _Optional[_Iterable[str]] = ..., task1_tier: _Optional[_Union[_common_pb2.TaskTier, str]] = ..., task2_tier: _Optional[_Union[_common_pb2.TaskTier, str]] = ..., task3_tier: _Optional[_Union[_common_pb2.TaskTier, str]] = ..., task4_tier: _Optional[_Union[_common_pb2.TaskTier, str]] = ..., uav_geofence: _Optional[_Iterable[_Union[_common_pb2.LatLng, _Mapping]]] = ...) -> None: ...
