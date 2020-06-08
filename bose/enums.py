from enum import IntEnum


class FunctionBlock(IntEnum):
    PRODUCT_INFO = 0
    STATUS = 2
    AUDIO_MANAGEMENT = 5
    # TODO: missing values


class ProductInfoFunction(IntEnum):
    BMAP_VERSION = 1
    PRODUCT_ID_VARIANT = 3
    FIRMWARE_VERSION = 5
    SERIAL_NUMBER = 7
    # TODO: missing values


class StatusFunction(IntEnum):
    BATTERY_LEVEL = 2
    # TODO: missing values


class AudioManagementFunction(IntEnum):
    SOURCE = 1
    CONTROL = 3
    STATUS = 4
    VOLUME = 5
    NOW_PLAYING = 6
    # TODO: missing values


class Operator(IntEnum):
    SET = 0
    GET = 1
    SET_GET = 2
    STATUS = 3
    ERROR = 4
    START = 5
    RESULT = 6
    PROCESSING = 7
