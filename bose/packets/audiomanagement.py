from bose import Packet, FunctionBlock, Function, Operator, AudioManagementFunction


class VolumeGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.VOLUME, Operator.GET)


class VolumeSetGetPacket(Packet):
    def __init__(self, volume: int) -> None:
        super().__init__(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.VOLUME, Operator.SET_GET, bytes([volume]))


class VolumeStatusPacket(Packet):
    @property
    def max_volume(self):
        return self.payload[0]

    @property
    def cur_volume(self):
        return self.payload[1]


MAP = {
    (AudioManagementFunction.VOLUME, Operator.STATUS): VolumeStatusPacket
}