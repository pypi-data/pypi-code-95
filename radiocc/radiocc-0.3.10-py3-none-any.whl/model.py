#!/usr/bin/env python3

"""
radiocc structure data models.
"""

from enum import auto
from pathlib import Path
from typing import List, Optional, Union

from nptyping import NDArray
from pudb import set_trace as bp  # noqa

from radiocc.util import AutoEnum


class Folders(AutoEnum):
    """Folders"""

    INFORMATION = auto()
    TO_PROCESS = auto()
    RESULTS = auto()


class ResultsFolders(AutoEnum):
    """Results folders"""

    DATA = auto()
    PLOTS = auto()
    EPHEMERIDS = auto()


class FoldersError(AutoEnum):
    """Possible error related to the setting of the path to the folders."""

    NotADir = auto()
    MissingFolder = auto()


class Bands(AutoEnum):
    """Possible frequency bands."""

    S = auto()
    X = auto()
    Diff = auto()


class Layers(AutoEnum):
    """Possible atmospheric layers."""

    Atmo = auto()
    Iono = auto()


class ProcessType(AutoEnum):
    """Possible type of folder to be processed."""

    MEX = auto()
    MAVEN = auto()


class LV2Loops(AutoEnum):
    """Possible type of folder in LVL2 data loop."""

    IFMS = auto()
    DSN = auto()


class Scenario:
    """Structure representation of a scenario."""

    def __init__(
        self, TO_PROCESS: Path, BAND: Bands, LAYER: Layers, INDEX_PROCESS: int
    ) -> None:
        self.TO_PROCESS = TO_PROCESS
        self.RESULT = (
            self.TO_PROCESS.parent.parent / Folders.RESULTS.name / self.TO_PROCESS.name
        )
        self.BAND = BAND
        self.LAYER = LAYER
        self.INDEX_PROCESS = INDEX_PROCESS


class MexData:
    """Input data from MEX."""

    ET: NDArray[float]
    UTC: List[str]
    DISTANCE: NDArray[float]
    DOPPLER: NDArray[float]
    DIFF_DOPPLER: NDArray[float]
    ERROR: NDArray[float]
    FSUP: float
    SURFACES_CONDITIONS: NDArray[bool]
    INTEGRAL_CONDITIONS: NDArray[bool]


class MavenData:
    """Input data from MAVEN."""

    ET: NDArray[float]
    # FSKY: NDArray[float]
    DOPPLER: NDArray[float]


class L2Data:
    """Input data."""

    FOLDER_TYPE: ProcessType
    METADATA_FILE: Path
    DATA_FILE: Path
    dsn_station_naif_code: int
    DISTANCE_UNIT: str
    PLANET_NAIF_CODE: int
    SPACECRAFT_NAIF_CODE: int
    DATA: Union[MexData, MavenData]


class Export:
    """Structure representation of the data to be exported for a scenario."""

    DATA_PATH: Path
    PLOT_PATH: Path
    EPHE_PATH: Path
    DOPPLER: NDArray[float]
    DOPPLER_DEBIAS: NDArray[float]
    DOPPLER_BIAS_FIT: NDArray[float]
    DISTANCE: NDArray[float]
    REFRACTIVITY: NDArray[float]
    NE: NDArray[float]
    TEC: Optional[NDArray[float]]
    ERROR: NDArray[float]
    ERROR_REFRAC: NDArray[float]
    ERROR_ELEC: NDArray[float]
