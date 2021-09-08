from enum import Enum

LIGHT_API_KEY = 'light'
LUX_API_KEY = 'lux'


class PrecursorEnum(Enum):
    WEBP0 = 'webp0'
    AVIFO0 = 'avifo0'
    JP2O0 = 'jp2o0'
    PRJPG = 'prjpg'
    PNGZO = 'pngzo'
    JXL0 = 'jxl0'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, PrecursorEnum))


class PrecursorToExtensionEnum(Enum):
    WEBP0 = '.webp'
    AVIFO0 = '.AVIF'
    JP2O0 = '.jp2'
    PRJPG = '.jpeg'
    PNGZO = '.png'
    JXL0 = '.jxl'
