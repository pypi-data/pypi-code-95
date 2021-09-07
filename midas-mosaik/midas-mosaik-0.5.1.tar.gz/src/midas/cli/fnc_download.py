import logging
import os
import platform
import shutil
from datetime import datetime
from zipfile import ZipFile

import h5py
import pandas as pd
import wget
from midas.util.runtime_config import RuntimeConfig

LOG = logging.getLogger("midas.cli")


if platform.system() == "Windows" or platform.system() == "Darwin":
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context


def download(
    default_load_profiles=False,
    commercials=False,
    simbench=False,
    smartnord=False,
    weather=False,
    keep_tmp=False,
    force=False,
):
    """Download the required datasets.

    There are currently five categories of datasets:
        * Default load profiles from BDEW
        * Commercial dataset from openei.org
        * Simbench data from the simbench grids
        * Smart Nord dataset from the research project Smart Nord
        * Weather dataset from opendata.dwd.de

    The default behavior of this function is to download all missing
    datasets and, afterwards, remove the temporary directory created
    during this process.

    If at least one of the flags is set to *True*, only those datasets
    will be downloaded. If *force* is *True*, the datasets will be
    downloaded regardless of any existing dataset. If *keep_tmp* is
    *True*, the temporary downloaded files will not be removed
    afterwards.

    """
    # Check parameters
    if not any(
        [default_load_profiles, commercials, simbench, smartnord, weather]
    ):
        default_load_profiles = (
            commercials
        ) = simbench = smartnord = weather = True

    # Create paths
    data_path = RuntimeConfig().paths["data_path"]
    tmp_path = os.path.abspath(os.path.join(data_path, "tmp"))
    os.makedirs(tmp_path, exist_ok=True)

    if default_load_profiles:
        _download_dlp(data_path, tmp_path, force)

    if commercials:
        _download_commercials(data_path, tmp_path, force)

    if simbench:
        _download_simbench(data_path, tmp_path, force)

    if smartnord:
        _download_smart_nord(data_path, tmp_path, force)

    if weather:
        _download_weather(data_path, tmp_path, force)

    # Clean up
    if not keep_tmp:
        shutil.rmtree(tmp_path)


def _download_dlp(data_path, tmp_path, force):
    """Download and convert default load profiles.

    The default load profiles can be downloaded from the BDEW (last
    visited on 2020-07-07):

    https://www.bdew.de/energie/standardlastprofile-strom/

    """

    LOG.info("Preparing default load profiles...")
    # Specify the paths, we only have one provider for those profiles.
    config = RuntimeConfig().data["default_load_profiles"][0]
    output_path = os.path.abspath(os.path.join(data_path, config["name"]))

    if os.path.exists(output_path):
        LOG.debug("Found existing dataset at %s.", output_path)
        if not force:
            return

    # Download the file
    fname = config["base_url"].rsplit("/", 1)[-1]
    if not os.path.exists(os.path.join(tmp_path, fname)) or force:
        LOG.debug("Downloading '%s'...", config["base_url"])
        fname = wget.download(config["base_url"], out=tmp_path)
        print()  # To get a new line after wget output
        LOG.debug("Download complete.")

    # Specify unzip target
    target = os.path.join(tmp_path, "dlp")
    if os.path.exists(target):
        LOG.debug("Removing existing files.")
        shutil.rmtree(target)

    # Extract the file

    LOG.debug("Extracting profiles...")
    unzip(tmp_path, fname, target)
    # with ZipFile(os.path.join(tmp_path, fname), "r") as zip_ref:
    #     zip_ref.extractall(os.path.join(tmp_path, target))
    LOG.debug("Extraction complete.")

    excel_path = os.path.join(target, config["filename"])

    # Load excel sheet
    data = pd.read_excel(
        io=excel_path,
        sheet_name=config["sheet_names"],
        header=[1, 2],
        skipfooter=1,
    )

    # Create a hdf5 datebase from the sheet
    LOG.debug("Creating hdf5 database...")
    h5f = h5py.File(output_path, "w")
    for name in config["sheet_names"]:
        grp = h5f.create_group(name)
        for season in config["seasons"]:
            subgrp = grp.create_group(season[1])
            for day in config["days"]:
                subgrp.create_dataset(
                    day[1], data=data[name][(season[0], day[0])]
                )
    h5f.attrs["hint"] = "Quarter-hourly power values for annual consumption."
    h5f.attrs["ref_value"] = "1000 kWh/a"
    h5f.close()
    LOG.info("Successfully created database for default load profiles.")


def _download_commercials(data_path, tmp_path, force):
    """Download and convert the commercial dataset.

    The datasets are downloaded from
    https://openei.org/datasets/files/961/pub

    """
    LOG.info("Preparing commercial datasets...")

    # We allow multiple datasets here (although not tested, yet)
    for config in RuntimeConfig().data["commercials"]:
        output_path = os.path.abspath(os.path.join(data_path, config["name"]))

        if os.path.exists(output_path):
            LOG.debug("Found existing dataset at %s.", output_path)
            if not force:
                continue

        # Construct the final download locations
        loc_url = config["base_url"] + config["loc_url"]
        files = [
            (loc_url + f + config["post_fix"]).rsplit("/", 1)[1]
            for f, _ in config["data_urls"]
        ]
        for idx in range(len(files)):
            file_path = os.path.join(tmp_path, files[idx])
            if not os.path.exists(file_path) or force:
                if not force:
                    os.remove(file_path)
                LOG.debug("Downloading '%s'...", files[idx])
                files[idx] = wget.download(
                    loc_url + config["data_urls"][idx][0] + config["post_fix"],
                    out=tmp_path,
                )
                print()
            else:
                files[idx] = file_path
        LOG.debug("Download complete.")

        # Converting data
        date_range = pd.date_range(
            start="2004-01-01 00:00:00",
            end="2004-12-31 23:00:00",
            freq="H",
            tz="Europe/Berlin",
        )
        # Since 2004 is a leap year, we need to add an additional
        # day.
        dr_pt1 = pd.date_range(
            start="2004-01-01 00:00:00",
            end="2004-02-28 23:00:00",
            freq="H",
            tz="Europe/Berlin",
        )
        LOG.debug("Converting files...")
        # Now assemble the distinct files to one dataframe
        data = pd.DataFrame(index=date_range)
        for (src, tar), file_ in zip(config["data_urls"], files):
            fpath = os.path.join(tmp_path, file_)
            tsdat = pd.read_csv(fpath, sep=",")
            tsdat1 = tsdat.iloc[: len(dr_pt1)]
            tsdat1 = tsdat1.append(tsdat1.iloc[-24:])
            tsdat2 = tsdat.iloc[len(dr_pt1) :]
            tsdat = tsdat1.append(tsdat2)
            tsdat.index = date_range
            data[tar] = tsdat[config["el_cols"]].sum(axis=1) * 1e-3
        LOG.debug("Conversion complete.")

        # Create hdf5 database
        data.to_hdf(output_path, "load_pmw", "w")
        LOG.info("Successfully created database for commercial dataset.")


def _download_simbench(data_path, tmp_path, force):
    """Download and convert simbench datasets.

    Simbench datasets are actually not downloaded but stored in the
    python package simbench. The datasets are extracted from the grid.

    """
    import simbench as sb

    LOG.info("Preparing Simbench datasets...")

    # We allow multiple datasets here
    for config in RuntimeConfig().data["simbench"]:
        output_path = os.path.abspath(os.path.join(data_path, config["name"]))
        simbench_code = output_path.rsplit("/", 1)[1].split(".")[0]

        if os.path.exists(output_path):
            LOG.debug("Found existing datasets at '%s'.", output_path)
            if not force:
                continue
            else:
                LOG.debug("Loading profiles anyways...")
        else:
            LOG.debug(
                "No dataset found. Start loading '%s' profiles...",
                simbench_code,
            )

        grid = sb.get_simbench_net(simbench_code)
        profiles = sb.get_absolute_values(grid, True)
        load_map = pd.DataFrame(columns=["idx", "bus", "name"])
        sgen_map = pd.DataFrame(columns=["idx", "bus", "name"])

        LOG.debug("Loading loads...")
        for idx in range(len(grid.load)):
            load = grid.load.loc[idx]
            load_map = load_map.append(
                {"idx": idx, "bus": int(load["bus"]), "name": load["name"]},
                ignore_index=True,
            )
        LOG.debug("Loading sgens...")
        for idx in range(len(grid.sgen)):
            sgen = grid.sgen.loc[idx]
            sgen_map = sgen_map.append(
                {"idx": idx, "bus": int(sgen["bus"]), "name": sgen["name"]},
                ignore_index=True,
            )
        LOG.debug("Creating database...")
        profiles[("load", "p_mw")].to_hdf(output_path, "load_pmw", "w")
        profiles[("load", "q_mvar")].to_hdf(output_path, "load_qmvar")
        profiles[("sgen", "p_mw")].to_hdf(output_path, "sgen_pmw")
        load_map.to_hdf(output_path, "load_default_mapping")
        sgen_map.to_hdf(output_path, "sgen_default_mapping")

        LOG.info(
            "Successfully created database for Simbench grid '%s'.",
            simbench_code,
        )


def _download_smart_nord(data_path, tmp_path, force):
    """Download and convert the Smart Nord dataset.

    The dataset is stored inside of gitlab and will be downloaded from
    there and converted afterwards.

    """
    import subprocess
    import tarfile

    LOG.info("Preparing Smart Nord datasets...")
    token = "fDaPqqSuMBhsXD8nQ_Nn"  # read only Gitlab token for midas_data

    # There is only one dataset
    config = RuntimeConfig().data["smart_nord"][0]
    output_path = os.path.abspath(os.path.join(data_path, config["name"]))
    if os.path.exists(output_path):
        LOG.debug("Found existing datasets at %s.", output_path)
        if not force:
            return

    zip_path = os.path.join(
        tmp_path, "smart_nord_data", "HouseholdProfiles.tar.gz"
    )
    if not os.path.exists(zip_path):
        LOG.debug("Downloading dataset...")
        subprocess.check_output(
            [
                "git",
                "clone",
                f"https://midas:{token}@gitlab.com/midas-mosaik/midas-data",
                os.path.join(tmp_path, "smart_nord_data"),
            ]
        )
        LOG.debug("Download complete.")
    LOG.debug("Extracting...")
    with tarfile.open(zip_path, "r:gz") as tar_ref:
        tar_ref.extractall(tmp_path)
    LOG.debug("Extraction complete.")

    tmp_name = os.path.join(tmp_path, "HouseholdProfiles.hdf5")
    shutil.move(tmp_name, output_path)
    LOG.info("Successfully created database for Smart Nord datasets.")


def _download_weather(data_path, tmp_path, force):
    """Download and convert the weather datasets.

    The weather data is downloaded from https://opendata.dwd.de,
    the selected weather station is located in Bremen.

    At the beginning of every new year, the data from the previous
    year is added to the dataset. Unfortunately, the download link
    changes at the same time, now including the latest year of data.

    To prevent a failure every year, the year value in the download
    link is increased, but that may break at anytime if DWD decides to
    change the download links in any other way.

    The year is included in the 'post_fix' key of the runtime config.

    """
    LOG.info("Preparing weather datasets...")

    # We allow multiple datasets here
    for config in RuntimeConfig().data["weather"]:
        output_path = os.path.abspath(os.path.join(data_path, config["name"]))

        if os.path.exists(output_path):
            LOG.debug("Found existing dataset at %s.", output_path)
            if not force:
                continue
            else:
                LOG.debug("Downloading weather data anyways...")
        else:
            LOG.debug("No dataset found. Start downloading weather data ...")

        base_url = config["base_url"]
        post_fix = config["post_fix"]
        year = int(post_fix[:4])
        for url in [
            "solar_url",
            "air_url",
            "cloud_url",
            "sun_url",
            "wind_url",
        ]:

            for idx in range(10):
                if url == "solar_url":
                    full_url = base_url + config[url]
                else:
                    # The other urls follow the same schema, including the
                    # latest year of data in the download link.
                    full_url = base_url + config[url] + f"{year}{post_fix[4:]}"
                fname = full_url.rsplit("/", 1)[-1]
                fpath = os.path.join(tmp_path, fname)
                if not os.path.exists(fpath):
                    try:
                        LOG.debug("Start downloading '%s'...", full_url)
                        fpath = wget.download(full_url, out=tmp_path)
                        print()
                        LOG.debug("Download complete.")
                        break
                    except Exception as err:
                        LOG.warning(
                            "Error during the download of file '%s': '%s'.\n"
                            "Probably the year has changed. Will try to fix "
                            "this automatically.",
                            full_url,
                            err,
                        )
                        fpath = None
                        if url != "solar_url":
                            year += 1
                        continue
                break

            if fpath is None:
                raise ValueError(
                    "Could not download weather data. Sorry for that. "
                    "This needs to be fixed manually :("
                )
            else:
                unzip(tmp_path, fpath, url.split("_")[0])

        LOG.debug("Creating database...")
        # We start at 2009 because the solar dataset has no data before
        # that year.
        data = pd.DataFrame(
            index=pd.date_range(
                start="2009-01-01 00:00:00",
                end=f"{year}-12-31 23:00:00",
                tz="Europe/Berlin",
                freq="H",
            )
        )
        data = load_data(tmp_path, "air", data, year)
        data = load_data(tmp_path, "solar", data, year)
        data = load_data(tmp_path, "wind", data, year)
        data = load_data(tmp_path, "cloud", data, year)
        data = load_data(tmp_path, "sun", data, year)

        data.to_hdf(output_path, "weather", "w")

        LOG.info("Successfully created database for weather data.")


def unzip(path, fname, target):
    """Unzip a file.

    Parameters
    ----------
    path: str
        The path where the file to unzip is located. This is also the
        path where the unzipped files will be located.
    fname: str
        The name of the file to unzip.
    target: str
        The name of the folder to which the files of the archive will
        be extracted to.

    """
    with ZipFile(os.path.join(path, fname), "r") as zip_ref:
        zip_ref.extractall(os.path.join(path, target))


# Horizontal solar radiation is provided as hourly sum in Joule/cm^2
# (i.e., correct would be Joule/s/cm^2 * 3600s), but we want Watt/m^2
# for our PV models. Since 1*W = 1*J/s we first need to get back to
# J/s by dividing by 3600. Next, we want to convert from cm^2 to m^2,
# which is by multiplying with 0.0001, however, since cm^2 is in the
# divisor, we need to divide by that value (or multiply with the
# reciprocal). So the calculation we need to apply is
# 1 / (3.6*1e^3) * 1 / 1e^-4 = 1e^4 / (3.6*1e^3) = 1e^1 / 3.6
# which is equal to:
JOULE_TO_WATT = 10 / 3.6
DATA_COLS = {
    "air": [("TT_TU", "t_air_degree_celsius", 1)],
    "solar": [
        ("FD_LBERG", "dh_w_per_m2", JOULE_TO_WATT),
        ("FG_LBERG", "gh_w_per_m2", JOULE_TO_WATT),
    ],
    "wind": [("   F", "wind_v_m_per_s", 1), ("   D", "wind_dir_degree", 1)],
    "cloud": [(" V_N", "cloud_percent", 12.5)],
    "sun": [("SD_SO", "sun_hours_min_per_h", 1)],
}


def load_data(path, target, data, year):
    """Load data from a csv file and add them to a dataframe.

    Parameters
    ----------
    path: str
        The path of the folder containing a folder with csv files.
    target: str
        The name of the folder which contains csv files.
    data: pd.DataFrame
        The dataframe to which the content of the csv file will be
        added.
    year: int
        Since the year may change over the years, we pass it here.

    """
    fname = os.path.join(path, target)
    files = os.listdir(fname)
    data_file = [f for f in files if f.startswith("produkt")][0]
    fname = os.path.join(fname, data_file)

    if target == "solar":
        # We need a different parser for the solar dataset
        def parser(date):
            return datetime.strptime(date.split(":")[0], "%Y%m%d%H")

    else:

        def parser(date):
            return datetime.strptime(date, "%Y%m%d%H")

    # Read and prepare the content of the csv file.
    csv = pd.read_csv(
        fname, sep=";", index_col=1, parse_dates=[1], date_parser=parser
    )
    # We want to start at 2009 and go to the latest year.
    start_date = "2009-01-01 00:00:00"
    end_date = f"{year}-12-31 23:00:00"
    csv = csv.loc[start_date:end_date]
    # Some values might be missing to we fill them with the nearest
    # observations.
    index = pd.date_range(start=start_date, end=end_date, freq="H")
    csv = csv.reindex(index, method="nearest")

    # Now we can copy the content of the csv to the dataframe
    for src_col, tar_col, fac in DATA_COLS[target]:
        data[tar_col] = csv[src_col].values * fac

        if target == "air":
            # We need the day average air temperature for some of our
            # models.
            tar_col2 = f"day_avg_{tar_col}"
            data[tar_col2] = (
                csv[src_col].values.reshape(-1, 24).mean(axis=1).repeat(24)
            )

    return data
