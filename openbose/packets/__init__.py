from typing import Dict, Tuple, Type

from openbose import FunctionBlock, Function, Operator, Packet
from openbose.packets import productinfo, status, settings, audiomanagement, devicemanagement


FUNCTION_BLOCK_FUNCTION_OPERATOR_PACKET_TYPE: Dict[FunctionBlock, Dict[Tuple[Function, Operator], Type[Packet]]] = {
    FunctionBlock.PRODUCT_INFO: productinfo.FUNCTION_OPERATOR_PACKET_TYPE,
    FunctionBlock.SETTINGS: settings.FUNCTION_OPERATOR_PACKET_TYPE,
    FunctionBlock.STATUS: status.FUNCTION_OPERATOR_PACKET_TYPE,
    FunctionBlock.DEVICE_MANAGEMENT: devicemanagement.FUNCTION_OPERATOR_PACKET_TYPE,
    FunctionBlock.AUDIO_MANAGEMENT: audiomanagement.FUNCTION_OPERATOR_PACKET_TYPE,
}


def refine_packet(packet: Packet) -> "Packet":
    packet_type = FUNCTION_BLOCK_FUNCTION_OPERATOR_PACKET_TYPE.get(packet.function_block, {}).get((packet.function, packet.operator))
    if packet_type is not None:
        return packet_type(
            packet.function_block,
            packet.function,
            packet.operator,
            packet.payload,
            packet.device_id,
            packet.port
        )
    else:
        return packet
