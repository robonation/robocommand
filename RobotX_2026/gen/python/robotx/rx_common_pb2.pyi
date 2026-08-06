from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class RxTask(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_UNKNOWN: _ClassVar[RxTask]
    TASK_NONE: _ClassVar[RxTask]
    TASK_SAFE_PASSAGE: _ClassVar[RxTask]
    TASK_INFRA_SURVEY_REPAIR: _ClassVar[RxTask]
    TASK_COORDINATED_LOGISTICS: _ClassVar[RxTask]
    TASK_DYNAMIC_INCIDENT: _ClassVar[RxTask]

class VehicleType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TYPE_UNKNOWN: _ClassVar[VehicleType]
    TYPE_USV: _ClassVar[VehicleType]
    TYPE_UUV: _ClassVar[VehicleType]
    TYPE_UAV: _ClassVar[VehicleType]

class BeaconState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BEACON_STATE_UNKNOWN: _ClassVar[BeaconState]
    BEACON_STATE_OFF: _ClassVar[BeaconState]
    BEACON_STATE_FLASHING_RED: _ClassVar[BeaconState]
    BEACON_STATE_FLASHING_GREEN: _ClassVar[BeaconState]
    BEACON_STATE_FLASHING_BLUE: _ClassVar[BeaconState]
    BEACON_STATE_STEADY_BLUE: _ClassVar[BeaconState]

class PipelineSegmentStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PIPELINE_SEGMENT_UNKNOWN: _ClassVar[PipelineSegmentStatus]
    PIPELINE_SEGMENT_INTACT: _ClassVar[PipelineSegmentStatus]
    PIPELINE_SEGMENT_DAMAGED: _ClassVar[PipelineSegmentStatus]

class FlightPhase(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FLIGHT_PHASE_UNKNOWN: _ClassVar[FlightPhase]
    FLIGHT_PHASE_GROUNDED: _ClassVar[FlightPhase]
    FLIGHT_PHASE_AIRBORNE: _ClassVar[FlightPhase]

class Color(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COLOR_UNKNOWN: _ClassVar[Color]
    COLOR_RED: _ClassVar[Color]
    COLOR_GREEN: _ClassVar[Color]
    COLOR_BLUE: _ClassVar[Color]
    COLOR_ANY: _ClassVar[Color]
TASK_UNKNOWN: RxTask
TASK_NONE: RxTask
TASK_SAFE_PASSAGE: RxTask
TASK_INFRA_SURVEY_REPAIR: RxTask
TASK_COORDINATED_LOGISTICS: RxTask
TASK_DYNAMIC_INCIDENT: RxTask
TYPE_UNKNOWN: VehicleType
TYPE_USV: VehicleType
TYPE_UUV: VehicleType
TYPE_UAV: VehicleType
BEACON_STATE_UNKNOWN: BeaconState
BEACON_STATE_OFF: BeaconState
BEACON_STATE_FLASHING_RED: BeaconState
BEACON_STATE_FLASHING_GREEN: BeaconState
BEACON_STATE_FLASHING_BLUE: BeaconState
BEACON_STATE_STEADY_BLUE: BeaconState
PIPELINE_SEGMENT_UNKNOWN: PipelineSegmentStatus
PIPELINE_SEGMENT_INTACT: PipelineSegmentStatus
PIPELINE_SEGMENT_DAMAGED: PipelineSegmentStatus
FLIGHT_PHASE_UNKNOWN: FlightPhase
FLIGHT_PHASE_GROUNDED: FlightPhase
FLIGHT_PHASE_AIRBORNE: FlightPhase
COLOR_UNKNOWN: Color
COLOR_RED: Color
COLOR_GREEN: Color
COLOR_BLUE: Color
COLOR_ANY: Color
