#!/usr/bin/env python3

from bose import *

address = "4C:87:5D:53:F2:CF"
channel = 8

print("Connecting...")
with Connection(address, channel) as conn:
    print("Connected")

    def command(packet: Packet):
        print("Sending...:", packet)
        conn.write(packet)
        print("Sent")

        print("Receiving...")
        packet = conn.read()
        print("Received:", packet)


    command(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.BMAP_VERSION, Operator.GET))
    command(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.PRODUCT_ID_VARIANT, Operator.GET))
    command(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.SERIAL_NUMBER, Operator.GET))
    command(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.FIRMWARE_VERSION, Operator.GET))

    command(Packet(FunctionBlock.STATUS, StatusFunction.BATTERY_LEVEL, Operator.GET))

    command(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.STATUS, Operator.GET))
    command(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.VOLUME, Operator.GET))
    # command(bytes([5, 6, 5, 0])) # audio now playing
    # print(s.recv(128))
    # print(s.recv(128))
    # print(s.recv(128))
    # print(s.recv(128))
    # print(s.recv(128))
