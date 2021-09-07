""" Module for generating synthetic datasets """

___all__ = [
    "gfdl_plev19_vertical_coord",
]

import cftime
import xarray as xr
import numpy as np
from mdtf_test_data.util.rectilinear import construct_rect_grid
import mdtf_test_data.generators as generators


def gfdl_plev19_vertical_coord():
    """Generates GFDL CMIP-like 19-level pressure coordinate

    Returns
    -------
    xarray.DataArray
        GFDL CMIP-like 19-level pressure coordinate
    """

    plev19 = np.array(
        [
            100000.0,
            92500.0,
            85000.0,
            70000.0,
            60000.0,
            50000.0,
            40000.0,
            30000.0,
            25000.0,
            20000.0,
            15000.0,
            10000.0,
            7000.0,
            5000.0,
            3000.0,
            2000.0,
            1000.0,
            500.0,
            100.0,
        ]
    )

    plev19_attrs = {
        "long_name": "pressure",
        "units": "Pa",
        "axis": "Z",
        "positive": "down",
    }

    dset_out = xr.Dataset()
    dset_out["plev19"] = xr.DataArray(
        plev19, dims={"plev19": plev19}, coords={"plev19": plev19}, attrs=plev19_attrs
    )

    return dset_out
