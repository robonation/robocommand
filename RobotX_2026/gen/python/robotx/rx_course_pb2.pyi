import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RxCourse(_message.Message):
    __slots__ = ("course_id", "pinger_freq_hz", "corners", "sent_at")
    COURSE_ID_FIELD_NUMBER: _ClassVar[int]
    PINGER_FREQ_HZ_FIELD_NUMBER: _ClassVar[int]
    CORNERS_FIELD_NUMBER: _ClassVar[int]
    SENT_AT_FIELD_NUMBER: _ClassVar[int]
    course_id: str
    pinger_freq_hz: int
    corners: _containers.RepeatedCompositeFieldContainer[_common_pb2.LatLng]
    sent_at: _timestamp_pb2.Timestamp
    def __init__(self, course_id: _Optional[str] = ..., pinger_freq_hz: _Optional[int] = ..., corners: _Optional[_Iterable[_Union[_common_pb2.LatLng, _Mapping]]] = ..., sent_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
