from bose import FunctionBlock
from bose.packets import productinfo, status, settings, audiomanagement, devicemanagement

MAP = {
    FunctionBlock.PRODUCT_INFO: productinfo.MAP,
    FunctionBlock.SETTINGS: settings.MAP,
    FunctionBlock.STATUS: status.MAP,
    FunctionBlock.DEVICE_MANAGEMENT: devicemanagement.MAP,
    FunctionBlock.AUDIO_MANAGEMENT: audiomanagement.MAP,
}