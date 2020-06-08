from .enums import *


class PacketBase:
    function_block: FunctionBlock
    function: Function
    operator: Operator
    device_id: int
    port: int

    def __init__(self, function_block: FunctionBlock, function: Function, operator: Operator, device_id: int, port: int) -> None:
        self.function_block = function_block
        self.function = function
        self.operator = operator
        self.device_id = device_id
        self.port = port


class PacketHeader(PacketBase):
    payload_length: int

    def __init__(self, function_block: FunctionBlock, function: Function, operator: Operator, payload_length: int, device_id: int, port: int) -> None:
        super().__init__(function_block, function, operator, device_id, port)
        self.payload_length = payload_length

    def to_bytes(self) -> bytes:
        return bytes([
            self.function_block,
            self.function,
            (self.device_id << 6) | (self.port << 4) | self.operator,
            self.payload_length
        ])


class Packet(PacketBase):
    payload: bytes

    def __init__(self, function_block: FunctionBlock, function: Function, operator: Operator, payload: bytes = b"", device_id: int = 0, port: int = 0) -> None:
        super().__init__(function_block, function, operator, device_id, port)
        self.payload = payload

    @property
    def header(self) -> PacketHeader:
        return PacketHeader(
            self.function_block,
            self.function,
            self.operator,
            len(self.payload),
            self.device_id,
            self.port
        )

    def to_bytes(self) -> bytes:
        return self.header.to_bytes() + self.payload
