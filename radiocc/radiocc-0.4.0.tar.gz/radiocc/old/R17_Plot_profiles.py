import numpy as np
import os
import matplotlib.pyplot as plt
import csv
import pylab
import matplotlib.ticker
import sys
import pandas as pd
import sys
import scipy.stats as sc
import matplotlib
import glob

from pudb import set_trace as bp  # noqa


def PLOT(
    DATA_ID,
    i_Profile,
    DATA_PRO,
    Patzold_DIR,
    CODE_DIR,
    Bande,
    DATA_DIR,
    Threshold_Cor,
    Threshold_Surf,
    DATA_FINAL_DIR_ATMO,
    DATA_FINAL_DIR_IONO,
    PLOT_DIR,
    Threshold_int,
):

    ############################## NEW PART #########################
    ############################## PATZOLD FINDER ###################

    DATA = DATA_ID[i_Profile]

    os.listdir(DATA_PRO)
    path = np.array(pd.Series(os.listdir(DATA_PRO)).str.split(",").tolist())
    count = np.where(path == DATA)

    DATA_path = DATA_PRO + "/" + path[count][0]

    TXT = DATA_path + "/AAREADME.TXT"

    info = open(TXT, "r")
    info.readline()
    for line in info:
        if "Data from Experiments" in line:
            the_line = line
    cond = -999
    test = np.array(pd.Series(the_line).str.split("/").tolist())

    day_number = (test[0][1]).astype(np.int).astype(np.string_).decode("UTF-8")
    year = np.array(pd.Series(test[0][0]).str.split(" ").tolist())[0][-1]

    # Go to the good year folder :

    Patzold_iono = Patzold_DIR + "/OCC_IONO/"
    Patzold_atmo = Patzold_DIR + "/OCC_ATMO/"

    index_file_iono = np.where(np.array(os.listdir(Patzold_iono)) == year)
    index_file_atmo = np.where(np.array(os.listdir(Patzold_atmo)) == year)

    if np.shape(index_file_iono)[0] == 0:
        print("No IONO Patzold data file available for this year")
        cond = 0
    else:
        Patzold_iono = Patzold_iono + os.listdir(Patzold_iono)[index_file_iono[0][0]]

    if np.shape(index_file_atmo)[0] == 0:
        print("No ATMO Patzold data file available for this year")
        cond = 0
    else:
        Patzold_atmo = Patzold_atmo + os.listdir(Patzold_atmo)[index_file_atmo[0][0]]

        # Go to the good folder according to the day number
        step = 0
        for file in glob.glob(Patzold_iono + "/" + "*" + str(day_number) + "*"):
            step = step + 1
            if step > 0:
                path_new = file
        step1 = 0
        for file1 in glob.glob(Patzold_atmo + "/" + "*" + str(day_number) + "*"):
            step1 = step1 + 1
            if step1 > 0:
                path_new_1 = file1

        if step == 0:
            print("No IONO Patzold data file available for this orbit")
            cond = 0
        else:
            Patzold_iono = path_new + "/"

        if step1 == 0:
            print("No ATMO Patzold data file available for this orbit")
            cond = 0
        else:
            Patzold_atmo = path_new_1 + "/"

            # Les fichiers avec l'acronyme IIX :
            files_AIX = []
            files_IIX = []

            for file in glob.glob(Patzold_iono + "*IIX*.TAB"):
                files_IIX.append(file)

            for file in glob.glob(Patzold_atmo + "*AIX*.TAB"):
                files_AIX.append(file)
            if np.shape(files_IIX)[0] == 0:
                print("No IONO Patzold processed data file available for this orbit")
                cond = 0
            else:
                path_iono = files_IIX[-1]

            # Les fichiers avec l'acronyme AIX :

            if np.shape(files_AIX)[0] == 0:
                print("No ATMO Patzold processed data file available for this orbit")
                cond = 0
            else:
                path_atmo = files_AIX[-1]

    ###################################### END ####################################

    ########Patzold data#########################################################################

    if cond == 0:
        file_ion = []
    else:
        file_ion = path_iono

    if cond == 0:
        file_atmo = []
    else:
        file_atm = path_atmo

    file_iono = np.genfromtxt(file_ion, dtype=None)
    file_atmo = np.genfromtxt(file_atm, dtype=None)

    ###Loading Python output#################################################################################

    Python_OUT_IONO = []
    N_data_IONO = []

    # output filename
    if Bande == "X":
        Python_OUT_IONO.append(
            DATA_FINAL_DIR_IONO + "/OUT_DPX_IONO_v12a_" + str(i_Profile + 1) + ".txt"
        )
    if Bande == "S":
        Python_OUT_IONO.append(
            DATA_FINAL_DIR_IONO + "/OUT_DPS_IONO_v12a_" + str(i_Profile + 1) + ".txt"
        )
    if Bande == "Diff":
        Python_OUT_IONO.append(
            DATA_FINAL_DIR_IONO + "/OUT_Diff_IONO_v12a_" + str(i_Profile + 1) + ".txt"
        )

    output_data_IONO = np.genfromtxt(Python_OUT_IONO[-1], dtype=None)
    N_data_IONO = len(output_data_IONO)
    Doppler = []
    Doppler_debias = []
    Doppler_biasfit = []
    distance = []
    refractivity1 = []
    Ne = []
    error = []
    error_refrac1 = []
    error_elec = []

    for i in range(N_data_IONO):
        Doppler.append(output_data_IONO[i][0])
        Doppler_debias.append(output_data_IONO[i][1])
        Doppler_biasfit.append(output_data_IONO[i][2])
        distance.append(output_data_IONO[i][3])
        refractivity1.append(output_data_IONO[i][4])
        Ne.append(output_data_IONO[i][5])
        error.append(output_data_IONO[i][6])
        error_refrac1.append(output_data_IONO[i][7])
        error_elec.append(output_data_IONO[i][8])

    Python_OUT_ATMO = []
    N_data_ATMO = []

    # output filename
    if Bande == "X":
        Python_OUT_ATMO.append(
            DATA_FINAL_DIR_ATMO + "/OUT_DPX_ATMO_v12a_" + str(i_Profile + 1) + ".txt"
        )
    if Bande == "S":
        Python_OUT_ATMO.append(
            DATA_FINAL_DIR_ATMO + "/OUT_DPS_ATMO_v12a_" + str(i_Profile + 1) + ".txt"
        )
    if Bande == "Diff":
        Python_OUT_ATMO.append(
            DATA_FINAL_DIR_ATMO + "/OUT_Diff_ATMO_v12a_" + str(i_Profile + 1) + ".txt"
        )
    # print('*** ' + Python_OUT[-1] + '\n')
    output_data_ATMO = np.genfromtxt(Python_OUT_ATMO[-1], dtype=None)
    N_data_ATMO = len(output_data_ATMO)
    Doppler = []
    Doppler_debias = []
    Doppler_biasfit = []
    distance = []
    refractivity2 = []
    Nn = []
    error = []
    error_refrac2 = []
    error_neut = []

    for i in range(N_data_ATMO):
        Doppler.append(output_data_ATMO[i][0])
        Doppler_debias.append(output_data_ATMO[i][1])
        Doppler_biasfit.append(output_data_ATMO[i][2])
        distance.append(output_data_ATMO[i][3] / 1e3)
        refractivity2.append(output_data_ATMO[i][4])
        Nn.append(output_data_ATMO[i][5])
        error.append(output_data_ATMO[i][6])
        error_refrac2.append(output_data_ATMO[i][7])
        error_neut.append(output_data_ATMO[i][8])

    # #########print L2_data#################################################################################
    # os.chdir(DATA_PRO)
    # PATH = os.path.normpath(DATA_PRO + os.sep + os.pardir)

    # if Bande == 'X':
    #     if os.path.getsize(PATH+'/INFORMATION/PATH_X.txt') == 0 :
    #         print('No data available in X')
    #         sys.exit('No data to plot')
    #     else:
    #         file = open(PATH+'/INFORMATION/PATH_X.txt', 'r')
    #         PATH_X = file.read()
    #         L2_data = np.genfromtxt(PATH_X,dtype=None)
    # else :
    #     if os.path.getsize(PATH+'/INFORMATION/PATH_S.txt') == 0 :
    #         print('No data available in S')
    #         sys.exit('No data to plot')
    #     else:
    #         file = open(PATH+'/INFORMATION/PATH_S.txt', 'r')
    #         PATH_S = file.read()
    #         L2_data = np.genfromtxt(PATH_S,dtype=None)

    # Patzold IONO labels
    SAMPLE_NUMBER_IONO = []
    UTC_TIME_IONO = []
    EPHEMERIS_SECONDS_IONO = []
    RADIUS_IONO = []
    REFRACTIVITY_IONO = []
    ELECTRON_NUMBER_DENSITY_IONO = []
    SIGMA_ELECTRON_NUMBER_DENSITY_IONO = []

    for i in range(len(file_iono)):
        SAMPLE_NUMBER_IONO.append(file_iono[i][0])
        UTC_TIME_IONO.append(file_iono[i][1])
        EPHEMERIS_SECONDS_IONO.append((file_iono[i][2]))
        RADIUS_IONO.append((file_iono[i][3]))
        REFRACTIVITY_IONO.append(file_iono[i][7])
        ELECTRON_NUMBER_DENSITY_IONO.append((float(file_iono[i][9])))
        SIGMA_ELECTRON_NUMBER_DENSITY_IONO.append(file_iono[i][10])

    # Patzold ATMO labels
    UTC_TIME_ATMO = []
    EPHEMERIS_SECONDS_ATMO = []
    RADIUS_ATMO = []
    NUMBER_DENSITY_ATMO = []

    for i in range(len(file_atmo)):
        UTC_TIME_ATMO.append(file_atmo[i][1])
        EPHEMERIS_SECONDS_ATMO.append(file_atmo[i][2])
        RADIUS_ATMO.append(file_atmo[i][3])
        NUMBER_DENSITY_ATMO.append(file_atmo[i][20])

    distance = np.array(distance) - Threshold_Surf / 1e3
    RADIUS_IONO = np.array(RADIUS_IONO) - Threshold_Surf / 1e3
    RADIUS_ATMO = np.array(RADIUS_ATMO) - Threshold_Surf / 1e3

    ########Plot files##########################################################################
    # retval = os.getcwd()
    # print("Current working directory %s" % retval)
    # min_y = Threshold_Surf
    # max_y = Threshold_Cor

    # min_y = Threshold_Surf
    # max_y = Threshold_Cor
    Doppler = np.array(Doppler)
    Doppler_debias = np.array(Doppler_debias)
    cond_dop = Doppler < 1
    cond_deb = Doppler_debias < 1

    fig6 = plt.figure(6)
    plt.errorbar(
        Doppler,
        distance,
        xerr=np.array(error),
        fmt="o",
        color="black",
        ecolor="lightgray",
        elinewidth=1,
        capsize=1,
        ms=1,
        label="Raw L2 Data",
    )  # (1+880./749.)
    plt.errorbar(
        Doppler_debias,
        distance,
        xerr=np.array(error),
        fmt="o",
        color="red",
        ecolor="lightgray",
        elinewidth=1,
        capsize=1,
        ms=1,
        label="Debias Raw L2 Data",
    )  # (1+880./749.)

    Doppler = Doppler[cond_dop]
    Doppler_debias = Doppler_debias[cond_deb]

    min_x1 = (
        np.nanmedian(Doppler_debias)
        - sc.median_absolute_deviation(Doppler_debias, nan_policy="omit") * 5
    )
    min_x2 = (
        np.nanmedian(Doppler)
        - sc.median_absolute_deviation(Doppler, nan_policy="omit") * 5
    )
    max_x1 = (
        np.nanmedian(Doppler_debias)
        + sc.median_absolute_deviation(Doppler_debias, nan_policy="omit") * 5
    )
    max_x2 = (
        np.nanmedian(Doppler)
        + sc.median_absolute_deviation(Doppler, nan_policy="omit") * 5
    )
    min_x = min([min_x1, min_x2])
    max_x = max([max_x1, max_x2])

    # plt.plot(Wang_dig_1, Wang_dig_2, label = 'Wang et al. ')
    plt.xlabel("Doppler Frequency Residuals (Hz)")
    plt.ylabel("Altitude (km)")
    plt.xlim(min_x, max_x)
    plt.ylim(ymin=0)
    plt.legend()
    plt.grid(True)
    fig6.set_size_inches(8, 6)  # Inch
    plt.close(fig6)
    ############################ REFRACTIVITY ATMO

    fig20 = plt.figure(20)
    cond_ref2 = np.where(np.array(refractivity2) > -1)
    if Bande == "X":
        plt.errorbar(
            np.array(refractivity2)[cond_ref2],
            np.array(distance)[cond_ref2],
            xerr=np.array(error_refrac2)[cond_ref2],
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="X-Band Data",
        )

    if Bande == "S":

        plt.errorbar(
            np.array(refractivity2)[cond_ref2],
            np.array(distance)[cond_ref2],
            xerr=np.array(error_refrac2)[cond_ref2],
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="S-Band Data",
        )

    if Bande == "Diff":

        plt.errorbar(
            np.array(refractivity2)[cond_ref2],
            np.array(distance)[cond_ref2],
            xerr=np.array(error_refrac2)[cond_ref2],
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="Differential Doppler Data",
        )

    plt.xlabel("Refractivity")
    plt.ylabel("Altitude (km)")
    pylab.legend(loc="upper right")

    min_x = np.nanmin(np.array(refractivity2)[cond_ref2])
    max_x = (
        np.nanmedian(np.array(refractivity2)[cond_ref2])
        + sc.median_absolute_deviation(
            np.array(refractivity2)[cond_ref2], nan_policy="omit"
        )
        * 15
    )

    plt.xlim(min_x, max_x)
    plt.grid(True)
    plt.legend()
    fig20.set_size_inches(8, 6)  # Inch

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "refractivity_ATMO_X.png", dpi=600)
    if Bande == "S":
        plt.savefig(PLOT_DIR + "/" + "refractivity_ATMO_S.png", dpi=600)
    if Bande == "Diff":
        plt.savefig(PLOT_DIR + "/" + "refractivity_ATMO_Diff.png", dpi=600)

    plt.close(fig20)

    ########################## REFRACTIVITY IONO

    fig10 = plt.figure(10)
    cond_ref1 = np.where(np.array(refractivity1) > -1)

    if Bande == "X":
        plt.errorbar(
            np.array(refractivity1)[cond_ref1],
            np.array(distance)[cond_ref1],
            xerr=np.array(error_refrac1)[cond_ref1],
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="X-Band Data",
        )

    if Bande == "S":
        plt.errorbar(
            np.array(refractivity1)[cond_ref1],
            np.array(distance)[cond_ref1],
            xerr=np.array(error_refrac1)[cond_ref1],
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="S-Band Data",
        )

    if Bande == "Diff":
        plt.errorbar(
            np.array(refractivity1)[cond_ref1],
            np.array(distance)[cond_ref1],
            xerr=np.array(error_refrac1)[cond_ref1],
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="Differential Doppler  Data",
        )

    plt.xlabel("Refractivity")
    plt.ylabel("Altitude (km)")
    pylab.legend(loc="upper right")

    min_x = np.nanmin(np.array(refractivity1)[cond_ref1])
    max_x = (
        np.nanmedian(np.array(refractivity1)[cond_ref1])
        + sc.median_absolute_deviation(
            np.array(refractivity1)[cond_ref1], nan_policy="omit"
        )
        * 15
    )

    plt.xlim(min_x, max_x)
    #    plt.ylim(min_y,max_y)
    #    mf = matplotlib.ticker.ScalarFormatter(useOffset=False, useMathText=True)
    #    mf.set_powerlimits((-3,3))
    #    plt.gca().xaxis.set_major_formatter(mf)
    plt.grid(True)
    fig10.set_size_inches(8, 6)  # Inch

    if Bande == "X":
        if cond != 0:
            plt.plot(
                np.array(
                    REFRACTIVITY_IONO[int(len(np.array(REFRACTIVITY_IONO)) / 2) :]
                ),
                RADIUS_IONO[int(len(np.array(REFRACTIVITY_IONO)) / 2) :],
                ":g",
                label="Patzold et al.",
            )

    plt.legend()

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "refractivity_IONO_X.png", dpi=600)
    if Bande == "S":
        plt.savefig(PLOT_DIR + "/" + "refractivity_IONO_S.png", dpi=600)
    if Bande == "Diff":
        plt.savefig(PLOT_DIR + "/" + "refractivity_IONO_Diff.png", dpi=600)

    plt.close(fig10)

    ########################## Electron Density
    fig8 = plt.figure(8)

    if Bande == "X":
        plt.errorbar(
            np.array(Ne),
            distance,
            xerr=error_elec,
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="X-Band Data" + year + "" + day_number,
        )

    if Bande == "S":
        plt.errorbar(
            np.array(Ne),
            distance,
            xerr=error_elec,
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="S-Band Data" + year + "" + day_number,
        )

    if Bande == "Diff":
        plt.errorbar(
            np.array(Ne),
            distance,
            xerr=error_elec,
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="Differential Doppler" + year + "" + day_number,
        )

    plt.xlabel("Electron density (el/m$^{3}$)")
    plt.ylabel("Altitude (km)")
    pylab.legend(loc="upper right")

    min_x = np.nanmedian(Ne) - sc.median_absolute_deviation(Ne, nan_policy="omit") * 3
    max_x = (
        np.nanmax(np.array(Ne)[np.array(Ne) < 1e13])
        + sc.median_absolute_deviation(
            np.array(Ne)[np.array(Ne) < 1e13], nan_policy="omit"
        )
        * 15
    )

    plt.xlim(min_x, max_x)
    #    plt.ylim(min_y,max_y)
    #    mf = matplotlib.ticker.ScalarFormatter(useOffset=False, useMathText=True)
    #    mf.set_powerlimits((-3,3))
    #    plt.gca().xaxis.set_major_formatter(mf)
    plt.grid(True)
    fig8.set_size_inches(8, 6)  # Inch

    if Bande == "X":
        if cond != 0:
            plt.plot(
                np.array(ELECTRON_NUMBER_DENSITY_IONO) * 1e6,
                RADIUS_IONO,
                ":g",
                label="Patzold et al.",
            )
            # plt.plot(Wang_X_Ne, Wang_X_alt, 'k', label = 'Wang et al.')

    plt.legend

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "Ne_X.png", dpi=600)
    if Bande == "S":
        plt.savefig(PLOT_DIR + "/" + "Ne_S.png", dpi=600)
    if Bande == "Diff":
        plt.savefig(PLOT_DIR + "/" + "Ne_Diff.png", dpi=600)
    plt.close(fig8)

    fig11 = plt.figure(11)
    xmini = 10 ** (10)
    index = np.where(np.array(Ne) > xmini)
    if Bande == "X":
        plt.errorbar(
            np.array(Ne[index[0][0] : index[0][-1]]),
            distance[index[0][0] : index[0][-1]],
            xerr=error_elec[index[0][0] : index[0][-1]],
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="X-Band Data" + year + "" + day_number,
        )

    if Bande == "S":
        plt.errorbar(
            np.array(Ne[index[0][0] : index[0][-1]]),
            distance[index[0][0] : index[0][-1]],
            xerr=error_elec[index[0][0] : index[0][-1]],
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="S-Band Data" + year + "" + day_number,
        )

    if Bande == "Diff":
        plt.errorbar(
            np.array(Ne[index[0][0] : index[0][-1]]),
            distance[index[0][0] : index[0][-1]],
            xerr=error_elec[index[0][0] : index[0][-1]],
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="Differential Doppler Data" + year + "" + day_number,
        )
    plt.xlabel("Electron density (el/m$^{3}$)")
    plt.ylabel("Altitude (km)")
    pylab.legend(loc="upper right")

    # plt.xlim(min_x, 1.5E11)
    #    plt.ylim(min_y,max_y)
    #    mf = matplotlib.ticker.ScalarFormatter(useOffset=False, useMathText=True)
    #    mf.set_powerlimits((-3,3))
    #    plt.gca().xaxis.set_major_formatter(mf)
    plt.grid(True)
    plt.legend()
    fig11.set_size_inches(8, 6)  # Inch
    plt.xscale("log")
    plt.xlim(xmin=xmini)
    if cond != 0:
        plt.plot(
            np.array(ELECTRON_NUMBER_DENSITY_IONO) * 1e6,
            RADIUS_IONO,
            ":g",
            label="Patzold et al.",
        )
    plt.legend()

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "Ne_X_log.png", dpi=600)
    if Bande == "S":
        plt.savefig(PLOT_DIR + "/" + "Ne_S_log.png", dpi=600)
    if Bande == "Diff":
        plt.savefig(PLOT_DIR + "/" + "Ne_Diff_log.png", dpi=600)
    plt.close(fig11)

    ########################## Neutral Density

    fig9 = plt.figure(9)
    if Bande == "X":
        plt.errorbar(
            np.array(Nn),
            distance,
            xerr=error_neut,
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="X-Band Data" + year + "" + day_number,
        )  # (1+880./749.)

    if Bande == "S":
        plt.errorbar(
            np.array(Nn),
            distance,
            xerr=error_neut,
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="S-Band Data" + year + "" + day_number,
        )  # (1+880./749.)

    if Bande == "Diff":
        plt.errorbar(
            np.array(Nn),
            distance,
            xerr=error_neut,
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="Differential Doppler Data" + year + "" + day_number,
        )  # (1+880./749.)

    plt.xlabel("Neutral number density (m$^{-3}$)")
    plt.ylabel("Altitude (km)")
    pylab.legend(loc="upper right")

    min_x = np.nanmedian(Nn) - sc.median_absolute_deviation(Nn, nan_policy="omit") * 3
    max_x = np.nanmedian(Nn) + sc.median_absolute_deviation(Nn, nan_policy="omit") * 9

    plt.xlim(xmin=-1e22, xmax=3e23)
    #    plt.ylim(min_y,max_y)
    fig9.set_size_inches(8, 6)  # Inch
    plt.grid(True)
    if cond != 0:
        plt.plot(
            np.array(NUMBER_DENSITY_ATMO),
            np.array(RADIUS_ATMO),
            ":g",
            label="Patzold et al",
        )
    plt.legend()

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "Neutral_X.png", dpi=600)
    if Bande == "S":
        plt.savefig(PLOT_DIR + "/" + "Neutral_S.png", dpi=600)
    if Bande == "Diff":
        plt.savefig(PLOT_DIR + "/" + "Neutral_Diff.png", dpi=600)
    plt.close(fig9)

    print("\t PLOTS DONE")
    return


def PLOT2(
    DATA_ID,
    i_Profile,
    DATA_PRO,
    CODE_DIR,
    Bande,
    DATA_DIR,
    Threshold_Cor,
    Threshold_Surf,
    DATA_FINAL_DIR,
    PLOT_DIR,
    Threshold_int,
):

    ############################## NEW PART #########################
    ############################## PATZOLD FINDER ###################

    DATA = DATA_ID[i_Profile]

    ###Loading Python output#################################################################################

    Python_OUT_IONO = []
    N_data_IONO = []

    # output filename
    Python_OUT_IONO.append(
        DATA_FINAL_DIR + "/" + Bande + "-IONO-" + str(i_Profile + 1) + ".txt"
    )

    output_data_IONO = np.genfromtxt(Python_OUT_IONO[-1], dtype=None)
    N_data_IONO = len(output_data_IONO)
    Doppler = []
    Doppler_debias = []
    Doppler_biasfit = []
    distance = []
    refractivity1 = []
    Ne = []
    error = []
    error_refrac1 = []
    error_elec = []

    for i in range(N_data_IONO):
        Doppler.append(output_data_IONO[i][0])
        Doppler_debias.append(output_data_IONO[i][1])
        Doppler_biasfit.append(output_data_IONO[i][2])
        distance.append(output_data_IONO[i][3])
        refractivity1.append(output_data_IONO[i][4])
        Ne.append(output_data_IONO[i][5])
        error.append(output_data_IONO[i][6])
        error_refrac1.append(output_data_IONO[i][7])
        error_elec.append(output_data_IONO[i][8])

    Python_OUT_ATMO = []
    N_data_ATMO = []

    # output filename
    Python_OUT_ATMO.append(
        DATA_FINAL_DIR + "/" + Bande + "-ATMO-" + str(i_Profile + 1) + ".txt"
    )

    # print('*** ' + Python_OUT[-1] + '\n')
    output_data_ATMO = np.genfromtxt(Python_OUT_ATMO[-1], dtype=None)
    N_data_ATMO = len(output_data_ATMO)
    Doppler = []
    Doppler_debias = []
    Doppler_biasfit = []
    distance = []
    refractivity2 = []
    Nn = []
    error = []
    error_refrac2 = []
    error_neut = []

    for i in range(N_data_ATMO):
        Doppler.append(output_data_ATMO[i][0])
        Doppler_debias.append(output_data_ATMO[i][1])
        Doppler_biasfit.append(output_data_ATMO[i][2])
        distance.append(output_data_ATMO[i][3])
        refractivity2.append(output_data_ATMO[i][4])
        Nn.append(output_data_ATMO[i][5])
        error.append(output_data_ATMO[i][6])
        error_refrac2.append(output_data_ATMO[i][7])
        error_neut.append(output_data_ATMO[i][8])

    # #########print L2_data#################################################################################
    # os.chdir(DATA_PRO)
    # PATH = os.path.normpath(DATA_PRO + os.sep + os.pardir)

    # if Bande == 'X':
    #     if os.path.getsize(PATH+'/INFORMATION/PATH_X.txt') == 0 :
    #         print('No data available in X')
    #         sys.exit('No data to plot')
    #     else:
    #         file = open(PATH+'/INFORMATION/PATH_X.txt', 'r')
    #         PATH_X = file.read()
    #         L2_data = np.genfromtxt(PATH_X,dtype=None)
    # else :
    #     if os.path.getsize(PATH+'/INFORMATION/PATH_S.txt') == 0 :
    #         print('No data available in S')
    #         sys.exit('No data to plot')
    #     else:
    #         file = open(PATH+'/INFORMATION/PATH_S.txt', 'r')
    #         PATH_S = file.read()
    #         L2_data = np.genfromtxt(PATH_S,dtype=None)

    ########Plot files##########################################################################
    # retval = os.getcwd()
    # print("Current working directory %s" % retval)

    distance = (np.array(distance) - Threshold_Surf) / 1e3
    # min_y = Threshold_Surf
    # max_y = Threshold_Cor

    # min_y = Threshold_Surf
    # max_y = Threshold_Cor
    Doppler = np.array(Doppler)
    Doppler_debias = np.array(Doppler_debias)
    cond_dop = np.logical_and(
        Doppler < 1, distance <= ((Threshold_int - Threshold_Surf) / 1e3)
    )
    cond_deb = np.logical_and(
        Doppler_debias < 1, distance <= ((Threshold_int - Threshold_Surf) / 1e3)
    )

    fig6 = plt.figure(6)
    plt.errorbar(
        Doppler,
        distance,
        xerr=np.array(error),
        fmt="o",
        color="black",
        ecolor="lightgray",
        elinewidth=1,
        capsize=1,
        ms=1,
        label="Raw L2 Data " + DATA,
    )  # (1+880./749.)
    plt.errorbar(
        Doppler_debias,
        distance,
        xerr=np.array(error),
        fmt="o",
        color="red",
        ecolor="lightgray",
        elinewidth=1,
        capsize=1,
        ms=1,
        label="Debias Raw L2 Data " + DATA,
    )  # (1+880./749.)

    Doppler1 = Doppler[cond_dop]
    Doppler_debias1 = Doppler_debias[cond_deb]

    min_x1 = (
        np.nanmedian(Doppler_debias1)
        - sc.median_absolute_deviation(Doppler_debias1, nan_policy="omit") * 5
    )
    min_x2 = (
        np.nanmedian(Doppler1)
        - sc.median_absolute_deviation(Doppler1, nan_policy="omit") * 5
    )
    max_x1 = (
        np.nanmedian(Doppler_debias1)
        + sc.median_absolute_deviation(Doppler_debias1, nan_policy="omit") * 5
    )
    max_x2 = (
        np.nanmedian(Doppler1)
        + sc.median_absolute_deviation(Doppler1, nan_policy="omit") * 5
    )
    min_x = min([min_x1, min_x2])
    max_x = max([max_x1, max_x2])
    max_y = (Threshold_int - Threshold_Surf) / 1e3
    # plt.plot(Wang_dig_1, Wang_dig_2, label = 'Wang et al. ')
    plt.xlabel("Doppler Frequency Residuals (Hz)", fontsize=13)
    plt.ylabel("Altitude (km)", fontsize=13)
    plt.xlim(min_x, max_x)
    plt.ylim(ymin=0, ymax=max_y)
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    #    plt.ylim(min_y,max_y)
    plt.grid(True)
    plt.legend()
    fig6.set_size_inches(8, 6)  # Inch

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "Doppler_X1.png", dpi=600)
    else:
        plt.savefig(PLOT_DIR + "/" + "Doppler_S1.png", dpi=600)
    plt.close(fig6)

    """
    fig7 = plt.figure(7)
    plt.errorbar(Doppler,distance,xerr=np.array(error), fmt='o', color='black',
                 ecolor='lightgray', elinewidth=1, capsize=1, ms = 1, label = 'Raw L2 Data '+DATA)#(1+880./749.)

    plt.xlabel('Doppler Frequency Residuals (Hz)',fontsize=13)
    plt.ylabel('Altitude (km)',fontsize=13)
    plt.xlim(min_x, max_x)
    plt.ylim(ymin=0,ymax=max_y)
    plt.legend()
    fig7.set_size_inches(8, 6) #Inch
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    plt.grid(True)
    if Bande == 'X':
        plt.savefig(PLOT_DIR + '/' + 'Doppler_X2.png',dpi=600)
    else :
        plt.savefig(PLOT_DIR + '/' + 'Doppler_S2.png',dpi=600)
    plt.close(fig7)
    """
    ############################ REFRACTIVITY ATMO

    fig20 = plt.figure(20)
    cond_ref2 = np.where(np.array(refractivity2) > -1)

    if Bande == "X":
        plt.errorbar(
            np.array(refractivity2)[cond_ref2],
            np.array(distance)[cond_ref2],
            xerr=np.array(error_refrac2)[cond_ref2],
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="X-Band Data " + DATA,
        )

    if Bande == "S":

        plt.errorbar(
            np.array(refractivity2)[cond_ref2],
            distance[cond_ref2],
            xerr=np.array(error_refrac2)[cond_ref2],
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="S-Band Data " + DATA,
        )

    if Bande == "Diff":

        plt.errorbar(
            np.array(refractivity2)[cond_ref2],
            distance[cond_ref2],
            xerr=np.array(error_refrac2)[cond_ref2],
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="Differential Doppler Data " + DATA,
        )

    plt.xlabel("Refractivity", fontsize=13)
    plt.ylabel("Altitude (km)", fontsize=13)
    pylab.legend(loc="upper right")

    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)

    min_x = np.nanmin(np.array(refractivity2)[cond_ref2])
    max_x = (
        np.nanmedian(np.array(refractivity2)[cond_ref2])
        + sc.median_absolute_deviation(
            np.array(refractivity2)[cond_ref2], nan_policy="omit"
        )
        * 3
    )

    plt.xlim(min_x, max_x)
    plt.grid(True)
    plt.legend()
    fig20.set_size_inches(8, 6)  # Inch

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "refractivity_ATMO_X.png", dpi=600)
    if Bande == "S":
        plt.savefig(PLOT_DIR + "/" + "refractivity_ATMO_S.png", dpi=600)
    if Bande == "Diff":
        plt.savefig(PLOT_DIR + "/" + "refractivity_ATMO_Diff.png", dpi=600)

    plt.close(fig20)

    ########################## REFRACTIVITY IONO

    fig10 = plt.figure(10)
    cond_ref1 = np.where(np.array(refractivity1) > -1)
    if Bande == "X":
        plt.errorbar(
            np.array(refractivity1)[cond_ref1],
            np.array(distance)[cond_ref1],
            xerr=np.array(error_refrac1)[cond_ref1],
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="X-Band Data " + DATA,
        )

    if Bande == "S":
        plt.errorbar(
            np.array(refractivity1)[cond_ref1],
            np.array(distance)[cond_ref1],
            xerr=np.array(error_refrac1)[cond_ref1],
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="S-Band Data " + DATA,
        )

    if Bande == "Diff":
        plt.errorbar(
            np.array(refractivity1)[cond_ref1],
            np.array(distance)[cond_ref1],
            xerr=np.array(error_refrac1)[cond_ref1],
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="Differential Doppler Data " + DATA,
        )

    plt.xlabel("Refractivity", fontsize=13)
    plt.ylabel("Altitude (km)", fontsize=13)
    pylab.legend(loc="upper right")

    min_x = np.nanmin(np.array(refractivity1)[cond_ref1])
    max_x = (
        np.nanmedian(np.array(refractivity1)[cond_ref1])
        + sc.median_absolute_deviation(
            np.array(refractivity1)[cond_ref1], nan_policy="omit"
        )
        * 3
    )

    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)

    # plt.xlim(min_x, max_x)
    #    plt.ylim(min_y,max_y)
    #    mf = matplotlib.ticker.ScalarFormatter(useOffset=False, useMathText=True)
    #    mf.set_powerlimits((-3,3))
    #    plt.gca().xaxis.set_major_formatter(mf)
    plt.grid(True)
    fig10.set_size_inches(8, 6)  # Inch
    plt.legend()

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "refractivity_IONO_X.png", dpi=600)
    if Bande == "S":
        plt.savefig(PLOT_DIR + "/" + "refractivity_IONO_S.png", dpi=600)
    if Bande == "Diff":
        plt.savefig(PLOT_DIR + "/" + "refractivity_IONO_Diff.png", dpi=600)

    plt.close(fig10)

    ########################Electron Density
    fig8 = plt.figure(8)

    if Bande == "X":
        plt.errorbar(
            np.array(Ne),
            distance,
            xerr=error_elec,
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="X-Band Data " + DATA,
        )

    if Bande == "S":
        plt.errorbar(
            np.array(Ne),
            distance,
            xerr=error_elec,
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="S-Band Data " + DATA,
        )

    if Bande == "Diff":
        plt.errorbar(
            np.array(Ne),
            distance,
            xerr=error_elec,
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="Differential Data " + DATA,
        )

    plt.xlabel("Electron density (el/m$^{3}$)", fontsize=13)

    #    plt.ylim(min_y,max_y)    plt.ylabel('Altitude (km)',fontsize=13)
    pylab.legend(loc="upper right")
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)

    min_x = np.nanmedian(Ne) - sc.median_absolute_deviation(Ne, nan_policy="omit") * 3
    max_x = (
        np.nanmax(np.array(Ne)[np.array(Ne) < 1e13])
        + sc.median_absolute_deviation(
            np.array(Ne)[np.array(Ne) < 1e13], nan_policy="omit"
        )
        * 3
    )
    # plt.xlim(min_x, max_x)
    #    mf = matplotlib.ticker.ScalarFormatter(useOffset=False, useMathText=True)
    #    mf.set_powerlimits((-3,3))
    #    plt.gca().xaxis.set_major_formatter(mf)
    plt.grid(True)
    fig8.set_size_inches(8, 6)  # Inch
    plt.legend()

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "Ne_X.png", dpi=600)
    if Bande == "S":
        plt.savefig(PLOT_DIR + "/" + "Ne_S.png", dpi=600)
    if Bande == "Diff":
        plt.savefig(PLOT_DIR + "/" + "Ne_Diff.png", dpi=600)
    plt.close(fig8)

    fig11 = plt.figure(11)
    xmini = 10 ** 8
    xmax = max_x
    index = np.where(np.array(Ne) > xmini)

    if Bande == "X":
        plt.errorbar(
            np.array(Ne[index[0][0] : index[0][-1]]),
            distance[index[0][0] : index[0][-1]],
            xerr=error_elec[index[0][0] : index[0][-1]],
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="X-Band Data " + DATA,
        )

    if Bande == "S":
        plt.errorbar(
            np.array(Ne[index[0][0] : index[0][-1]]),
            distance[index[0][0] : index[0][-1]],
            xerr=error_elec[index[0][0] : index[0][-1]],
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="S-Band Data " + DATA,
        )

    if Bande == "Diff":
        plt.errorbar(
            np.array(Ne),
            distance,
            xerr=error_elec,
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="Differential Doppler Data" + DATA,
        )

    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)

    plt.xlabel("Electron density (el/m$^{3}$)", fontsize=13)
    plt.ylabel("Altitude (km)", fontsize=13)
    pylab.legend(loc="upper right")

    # plt.xlim(min_x, 1.5E11)
    #    plt.ylim(min_y,max_y)
    #    mf = matplotlib.ticker.ScalarFormatter(useOffset=False, useMathText=True)
    #    mf.set_powerlimits((-3,3))
    #    plt.gca().xaxis.set_major_formatter(mf)
    plt.grid(True)
    plt.legend()
    fig11.set_size_inches(8, 6)  # Inch
    plt.xscale("log")
    plt.xlim(xmini, xmax)
    plt.legend()

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "Ne_X_log.png", dpi=600)
    if Bande == "S":
        plt.savefig(PLOT_DIR + "/" + "Ne_S_log.png", dpi=600)
    if Bande == "Diff":
        plt.savefig(PLOT_DIR + "/" + "Ne_Diff_log.png", dpi=600)
    plt.close(fig11)

    ########################Neutral Density
    fig9 = plt.figure(9)
    if Bande == "X":
        plt.errorbar(
            np.array(Nn),
            distance,
            xerr=error_neut,
            fmt="o",
            color="black",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="X-Band Data " + DATA,
        )  # (1+880./749.)

    if Bande == "S":
        plt.errorbar(
            np.array(Nn),
            distance,
            xerr=error_neut,
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="S-Band Data " + DATA,
        )  # (1+880./749.)

    if Bande == "Diff":
        plt.errorbar(
            np.array(Nn),
            distance,
            xerr=error_neut,
            fmt="o",
            color="blue",
            ecolor="lightgray",
            elinewidth=1,
            capsize=1,
            ms=1,
            label="Differential Doppler Data" + DATA,
        )  # (1+880./749.)

    plt.xlabel("Neutral number density (m$^{-3}$)", fontsize=13)
    plt.ylabel("Altitude (km)", fontsize=13)
    pylab.legend(loc="upper right")
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)

    min_x = np.nanmedian(Nn) - sc.median_absolute_deviation(Nn, nan_policy="omit") * 3
    max_x = np.nanmedian(Nn) + sc.median_absolute_deviation(Nn, nan_policy="omit") * 9

    plt.grid(True)
    plt.xlim(xmin=-1e22, xmax=3e23)
    #    plt.ylim(min_y,max_y)
    fig9.set_size_inches(8, 6)  # Inch
    plt.legend()

    if Bande == "X":
        plt.savefig(PLOT_DIR + "/" + "Neutral_X.png", dpi=600)
    if Bande == "S":
        plt.savefig(PLOT_DIR + "/" + "Neutral_S.png", dpi=600)
    if Bande == "Diff":
        plt.savefig(PLOT_DIR + "/" + "Neutral_Diff.png", dpi=600)
    plt.close(fig9)

    print("\t PLOTS DONE")
    return
