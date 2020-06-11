import socket
from typing import BinaryIO

from bose import Packet
from bose.packet import PacketHeader


class ConnectionBase:
    io: BinaryIO

    def __init__(self, io: BinaryIO = None) -> None:
        self.io = io

    def write(self, packet: Packet) -> None:
        self.io.write(packet.to_bytes())
        self.io.flush()

    def read(self) -> Packet:
        header = PacketHeader.from_bytes(self.io.read(4))
        payload = self.io.read(header.payload_length)
        return Packet.from_header(header, payload)


class Connection(ConnectionBase):
    address: str
    channel: int

    socket: socket

    def __init__(self, address: str, channel: int) -> None:
        super().__init__()
        self.address = address
        self.channel = channel

    def __enter__(self) -> "Connection":
        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.socket.connect((self.address, self.channel))
        self.io = self.socket.makefile("rwb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.io.close()
        self.socket.close()
