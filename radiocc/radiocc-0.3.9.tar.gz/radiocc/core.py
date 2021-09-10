#!/usr/bin/env python3

"""
Radio occultation.
"""

import os
from pathlib import Path
from typing import Union

import yaml
from colored import attr, fg
from dotmap import DotMap
from pudb import set_trace as bp  # noqa: F401

from radiocc import (
    Bands,
    Folders,
    FoldersError,
    Layers,
    ResultsFolders,
    Scenario,
    constants,
    export,
    old,
    process_parser,
    reconstruct,
)
from radiocc.old import R17_Plot_profiles

FILE_PATH = Path(os.path.realpath(__file__))
CONFIG_PATH = FILE_PATH.parent / "config.yaml"
BANDS = (Bands.X,)
LAYERS = (Layers.Iono, Layers.Atmo)


def start() -> None:
    """radiocc"""
    with open(CONFIG_PATH) as f:
        CONFIG = DotMap(yaml.safe_load(f))
    FOLDERS_PATH = Path(CONFIG.folders_path)

    check_folders_path_valid(FOLDERS_PATH)

    print(f"Path to the folders: {FOLDERS_PATH.resolve()}.")
    initialization(FOLDERS_PATH)


def gui() -> None:
    """Graphical interface"""
    raise SystemExit(
        NotImplementedError(
            f"{fg('red')}"
            "Error: "
            "the graphical interface is not implemented yet."
            f"{attr(0)}"
        )
    )


def check_folders_path_valid(
    path: Union[str, Path], check_until: FoldersError = FoldersError.MissingFolder
) -> None:
    """Check whether the data folder is valid."""
    PATH = Path(path)

    # Check dir.
    if not PATH.is_dir():
        raise SystemExit(
            ValueError(
                f"{fg('red')}Error: {PATH.resolve()} is not a valid directory{attr(0)}"
            )
        )
    if check_until == FoldersError.NotADir:
        return

    # Check folders.
    DIRS = list(PATH.glob("*"))
    FOLDERS = [folder.name for folder in list(Folders)]
    ALL_DIRS = all(Path(DIR) in DIRS for DIR in FOLDERS)
    if not ALL_DIRS:
        raise SystemExit(
            ValueError(
                f"{fg('red')}"
                f"Error: {PATH.resolve()} is missing at least a folder from {FOLDERS}"
                f"{attr(0)}"
            )
        )
    if check_until == FoldersError.MissingFolder:
        return


def initialization(FOLDERS_PATH: Path) -> None:
    """Initialization"""

    PROCESSES_PATH = FOLDERS_PATH / Folders.TO_PROCESS.name

    for INDEX_PROCESS, PROCESS_PATH in enumerate(PROCESSES_PATH.iterdir()):
        print(f"Reading {PROCESS_PATH.name}..")

        for BAND in BANDS:
            print(f"  Band: {BAND.name}")

            for LAYER in LAYERS:
                print(f"    Layer: {LAYER.name}")

                SCENARIO = Scenario(PROCESS_PATH, BAND, LAYER, INDEX_PROCESS)

                run(SCENARIO)

            band_export(SCENARIO)


def run(SCENARIO: Scenario) -> None:
    """Run a scenario."""
    process_parser.prepare_directories(SCENARIO)
    FOLDER_TYPE = process_parser.detect_folder_type(SCENARIO.TO_PROCESS)

    if FOLDER_TYPE is None:
        return None

    process_parser.load_spice_kernels(SCENARIO.TO_PROCESS, FOLDER_TYPE)
    L2_DATA = process_parser.read_L2_data(SCENARIO, FOLDER_TYPE)

    if L2_DATA is None:
        return None

    EXPORT = reconstruct.run(SCENARIO, L2_DATA)

    export.run(SCENARIO, L2_DATA, EXPORT)


def band_export(SCENARIO: Scenario) -> None:
    """Finish the plots for the layers of a scenario."""
    # Interface with old code.
    i_Profile = SCENARIO.INDEX_PROCESS
    DATA_PRO = str(SCENARIO.TO_PROCESS.parent)
    DATA_ID = str(SCENARIO.TO_PROCESS.resolve())
    CODE_DIR = str(Path(old.__file__).parent.resolve())
    DATA_DIR = str(SCENARIO.TO_PROCESS.parent.parent.resolve())
    PLOT_DIR = str((SCENARIO.RESULT / ResultsFolders.PLOTS.name).resolve())
    DATA_FINAL_DIR = str((SCENARIO.RESULT / ResultsFolders.DATA.name).resolve())

    R17_Plot_profiles.PLOT2(  # type: ignore [no-untyped-call]
        DATA_ID,
        i_Profile,
        DATA_PRO,
        CODE_DIR,
        SCENARIO.BAND.name,
        DATA_DIR,
        constants.Threshold_Cor,
        constants.Threshold_Surface,
        DATA_FINAL_DIR,
        PLOT_DIR,
        constants.Threshold_int,
    )
