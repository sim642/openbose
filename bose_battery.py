#!/usr/bin/env python3

import errno
import socket
import sys

device = "4C:87:5D:53:F2:CF"
port = 8

with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
    print("Connecting...")
    s.connect((device, port))
    print("Connected")

    def command(data):
        print("Sending...:", data)
        s.sendall(data)
        print("Sent")

        print("Receiving...")
        data = s.recv(128)
        print("Received:", data)


    command(bytes([0, 1, 1, 0])) # bmp version
    # command(bytes([0, 3, 1, 0])) # device id
    # command(bytes([0, 7, 1, 0])) # serial number
    # command(bytes([0, 5, 1, 0])) # firmware version
    command(bytes([2, 2, 1, 0])) # battery level

    command(bytes([5, 4, 1, 0])) # audio status
    command(bytes([5, 5, 1, 0])) # audio volume
    command(bytes([5, 6, 5, 0])) # audio now playing
    print(s.recv(128))
    print(s.recv(128))
    print(s.recv(128))
    print(s.recv(128))
    print(s.recv(128))
