#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 15:11:33 2019

@author: Gabriele Coiana
"""
import numpy as np
from decomp import  read,  util
import sys

# =============================================================================
# Parameters
input_file = sys.argv[1]
Masses = read.read_parameters(input_file)[0]
n_atom_unit_cell = read.read_parameters(input_file)[1]
N1,N2,N3 = read.read_parameters(input_file)[2:5]
kinput_scaled = read.read_parameters(input_file)[5::][0]
file_FC = read.read_parameters(input_file)[6]
file_trajectory = read.read_parameters(input_file)[7]
file_initial_conf = read.read_parameters(input_file)[8]
DT = read.read_parameters(input_file)[9]
Nb = read.read_parameters(input_file)[10]

tot_atoms_uc = int(np.sum(n_atom_unit_cell)) 
N1N2N3 = N1*N2*N3 # Number of cells
N = N1*N2*N3*tot_atoms_uc    # Number of atoms
cH = 1.066*1e-6 # to [H]
cev = 2.902*1e-05 # to [ev]
kbH = 3.1668085639379003*1e-06# a.u. [H/K]
kbev = 8.617333262*1e-05 # [ev/K]
# =============================================================================

print('\nHello, lets start!\n')
print('Getting input parameters...')
print(' Masses: ', Masses)
print(' Number of atoms per unit cell', n_atom_unit_cell)
print(' Supercell: ', N1, N2, N3)
print(' k path: ', [x.tolist() for x in kinput_scaled])
print(' Extent of timestep [ps]: ', DT*2.418884254*1e-05)
print()


print('Now reading FORCE_CONSTANTS...')
K = read.read_FC(file_FC)
print('Now calculating velocities...')

# =============================================================================
# Supercell and BZ cration
Nqs_path, ks_path, ks_scaled_path, kk, x_labels, Hk = util.get_commensurate_kpath(file_initial_conf, N1,N2,N3, N1,N2,N3, kinput_scaled, np.array([' ' for i in range(len(kinput_scaled))]))
SCell, Ruc, Suc, R0, R0_repeat, S0, masses, masses_uc = read.read_SPOSCAR_and_masses(file_initial_conf, n_atom_unit_cell, Masses, N1, N2, N3)
# =============================================================================

# =============================================================================
# MD positions and velocities
Rt = np.loadtxt(file_trajectory)[:,1:]
Num_timesteps = int(len(Rt[:,0]))
print(' Number of timesteps of simulation: ', Num_timesteps)
tall = np.arange(Num_timesteps)*DT*2.418884254*1e-05 #conversion to picoseconds
dt_ps = tall[1]-tall[0]
Vt = np.diff(Rt,axis=0)/dt_ps*np.sqrt(masses)/np.sqrt(3*(N))
T = np.sum(np.average(Vt**2*cev/kbev, axis=0))
print(' Temperature: ',T, ' K')
# =============================================================================

# =============================================================================
# Global vibrational DOS and C(t)
tau, freq, S = util.get_power_spectrum2(Vt, dt_ps, cev/(kbev*T), Nb)
# Vw, freq = np.fft.fft(Vt, axis=0), np.fft.fftfreq(Num_timesteps-1, dt_ps)

meta = util.max_freq(dt_ps, tau) #you want the max frequency plotted be 25 Thz
ZS, Zqs = np.zeros((meta,1+1+2+Nqs_path)), np.zeros((Nqs_path,meta,tot_atoms_uc*3+1))
print(' Frequency resolution [Thz]: ', freq[1]-freq[0])
tot_area = np.trapz(S,freq)
print(' The total DOS is ', tot_area*N)
print(' You are losing ',N - tot_area*N, ' kBT')
ZS[:,0], ZS[:,1] = freq[0:meta], S[0:meta]

Ctot = np.fft.ifft(S)
for t in range(int(len(Ctot)/2)):
    Ctot[t] = Ctot[t]*Num_timesteps/(Num_timesteps-t)
C = Ctot[0:int(len(Ctot)/2)].real
# =============================================================================


quasiparticles_kpoints, quasiparticles_info = np.zeros((Nqs_path, 3)), np.zeros((Nqs_path, 3, tot_atoms_uc*3))
print('\nDone. Performing calculation of renormalised FORCE CONSTANTS...\n')
kpoints_scal, kpoints = util.get_kgrid(N1,N2,N3, Hk)
# you're not using irreducible kpoints anymore, couse it doesn't work for BaTiO3, unless you do adjustments
# irr_kpoints, irr_kpoints_scal, weights, permutations_types = util.get_irr_ks(kpoints, kpoints_scal)
Ds = np.zeros((len(kpoints),tot_atoms_uc*3, tot_atoms_uc*3), dtype=complex)
for i in range(len(kpoints)):
    k = kpoints[i]
    k_scal = kpoints_scal[i]
    # thisk_permutations = permutations_types[i]
    # weight = weights[i]
    print('\t kpoint scaled: ', i, k_scal)
    # print('\t weight: ', weight)
    
# =============================================================================
# harmonic things
    D = util.get_D(k, K,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
    eigvals, eigvecs, omegas = util.get_eigvals_eigvec(D)
    eigvecH = np.conjugate(eigvecs.T)
# =============================================================================
    
# =============================================================================
#  MD 
    #Creating the collective variable based on the k point
    Tkt = util.create_Tkt(Num_timesteps-1, tot_atoms_uc, N1N2N3, Vt, R0_repeat, k)    
    # Sq = util.get_power_spectrum(Tkt, cev/(kbev*T)/Num_timesteps*dt_ps)
    tau, freq, Sq = util.get_power_spectrum2(Tkt, dt_ps, cev/(kbev*T), Nb)
    # area_q = np.trapz(Sq, freq)
    area_q = np.trapz(Sq, freq)
    print('\t DOS for this kpoint: ', area_q)
    
    #Projecting onto eigenvectors
    Qkt = np.dot(eigvecH,Tkt.T).T
    # Sq_proj = util.get_power_spectrum_proj(Qkt, cev/(kbev*T)/Num_timesteps*dt_ps)
    tau, freq_proj, Sq_proj = util.get_power_spectrum_proj2(Qkt, dt_ps, cev/(kbev*T), Nb)
    area_q_proj = np.trapz(Sq_proj, freq, axis=0)
    print('\t DOS for projected k-ni: ', area_q_proj)
    # area_q_proj[area_q_proj < 1e-05] = 100 # this is in case of acoustic Gamma
    # Sq_proj = Sq_proj/area_q_proj # this is to have the unoccupied DOS
    
    # print(np.trapz(S,freq))
    # import matplotlib.pyplot as plt
    # fig,ax = plt.subplots()
    # ax.plot(freq, Sq_proj)

    Params = np.zeros((3,tot_atoms_uc*3))
    for n in range(tot_atoms_uc*3):
        x_data, y_data = freq[0:int(tau/2)], Sq_proj[0:int(tau/2),n]
        popt, perr = util.fit_to_lorentzian(x_data, y_data, k, n)
        Params[:,n] = popt
        #now you go apply to Voigt equation for the sigmas
        sig = popt[-1]*0.42
        fmax, fl = util.voigt_eq(n, k_scal, x_data, y_data, sig)
        Params[-1,n] = fl
        if(np.any(np.all(np.isclose(k_scal , ks_scaled_path), axis=1))):
            print()
            print('\t\tFitting to Lorentzian, mode '+str(n)+'...')
            print('\t\tResonant frequency omega =',np.round(popt[0],2),' +-',np.round(perr[0],3))
            print('\t\tLinewidth gamma =',np.round(popt[2],2),' +-',np.round(perr[2],3))
            print()
# =============================================================================

# =============================================================================
#  renormalised D
    eigvals_renorm = (Params[0,:]*2*np.pi)**2
    omegas_renorm = np.sqrt(eigvals_renorm)/2/np.pi
    Lamdas_renorm = np.diag(eigvals_renorm)
    D_renorm = np.dot(np.dot(eigvecs,Lamdas_renorm),eigvecH)
    Ds[i,:,:] = D_renorm*np.sqrt(np.outer(masses_uc, masses_uc))
# =============================================================================

# =============================================================================
#  writing to file if in path
    check_is_symm_kpoint = util.check_is_symm(k_scal, ks_scaled_path)
    if(len(check_is_symm_kpoint) > 0):
        # print(check_is_symm_kpoint)
        for l in range(len(check_is_symm_kpoint)):
            kpoint = check_is_symm_kpoint[l]
            index_q = np.argwhere(np.all(np.isclose(kpoint , ks_scaled_path), axis=1)).flatten()
            quasiparticles_kpoints[index_q,:] = kpoint
            quasiparticles_info[index_q,:,:] = Params
            ZS[:,index_q+2] = Sq[0:meta].reshape(meta,1)
            Zqs[index_q,:,0] = Sq[0:meta]
            Zqs[index_q,:,1:] = Sq_proj[0:meta,:]
# =============================================================================
    print()

    
util.save_quasiparticles('Zqs', quasiparticles_kpoints, Zqs)
util.save_quasiparticles('quasiparticles', quasiparticles_kpoints, quasiparticles_info)  
util.save('C_t', np.vstack((tall[0:len(C)],C)).T)
util.save('ZS', ZS)



# SCell_fc, R0_fc, R_fc = util.get_R_FC(N1, N2, N3, 4,4,4,tot_atoms_uc, Suc, SCell) 
K_renorm = util.get_K_renorm_old(tot_atoms_uc,N1,N2,N3, SCell, R0, kpoints, Ds)
# K_renorm = util.get_K_renorm(tot_atoms_uc,N1,N2,N3, SCell, R0, irr_kpoints, permutations_types, Ds)
print('Calculated renormalized FORCE CONSTANTS')
util.save('K_renorm', K_renorm)
