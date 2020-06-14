from bose import packets
from bose.packet import Packet


def refine_packet(packet: Packet) -> "Packet":
    packet_type = packets.FUNCTION_BLOCK_FUNCTION_OPERATOR_PACKET_TYPE[packet.function_block][(packet.function, packet.operator)]
    return packet_type(
        packet.function_block,
        packet.function,
        packet.operator,
        packet.payload,
        packet.device_id,
        packet.port
    )
