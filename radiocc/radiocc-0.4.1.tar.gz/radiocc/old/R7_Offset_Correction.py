import numpy as np
import os
from scipy import signal as sg
from pudb import set_trace as bp  # noqa

from radiocc.model import ProcessType


# Type = "Quadratic" or "Linear", threshold [m]
def Off_Cor(
    Type,
    threshold,
    Doppler,
    Diff_doppler,
    ET,
    N_data,
    distance,
    CODE_DIR,
    i_integral,
    Threshold_Surface,
    Threshold_int,
    FOLDER_TYPE,
):

    Doppler_debias = np.full(N_data, np.nan)
    Doppler_biasfit = np.full(N_data, np.nan)

    # altitude threshold for fit
    Corr_ind = 0
    for i in range(len(distance)):
        if distance[i] > threshold:
            Corr_ind += 1
    if Corr_ind == len(distance):
        Corr_ind = Corr_ind - 1
    # Search for maximum

    if len(Doppler) % 2 == 1:
        taille = len(Doppler)
    else:
        taille = len(Doppler) - 1

    Smoothed_Doppler = sg.savgol_filter(Doppler, taille, 40)
    deriv = np.gradient(Smoothed_Doppler)

    good = np.logical_and(
        deriv[np.array(np.where(deriv[:-1] < 1e-5)) - 1] < 0,
        deriv[np.array(np.where(deriv[:-1] < 1e-5)) + 1] > 0,
    )

    targ = np.where(deriv[:-1] < 1e-5)
    index = targ[0][good[0]]
    good_one = index[-1]

    # FIT
    if Type == "Fit":
        p = np.polyfit(
            np.append(ET[:Corr_ind], ET[good_one]),
            np.append(Doppler[:Corr_ind], Doppler[good_one]),
            2,
        )

        for i in range(i_integral, N_data):
            Doppler_biasfit[i] = p[0] * ET[i] ** 2 + p[1] * ET[i] + p[2]
    ###########################################################################################

    delET = []
    for i in range(N_data):
        delET.append(ET[i])
    # FIXME:
    # checkout Doppler_biasfit computation ET vs delET

    # bias fit
    if Type == "Linear":
        p = np.polyfit(ET[i_integral:Corr_ind], Doppler[i_integral:Corr_ind], 1)
        p0 = p[0]
        p1 = p[1]
        for i in range(N_data):
            Doppler_biasfit[i] = p[0] * (ET[i]) + p[1]

    elif Type == "Quadratic":
        p = np.polyfit(ET[i_integral:Corr_ind], Doppler[i_integral:Corr_ind], 2)
        p0 = p[0]
        p1 = p[1]
        p2 = p[2]
        for i in range(N_data):
            Doppler_biasfit[i] = p[0] * (ET[i]) ** 2 + p[1] * (ET[i] - ET[0]) + p[2]

    else:
        print("Type is not recognized")

    # subtract bias and scale residual
    for i in range(N_data):
        Doppler_debias[i] = Doppler[i] - Doppler_biasfit[i]

    if Type == "Linear":
        return (
            i_integral,
            ET,
            delET,
            Doppler_debias,
            Doppler_biasfit,
            Corr_ind,
            p0,
            p1,
        )

    if Type == "Quadraticuadratic":
        return (
            i_integral,
            ET,
            delET,
            Doppler_debias,
            Doppler_biasfit,
            Corr_ind,
            p0,
            p1,
            p2,
        )
