from enum import IntEnum
from typing import Dict, Tuple, Type

from openbose import Packet, FunctionBlock, Operator, AudioManagementFunction


class SourceGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.SOURCE, Operator.GET)


class StatusGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.STATUS, Operator.GET)


class VolumeGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.VOLUME, Operator.GET)


class VolumeSetGetPacket(Packet):
    def __init__(self, volume: int) -> None:
        super().__init__(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.VOLUME, Operator.SET_GET, bytes([volume]))


class NowPlayingStartPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.NOW_PLAYING, Operator.START)


class SourceType(IntEnum):
    NONE = 0
    BLUETOOTH = 1
    AUXILIARY = 2


class SourceStatusPacket(Packet):
    @property
    def available_sources(self):
        # some bitset
        return (self.payload[0] << 8) | self.payload[1]

    @property
    def source_type(self) -> SourceType:
        return SourceType(self.payload[2])

    @property
    def mac_address(self):
        return self.payload[3:9].hex(sep=":", bytes_per_sep=1)


class Status(IntEnum):
    STOP = 0
    PLAY = 1
    PAUSE = 2
    # TODO: some are not actually valid statuses, only controls?
    # TRACK_FORWARD = 3
    # TRACK_BACK = 4
    FAST_FORWARD_PRESS = 5
    # FAST_FORWARD_RELEASE = 6
    REWIND_PRESS = 7
    # REWIND_RELEASE = 8


class StatusStatusPacket(Packet):
    @property
    def status(self) -> Status:
        return Status(self.payload[0])

    @property
    def track_position(self) -> int:
        # TODO: figure out usage and unit
        if len(self.payload) == 1 + 2:
            return (self.payload[1] << 8) | self.payload[2]
        else:
            return 0xFFFF


class VolumeStatusPacket(Packet):
    @property
    def max_volume(self):
        return self.payload[0]

    @property
    def cur_volume(self):
        return self.payload[1]


class NowPlayingAttribute(IntEnum):
    SONG_TITLE = 0
    ARTIST = 1
    ALBUM = 2
    TRACK_NUMBER = 3
    TOTAL_NUMBER_OF_TRACKS = 4
    GENRE = 5
    PLAYING_TIME = 6


class NowPlayingStatusPacket(Packet):
    @property
    def attribute(self) -> NowPlayingAttribute:
        return NowPlayingAttribute(self.payload[0])
    
    @property
    def value(self) -> str:
        return self.payload[1:].decode("utf-8")


class NowPlayingProcessingPacket(Packet):
    pass


class NowPlayingResultPacket(Packet):
    pass


FUNCTION_OPERATOR_PACKET_TYPE: Dict[Tuple[AudioManagementFunction, Operator], Type[Packet]] = {
    (AudioManagementFunction.SOURCE, Operator.STATUS): SourceStatusPacket,
    (AudioManagementFunction.STATUS, Operator.STATUS): StatusStatusPacket,
    (AudioManagementFunction.VOLUME, Operator.STATUS): VolumeStatusPacket,
    (AudioManagementFunction.NOW_PLAYING, Operator.STATUS): NowPlayingStatusPacket,
    (AudioManagementFunction.NOW_PLAYING, Operator.PROCESSING): NowPlayingProcessingPacket,
    (AudioManagementFunction.NOW_PLAYING, Operator.RESULT): NowPlayingResultPacket,
}