#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 20:17:48 2020

@author: ananya
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as sc

def PLOT1( distance,Doppler,Doppler_debias,refractivity, Ne,PLOT_DIR,item):

    Doppler=np.array(Doppler)
    Doppler_debias=np.array(Doppler_debias)
    cond_dop = Doppler<1
    cond_deb = Doppler_debias<1

    fig6 = plt.figure(6)
    plt.ion()
    plt.show()
    plt.plot(Doppler,distance/1000,':', color='black',label = 'Raw L2 Data')#(1+880./749.)
    plt.plot(Doppler_debias,distance/1000,':', color='blue', label = 'Debias Raw L2 Data')#(1+880./749.)

    Doppler = Doppler[cond_dop]
    Doppler_debias = Doppler_debias[cond_deb]

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
    plt.grid(True)
    plt.legend()
    fig6.set_size_inches(6, 10) #
    plt.savefig(PLOT_DIR+'/'+'Doppler-before-corr.png',dpi=600)
    plt.pause(1.0)
    plt.close()



    fig10 = plt.figure(10)
    plt.ion()
    plt.show()
    plt.plot(np.array(refractivity),np.array(distance/1000),':', color='blue', label ='after correction')

    plt.xlabel('Refractivity')
    plt.ylabel('Altitude (km)')

    plt.ylim(3400,4000)
    plt.xlim(-0.05,0.05)# S band
    plt.grid(True)
    fig10.set_size_inches(6, 10) #Inch

    plt.savefig(PLOT_DIR+'/'+'refractivity-before-corr.png',dpi=600)
    plt.pause(1.0)
    plt.close()

    fig3 = plt.figure(3)
    plt.ion()
    plt.show()

    plt.plot(np.array(Ne)*1E-6,np.array(distance/1000), ':', color='blue', label ='after correction')
    plt.xlabel('Electron density (el/cm$^{3}$)')

    plt.ylabel('Altitude (km)')

    plt.grid(True)
    fig3.set_size_inches(6, 10)
    plt.xlim(-4.0e4,3.0e4)
    plt.ylim(3400, 4000)

    plt.savefig(PLOT_DIR+'/'+'Ne_before-Corr.png',dpi=600)
    print('\t PLOT BEFORE CORRECTION DONE')

    plt.pause(1.0)
    input("Press [enter] to continue.")
    plt.close()
    #print(fit_coeff)

    return
