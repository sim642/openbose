from typing import Dict, Tuple, Type

from openbose import Packet, FunctionBlock, Operator, StatusFunction


class BatteryLevelGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.STATUS, StatusFunction.BATTERY_LEVEL, Operator.GET)


class BatteryLevelStatusPacket(Packet):
    @property
    def battery_level(self):
        return self.payload[0]


FUNCTION_OPERATOR_PACKET_TYPE: Dict[Tuple[StatusFunction, Operator], Type[Packet]] = {
    (StatusFunction.BATTERY_LEVEL, Operator.STATUS): BatteryLevelStatusPacket
}