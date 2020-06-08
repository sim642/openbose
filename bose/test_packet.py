from unittest import TestCase

from bose import *


class TestPacket(TestCase):
    def test_to_bytes(self):
        self.assertEqual(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.BMAP_VERSION, Operator.GET).to_bytes(), bytes([0, 1, 1, 0]))
        self.assertEqual(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.PRODUCT_ID_VARIANT, Operator.GET).to_bytes(), bytes([0, 3, 1, 0]))
        self.assertEqual(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.FIRMWARE_VERSION, Operator.GET).to_bytes(), bytes([0, 5, 1, 0]))
        self.assertEqual(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.SERIAL_NUMBER, Operator.GET).to_bytes(), bytes([0, 7, 1, 0]))

        self.assertEqual(Packet(FunctionBlock.STATUS, StatusFunction.BATTERY_LEVEL, Operator.GET).to_bytes(), bytes([2, 2, 1, 0]))

        self.assertEqual(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.SOURCE, Operator.GET).to_bytes(), bytes([5, 1, 1, 0]))
        self.assertEqual(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.CONTROL, Operator.GET).to_bytes(), bytes([5, 3, 1, 0]))
        self.assertEqual(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.STATUS, Operator.GET).to_bytes(), bytes([5, 4, 1, 0]))
        self.assertEqual(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.VOLUME, Operator.GET).to_bytes(), bytes([5, 5, 1, 0]))
        self.assertEqual(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.NOW_PLAYING, Operator.START).to_bytes(), bytes([5, 6, 5, 0]))

    def test_from_bytes(self):
        self.assertEqual(Packet.from_bytes(bytes([2, 2, 3, 1, 50])), Packet(FunctionBlock.STATUS, StatusFunction.BATTERY_LEVEL, Operator.STATUS, bytes([50])))
        self.assertNotEqual(Packet.from_bytes(bytes([2, 2, 3, 1, 50])), Packet(FunctionBlock.STATUS, StatusFunction.BATTERY_LEVEL, Operator.STATUS, bytes([20])))
