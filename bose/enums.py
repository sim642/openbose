from enum import IntEnum
from typing import Type, Dict


class FunctionBlock(IntEnum):
    PRODUCT_INFO = 0
    SETTINGS = 1
    STATUS = 2
    DEVICE_MANAGEMENT = 4
    AUDIO_MANAGEMENT = 5
    # TODO: missing values


class Function(IntEnum):
    pass


class ProductInfoFunction(Function):
    BMAP_VERSION = 1
    PRODUCT_ID_VARIANT = 3
    FIRMWARE_VERSION = 5
    SERIAL_NUMBER = 7
    # TODO: missing values


class SettingsFunction(Function):
    PRODUCT_NAME = 2
    # TODO: missing values


class StatusFunction(Function):
    BATTERY_LEVEL = 2
    # TODO: missing values


class DeviceManagementFunction(Function):
    DISCONNECT = 2
    # TODO: missing values


class AudioManagementFunction(Function):
    SOURCE = 1
    CONTROL = 3
    STATUS = 4
    VOLUME = 5
    NOW_PLAYING = 6
    # TODO: missing values


FUNCTION_BLOCK_FUNCTION_TYPE: Dict[FunctionBlock, Type[Function]] = {
    FunctionBlock.PRODUCT_INFO: ProductInfoFunction,
    FunctionBlock.SETTINGS: SettingsFunction,
    FunctionBlock.STATUS: StatusFunction,
    FunctionBlock.DEVICE_MANAGEMENT: DeviceManagementFunction,
    FunctionBlock.AUDIO_MANAGEMENT: AudioManagementFunction
}


class Operator(IntEnum):
    SET = 0
    GET = 1
    SET_GET = 2
    STATUS = 3
    ERROR = 4
    START = 5
    RESULT = 6
    PROCESSING = 7
