#!/usr/bin/env python3
# mypy: ignore-errors

"""
Reconstruct.
"""

from pathlib import Path
from typing import Any  # noqa

import numpy
from pudb import set_trace as bp  # noqa

from radiocc import constants, old
from radiocc.model import Export, L2Data, ProcessType, ResultsFolders, Scenario
from radiocc.old import (
    R4_State_Vectors_twoway_v2,
    R5_Foot_Print,
    R6_Framework_Conversion,
    R7_Offset_Correction,
    R8_Plot_Doppler_1,
    R15_Errors,
    R16_Biasfit_Correction,
    R17_Run_Routines1,
    R18_Occ_Info_MVN,
)


def run(  # noqa: C901
    scenario: Scenario,
    l2_data: L2Data,
) -> Export:
    # =================================================================================
    # Interface between new & old code
    # =================================================================================
    DATA = l2_data.DATA
    ET = DATA.ET
    N_data = ET.shape[0]
    Doppler = DATA.DOPPLER

    if l2_data.FOLDER_TYPE == ProcessType.MEX:
        Diff_doppler = DATA.DIFF_DOPPLER
        distance = DATA.DISTANCE
        i_Surface = numpy.where(DATA.SURFACES_CONDITIONS)[0]
        i_integral = numpy.where(DATA.INTEGRAL_CONDITIONS)[0]
        i_Surface = N_data - 1 if not i_Surface.size else i_Surface[0]
        i_integral = 0 if not i_Surface.size else i_integral[0]
        fsup = DATA.FSUP
        error = DATA.ERROR
    else:
        # fsky = DATA.FSKY
        error = numpy.zeros(N_data)
        error_ref = numpy.zeros(N_data)
        error_elec = numpy.zeros(N_data)
        error_neut = numpy.zeros(N_data)
        Diff_doppler = numpy.zeros(N_data)
        fsup = 7.2e9
        i_integral = None

    NAIF_SC = str(l2_data.SPACECRAFT_NAIF_CODE)
    NAIF_GS = str(l2_data.dsn_station_naif_code)
    NAIF_P = str(l2_data.PLANET_NAIF_CODE)

    item = scenario.LAYER.name.upper()
    Bande = scenario.BAND.name.upper()
    DATA_PRO = str(scenario.TO_PROCESS.parent)
    DATA_ID_i_profile = str(scenario.TO_PROCESS.resolve())
    CODE_DIR = str(Path(old.__file__).parent.resolve())
    DATA_DIR = str(scenario.TO_PROCESS.parent.parent.resolve())
    PLOT_DIR = str((scenario.RESULT / ResultsFolders.PLOTS.name).resolve())
    EPHE_DIR = str((scenario.RESULT / ResultsFolders.EPHEMERIDS.name).resolve())
    DATA_FINAL_DIR = str((scenario.RESULT / ResultsFolders.DATA.name).resolve())

    c = constants.c
    R_Planet = constants.R_Planet
    e = constants.e
    eps0 = constants.eps0
    me = constants.me
    CC = constants.CC
    kB = constants.kB
    V = constants.V
    Ref_frame = constants.Ref_frame
    B_Cor_Type = constants.B_Cor_Type
    Threshold_Cor = constants.Threshold_Cor
    Threshold_int = constants.Threshold_int
    Threshold_neut_upp = constants.Threshold_neut_upp
    Threshold_Surface = constants.Threshold_Surface
    # =================================================================================

    # R5: State_Vectors_twoway
    (
        t0_up,
        pos_GS_up,
        vel_GS_up,
        pos_MEX_up,
        vel_MEX_up,
        tMEX,
        t0_dn,
        pos_GS_dn,
        vel_GS_dn,
        pos_MEX_dn,
        vel_MEX_dn,
        t0_upp,
        pos_GS_upp,
        vel_GS_upp,
        pos_MEX_upp,
        vel_MEX_upp,
        pos_MEX,
        vel_MEX,
        ET_MEX_Mars,
    ) = R4_State_Vectors_twoway_v2.ephemerides(
        N_data, ET, NAIF_SC, NAIF_GS, NAIF_P, DATA_PRO, Ref_frame, l2_data.FOLDER_TYPE
    )

    # R6: footprint
    d_lat, d_lon, dist_Mars_Sun, spclon_SC, spclat_SC, re, f = R5_Foot_Print.long_lat(
        N_data, pos_MEX, vel_MEX, ET, ET_MEX_Mars, Ref_frame, l2_data.FOLDER_TYPE
    )

    # R7 coordinate frames
    (
        r_MEX_up,
        z_MEX_up,
        z_GS_up,
        vr_MEX_up,
        vz_MEX_up,
        vr_GS_up,
        vz_GS_up,
        gamma_up,
        beta_e_up,
        delta_s_up,
    ) = R6_Framework_Conversion.Occ_Plane_Conversion(
        N_data, pos_MEX_up, vel_MEX_up, pos_GS_up, vel_GS_up
    )

    # R7 coordinate frames
    (
        r_MEX_dn,
        z_MEX_dn,
        z_GS_dn,
        vr_MEX_dn,
        vz_MEX_dn,
        vr_GS_dn,
        vz_GS_dn,
        gamma_dn,
        beta_e_dn,
        delta_s_dn,
    ) = R6_Framework_Conversion.Occ_Plane_Conversion(
        N_data, pos_MEX_dn, vel_MEX_dn, pos_GS_dn, vel_GS_dn
    )

    if l2_data.FOLDER_TYPE == ProcessType.MAVEN:
        # R18 : Occ_info :
        distance = R18_Occ_Info_MVN.occultation_info(
            NAIF_P,
            NAIF_GS,
            ET,
            Ref_frame,
            NAIF_SC,
            DATA_PRO,
            DATA_ID_i_profile,
            Threshold_Surface,
            EPHE_DIR,
        )

        i_Surface = numpy.where(numpy.array(distance) <= Threshold_Surface)[0]
        if i_Surface.size == 0:
            i_Surface = N_data - 1
        else:
            i_Surface = i_Surface[0]
        i_integral = numpy.where(numpy.array(distance) <= Threshold_int)[0]
        if i_integral.size == 0:
            i_integral = 0
        else:
            i_integral = i_integral[0]

    if B_Cor_Type == "Linear":
        (
            i_integral,
            ET,
            delET,
            Doppler_debias,
            Doppler_biasfit,
            Corr_ind,
            p0,
            p1,
        ) = R7_Offset_Correction.Off_Cor(
            B_Cor_Type,
            Threshold_Cor,
            Doppler,
            Diff_doppler,
            ET,
            N_data,
            distance,
            CODE_DIR,
            i_integral,
            Threshold_Surface,
            Threshold_int,
            l2_data.FOLDER_TYPE,
        )
    if B_Cor_Type == "Quadratic":
        (
            i_integral,
            i_Surface,
            ET,
            delET,
            Doppler_debias,
            Doppler_biasfit,
            Corr_ind,
            p0,
            p1,
            p2,
        ) = R7_Offset_Correction.Off_Cor(
            i_integral,
            i_Surface,
            ET,
            delET,
            B_Cor_Type,
            Threshold_Cor,
            Doppler,
            Diff_doppler,
            ET,
            N_data,
            distance,
            CODE_DIR,
            i_integral,
            Threshold_Surface,
            Threshold_int,
            l2_data.FOLDER_TYPE,
        )

    # R5: Plot doppler after bias correction
    R8_Plot_Doppler_1.PLOT_Dop1(
        distance, Doppler, Doppler_debias, Doppler_biasfit, ET, PLOT_DIR, N_data
    )
    HAPPY_or_NOT = str(input("Enter 'YES' if the debias is good and 'NO' if bad: "))
    while HAPPY_or_NOT == "NO":
        NEW_THRESHOLD = float(input("Enter new threshold altitude = "))
        NEW_TYPE = str(input("Enter new type, Linear or Quadratic: "))
        if NEW_TYPE == "Linear":
            (
                i_integral,
                ET,
                delET,
                Doppler_debias,
                Doppler_biasfit,
                Corr_ind,
                p0,
                p1,
            ) = R7_Offset_Correction.Off_Cor(
                NEW_TYPE,
                NEW_THRESHOLD,
                Doppler,
                Diff_doppler,
                ET,
                N_data,
                distance,
                CODE_DIR,
                i_integral,
                Threshold_Surface,
                Threshold_int,
                l2_data.FOLDER_TYPE,
            )
        if NEW_TYPE == "Quadratic":
            (
                i_integral,
                ET,
                delET,
                Doppler_debias,
                Doppler_biasfit,
                Corr_ind,
                p0,
                p1,
                p2,
            ) = R7_Offset_Correction.Off_Cor(
                NEW_TYPE,
                NEW_THRESHOLD,
                Doppler,
                Diff_doppler,
                ET,
                N_data,
                distance,
                CODE_DIR,
                i_integral,
                Threshold_Surface,
                Threshold_int,
                l2_data.FOLDER_TYPE,
            )

        R8_Plot_Doppler_1.PLOT_Dop1(
            distance, Doppler, Doppler_debias, Doppler_biasfit, ET, PLOT_DIR, N_data
        )
        HAPPY_or_NOT = str(input("Enter 'YES' if the debias is good and 'NO' if bad: "))
        if HAPPY_or_NOT == "YES":
            break
    if item == "IONO":
        refractivity, Ne, TEC = R17_Run_Routines1.run(
            Doppler_debias,
            N_data,
            r_MEX_up,
            z_MEX_up,
            z_GS_up,
            vr_MEX_up,
            vz_MEX_up,
            vr_GS_up,
            vz_GS_up,
            gamma_up,
            beta_e_up,
            delta_s_up,
            r_MEX_dn,
            z_MEX_dn,
            z_GS_dn,
            vr_MEX_dn,
            vz_MEX_dn,
            vr_GS_dn,
            vz_GS_dn,
            gamma_dn,
            beta_e_dn,
            delta_s_dn,
            Bande,
            fsup,
            c,
            Diff_doppler,
            item,
            i_integral,
            i_Surface,
            R_Planet,
            e,
            eps0,
            me,
            distance,
            Doppler,
            PLOT_DIR,
            Threshold_neut_upp,
            CC,
            kB,
            EPHE_DIR,
            NAIF_SC,
            NAIF_P,
            NAIF_GS,
            ET,
            Ref_frame,
            DATA_ID_i_profile,
            DATA_DIR,
            Threshold_Surface,
        )
    if item == "ATMO":
        refractivity, Nn = R17_Run_Routines1.run(
            Doppler_debias,
            N_data,
            r_MEX_up,
            z_MEX_up,
            z_GS_up,
            vr_MEX_up,
            vz_MEX_up,
            vr_GS_up,
            vz_GS_up,
            gamma_up,
            beta_e_up,
            delta_s_up,
            r_MEX_dn,
            z_MEX_dn,
            z_GS_dn,
            vr_MEX_dn,
            vz_MEX_dn,
            vr_GS_dn,
            vz_GS_dn,
            gamma_dn,
            beta_e_dn,
            delta_s_dn,
            Bande,
            fsup,
            c,
            Diff_doppler,
            item,
            i_integral,
            i_Surface,
            R_Planet,
            e,
            eps0,
            me,
            distance,
            Doppler,
            PLOT_DIR,
            Threshold_neut_upp,
            CC,
            kB,
            EPHE_DIR,
            NAIF_SC,
            NAIF_P,
            NAIF_GS,
            ET,
            Ref_frame,
            DATA_ID_i_profile,
            DATA_DIR,
            Threshold_Surface,
        )

    RefCorr_GD_or_NOT = str(
        input("Enter 'YES' if the refractivity correction is good and 'NO' if bad: ")
    )
    while RefCorr_GD_or_NOT == "NO":
        if B_Cor_Type == "Linear":
            print("\t p0 = ", p0)
            print("\t p1 = ", p1)

        if B_Cor_Type == "Quadratic":
            print("\t p0 = ", p0)
            print("\t p1 = ", p1)
            print("\t p2 = ", p2)
        R16_Biasfit_Correction.Off_Cor2(
            B_Cor_Type, Doppler, Diff_doppler, ET, N_data, distance
        )
        if item == "IONO":
            refractivity, Ne, TEC = R17_Run_Routines1.run(
                Doppler_debias,
                N_data,
                r_MEX_up,
                z_MEX_up,
                z_GS_up,
                vr_MEX_up,
                vz_MEX_up,
                vr_GS_up,
                vz_GS_up,
                gamma_up,
                beta_e_up,
                delta_s_up,
                r_MEX_dn,
                z_MEX_dn,
                z_GS_dn,
                vr_MEX_dn,
                vz_MEX_dn,
                vr_GS_dn,
                vz_GS_dn,
                gamma_dn,
                beta_e_dn,
                delta_s_dn,
                Bande,
                fsup,
                c,
                Diff_doppler,
                item,
                i_integral,
                i_Surface,
                R_Planet,
                e,
                eps0,
                me,
                distance,
                Doppler,
                PLOT_DIR,
                Threshold_neut_upp,
                CC,
                kB,
                EPHE_DIR,
                NAIF_SC,
                NAIF_P,
                NAIF_GS,
                ET,
                Ref_frame,
                DATA_ID_i_profile,
                DATA_DIR,
                Threshold_Surface,
            )
        if item == "ATMO":
            refractivity, Nn = R17_Run_Routines1.run(
                Doppler_debias,
                N_data,
                r_MEX_up,
                z_MEX_up,
                z_GS_up,
                vr_MEX_up,
                vz_MEX_up,
                vr_GS_up,
                vz_GS_up,
                gamma_up,
                beta_e_up,
                delta_s_up,
                r_MEX_dn,
                z_MEX_dn,
                z_GS_dn,
                vr_MEX_dn,
                vz_MEX_dn,
                vr_GS_dn,
                vz_GS_dn,
                gamma_dn,
                beta_e_dn,
                delta_s_dn,
                Bande,
                fsup,
                c,
                Diff_doppler,
                item,
                i_integral,
                i_Surface,
                R_Planet,
                e,
                eps0,
                me,
                distance,
                Doppler,
                PLOT_DIR,
                Threshold_neut_upp,
                CC,
                kB,
                EPHE_DIR,
                NAIF_SC,
                NAIF_P,
                NAIF_GS,
                ET,
                Ref_frame,
                DATA_ID_i_profile,
                DATA_DIR,
                Threshold_Surface,
            )

        RefCorr_GD_or_NOT = str(
            input(
                "Enter 'YES' if the refractivity correction is good and 'NO' if bad: "
            )
        )

        if RefCorr_GD_or_NOT == "YES":
            break
    error_ref, error_elec, error_neut = R15_Errors.ERRORS(
        N_data, fsup, error, c, distance, Threshold_neut_upp, V, e, eps0, me, Bande, CC
    )

    # Return variables to be exported.

    export = Export()
    export.DATA_PATH = Path(DATA_FINAL_DIR)
    export.PLOT_PATH = Path(PLOT_DIR)
    export.EPHE_PATH = Path(EPHE_DIR)
    export.DOPPLER = Doppler
    export.DOPPLER_DEBIAS = Doppler_debias
    export.DOPPLER_BIAS_FIT = Doppler_biasfit
    export.DISTANCE = distance
    export.REFRACTIVITY = refractivity
    export.ERROR = error
    export.ERROR_REFRAC = error_ref

    if item == "IONO":
        export.NE = Ne
        export.ERROR_ELEC = error_elec
        export.TEC = TEC
    else:
        export.NE = Nn
        export.ERROR_ELEC = error_neut
        export.TEC = None

    return export
