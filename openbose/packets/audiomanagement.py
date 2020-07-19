from typing import Dict, Tuple, Type

from openbose import Packet, FunctionBlock, Operator, AudioManagementFunction


class SourceGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.SOURCE, Operator.GET)


class VolumeGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.VOLUME, Operator.GET)


class VolumeSetGetPacket(Packet):
    def __init__(self, volume: int) -> None:
        super().__init__(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.VOLUME, Operator.SET_GET, bytes([volume]))


class SourceStatusPacket(Packet):
    @property
    def available_sources(self):
        # some bitset
        return (self.payload[0] << 8) | self.payload[1]

    @property
    def source_type(self) -> int:
        # TODO: enum: NONE, BLUETOOTH, AUXILIARY
        return self.payload[2]

    @property
    def mac_address(self):
        return self.payload[3:9].hex(sep=":", bytes_per_sep=1)


class VolumeStatusPacket(Packet):
    @property
    def max_volume(self):
        return self.payload[0]

    @property
    def cur_volume(self):
        return self.payload[1]


FUNCTION_OPERATOR_PACKET_TYPE: Dict[Tuple[AudioManagementFunction, Operator], Type[Packet]] = {
    (AudioManagementFunction.SOURCE, Operator.STATUS): SourceStatusPacket,
    (AudioManagementFunction.VOLUME, Operator.STATUS): VolumeStatusPacket
}