""" Module for generating synthetic datasets """

___all__ = [
    "generate_daily_time_axis",
    "generate_hourly_time_axis",
    "generate_monthly_time_axis",
    "xr_times_from_tuples",
]

import cftime
import xarray as xr
import numpy as np

DAYSINMONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def generate_daily_time_axis(startyear, nyears, timefmt="ncar"):
    """Construct a daily noleap time dimension with associated bounds

    Parameters
    ----------
    startyear : int
        Start year for requested time axis
    nyears : int
        Number of years in requested time axis
    timefmt : str, optional
        Time axis format, either "cmip", "gfdl" or "ncar", "ncar" by default

    Returns
    -------
    xarray.DataArray
        time and time_bnds xarray DataArray types
    """
    months = list(np.arange(1, 13))
    days = [np.arange(1, DAYSINMONTH[n] + 1) for n, x in enumerate(months)]
    days = [item for sublist in days for item in sublist]
    days = days * nyears
    months = [[months[n]] * DAYSINMONTH[n] for n, x in enumerate(months)]
    months = [item for sublist in months for item in sublist]
    months = months * nyears
    years = list(np.arange(startyear, startyear + nyears))
    years = [[years[x]] * 365 for x in range(0, len(years))]
    years = [item for sublist in years for item in sublist]

    if timefmt == "gfdl":
        hours = [12] * len(days)
    else:
        hours = [0] * len(days)

    timetuple = list(zip(years, months, days, hours))
    boundstuple = list(zip(years, months, days)) + [(startyear + nyears, 1, 1)]

    return xr_times_from_tuples(timetuple, boundstuple, timefmt=timefmt)


def generate_hourly_time_axis(startyear, nyears, dhour, timefmt="ncar"):
    """Construct an hourly noleap time dimension with associated bounds

    Parameters
    ----------
    startyear : int
        Start year for requested time axis
    nyears : int
        Number of years in requested time axis
    dhour : int
        Delta skip for hours (e.g. 1 hour, 3 hours, 6 hours)
    timefmt : str, optional
        Time axis format, either "cmip", "gfdl" or "ncar", "ncar" by default

    Returns
    -------
    xarray.DataArray
        time and time_bnds xarray DataArray types
    """

    nhours = int(24 / dhour)
    hours = list(np.arange(0, 24, dhour))
    hours = hours * 365 * nyears
    months = list(np.arange(1, 13))
    days = [np.arange(1, DAYSINMONTH[n] + 1) for n in range(0, len(months))]
    days = [item for sublist in days for item in sublist]
    days = [item for item in days for i in range(nhours)]
    days = days * nyears
    months = [[months[n]] * DAYSINMONTH[n] for n, x in enumerate(months)]
    months = [item for sublist in months for item in sublist]
    months = [item for item in months for i in range(nhours)]
    months = months * nyears
    years = list(np.arange(startyear, startyear + nyears))
    years = [[years[x]] * 365 for x in range(0, len(years))]
    years = [item for sublist in years for item in sublist]
    years = [item for item in years for i in range(nhours)]
    timetuple = list(zip(years, months, days, hours))
    boundstuple = (
        [(startyear, 1, 1, 0)]
        + list(zip(years, months, days, hours))
        + [(startyear + nyears, 1, 1, dhour)]
    )
    boundstuple = boundstuple[0:-1]

    return xr_times_from_tuples(timetuple, boundstuple, timefmt=timefmt)


def generate_monthly_time_axis(startyear, nyears, timefmt="ncar"):
    """Construct a monthly noleap time dimension with associated bounds

    Parameters
    ----------
    startyear : int
        Start year for requested time axis
    nyears : int
        Number of years in requested time axis
    timefmt : str, optional
        Time axis format, either "cmip", "gfdl" or "ncar", "ncar" by default

    Returns
    -------
    xarray.DataArray
        time and time_bnds xarray DataArray types
    """

    nyears = nyears + 1

    years = np.arange(startyear, startyear + nyears)
    years = [year for year in years for x in range(12)]
    months = list(np.arange(1, 13)) * nyears
    days = 1 if timefmt == "ncar" else 15
    days = [days] * len(months)
    timetuple = list(zip(years, months, days))
    timetuple = timetuple[1:-11] if timefmt == "ncar" else timetuple[0:-12]

    days = [1] * len(months)
    boundstuple = list(zip(years, months, days))
    boundstuple = boundstuple[0:-11]

    return xr_times_from_tuples(timetuple, boundstuple, timefmt=timefmt)


def xr_times_from_tuples(timetuple, boundstuple, timefmt="ncar"):
    """[summary]

    Parameters
    ----------
    timetuple : list of tuples of ints
        List of tuples containing time coordinate values [(Y,M,D,H,...) ...]
    boundstuple : list of tuples of ints
        List of tuples containing time bounds values [((Y,M,D,...)(Y,M,D,...)) ...]
    timefmt : str, optional
        Modeling center format, either "cmip", "gfdl" or "ncar", "ncar" by default

    Returns
    -------
    xarray.Dataset
        Returns an xarray dataset
    """

    dset_out = xr.Dataset()

    nbnds = np.array([0.0, 1.0])

    times = [cftime.DatetimeNoLeap(*x, calendar="noleap") for x in timetuple]
    bounds = [cftime.DatetimeNoLeap(*x, calendar="noleap") for x in boundstuple]
    bounds = list(zip(bounds[0:-1], bounds[1::]))

    if timefmt == "gfdl":
        bounds_index_name = "bnds"
        bnds_attrs = {"long_name": "time axis boundaries"}
        time_attrs = {
            "long_name": "time",
            "cartesian_axis": "T",
            "calendar_type": "noleap",
            "bounds": "time_bnds",
        }

    elif timefmt == "cmip":
        bounds_index_name = "bnds"
        bnds_attrs = {"long_name": "time axis boundaries"}
        time_attrs = {
            "long_name": "time",
            "axis": "T",
            "calendar_type": "noleap",
            "bounds": "time_bnds",
            "standard_name": "time",
            "description": "Temporal mean",
        }
    else:
        bounds_index_name = "nbnds"
        bnds_attrs = {"long_name": "time interval endpoints"}
        time_attrs = {"long_name": "time", "bounds": "time_bnds"}

    dims = (("time", times), (bounds_index_name, nbnds))

    dset_out["time_bnds"] = xr.DataArray(
        bounds,
        coords=dims,
        attrs=bnds_attrs,
    )

    dset_out["time"] = xr.DataArray(
        times,
        dims={"time": times},
        coords={"time": (times)},
        attrs=time_attrs,
    )

    if timefmt == "gfdl":
        dset_out["average_T1"] = (("time"), [x[0] for x in bounds])
        dset_out.average_T1.attrs = {"long_name": "Start time for average period"}

        dset_out["average_T2"] = (("time"), [x[1] for x in bounds])
        dset_out.average_T2.attrs = {"long_name": "End time for average period"}

        dset_out["average_DT"] = (("time"), [(x[1] - x[0]) for x in bounds])
        dset_out.average_DT.attrs = {"long_name": "Length of average period"}

    if timefmt == "ncar":
        dset_out["date"] = (
            ("time"),
            [int(x.strftime("%Y%m%d")) for x in dset_out.time.values],
        )
        dset_out.date.attrs = {"long_name": "current date (YYYYMMDD)"}

    if bounds_index_name in list(dset_out.variables):
        dset_out = dset_out.drop_vars(bounds_index_name)
    startyear = str(dset_out.time.values[0].strftime("%Y")).replace(" ", "0")
    dset_out.attrs["base_time_unit"] = f"days since {startyear}-01-01"

    if timefmt == "cmip":
        dset_out["bnds"].attrs["long_name"] = "vertex number"
        dset_out["time_bnds"].encoding["units"] = dset_out.attrs["base_time_unit"]

    return dset_out
