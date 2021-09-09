import base64
import fsspec
import logging
import numcodecs
import numpy as np
import zarr

from fsspec_reference_maker.utils import _unstrip_protocol
logger = logging.getLogger("fits-to-zarr")


BITPIX2DTYPE = {8: 'uint8', 16: '>i2', 32: '>i4', 64: '>i8',
                -32: 'float32', -64: 'float64'}


def process_files(url, storage_options, extension, coordinate_keys, coordinate_dtypes,
                  variable_name_key, make_wcs_coords=False):
    """

    :param url: str
        Where the files are
    :param storage_options: dict
        How to load them
    :param extension: int|list(int)
        The FITS extension index to load.
        TODO:
        If if extension is a list, it adds another dimension; or could be list of variables
        per iinput file
    :param coordinate_keys: list(str)
        Header keywords to take as coordinate for file. The order is important.
    :param coordinate_dtypes: dict(str, str)
        numpy dtype to coerce header value strings into coord
    :param variable_name_key: str (optional)
        If the dataset has several variables, this key gives the variable of each dataset
    :param make_wcs_coords: bool
        Whether to calculate world coordinates for the output. Note that the WCS keys will
        always be copied, so you can construct this post-hoc with astropy anyway.
    :return: dict
        combined references dict
    """
    from astropy.io import fits
    if isinstance(extension, list):
        raise NotImplementedError
    ofs = fsspec.open_files(url, mode="rb", **storage_options)
    locs = []
    coords = {c: [] for c in coordinate_keys}
    vars = []
    attrs = None
    dtypes = {}
    shape = None

    out = {}
    filters = {}
    g = zarr.open_group(out, mode='w')

    for i, of in enumerate(ofs):
        with of as f:
            u = _unstrip_protocol(f.path, f.fs)
            logger.info("%s, %i of %i", u, i, len(ofs))
            hdul = fits.open(f, do_not_scale_image_data=True)
            hdu = hdul[extension]
            hdu.header.__str__()  # causes fixing of invalid cards
            var = hdu.header[variable_name_key]
            vars.append(var)
            if var in dtypes:
                assert dtypes[var] == BITPIX2DTYPE[hdu.header['BITPIX']]
                assert shape == [hdu.header[f"NAXIS{i + 1}"] for i in range(hdu.header["NAXIS"])]
            elif shape is None:
                # only runs once
                shape = [hdu.header[f"NAXIS{i + 1}"] for i in range(hdu.header["NAXIS"])]
                dtype = BITPIX2DTYPE[hdu.header['BITPIX']]
                size = np.dtype(dtype).itemsize
                for s in shape:
                    size *= s
                attrs = dict(hdu.header)
                dtypes[var] = dtype

            info = hdu.fileinfo()
            for c in coordinate_keys:
                coords[c].append(hdu.header[c])
            if 'BSCALE' in hdu.header or 'BZERO' in hdu.header and var not in filters:
                filters[var] = numcodecs.FixedScaleOffset(
                    offset=float(hdu.header.get("BZERO", 0)),
                    scale=float(hdu.header.get("BSCALE", 1)),
                    astype=dtype,
                    dtype=float
                )
            locs.append([u, info['datLoc'], size])

    coords = {c: np.array(v, dtype=coordinate_dtypes[c]) for c, v in coords.items()}
    for c, v in coords.items():
        arr = g.array(c, v)
        arr.attrs["_ARRAY_DIMENSIONS"] = [c]
    # TODO: if more than one var, check they have the same coords

    total_shape = [len(v) for v in coords.values()] + shape
    vars = np.array(vars)
    var_values = np.unique(vars)
    for var in var_values:
        filt = filters.get(var, None)
        arr = g.empty(var, dtype=dtypes[var] if filt is None else float, shape=tuple(total_shape),
                      compression=None,
                      filters=[filt] if filt is not None else [],
                      chunks=[1 for v in coords] + shape)
        arr.attrs["_ARRAY_DIMENSIONS"] = coordinate_keys + ["z", "y", "x"][-len(shape):]
        for i, loc in enumerate([lo for lo, v in zip(locs, vars) if v == var]):
            parts = ".".join([str(i)] + ["0"] * len(shape))
            out[f"{var}/{parts}"] = loc

    for key in coordinate_keys + [variable_name_key]:
        del attrs[key]
    g.attrs.update({k: str(v) if not isinstance(v, (int, float, str)) else v
                    for k, v in attrs.items()})
    for k, v in out.copy().items():
        if isinstance(v, bytes):
            try:
                # easiest way to test if data is ascii
                out[k] = v.decode('ascii')
            except UnicodeDecodeError:
                out[k] = (b"base64:" + base64.b64encode(v)).decode()

    return out


def add_wcs_coords(hdu, shape, zarr_group=None, dataset=None, dtype=float):
    from astropy.wcs import WCS
    from astropy.io import fits

    if zarr_group is None and dataset is None:
        raise ValueError("please provide a zarr group or xarray dataset")

    if not isinstance(hdu, fits.hdu.base._BaseHDU):
        # assume dict-like
        head = fits.Header()
        hdu2 = hdu.copy()
        hdu2.pop("COMMENT", None)  # comment fields can be non-standard
        head.update(hdu2)
        hdu = fits.PrimaryHDU(header=head)

    wcs = WCS(hdu)
    coords = [coo.ravel() for coo in np.meshgrid(*(np.arange(sh) for sh in shape))]  # ?[::-1]
    world_coords = wcs.pixel_to_world(*coords)
    for i, (name, world_coord) in enumerate(zip(wcs.axis_type_names, world_coords)):
        dims = ['z', 'y', 'x'][3 - len(shape):]
        attrs = {"unit": world_coord.unit.name,
                 "type": hdu.header[f"CTYPE{i + 1}"],
                 "_ARRAY_DIMENSIONS": dims}
        if zarr_group is not None:
            arr = zarr_group.empty(name, shape=shape,
                                   chunks=shape, overwrite=True, dtype=dtype)
            arr.attrs.update(attrs)
            arr[:] = world_coord.value.reshape(shape)
        if dataset is not None:
            import xarray as xr
            coo = xr.Coordinate(data=world_coord.value.reshape(shape),
                                dims=dims, attrs=attrs)
            dataset = dataset.assign_coordinates(name=coo)
    if dataset is not None:
        return dataset


def example_sdo():
    coordinate_keys = ["DATE-OBS"]
    coordinate_dtypes = {"DATE-OBS": "M8"}
    return process_files(
        # 094, 131, 171, 193, 211,304, 335
        'gcs://pangeo-data/SDO_AIA_Images/193/aia_lev1_*fits',
        {},
        0,
        coordinate_keys,
        coordinate_dtypes,
        variable_name_key="WAVELNTH",
        make_wcs_coords=True
    )
