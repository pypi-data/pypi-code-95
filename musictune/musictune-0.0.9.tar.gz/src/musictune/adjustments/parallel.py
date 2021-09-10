import dask.array as da

from . import single


def to_float(img):
    return da.map_blocks(single.to_float, img, dtype='f4')
