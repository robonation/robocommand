from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RobotState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATE_UNKNOWN: _ClassVar[RobotState]
    STATE_KILLED: _ClassVar[RobotState]
    STATE_MANUAL: _ClassVar[RobotState]
    STATE_AUTO: _ClassVar[RobotState]

class TaskTier(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TIER_UNKNOWN: _ClassVar[TaskTier]
    TIER_NONE: _ClassVar[TaskTier]
    TIER_CORE: _ClassVar[TaskTier]
    TIER_ADVANCED: _ClassVar[TaskTier]
    TIER_DISRUPTIVE: _ClassVar[TaskTier]
STATE_UNKNOWN: RobotState
STATE_KILLED: RobotState
STATE_MANUAL: RobotState
STATE_AUTO: RobotState
TIER_UNKNOWN: TaskTier
TIER_NONE: TaskTier
TIER_CORE: TaskTier
TIER_ADVANCED: TaskTier
TIER_DISRUPTIVE: TaskTier

class LatLng(_message.Message):
    __slots__ = ("latitude", "longitude")
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    latitude: float
    longitude: float
    def __init__(self, latitude: _Optional[float] = ..., longitude: _Optional[float] = ...) -> None: ...
