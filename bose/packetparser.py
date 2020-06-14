from bose import packets
from bose.packet import PacketHeader, Packet


def from_header(header: PacketHeader, payload: bytes) -> "Packet":
    assert len(payload) == header.payload_length
    type = packets.MAP[header.function_block][(header.function, header.operator)]
    return type(
        header.function_block,
        header.function,
        header.operator,
        payload,
        header.device_id,
        header.port
    )
