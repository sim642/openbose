from typing import Dict, Tuple, Type, Optional

from openbose import Packet, Operator, DeviceManagementFunction, FunctionBlock, ProductType


class ConnectResultPacket(Packet):
    @property
    def mac_address(self):
        return self.payload[0:6].hex(sep=":", bytes_per_sep=1)

    # TODO: what is self.payload[6]? official app doesn't use


class DisconnectProcessingPacket(Packet):
    pass


class ListDevicesGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.DEVICE_MANAGEMENT, DeviceManagementFunction.LIST_DEVICES, Operator.GET)


class ListDevicesStatusPacket(Packet):
    @property
    def mac_addresses(self):
        # ignore self.payload[0]
        mac_addresses = []
        for i in range(1, len(self.payload), 6):
            mac_address_bytes = self.payload[i:i + 6]
            mac_addresses.append(mac_address_bytes.hex(sep=":", bytes_per_sep=1))
        return mac_addresses


class InfoGetPacket(Packet):
    def __init__(self, mac_address) -> None:
        payload = bytes.fromhex(mac_address.replace(":", ""))
        super().__init__(FunctionBlock.DEVICE_MANAGEMENT, DeviceManagementFunction.INFO, Operator.GET, payload)


class InfoStatusPacket(Packet):
    @property
    def mac_address(self):
        return self.payload[0:6].hex(sep=":", bytes_per_sep=1)

    @property
    def connected(self) -> bool:
        return bool(self.payload[6] & 1)

    @property
    def local_device(self) -> bool:
        # True = primary, False = secondary
        return bool((self.payload[6] >> 1) & 1)

    @property
    def bose_product(self) -> bool:
        return bool((self.payload[6] >> 2) & 1)

    @property
    def product_type(self) -> Optional[ProductType]:
        if self.bose_product:
            return ProductType((self.payload[6] >> 7) & 1)
        else:
            return None

    # what do self.payload[7] and self.payload[8] mean for non-bose devices?

    @property
    def product_id(self) -> Optional[int]:
        if self.bose_product:
            return (self.payload[7] << 8) | self.payload[8]
        else:
            return None

    @property
    def variant_id(self) -> Optional[int]:
        if self.bose_product:
            return self.payload[9]
        else:
            return None

    @property
    def name(self) -> str:
        name_index = 10 if self.bose_product else 9
        return self.payload[name_index:].decode("utf-8")


FUNCTION_OPERATOR_PACKET_TYPE: Dict[Tuple[DeviceManagementFunction, Operator], Type[Packet]] = {
    (DeviceManagementFunction.CONNECT, Operator.RESULT): ConnectResultPacket,
    (DeviceManagementFunction.DISCONNECT, Operator.PROCESSING): DisconnectProcessingPacket,
    (DeviceManagementFunction.LIST_DEVICES, Operator.STATUS): ListDevicesStatusPacket,
    (DeviceManagementFunction.INFO, Operator.STATUS): InfoStatusPacket
}