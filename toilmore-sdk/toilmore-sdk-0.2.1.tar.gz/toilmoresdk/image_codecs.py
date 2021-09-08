from enum import Enum
import re
from typing import Optional

from .isobmff import file_is_avif


class RecognizedImageType(Enum):
    """
    The numbers are a bit arbitrary, to avoid
    confusing the values with arithmetic...

    TO-DO: Recognize more image types ...
    """
    GIF = 201
    PNG = 301
    JPG = 401
    WEBP = 501
    JPEG2000 = 601
    AVIF = 701
    TIFF = 801
    BMP = 901

    @property
    def inherent_lossless(self) -> bool:
        return self in (RecognizedImageType.PNG, )

    @staticmethod
    def list():
        return list(map(lambda c: c.name, RecognizedImageType))


_GIF_RE = re.compile(rb'GIF8[79]a')
_JPEG2000_PREFIX = b'\x00\x00\x00\x0c\x6a\x50\x20\x20\x0d\x0a\x87\x0a'


def image_type_from_first_bytes(
    first_bytes: bytes
) -> Optional[RecognizedImageType]:
    """
    NOTE that we can use `img.format` if we have `img` as a PIL.Image instance;
    use this only in those cases where you don't want to open and load the full
    file for performance reasons or if PILIM can't open the file natively
    (e.g. for WEBP, TIFF and OpenEXR, FLIF, BGP....)

    :param first_bytes: only 16 bytes needed
    :return:
    """
    if first_bytes[:4] == b'\x89PNG':
        return RecognizedImageType.PNG
    elif first_bytes[:2] == b'\xff\xd8':
        return RecognizedImageType.JPG
    elif first_bytes[:4] == b'RIFF' and first_bytes[8:12] == b'WEBP':
        return RecognizedImageType.WEBP
    elif re.match(_GIF_RE, first_bytes[:6]):
        return RecognizedImageType.GIF
    elif first_bytes[:4] in (b'II\x2a\x00', b'MM\x00\x2a'):
        return RecognizedImageType.TIFF
    elif first_bytes[:len(_JPEG2000_PREFIX)] == _JPEG2000_PREFIX:
        # Note: JPEG2000 files use roughly the same box
        # organization than HEIF/AVIF files...
        return RecognizedImageType.JPEG2000
    elif first_bytes[:2] == b'BM':
        return RecognizedImageType.BMP
    elif file_is_avif(first_bytes):
        return RecognizedImageType.AVIF
    else:
        return None
