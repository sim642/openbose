from dataclasses import dataclass

from .enums import *


@dataclass
class PacketBase:
    function_block: FunctionBlock
    function: Function
    operator: Operator
    device_id: int
    port: int


@dataclass
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

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketHeader":
        function_block = FunctionBlock(data[0])
        function_type = FUNCTION_BLOCK_FUNCTION_TYPE[function_block]
        return PacketHeader(
            function_block,
            function_type(data[1]),
            Operator(data[2] & 15),
            data[3],
            data[2] >> 6,
            (data[2] >> 4) & 3
        )


@dataclass
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

    @classmethod
    def from_bytes(cls, data: bytes) -> "Packet":
        header = PacketHeader.from_bytes(data[:4])
        payload = data[4:]
        assert len(payload) == header.payload_length
        return Packet(
            header.function_block,
            header.function,
            header.operator,
            payload,
            header.device_id,
            header.port
        )
