from typing import Dict, Tuple, Type

from bose import Packet, Operator, DeviceManagementFunction


class ConnectResultPacket(Packet):
    @property
    def mac_address(self):
        return self.payload[0:6].hex(sep=":", bytes_per_sep=1)

    # TODO: what is self.payload[6]? official app doesn't use


class DisconnectProcessingPacket(Packet):
    pass


FUNCTION_OPERATOR_PACKET_TYPE: Dict[Tuple[DeviceManagementFunction, Operator], Type[Packet]] = {
    (DeviceManagementFunction.CONNECT, Operator.RESULT): ConnectResultPacket,
    (DeviceManagementFunction.DISCONNECT, Operator.PROCESSING): DisconnectProcessingPacket
}