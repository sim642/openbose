from bose import Packet, FunctionBlock, Function, Operator, AudioManagementFunction, DeviceManagementFunction


class DisconnectProcessingPacket(Packet):
    pass


MAP = {
    (DeviceManagementFunction.DISCONNECT, Operator.PROCESSING): DisconnectProcessingPacket
}