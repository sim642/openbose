#!/usr/bin/env python3

from bose import *

address = "4C:87:5D:53:F2:CF"
channel = 8

with Connection(address, channel) as conn:

    def write(packet: Packet):
        print("-->", packet)
        conn.write(packet)

    def read() -> Packet:
        packet = conn.read()
        print("<--", packet)
        return packet


    def command_get(packet: Packet):
        write(packet)
        read()

    def command_start(packet: Packet):
        write(packet)
        processing_packet = Packet(packet.function_block, packet.function, Operator.PROCESSING)
        result_packet = Packet(packet.function_block, packet.function, Operator.RESULT)
        assert read() == processing_packet
        while read() != result_packet:
            pass


    command_get(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.BMAP_VERSION, Operator.GET))
    # command_get(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.PRODUCT_ID_VARIANT, Operator.GET))
    # command_get(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.SERIAL_NUMBER, Operator.GET))
    # command_get(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.FIRMWARE_VERSION, Operator.GET))

    command_get(Packet(FunctionBlock.STATUS, StatusFunction.BATTERY_LEVEL, Operator.GET))

    # command_get(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.STATUS, Operator.GET))
    # command_get(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.VOLUME, Operator.GET))
    command_start(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.NOW_PLAYING, Operator.START))
