#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 19:52:33 2020

@author: ananya
"""

from pudb import set_trace as bp  # noqa

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as sc

def PLOT_Dop1(distance,Doppler,Doppler_debias, Doppler_biasfit, ET, PLOT_DIR, N_data):
    Doppler=np.array(Doppler)
    Doppler_debias=np.array(Doppler_debias)
    cond_dop = Doppler<1
    cond_deb = Doppler_debias<1

    fig6 = plt.figure(6)
    plt.ion()
    plt.show()
    plt.plot(Doppler,distance/1000,':', color='black',label = 'Raw L2 Data')#(1+880./749.)
    plt.plot(Doppler_debias,distance/1000,':', color='blue', label = 'Debias Raw L2 Data')#(1+880./749.)

    # FIXME:
    # + MEX enables lines below but not MAVEN, do we keep that?
    # + same for comment below 'xlim'
    #
    # Doppler = Doppler[cond_dop]
    # Doppler_debias = Doppler_debias[cond_deb]

    min_x1 = np.nanmedian(Doppler_debias)- sc.median_absolute_deviation(Doppler_debias,nan_policy='omit')*5
    min_x2 = np.nanmedian(Doppler)- sc.median_absolute_deviation(Doppler,nan_policy='omit')*5
    max_x1 = np.nanmedian(Doppler_debias)+ sc.median_absolute_deviation(Doppler_debias,nan_policy='omit')*5
    max_x2 = np.nanmedian(Doppler)+ sc.median_absolute_deviation(Doppler,nan_policy='omit')*5
    min_x = min([min_x1,min_x2])
    max_x = max([max_x1,max_x2])
    plt.xlabel('Doppler Frequency Residuals (Hz)')
    plt.ylabel('Altitude (km)')

    plt.ylim(3400, 4000)
    plt.xlim(min_x, max_x)
    # plt.xlim(-0.2,0.2)
    plt.grid(True)
    plt.legend()
    fig6.set_size_inches(6, 10) #
    plt.savefig(PLOT_DIR+'/'+'Doppler_before_corrtn.png',dpi=600)
    plt.pause(1.0)
    input("Press [enter] to continue.")
    plt.close()

    # FIXME:
    # keep it?

    delET = []#np.full(N_data, np.nan)
    for i in range(N_data):
        delET.append(ET[i] - ET[0])

    fig7 = plt.figure(7)
    plt.ion()
    plt.show()
    plt.plot(delET, Doppler,':', color='black',label = 'Raw L2 Data')#(1+880./749.)
    plt.plot(delET, np.array(Doppler_debias)*100, ':', color='blue', label = 'Debias Raw L2 Data')#(1+880./749.)  

    plt.ylabel('Doppler Frequency Residuals (Hz)')
    plt.xlabel('Time (sec)')

    #plt.xlim(0, 6000)
    plt.ylim(-10,10)
    # plt.xlim(-0.2,0.2)
    plt.grid(True)
    plt.legend()
    fig7.set_size_inches(6, 10) #
    plt.savefig(PLOT_DIR+'/'+'Doppler_ET_before_Corr.png',dpi=600)
    plt.pause(1.0)
    input("Press [enter] to continue.")
    plt.close() 

    return
