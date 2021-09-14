#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 12:22:41 2020

@author: ananya
"""
import R8_Plot_Doppler_1
import R9_BendAng_ImpParam_up
import R9_BendAng_ImpParam_dn
import R10_Avg_BendAng_ImpParam
import R11_Refractivity_and_Bending_Radius_v2
import R12_Electron_Density
import R13_Neutral_Number_Density
import R14_Plot_check
import R16_Biasfit_Correction

def run(Doppler_debias,N_data, r_MEX_up, z_MEX_up, z_GS_up, vr_MEX_up, vz_MEX_up, vr_GS_up, vz_GS_up, gamma_up, beta_e_up,ET, \
        delta_s_up, r_MEX_dn, z_MEX_dn, z_GS_dn, vr_MEX_dn, vz_MEX_dn, vr_GS_dn, vz_GS_dn, gamma_dn, beta_e_dn, delta_s_dn, B_Cor_Type, \
        Bande,fsup,c, Diff_doppler, item,i_integral, i_Surface, R_Planet,e, eps0, me, distance,Doppler, PLOT_DIR, Threshold_neut_upp,CC, kB):

    R16_Biasfit_Correction.Off_Cor2(B_Cor_Type, Doppler, Diff_doppler, ET, N_data, distance)
    R8_Plot_Doppler_1.PLOT_Dop1(distance,Doppler,Doppler_debias,PLOT_DIR)
    HAPPY_or_NOT = str(input("Enter 'YES' if the debias is good and 'NO' if bad: " ))
    if HAPPY_or_NOT == 'YES':
            kx = 880./749.
            ks = 240./749.
            Doppler_debias_dn_iono_x = Doppler_debias/(1.0+(kx*kx))
            Doppler_debias_up_iono_x = Doppler_debias/(kx+(1.0/kx))

            Doppler_debias_dn_iono_s = Doppler_debias/(1.0+(ks**2))
            Doppler_debias_up_iono_s = Doppler_debias_up_iono_x

            Doppler_debias_dn_atmo_x = Doppler_debias/2.0
            Doppler_debias_up_atmo_x = Doppler_debias/(2.0*kx)

            Doppler_debias_dn_atmo_s = Doppler_debias/2.0
            Doppler_debias_up_atmo_s = Doppler_debias_up_atmo_x

            Diff_Doppler_debias_dn_iono_s = Diff_doppler/(1.-(9./121.))

            if Bande == 'X':

                if item == 'IONO' :


                    # R8: bending angle & impact parameter up
                    imp_param_up, bend_ang_up, delta_r_up, beta_r_up \
                        = R9_BendAng_ImpParam_up.Bend_up(N_data, r_MEX_up, z_MEX_up, z_GS_up, vr_MEX_up, \
                                                   vz_MEX_up, vr_GS_up, vz_GS_up, gamma_up, beta_e_up, \
                                                   delta_s_up, Doppler_debias_up_iono_x,fsup,c)

                    # R8: bending angle & impact parameter down
                    imp_param_dn, bend_ang_dn, delta_r_dn, beta_r_dn \
                        = R9_BendAng_ImpParam_dn.Bend_dn(N_data, r_MEX_dn, z_MEX_dn, z_GS_dn, vr_MEX_dn, \
                                                   vz_MEX_dn, vr_GS_dn, vz_GS_dn, gamma_dn, beta_e_dn, \
                                                   delta_s_dn, Doppler_debias_dn_iono_x,Bande,fsup,c)

                    # R9: Average bending angle & impact parameter
                    imp_param, bend_ang \
                        = R10_Avg_BendAng_ImpParam.Avg(imp_param_up, bend_ang_up, imp_param_dn, bend_ang_dn,Bande)


                if item == 'ATMO' :
                    # R8: bending angle & impact parameter up
                    imp_param_up, bend_ang_up, delta_r_up, beta_r_up \
                        = R9_BendAng_ImpParam_up.Bend_up(N_data, r_MEX_up, z_MEX_up, z_GS_up, vr_MEX_up, \
                                                   vz_MEX_up, vr_GS_up, vz_GS_up, gamma_up, beta_e_up, \
                                                   delta_s_up, Doppler_debias_up_atmo_x,fsup,c)

                    # R8: bending angle & impact parameter down
                    imp_param_dn, bend_ang_dn, delta_r_dn, beta_r_dn \
                        = R9_BendAng_ImpParam_dn.Bend_dn(N_data, r_MEX_dn, z_MEX_dn, z_GS_dn, vr_MEX_dn, \
                                                   vz_MEX_dn, vr_GS_dn, vz_GS_dn, gamma_dn, beta_e_dn, \
                                                   delta_s_dn, Doppler_debias_dn_atmo_x,Bande,fsup,c)

                    # R9: Average bending angle & impact parameter
                    imp_param, bend_ang \
                        = R10_Avg_BendAng_ImpParam.Avg(imp_param_up, bend_ang_up, imp_param_dn, bend_ang_dn,Bande)


            if Bande == 'S':
                if item == 'IONO' :
                    # R8: bending angle & impact parameter up
                    imp_param_up, bend_ang_up, delta_r_up, beta_r_up \
                        = R9_BendAng_ImpParam_up.Bend_up(N_data, r_MEX_up, z_MEX_up, z_GS_up, vr_MEX_up, \
                                                   vz_MEX_up, vr_GS_up, vz_GS_up, gamma_up, beta_e_up, \
                                                   delta_s_up, Doppler_debias_up_iono_s,fsup,c)

                    # R8: bending angle & impact parameter down
                    imp_param_dn, bend_ang_dn, delta_r_dn, beta_r_dn \
                        = R9_BendAng_ImpParam_dn.Bend_dn(N_data, r_MEX_dn, z_MEX_dn, z_GS_dn, vr_MEX_dn, \
                                                   vz_MEX_dn, vr_GS_dn, vz_GS_dn, gamma_dn, beta_e_dn, \
                                                   delta_s_dn, Doppler_debias_dn_iono_s,Bande,fsup,c)

                    # R9: Average bending angle & impact parameter
                    imp_param, bend_ang \
                        = R10_Avg_BendAng_ImpParam.Avg(imp_param_up, bend_ang_up, imp_param_dn, bend_ang_dn,Bande)


                if item == 'ATMO' :
                    # R8: bending angle & impact parameter up
                    imp_param_up, bend_ang_up, delta_r_up, beta_r_up \
                        = R9_BendAng_ImpParam_up.Bend_up(N_data, r_MEX_up, z_MEX_up, z_GS_up, vr_MEX_up, \
                                                   vz_MEX_up, vr_GS_up, vz_GS_up, gamma_up, beta_e_up, \
                                                   delta_s_up, Doppler_debias_up_atmo_s,fsup,c)

                    # R8: bending angle & impact parameter down
                    imp_param_dn, bend_ang_dn, delta_r_dn, beta_r_dn \
                        = R9_BendAng_ImpParam_dn.Bend_dn(N_data, r_MEX_dn, z_MEX_dn, z_GS_dn, vr_MEX_dn, \
                                                   vz_MEX_dn, vr_GS_dn, vz_GS_dn, gamma_dn, beta_e_dn, \
                                                   delta_s_dn, Doppler_debias_dn_atmo_s,Bande,fsup,c)

                    # R9: Average bending angle & impact parameter
                    imp_param, bend_ang \
                        = R10_Avg_BendAng_ImpParam.Avg(imp_param_up, bend_ang_up, imp_param_dn, bend_ang_dn,Bande)

            if Bande == 'Diff':


                if item == 'IONO' :


                    # R8: bending angle & impact parameter down
                    imp_param, bend_ang, delta_r_diff, beta_r_diff \
                        = R9_BendAng_ImpParam_dn.Bend_dn(N_data, r_MEX_dn, z_MEX_dn, z_GS_dn, vr_MEX_dn, \
                                                   vz_MEX_dn, vr_GS_dn, vz_GS_dn, gamma_dn, beta_e_dn, \
                                                   delta_s_dn, Diff_Doppler_debias_dn_iono_s,Bande,fsup,c)


                if item == 'ATMO' :

                    # R8: bending angle & impact parameter down
                    imp_param, bend_ang, delta_r_dn, beta_r_dn \
                        = R9_BendAng_ImpParam_dn.Bend_dn(N_data, r_MEX_dn, z_MEX_dn, z_GS_dn, vr_MEX_dn, \
                                                   vz_MEX_dn, vr_GS_dn, vz_GS_dn, gamma_dn, beta_e_dn, \
                                                   delta_s_dn, Doppler_debias_dn_atmo_s,Bande,fsup,c)   #NEED TO CHECK????

            # R11
            ref_index,refractivity, bend_radius, Sum_tot   =                          \
                R11_Refractivity_and_Bending_Radius_v2.Abel_Analytical(N_data, i_integral, i_Surface,\
                                                                   imp_param, bend_ang, R_Planet)

            if item == 'IONO' :

                Ne  = R12_Electron_Density.Elec(N_data, refractivity, e, eps0, me,Bande,fsup,c)
                TEC = R12_Electron_Density.TEC_Calc(N_data, Ne, i_integral, i_Surface,      \
                                                   bend_radius, R_Planet)

                R14_Plot_check.PLOT1(distance,Doppler,Doppler_debias,refractivity, Ne,PLOT_DIR,item)
            if item == 'ATMO' :

                # R13: neutral density (Level 04)
                Nn, i_neut_upp =                                                          \
                    R13_Neutral_Number_Density.Neut(N_data, bend_radius, refractivity,    \
                                                    Threshold_neut_upp, i_Surface, CC, kB)
                R14_Plot_check.PLOT2(distance,Doppler,Doppler_debias,refractivity, Nn,PLOT_DIR,item)

    return
