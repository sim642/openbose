from typing import Dict, Tuple, Type

from bose import Packet, FunctionBlock, Operator, SettingsFunction


class ProductNameGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.SETTINGS, SettingsFunction.PRODUCT_NAME, Operator.GET)


class ProductNameStatusPacket(Packet):
    @property
    def is_default_product_name(self):
        return bool(self.payload[0] & 0x01)

    @property
    def product_name(self):
        return self.payload[1:].decode("utf-8")


FUNCTION_OPERATOR_PACKET_TYPE: Dict[Tuple[SettingsFunction, Operator], Type[Packet]] = {
    (SettingsFunction.PRODUCT_NAME, Operator.STATUS): ProductNameStatusPacket
}