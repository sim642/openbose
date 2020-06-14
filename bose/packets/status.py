from dataclasses import dataclass

from bose import Packet, FunctionBlock, Function, Operator, AudioManagementFunction, StatusFunction


class BatteryLevelGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.STATUS, StatusFunction.BATTERY_LEVEL, Operator.GET)


class BatteryLevelStatusPacket(Packet):
    @property
    def battery_level(self):
        return self.payload[0]


MAP = {
    (StatusFunction.BATTERY_LEVEL, Operator.STATUS): BatteryLevelStatusPacket
}