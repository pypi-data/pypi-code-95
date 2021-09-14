from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import dask.array as da
    import numpy as np

    from bioformats_jar import loci


def dtype(reader: loci.formats.IFormatReader) -> str:
    fmt2type: dict[int, str] = {
        0: "i1",  # int8
        1: "u1",  # uint8
        2: "i2",  # int16
        3: "u2",  # uint16
        4: "i4",  # int32
        5: "u4",  # uint32
        6: "f4",  # float32
        7: "f8",  # float64
    }
    le = reader.isLittleEndian()
    return ("<" if le else ">") + fmt2type[reader.getPixelType()]


def shape(reader: loci.formats.IFormatReader) -> tuple[int, int, int, int, int]:
    # currently hardcoded as TCZYX
    r = reader
    return (
        r.getSizeT(),
        r.getRGBChannelCount() if r.isRGB() else r.getSizeC(),
        r.getSizeZ(),
        r.getSizeY(),
        r.getSizeX(),
    )


def set_loci_log_level(level="ERROR"):
    from bioformats_jar import loci

    loci.common.DebugTools.setRootLevel(level)


def reader2dask(reader: loci.formats.IFormatReader) -> da.Array:
    from threading import Lock

    import dask.array as da

    lock = Lock()
    nt, nc, nz, ny, nx = shape(reader)
    return da.map_blocks(
        _load_block,
        reader,
        lock,
        chunks=((1,) * nt, (1,) * nc, (1,) * nz, (ny,), (nx,)),
        dtype=dtype(reader),
    )


def _load_block(
    reader: loci.formats.IFormatReader, lock, block_info: dict
) -> np.ndarray:
    """Load a single plane with a loci reader"""
    import numpy as np

    info = block_info[None]
    idx = reader.getIndex(*info["chunk-location"][2::-1])  # Z, C, T
    with lock:
        im = np.frombuffer(reader.openBytes(idx)[:], dtype=info["dtype"]).copy()
    im.shape = info["shape"][-2:]
    return im[np.newaxis, np.newaxis, np.newaxis]
