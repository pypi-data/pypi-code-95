#!/usr/bin/env python3

"""
Radio occultation.
"""

from pathlib import Path

from pudb import set_trace as bp  # noqa: F401

from radiocc import (
    Bands,
    Config,
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

BANDS = (Bands.X,)
LAYERS = (Layers.Iono, Layers.Atmo)


def initialization(CFG: Config) -> None:
    """Initialization"""

    for INDEX_PROCESS, PROCESS_PATH in enumerate(CFG.to_process.iterdir()):
        print(f"Reading {PROCESS_PATH.name}..")

        for BAND in BANDS:
            print(f"  Band: {BAND.name}")

            for LAYER in LAYERS:
                print(f"    Layer: {LAYER.name}")

                SCENARIO = Scenario(PROCESS_PATH, BAND, LAYER, INDEX_PROCESS)

                run(CFG, SCENARIO)

            band_export(CFG, SCENARIO)


def run(CFG: Config, SCENARIO: Scenario) -> None:
    """Run a scenario."""
    process_parser.prepare_directories(CFG, SCENARIO)
    FOLDER_TYPE = process_parser.detect_folder_type(SCENARIO.TO_PROCESS)

    if FOLDER_TYPE is None:
        return None

    process_parser.load_spice_kernels(SCENARIO.TO_PROCESS, FOLDER_TYPE)
    L2_DATA = process_parser.read_L2_data(CFG, SCENARIO, FOLDER_TYPE)

    if L2_DATA is None:
        return None

    EXPORT = reconstruct.run(CFG, SCENARIO, L2_DATA)

    export.run(SCENARIO, L2_DATA, EXPORT)


def band_export(CFG: Config, SCENARIO: Scenario) -> None:
    """Finish the plots for the layers of a scenario."""
    # Interface with old code.
    RESULTS = SCENARIO.results(CFG.results)
    i_Profile = SCENARIO.INDEX_PROCESS
    DATA_PRO = str(SCENARIO.TO_PROCESS.parent)
    DATA_ID = str(SCENARIO.TO_PROCESS.resolve())
    CODE_DIR = str(Path(old.__file__).parent.resolve())
    DATA_DIR = str(SCENARIO.TO_PROCESS.parent.parent.resolve())
    PLOT_DIR = str((RESULTS / ResultsFolders.PLOTS.name).resolve())
    DATA_FINAL_DIR = str((RESULTS / ResultsFolders.DATA.name).resolve())

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
