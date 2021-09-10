#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 07:32:42 2020

@author: ananya
"""

import numpy as np
def Off_Cor2(Type, Doppler, Diff_doppler, ET, N_data, distance):
    Doppler_debias = np.full(N_data, np.nan)
    Doppler_biasfit = np.full(N_data, np.nan)



    if Type == 'Linear':
        #p = np.polyfit(ET[i_integral:Corr_ind],Doppler[i_integral:Corr_ind],1)
        p0 = float(input("Enter the new p[0], i.e; p[0] +dp[0] = " ))
        p1 = float(input("Enter the new p[1], i.e; p[1] +dp[1] = " ))
        for i in range(N_data):
            Doppler_biasfit[i] = p0 * (ET[i]) + p1

    elif Type == 'Quadratic':
        #p = np.polyfit(ET[i_integral:Corr_ind],Doppler[i_integral:Corr_ind],2)
        p0 = float(input("Enter the new p[0], i.e; p[0] +dp[0] = " ))
        p1 = float(input("Enter the new p[1], i.e; p[1] +dp[1] = " ))
        p2 = float(input("Enter the new p[2], i.e; p[2] +dp[2] = " ))
        for i in range(N_data):
            Doppler_biasfit[i] = p0 * (ET[i])**2 + p1*(ET[i]-ET[0]) + p2
    else:
        print('Type is not recognized')

    for i in range(N_data):
        Doppler_debias[i]  = (Doppler[i]- Doppler_biasfit[i])

    return Doppler_debias, Doppler_biasfit
