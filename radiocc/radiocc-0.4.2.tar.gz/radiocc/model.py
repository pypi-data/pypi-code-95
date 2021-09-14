#!/usr/bin/env python3

"""
radiocc structure data models.
"""

from enum import auto
from pathlib import Path
from typing import List, Optional, Union

from nptyping import NDArray
from pudb import set_trace as bp  # noqa

from radiocc.util import AutoEnum, GetAttributes, raise_error


class Folders(AutoEnum):
    """Folders"""

    information = auto()
    to_process = auto()
    results = auto()


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


class ConfigKeysReq(AutoEnum):
    """Required keys in config file."""


class ConfigKeysOpt(AutoEnum):
    """Optional keys in config file."""

    information = auto()
    to_process = auto()
    results = auto()
    folders = auto()


class Config(GetAttributes):
    """Structure representation the config."""

    def __init__(self, INFORMATION: Path, TO_PROCESS: Path, RESULTS: Path) -> None:
        self.information = INFORMATION
        self.to_process = TO_PROCESS
        self.results = RESULTS

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "\n".join(
            f"{attribute}: {value}"
            for (attribute, value) in self.get_attributes().items()
        )


class ConfigBuilder(GetAttributes):
    """Structure representation the config."""

    information: Optional[Path] = None
    to_process: Optional[Path] = None
    results: Optional[Path] = None

    def build(self) -> Config:
        for (attribute, value) in self.get_attributes().items():
            if value is None:
                raise_error(f"the config variable {attribute} could not be set.")

        return Config(
            self.information, self.to_process, self.results  # type: ignore [arg-type]
        )


class Scenario:
    """Structure representation of a scenario."""

    def __init__(
        self, TO_PROCESS: Path, BAND: Bands, LAYER: Layers, INDEX_PROCESS: int
    ) -> None:
        self.TO_PROCESS = TO_PROCESS
        self.BAND = BAND
        self.LAYER = LAYER
        self.INDEX_PROCESS = INDEX_PROCESS

    def results(self, RESULTS: Path) -> Path:
        return RESULTS / self.TO_PROCESS.name


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
