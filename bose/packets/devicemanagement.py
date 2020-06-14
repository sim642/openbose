from typing import Dict, Tuple, Type

from bose import Packet, Operator, DeviceManagementFunction


class DisconnectProcessingPacket(Packet):
    pass


FUNCTION_OPERATOR_PACKET_TYPE: Dict[Tuple[DeviceManagementFunction, Operator], Type[Packet]] = {
    (DeviceManagementFunction.DISCONNECT, Operator.PROCESSING): DisconnectProcessingPacket
}