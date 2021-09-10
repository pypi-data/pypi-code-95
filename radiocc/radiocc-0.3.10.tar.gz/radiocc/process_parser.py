#!/usr/bin/env python3

"""
Parse the folder to be processed.
"""

import re
import time
from pathlib import Path
from typing import Optional

import numpy
import spiceypy as spice
from colored import attr, fg
from nptyping import NDArray
from pudb import set_trace as bp  # noqa

from radiocc import (
    Folders,
    L2Data,
    LV2Loops,
    MavenData,
    MexData,
    ProcessType,
    ResultsFolders,
    Scenario,
    constants,
    util,
)

SPICE_FOLDERS = dict(
    SPK=("*.bsp",),
    SCLK=("*.tsc",),
    PCK=("*.tpc", "*.bpc"),
    ORBNUM=("*.orb",),
    LSK=("*.tls",),
    FK=("*.tf",),
    CK=("*.bc",),
)
SPICE_RPATH = dict(MEX="EXTRAS/ANCILLARY/SPICE", MAVEN="SPICE")
LV2_RPATH = "DATA/LEVEL02"
DATA_RPATH_MAVEN = "DATA"
METADATA_SUFFIX_MEX = ".LBL"
STATION_RPATH = "STATION.txt"
START_STATIONS_NAIF_CODE = 399000
DEFAULT_DSN_STATION_NAIF_CODE = 398990
DEFAULT_DSN_STATION_NAME = "NEW NORCIA"
BODIES_RPATH = "PLANETS_SATELLITE.txt"
SPACECRAFT_RPATH = "SPACECRAFT.txt"
DATA_COL_IDX_MEX = dict(
    utc=1, et=3, distance=4, fsup=6, Doppler=11, diff_Doppler=13, sigma_observed=14
)
METADATA_COL_IDX_MVN = dict(
    station=22,
)
DATA_COL_IDX_MVN = dict(
    ertyr=0,
    ertdoy=1,
    ertsec=2,
    fsky=3,
    fresid=4,
)
SPACECRAFT_NAIF_CODES = dict(MEX=-41, MAVEN=-202)


INVALID_SIGMA_OBSERVED = -99999.999999
DEFAULT_ERROR = 1e-2  # 10 mHz Hinson et al. (1999)
DISTANCE_SHIFT_UNIT = 4
UNITS = dict(KILOMETER=1e3, METER=1)


def prepare_directories(scenario: Scenario) -> None:
    """Prepare directories."""
    # Create directories if they do not exist yet.
    (scenario.RESULT / ResultsFolders.DATA.name).mkdir(parents=True, exist_ok=True)
    (scenario.RESULT / ResultsFolders.PLOTS.name).mkdir(parents=True, exist_ok=True)
    (scenario.RESULT / ResultsFolders.EPHEMERIDS.name).mkdir(
        parents=True, exist_ok=True
    )


def load_spice_kernels(PROCESS_PATH: Path, FOLDER_TYPE: ProcessType) -> None:
    """Load SPICE kernels."""
    SPICE_PATH = PROCESS_PATH / SPICE_RPATH[FOLDER_TYPE.name]

    # Ensure no conflict with previously loaded kernels.
    spice.kclear()

    # Iterate SPICE bundle folders.
    for FOLDER, FILTERS in SPICE_FOLDERS.items():
        for FILTER in FILTERS:
            FILES = list((SPICE_PATH / FOLDER).glob(FILTER))
            FILES.extend(list((SPICE_PATH / FOLDER).glob(FILTER.upper())))

            # Iterate files in each folder.
            for FILE in FILES:
                spice.furnsh(str(FILE))

    print("      SPICE kernels loaded.")


def detect_folder_type(PROCESS_PATH: Path) -> Optional[ProcessType]:
    """Detect folder type."""
    # Detect if MEX or MAVEN format.
    folder_type: Optional[ProcessType] = None
    print(f"      {PROCESS_PATH.name}")
    if PROCESS_PATH.name[:3] == "MEX" and PROCESS_PATH.name[-4:] == "V1.0":
        folder_type = ProcessType.MEX
    elif PROCESS_PATH.name[:3] == "mvn":
        folder_type = ProcessType.MAVEN

    # Exit if neither MEX nor MAVEN.
    if folder_type is None:
        s = "      "
        print(
            f"{s}Folder {PROCESS_PATH} follows neither MEX nor MAVEN conventions.\n"
            "\n"
            f"{s}MEX format should respect:\n"
            f"{s}  + folder name should start with `MEX`.\n"
            "\n"
            f"{s}MAVEN conventions are:\n"
            f"{s}  + folder name should start with `mvn`.\n"
        )

    return folder_type


def get_data_file(SCENARIO: Scenario, FOLDER_TYPE: ProcessType) -> Optional[Path]:
    """Get the data input file."""
    if FOLDER_TYPE == ProcessType.MEX:
        # Get DATA LEVEL02
        LV2_PATH = SCENARIO.TO_PROCESS / LV2_RPATH
        LV2_ITER = util.directories(LV2_PATH)
        try:
            LV2_LOOP = next(LV2_ITER)
        except StopIteration:
            s = "      "
            print(f"{s}Folder {LV2_PATH} should contain an OPEN or CLOSED loop folder.")
            return None

        # Check if IFMS or DSN.
        LOOP_ITER = util.directories(LV2_LOOP)
        LOOP_OPTION = next(LOOP_ITER)
        if LOOP_OPTION.name == LV2Loops.IFMS.name:
            DATA_FOLDER = LOOP_OPTION / "DP1"
            DATA_FILTER_RAW = "D1"
        elif LOOP_OPTION.name == LV2Loops.DSN.name:
            DATA_FOLDER = LOOP_OPTION / f"DP{SCENARIO.BAND.name}"
            DATA_FILTER_RAW = "DP"
        else:
            s = "      "
            print(
                f"{s}The {LV2_LOOP} folder expect to contain either IFMS or DSN data."
            )
            return None

        print(
            "      Data architecture: "
            f"{LV2_PATH.name}/{LV2_LOOP.name}/{LOOP_OPTION.name}/{DATA_FOLDER.name}"
        )

        # Get TAB filter to select the good input file.
        DATA_FOLDER_FILTER = f"{DATA_FILTER_RAW}{SCENARIO.BAND.name}"
        DATA_FILTER = f"*_{DATA_FOLDER_FILTER}_*.TAB"

    elif FOLDER_TYPE == ProcessType.MAVEN:
        DATA_FOLDER = SCENARIO.TO_PROCESS / DATA_RPATH_MAVEN
        DATA_FILTER = "*.tab"

    else:
        print(
            f"{fg('red')}"
            "      Error: the data input folder is neither MEX nor MAVEN."
            f"{attr(0)}"
        )

    DATA_FILES_ITER = iter(sorted(DATA_FOLDER.glob(DATA_FILTER), reverse=False))

    # Check that the data folder actually contains some files.
    try:
        DATA_FILE = next(DATA_FILES_ITER)
    except StopIteration:
        print(
            f"{fg('red')}"
            f"      Error: the folder {DATA_FOLDER} does not contain any input file "
            f"matching glob: {DATA_FILTER}."
            f"{attr(0)}"
        )
        return None

    return DATA_FILE


def get_metadata_file(
    SCENARIO: Scenario, FOLDER_TYPE: ProcessType, DATA_FILE: Path
) -> Optional[Path]:
    """Get the data input file."""
    # Get the meta data folder.
    if FOLDER_TYPE == ProcessType.MEX:
        METADATA_FILE = DATA_FILE.with_suffix(METADATA_SUFFIX_MEX)
    else:
        METADATA_FILTER = "*.csv"
        METADATA_FILES_ITER = iter(
            sorted(DATA_FILE.parent.glob(METADATA_FILTER), reverse=False)
        )

        # Check that the data folder actually contains the metadata folder.
        try:
            METADATA_FILE = next(METADATA_FILES_ITER)
        except StopIteration:
            print(
                f"{fg('red')}"
                f"      Error: the folder {DATA_FILE.parent} does not contain any input"
                f" metadata file matching glob: {METADATA_FILTER}."
                f"{attr(0)}"
            )
            return None

    return METADATA_FILE


def get_data_and_meta_files(
    SCENARIO: Scenario, FOLDER_TYPE: ProcessType
) -> Optional[L2Data]:
    """Get data file and metadata file."""
    DATA_FILE = get_data_file(SCENARIO, FOLDER_TYPE)

    if DATA_FILE is None:
        return None

    METADATA_FILE = get_metadata_file(SCENARIO, FOLDER_TYPE, DATA_FILE)

    if METADATA_FILE is None:
        return None

    l2_data = L2Data()
    l2_data.FOLDER_TYPE = FOLDER_TYPE
    l2_data.DATA_FILE = DATA_FILE
    l2_data.METADATA_FILE = METADATA_FILE

    return l2_data


def read_input_metadata(l2_data: L2Data) -> L2Data:
    """Read input metadata."""
    if l2_data.FOLDER_TYPE == ProcessType.MEX:
        # Read LBL file.
        with l2_data.METADATA_FILE.open("r") as F:
            LBL_LINES = F.readlines()

        # Get information in LBL file.
        information_in_LBL = dict(DSN_STATION_NUMBER=False, DISTANCE=False)
        for idx, LINE in enumerate(LBL_LINES):
            if "DSN_STATION_NUMBER" in LINE:
                DSN_STATION_NUMBER = int(float(LINE.split("=")[1]))
                DSN_STATION_NAIF_CODE = START_STATIONS_NAIF_CODE + DSN_STATION_NUMBER
                information_in_LBL["DSN_STATION_NUMBER"] = True

            elif any(
                NAME in LINE for NAME in ("DISTANCE", "GEOMETRIC IMPACT PARAMETER")
            ):
                UNIT = re.search('"(.*?)"', LBL_LINES[idx + DISTANCE_SHIFT_UNIT])
                if UNIT:
                    DISTANCE_UNIT = UNIT.group(1)
                else:
                    raise SystemExit(
                        NotImplementedError(
                            f"{fg('red')}"
                            "Error: "
                            "Cannot parse distance unit."
                            f"{attr(0)}"
                        )
                    )

                information_in_LBL["DISTANCE"] = True

            if all(information_in_LBL.values()):
                break

        l2_data.DISTANCE_UNIT = DISTANCE_UNIT

    elif l2_data.FOLDER_TYPE == ProcessType.MAVEN:
        # FIXME
        # mypy issue with numpy untyped call
        DATA_ARRAY = numpy.genfromtxt(
            l2_data.METADATA_FILE,
            dtype=None,
            comments="#",
            delimiter=",",
            skip_header=1,
        )
        STATION_ID = DATA_ARRAY[2][METADATA_COL_IDX_MVN["station"]]
        DSN_STATION_NAIF_CODE = START_STATIONS_NAIF_CODE + STATION_ID

    else:
        print(
            f"{fg('red')}"
            "      Error: the data input folder is neither MEX nor MAVEN."
            f"{attr(0)}"
        )

    l2_data.dsn_station_naif_code = DSN_STATION_NAIF_CODE
    return l2_data


def check_input_info(l2_data: L2Data, INFORMATION_PATH: Path) -> L2Data:
    """Check input data with the information folder."""
    # Read station information file.
    STATION_PATH = INFORMATION_PATH / STATION_RPATH
    with STATION_PATH.open("r") as F:
        STATIONS_LINES = F.readlines()

    # Check station NAIF ID in information file.
    DSN_STATION_UNKNOWN = True
    for LINE in STATIONS_LINES:
        if str(l2_data.dsn_station_naif_code) in LINE:
            DSN_STATION_UNKNOWN = False
            # dsn_station_name = LINE.split(" ")[1]
            break

    if DSN_STATION_UNKNOWN:
        s = "      "
        print(
            f"{s}The station {l2_data.dsn_station_naif_code} has not been found in the "
            f"base {STATION_PATH.resolve()}. The default station "
            f"{DEFAULT_DSN_STATION_NAME} ({DEFAULT_DSN_STATION_NAIF_CODE}) is "
            "considered.\n"
        )
        DSN_STATION_NAIF_CODE = DEFAULT_DSN_STATION_NAIF_CODE
        # dsn_station_name = DEFAULT_DSN_STATION_NAME
        l2_data.dsn_station_naif_code = DSN_STATION_NAIF_CODE
    else:
        print(f"    station found: {l2_data.dsn_station_naif_code}.")

    # Read planets & satellites information file.
    BODIES_PATH = INFORMATION_PATH / BODIES_RPATH
    with BODIES_PATH.open("r") as F:
        BODIES_LINES = F.readlines()

    # Get planet NAIF ID in information file.
    for LINE in BODIES_LINES:
        if constants.Planet in LINE:
            PLANET_NAIF_CODE = int(float(LINE.split()[0]))
            break

    # Read spacecraft information file.
    # SPACECRAFT_PATH = INFORMATION_PATH / SPACECRAFT_RPATH
    # with SPACECRAFT_PATH.open("r") as F:
    #     SPACECRAFT_LINES = F.readlines()

    # # Get spacecraft NAIF ID in information file.
    # for LINE in SPACECRAFT_LINES:
    #     if  in LINE:
    #         SPACRAFT_NAIF_CODE = int(float(LINE.split()[0]))
    #         break
    SPACECRAFT_NAIF_CODE = SPACECRAFT_NAIF_CODES[l2_data.FOLDER_TYPE.name]

    # Export.
    l2_data.PLANET_NAIF_CODE = PLANET_NAIF_CODE
    l2_data.SPACECRAFT_NAIF_CODE = SPACECRAFT_NAIF_CODE
    return l2_data


def read_L2_metadata(l2_data: L2Data, INFORMATION_PATH: Path) -> L2Data:
    """Read L2 data."""
    l2_data = read_input_metadata(l2_data)
    l2_data = check_input_info(l2_data, INFORMATION_PATH)
    return l2_data


def read_tab_data(l2_data: L2Data) -> L2Data:
    """read the tab file."""
    # Read data from TAB file.
    # FIXME
    # mypy issue with numpy untyped call
    DATA_ARRAY = numpy.genfromtxt(l2_data.DATA_FILE, dtype=None, encoding="utf-8")
    DATA_NROWS = DATA_ARRAY.shape[0]

    if l2_data.FOLDER_TYPE == ProcessType.MEX:
        # Initialize individual column arrays.
        et = numpy.zeros(DATA_NROWS)
        utc = [""] * DATA_NROWS
        distance = numpy.zeros(DATA_NROWS)
        Doppler = numpy.zeros(DATA_NROWS)
        diff_Doppler = numpy.zeros(DATA_NROWS)
        error = numpy.zeros(DATA_NROWS)
        validity_sigma_observed = False

        # Fill arrays from TAB_ARRAY.
        fsup = DATA_ARRAY[0][DATA_COL_IDX_MEX["fsup"]]
        for idx, LINE in enumerate(DATA_ARRAY):
            et[idx] = LINE[DATA_COL_IDX_MEX["et"]]
            utc[idx] = LINE[DATA_COL_IDX_MEX["utc"]]
            distance[idx] = LINE[DATA_COL_IDX_MEX["distance"]]
            Doppler[idx] = LINE[DATA_COL_IDX_MEX["Doppler"]]
            diff_Doppler[idx] = LINE[DATA_COL_IDX_MEX["diff_Doppler"]]

            # FIXME:
            # + float comparison (compare with epsilon value)
            SIGMA_OBSERVED = LINE[DATA_COL_IDX_MEX["sigma_observed"]]
            validity_sigma_observed = float(SIGMA_OBSERVED) == INVALID_SIGMA_OBSERVED
            if validity_sigma_observed:
                error[idx] = DEFAULT_ERROR
            else:
                error[idx] = SIGMA_OBSERVED

        distance *= UNITS[l2_data.DISTANCE_UNIT]

        SURFACES_CONDITIONS: NDArray[float] = distance <= constants.Threshold_Surface
        INTEGRAL_CONDITIONS: NDArray[float] = distance <= constants.Threshold_int

        # Export data.
        mex_data = MexData()
        mex_data.ET = et
        mex_data.UTC = utc
        mex_data.DISTANCE = distance
        mex_data.DOPPLER = Doppler
        mex_data.DIFF_DOPPLER = diff_Doppler
        mex_data.ERROR = error
        mex_data.FSUP = fsup
        mex_data.SURFACES_CONDITIONS = SURFACES_CONDITIONS
        mex_data.INTEGRAL_CONDITIONS = INTEGRAL_CONDITIONS
        l2_data.DATA = mex_data

    elif l2_data.FOLDER_TYPE == ProcessType.MAVEN:
        et = numpy.zeros(DATA_NROWS)
        # fsky = numpy.zeros(DATA_NROWS)
        doppler = numpy.zeros(DATA_NROWS)

        for idx, LINE in enumerate(DATA_ARRAY):
            ERTYR = LINE[DATA_COL_IDX_MVN["ertyr"]]
            ERTDOY = LINE[DATA_COL_IDX_MVN["ertdoy"]]
            ERTSEC = LINE[DATA_COL_IDX_MVN["ertsec"]]
            # fsky[idx] = LINE[DATA_COL_IDX_MVN["fsky"]]
            doppler[idx] = LINE[DATA_COL_IDX_MVN["fresid"]]

            time_format = time.strftime("%H:%M:%S", time.gmtime(ERTSEC))
            Utime = str(ERTYR) + "-" + str(ERTDOY) + "T" + str(time_format)
            et[idx] = spice.str2et(Utime)

        # Export data.
        mvn_data = MavenData()
        mvn_data.ET = et
        # data.FSKY = fsky
        mvn_data.DOPPLER = doppler
        l2_data.DATA = mvn_data

    else:
        print(
            f"{fg('red')}"
            "      Error: the data input folder is neither MEX nor MAVEN."
            f"{attr(0)}"
        )

    return l2_data


def read_L2_data(SCENARIO: Scenario, FOLDER_TYPE: ProcessType) -> Optional[L2Data]:
    """Read L2 data."""
    if FOLDER_TYPE is None:
        return None

    # Get the file containing the inputs.
    l2_data = get_data_and_meta_files(SCENARIO, FOLDER_TYPE)

    if l2_data is None:
        return None

    # Parse the data from the input data file.
    INFORMATION_PATH = SCENARIO.TO_PROCESS.parent.parent / Folders.INFORMATION.name
    l2_data = read_L2_metadata(l2_data, INFORMATION_PATH)
    l2_data = read_tab_data(l2_data)

    return l2_data
