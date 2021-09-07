""" Module for generating synthetic datasets """

___all__ = [
    "gfdl_vertical_coord",
]

import cftime
import xarray as xr
import numpy as np
from mdtf_test_data.util.rectilinear import construct_rect_grid
import mdtf_test_data.generators as generators


def gfdl_vertical_coord():
    """Generates GFDL AM4 pressure coordinate

    Returns
    -------
    xarray.DataArray
        GFDL AM4 pressure levels and half levels
    """

    pfull = np.array(
        [
            2.164043,
            5.845308,
            10.74508,
            17.106537,
            25.113805,
            35.221197,
            48.137904,
            64.560184,
            85.114482,
            110.419627,
            141.09261,
            177.729388,
            220.892397,
            271.066624,
            328.516337,
            392.785273,
            461.947262,
            532.465907,
            600.430867,
            663.107383,
            719.307118,
            768.814284,
            811.846869,
            848.836021,
            880.346139,
            906.995722,
            929.394583,
            948.128523,
            963.73257,
            976.687397,
            987.392458,
            996.109949,
        ]
    )

    phalf = np.array(
        [
            1.0,
            4.0,
            8.186021,
            13.788865,
            20.917952,
            29.836408,
            41.217896,
            55.792215,
            74.201906,
            97.047864,
            124.966648,
            158.549553,
            198.396959,
            245.027221,
            298.888576,
            360.040179,
            427.458025,
            498.243573,
            568.220535,
            633.836047,
            693.266329,
            745.991986,
            792.097373,
            831.921945,
            865.977814,
            894.872525,
            919.22792,
            939.635932,
            956.672132,
            970.827661,
            982.570665,
            992.23,
            1000.0,
        ]
    )

    pfull_attrs = {
        "long_name": "ref full pressure level",
        "units": "mb",
        "cartesian_axis": "Z",
        "positive": "down",
        "edges": "phalf",
    }

    phalf_attrs = {
        "long_name": "ref half pressure level",
        "units": "mb",
        "cartesian_axis": "Z",
        "positive": "down",
    }

    dset_out = xr.Dataset()
    dset_out["pfull"] = xr.DataArray(
        pfull, dims={"pfull": pfull}, coords={"pfull": pfull}, attrs=pfull_attrs
    )
    dset_out["phalf"] = xr.DataArray(
        phalf, dims={"phalf": phalf}, coords={"phalf": phalf}, attrs=phalf_attrs
    )

    return dset_out
