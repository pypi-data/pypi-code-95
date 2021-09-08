"""
This module contains functions for understanding the ISO Base Media File Format
(ISO-BMFF), ISO standard 14496-12.

We need these functions in order to understand the contents of AVIF and HEIF
image file formats.

Note that this module requires Python 3.7+, so it can be used in sc_pack v2,
ml_image_optimization and toilmore, but not imported from `opt_pipeline`.
If the need to use it there arises, please refactor to avoid the use of
dataclasses.

"""

import struct
from dataclasses import dataclass
from typing import Set, Optional


@dataclass
class ISOBMFFBox:
    start_offset: int
    byte_size: int
    boxtype: bytes
    skip: int
    version: Optional[int]
    flags: Optional[int]

    def payload(self, contents: bytes) -> bytes:
        return contents[
           self.start_offset + self.skip:self.start_offset + self.byte_size
        ]


def parse_isobmffbox(
        buffer: bytes,
        from_offset: int,
        full_box: bool = False
) -> ISOBMFFBox:
    size_compact, tc0, tc1, tc2, tc3 = struct.unpack_from(
        ">Icccc",
        buffer,
        from_offset
    )
    type_compact_s4 = b''.join((tc0, tc1, tc2, tc3))
    skip = 8  # Contains the number of bytes we need to skip to get to the next
    # box *inside* this one
    next_format_string = ""
    has_extended_size = False
    has_extended_type = False
    if size_compact == 1:
        has_extended_size = True
        next_format_string = ">Q"
        skip += 8
    if type_compact_s4 == b'uuid':
        has_extended_type = True
        next_format_string += ">16c"
        skip += 16
    if has_extended_size or has_extended_type:
        next_items = struct.unpack_from(
            next_format_string,
            buffer,
            from_offset + 8
        )
    if has_extended_size:
        # noinspection PyUnboundLocalVariable
        box_size = next_items[0]
    elif size_compact == 0:
        box_size = len(buffer) - from_offset
    else:
        box_size = size_compact
    if has_extended_type:
        ni_offset = 1 if has_extended_size else 0
        boxtype = b''.join(next_items[ni_offset:])
    else:
        boxtype = type_compact_s4

    if full_box:
        (w,) = struct.unpack_from('>I', buffer, from_offset + skip)
        version = w >> 24
        flags = w & 0x00ffffff
        skip += 4
        return ISOBMFFBox(
            start_offset=from_offset,
            byte_size=box_size,
            boxtype=boxtype,
            skip=skip,
            version=version,
            flags=flags
        )
    else:
        return ISOBMFFBox(
            start_offset=from_offset,
            byte_size=box_size,
            boxtype=boxtype,
            skip=skip,
            version=None,
            flags=None
        )


def parse_ftyp_payload(ftyp: ISOBMFFBox, contents: bytes):
    payload = ftyp.payload(contents)
    m0, m1, m2, m3, v = struct.unpack_from(">ccccI", payload)
    major = b''.join((m0, m1, m2, m3))
    icursor = 8  # A cursor inside payload ...
    minors = []
    while icursor < len(payload):
        m0, m1, m2, m3 = struct.unpack_from(">cccc", payload, icursor)
        minor = b''.join((m0, m1, m2, m3))
        minors.append(minor)
        icursor += 4
    return major, v, minors


def brands_in_heif_file(ftyp: ISOBMFFBox,  content: bytes) -> Set[bytes]:
    """

    :param ftyp: The box parsed from the start of the file.
    :param content: The full contents of the file, or at least a size-able
    chunk of it (say, first 120 bytes).
    :return:
    """
    main_brand, _version, other_brands = parse_ftyp_payload(ftyp, content)
    result = {main_brand}
    result.update(other_brands)
    return result


def file_is_avif(content: bytes) -> bool:
    """
    :param content: The full contents of the file, or at least a size-able
    chunk of it (say, first 120 bytes).
    :return:
    """
    # First, let's ensure this is an ISOBMFF file
    maybe_ftyp = parse_isobmffbox(content, 0, False)
    if maybe_ftyp.boxtype == b'ftyp':
        # Good!
        brands = brands_in_heif_file(maybe_ftyp, content)
        return (b'avif' in brands)
    else:
        return False


@dataclass
class BasicJP2000Metadata:
    """
    Contains basic size and alpha information for JPEG2000
    images.
    """
    img_width: int
    img_height: int
    channel_count: int


def navigate_to_ihdr_box_jp2000(
        contents: bytes) -> ISOBMFFBox:
    sigbox = parse_isobmffbox(contents, 0)
    ftyp_box = parse_isobmffbox(contents, sigbox.byte_size)
    header_superbox = parse_isobmffbox(
        contents,
        sigbox.byte_size + ftyp_box.byte_size
    )
    ihdr_box = parse_isobmffbox(
        contents,
        sigbox.byte_size + ftyp_box.byte_size + header_superbox.skip
    )
    return ihdr_box


def parse_jp2_ihdr_box(
        ihdr_box: ISOBMFFBox,
        contents: bytes
        ) -> BasicJP2000Metadata:
    """

    :param ihdr_box: The box with the JPEG2000 image header
    :param contents: The first few bytes of the image data ...
    :return:
    """
    use_offset = ihdr_box.start_offset + ihdr_box.skip
    (img_height, img_width, channel_count) = \
        struct.unpack_from(">IIH", contents, use_offset)
    return BasicJP2000Metadata(
        img_width=img_width,
        img_height=img_height,
        channel_count=channel_count
        )


def basic_metadata_of_JPEG2000(
        contents: bytes) -> BasicJP2000Metadata:
    """

    :param contents: The first few bytes
    :return: Basic stuff, like pixel size and such
    """
    try:
        ihdr_box = navigate_to_ihdr_box_jp2000(contents)
    except struct.error:
        raise ValueError('BadImageDataOrTooShort')
    return parse_jp2_ihdr_box(ihdr_box, contents)


@dataclass
class BasicAVIFMetadata:
    """
    Contains basic size and alpha information for JPEG2000
    images.
    """
    img_width: int
    img_height: int


def basic_metadata_of_avif(
        contents: bytes) -> BasicAVIFMetadata:
    # Attention: for this function we basically need to read the entire file,
    # no shortcuts.... (WHAT ARE THOSE DAMN TWITS THINKING!?)
    ispe_box = get_ispe_box(contents)
    (image_width, image_height) = parse_ispe_box(ispe_box, contents)
    return BasicAVIFMetadata(
        img_width=image_width,
        img_height=image_height
    )


def parse_ispe_box(ispe: ISOBMFFBox, contents:bytes):
    (image_width, image_height) = struct.unpack_from(
        '>II',
        contents[ispe.start_offset+ispe.skip:ispe.start_offset+ispe.byte_size]
    )
    return image_width, image_height


def get_ispe_box(contents: bytes) -> ISOBMFFBox:
    """
    Let's go box-diving!
    :param contents:  The entire file
    :return: The ispe box, if it exists
    """
    ftyp = parse_isobmffbox(contents, 0)
    cursor = ftyp.byte_size
    nb = parse_isobmffbox(contents, cursor)
    while nb.boxtype != b'meta':
        cursor += nb.byte_size
        nb = parse_isobmffbox(contents, cursor)
    assert nb.boxtype == b'meta'
    # Re-parse, this is a fullbox
    meta_box = parse_isobmffbox(contents, cursor, full_box=True)
    # meta: Go in!
    cursor = cursor + meta_box.skip
    nb = parse_isobmffbox(contents, cursor)
    while nb.boxtype != b'iprp':
        cursor += nb.byte_size
        nb = parse_isobmffbox(contents, cursor)
    assert nb.boxtype == b'iprp'
    # iprp: Go in!
    cursor = cursor + nb.skip
    nb = parse_isobmffbox(contents, cursor)
    while nb.boxtype != b'ipco':
        cursor += nb.byte_size
        nb = parse_isobmffbox(contents, cursor)
    assert nb.boxtype == b'ipco'
    # ipco: Go in!
    cursor = cursor + nb.skip
    nb = parse_isobmffbox(contents, cursor)
    while nb.boxtype != b'ispe':
        cursor += nb.byte_size
        nb = parse_isobmffbox(contents, cursor)
    assert nb.boxtype == b'ispe'
    ispe = parse_isobmffbox(contents, cursor, full_box=True)
    return ispe
