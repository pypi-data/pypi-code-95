#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 14:40:14 2020

@author: gc4217
"""
import numpy as np
from scipy import signal
import os, sys
from decomp import plot, read, util

# =============================================================================
# Parameters
input_file =  sys.argv[1]
plot_type = read.read_post_proc(input_file)[0]
Masses = read.read_post_proc(input_file)[1]
n_atom_unit_cell = read.read_post_proc(input_file)[2]
N1, N2, N3 = read.read_post_proc(input_file)[3:6]
file_forces = read.read_post_proc(input_file)[6]
file_SPOSCAR = read.read_post_proc(input_file)[7]
max_Z = read.read_post_proc(input_file)[8]
gaussian_smoothing = read.read_post_proc(input_file)[9]
interp = read.read_post_proc(input_file)[10]
kinput = read.read_post_proc(input_file)[11::][0]
labels = read.read_post_proc(input_file)[12]
modes = read.read_post_proc(input_file)[13]
temperatures_folders = read.read_post_proc(input_file)[14]
NAC = read.read_post_proc(input_file)[15]
appendix = read.read_post_proc(input_file)[16]

K = read.read_FC(file_forces)
BORN_file = 'BORN'
prefix = ''


tot_atoms_uc = int(np.sum(n_atom_unit_cell)) 
N1N2N3, N = N1*N2*N3, N1*N2*N3*tot_atoms_uc
Nqs_path, ks_path, ks_scaled_path, distances_comm, x_labels, Hk = util.get_commensurate_kpath(file_SPOSCAR, N1,N2,N3, N1,N2,N3, kinput, labels)
SCell, Ruc, Suc, R0, R0_repeat, S0, masses, masses_uc = read.read_SPOSCAR_and_masses(file_SPOSCAR, n_atom_unit_cell, Masses, N1, N2, N3)  
# =============================================================================

if(plot_type==0):
    print('Generating plot 0...')
    namedir = plot.create_folder('')
    freq = np.loadtxt(prefix+'ZS'+appendix, usecols=0)
    meta = len(freq)
    for i in range(Nqs_path):
        to_skip = (1+meta)*i
        ZZ = np.genfromtxt(prefix+'Zqs'+appendix,skip_header=to_skip+1, max_rows=meta)
        Z_q = ZZ[:,0]
        Z = ZZ[:,1:]
        to_skip2 = 4*i
        Params = np.genfromtxt(prefix+'quasiparticles'+appendix,skip_header=to_skip2+1, max_rows=3)
        
        k_scaled = ks_scaled_path[i]
        k = ks_path[i]
        
        # harmonic things
        D = util.get_D(k, K,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals = np.linalg.eigvalsh(D)
        idx = np.argsort(eigvals)
        eigvals = eigvals[idx]
        omegas = np.sqrt(eigvals)/2/np.pi

        freq_disp = omegas
        print(' Creating plots for k point = ', k_scaled)
        for n in range(tot_atoms_uc*3):
            params = Params[:,n]
            if(gaussian_smoothing != 0):
                if(gaussian_smoothing < 0):
                    sig, mi = params[-1]/2, freq[int(len(freq)/2)]
            else:
                sig, mi = gaussian_smoothing, freq[int(len(freq)/2)]
            if(sig==0):
                sig = 0.0001

            gaussian = util.norm_gaussian(freq, mi, sig)                
            # convolution_lorentzian = signal.fftconvolve(Z[:,n], plot.lorentzian(freq, freq[int(len(freq)/2)], params[1], params[2]), mode='same') / sum( plot.lorentzian(freq, *params))
            convolution = signal.fftconvolve(Z[:,n],gaussian, mode='same') / sum( gaussian)
            
            plot.save_proj(freq, Z[:,n],Z_q, convolution, ks_scaled_path[i],freq_disp[n],n,namedir, params, max_Z)


if(plot_type==1):
    print('Generating plot 1...')
    freq = np.loadtxt('ZS'+appendix, usecols=0)
    meta = len(freq)
    ZQS = [np.zeros(meta)]
    count = 1
    accepted_qpoints = []
    accepted_labels = []
    for i in range(Nqs_path):
        to_skip = (1+meta)*i
        qpoint = np.genfromtxt(prefix+'Zqs'+appendix,skip_header=to_skip+0, max_rows=1)
        for j in range(len(kinput)):
            if(np.allclose(qpoint, kinput[j]) and (qpoint.tolist() not in accepted_qpoints)):
                accepted_qpoints.append(qpoint.tolist())
                accepted_labels.append(labels[j])
                Zq = np.genfromtxt(prefix+'Zqs'+appendix,skip_header=to_skip+1, max_rows=meta)[:,0]
                
                sig, mi = gaussian_smoothing, freq[int(len(freq)/2)]
                if(sig<=0):
                    sig = 0.0001

                gaussian = util.norm_gaussian(freq, mi, sig)                
                # convolution_lorentzian = signal.fftconvolve(Z[:,n], plot.lorentzian(freq, freq[int(len(freq)/2)], params[1], params[2]), mode='same') / sum( plot.lorentzian(freq, *params))
                convolution = signal.fftconvolve(Zq,gaussian, mode='same') / sum( gaussian)
                ZQS.append(convolution)
                count = count + 1
            
    ZQS = np.array(ZQS).T
    ZQS[:,0] = np.sum(ZQS[:,1::],axis=1)
    plot.plot1(freq,ZQS, accepted_labels)
    
    
if(plot_type==2): 
    print('Generating plot 2...')
    freq = np.loadtxt('ZS'+appendix, usecols=0)
    meta = len(freq)
    ZQS = []#np.zeros((meta, tot_atoms_uc*3+1, len(kinput)))
    count = 0
    accepted_qpoints = []
    accepted_labels = []
    freqs_from_disp = np.zeros((tot_atoms_uc*3,len(kinput)))
    for i in range(Nqs_path):
        to_skip = (1+meta)*i
        qpoint = np.genfromtxt(prefix+'Zqs'+appendix,skip_header=to_skip+0, max_rows=1)
        to_skip2 = 4*i
        Params = np.genfromtxt(prefix+'quasiparticles'+appendix,skip_header=to_skip2+1, max_rows=3)
        
        for j in range(len(kinput)):
            k_scaled = kinput[j]
            k = np.dot(Hk, k_scaled)
            if(np.allclose(qpoint, k_scaled) and (qpoint.tolist() not in accepted_qpoints)):
                accepted_qpoints.append(qpoint.tolist())
                accepted_labels.append(labels[j])
                # harmonic things
                D = util.get_D(k, K,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
                eigvals = np.linalg.eigvalsh(D)
                idx = np.argsort(eigvals)
                eigvals = eigvals[idx]
                omegas = np.sqrt(eigvals)/2/np.pi

                for m in range(Nqs_path):
                    if(np.allclose(qpoint,ks_scaled_path[m])):
                        freqs_from_disp[:,count] = omegas
                        break
                
                Zq = np.genfromtxt(prefix+'Zqs'+appendix,skip_header=to_skip+1, max_rows=meta)
                for n in range(tot_atoms_uc*3):
                    params = Params[:,n]
                    if(gaussian_smoothing != 0):
                        if(gaussian_smoothing < 0):
                            sig, mi = params[-1]/2, freq[int(len(freq)/2)]
                    else:
                        sig, mi = gaussian_smoothing, freq[int(len(freq)/2)]
                    if(sig==0):
                        sig = 0.0001
    
                    gaussian = util.norm_gaussian(freq, mi, sig)                
                    # convolution_lorentzian = signal.fftconvolve(Z[:,n], plot.lorentzian(freq, freq[int(len(freq)/2)], params[1], params[2]), mode='same') / sum( plot.lorentzian(freq, *params))
                    convolution = signal.fftconvolve(Zq[:,n+1],gaussian, mode='same') / sum( gaussian)
                    Zq[:,n+1] = convolution
                ZQS.append(Zq[:,:])
                count = count + 1
                
    ZQS = np.array(ZQS)
    plot.plot2(freq,ZQS, modes, accepted_labels, freqs_from_disp)
    
    
if(plot_type==3):
    print('Generating plot 3...')
    subdirectories = [x[1] for x in os.walk(temperatures_folders)][0]
    subdirectories.sort(key= lambda x: float(x.strip('K')))
    Ts = [int(x.strip('K')) for x in subdirectories]
    frequencies = np.zeros((2,tot_atoms_uc*3,len(kinput),len(Ts)))
    count_T = 0
    for subdir in subdirectories:
        count_q = 0
        accepted_qpoints = []
        accepted_labels = []

        for i in range(Nqs_path):
            to_skip = (4)*i
            qpoint = np.genfromtxt(temperatures_folders+subdir+prefix+'/quasiparticles'+appendix,skip_header=to_skip+0, max_rows=1)
            for j in range(len(kinput)):
                if(np.allclose(qpoint, kinput[j]) and (qpoint.tolist() not in accepted_qpoints)):
                    accepted_qpoints.append(qpoint.tolist())
                    accepted_labels.append(labels[j])
                    omegas_gammas = np.genfromtxt(temperatures_folders+subdir+prefix+'/quasiparticles'+appendix,skip_header=to_skip+1, max_rows=3)
                    frequencies[:,:,count_q, count_T] = omegas_gammas[0::2,:]
                    count_q = count_q + 1
        count_T = count_T + 1
    
    diff =len(frequencies[0,0,:,0]) -  len(accepted_labels) 
    if(diff != 0): #this is to eliminate repetitive kpoints if present
        for h in range(diff):
            frequencies = np.delete(frequencies, -1, axis=2)
    plot.plot3(Ts, frequencies, modes, accepted_labels)

   
if(plot_type==4):
    print('Generating plot 4...')
    freq = np.loadtxt('ZS', usecols=0)
    meta = len(freq)
    K_renorm = np.loadtxt('K_renorm')
    
    # take the path the user inputs and find all the k points you can plot
    ks_scal_path_many, ks_path_many, distances = util.get_kpath_many(ks_scaled_path, Hk, npoints=interp+1)
    
    # SCell_fc, R0_fc, R_fc = util.get_R_FC(N1, N2, N3, 4,4,4,tot_atoms_uc, Suc, SCell) 
# =============================================================================
    freq_DOS, DOS, DOS_renorm = np.arange(0,25,0.01), np.zeros(len(np.arange(0,25,0.01))), np.zeros(len(np.arange(0,25,0.01)))
    kpoints_scal, kpoints = util.get_kgrid(interp,interp,interp, Hk)
    N1N2N3_k = interp*interp*interp
    irr_ks, irr_ks_sc, weights, permutation_types = util.get_irr_ks(kpoints, kpoints_scal)    
    for i in range(len(irr_ks)):
        k = irr_ks[i]
        weight = weights[i]
        print('\t processing DOS k-point:', i, irr_ks_sc[i])
        # Renormalised          
        D = util.get_D(k, K_renorm,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_renorm, omegas_renorm = util.get_eigvals(D)
        # 0K dispersion
        D_0K = util.get_D(k, K,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_0K, omegas_0K = util.get_eigvals(D_0K)

        sigma = gaussian_smoothing
        DOS = DOS + np.sum(util.norm_gaussian(freq_DOS,omegas_0K,sigma), axis=1)*weight/(3*tot_atoms_uc*N1N2N3_k*2)
        DOS_renorm = DOS_renorm + np.sum(util.norm_gaussian(freq_DOS,omegas_renorm,sigma), axis=1)*weight/(3*tot_atoms_uc*N1N2N3_k*2)
    DOS_info = np.vstack((freq_DOS, DOS, DOS_renorm)).T
# =============================================================================
    
# =============================================================================    
    count_k = 0
    frequencies = np.zeros((1,tot_atoms_uc*3,len(ks_path_many)))
    frequencies_disp = np.zeros((1,tot_atoms_uc*3,len(ks_path_many)))
    EIGVECS, EIGVECS_0K = [], []
    for i in range(len(ks_path_many)):
        k = ks_path_many[i]
        
        #NAC
        if NAC:
            if(np.allclose(k, [0,0,0])):
                kpoint_nac = ks_path_many[i+1]
            else:
                kpoint_nac = k
            eps_inf, BORN, Vuc = util.get_nac_params(BORN_file, SCell, N1, N2, N3, tot_atoms_uc)
            C_nac = util.get_nac_C(kpoint_nac, Vuc, BORN, eps_inf, masses_uc, N1N2N3)
            K_corr_0K, K_corr_renorm = util.get_K_corr(K, C_nac), util.get_K_corr(K_renorm, C_nac)
        else:
            K_corr_0K, K_corr_renorm = K, K_renorm
        
        print('\t processing k-point:', i, ks_scal_path_many[i])
        # Renormalised          
        D_renorm = util.get_D(k, K_corr_renorm,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_renorm, eigvecs_renorm, omegas_renorm = util.get_eigvals_eigvec(D_renorm)
        # 0K dispersion
        D_0K = util.get_D(k, K_corr_0K,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_0K, eigvecs_0K, omegas_0K = util.get_eigvals_eigvec(D_0K)
        
        EIGVECS_0K.append(eigvecs_0K)
        EIGVECS.append(eigvecs_renorm)
            
        frequencies[:,:,count_k] = omegas_renorm 
        frequencies_disp[:,:,count_k] = omegas_0K 
        count_k = count_k + 1
# =============================================================================
        
        
    # this is to reshape spectra according to real branches
    indexes, freqs_reshaped = util.get_real_branches(frequencies[0,:,:], EIGVECS, masses_uc, ks_path_many)
    indexes, freqs_disp_reshaped = util.get_real_branches(frequencies_disp[0,:,:], EIGVECS_0K, masses_uc, ks_path_many)
    frequencies_reshaped, frequencies_disp_reshaped  = np.copy(frequencies), np.copy(frequencies_disp)
    frequencies_reshaped[0,:,:], frequencies_disp_reshaped[0,:,:] = freqs_reshaped, freqs_disp_reshaped

    plot.plot4(distances, distances_comm, frequencies_reshaped, frequencies_disp_reshaped,  x_labels, DOS_info)
    
    
if(plot_type==40):
    print('Generating plot 40...')
    freq = np.loadtxt('ZS'+appendix, usecols=0)
    meta = len(freq)
    if(gaussian_smoothing != 0.):
        sig, mi = gaussian_smoothing, freq[int(len(freq)/2)]
        if(gaussian_smoothing < 0):
            print('automatic sigma not allowed in this mode, sigma set to 0.1')
            sig, mi = 0.1, freq[int(len(freq)/2)]
    else:
        sig, mi = 0.001, freq[int(len(freq)/2)]
    
    # take the path the user inputs and find all the k points you can plot
    ks_scal_path_many, ks_path_many, distances = util.get_kpath_many(ks_scaled_path, Hk, npoints=interp+1)
    
    K_renorm = np.loadtxt('K_renorm')
    # SCell_fc, R0_fc, R_fc = util.get_R_FC(N1, N2, N3, 4,4,4,tot_atoms_uc, Suc, SCell) 
            
# =============================================================================
    freq_DOS, DOS = np.arange(0,25,0.01), np.zeros(len(np.arange(0,25,0.01)))
    kpoints_scal, kpoints = util.get_kgrid(interp, interp, interp, Hk)
    N1N2N3_k = interp*interp*interp
    irr_ks, irr_ks_sc, weights, permutation_types = util.get_irr_ks(kpoints, kpoints_scal)
    for i in range(len(irr_ks)):
        k = irr_ks[i]
        weight = weights[i]
        print('\t processing DOS k-point:', i, irr_ks_sc[i])
        # 0K dispersion
        D_0K = util.get_D(k, K,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_0K, omegas_0K = util.get_eigvals(D_0K)
        sigma = sig # using same sigma for 0K DOS and spectra
        DOS = DOS + np.sum(util.norm_gaussian(freq_DOS,omegas_0K,sigma), axis=1)*weight/(3*tot_atoms_uc*N1N2N3_k*2)
    DOS_info = np.vstack((freq_DOS, DOS)).T
# =============================================================================
   
# =============================================================================            
    count_k = 0
    frequencies = np.zeros((1,tot_atoms_uc*3,len(ks_path_many)))
    frequencies_disp = np.zeros((1,tot_atoms_uc*3,len(ks_path_many)))
    EIGVECS, EIGVECS_0K, EIGVECS_MD = [], [], []
    for i in range(len(ks_path_many)):
        k = ks_path_many[i]
        k_scal = ks_scal_path_many[i]
        print('\t processing path k-point:', i, ks_scal_path_many[i])
        # NAC
        if NAC:
            if(np.allclose(k, [0,0,0])):
                kpoint_nac = ks_path_many[i+1]
            else:
                kpoint_nac = k
            eps_inf, BORN, Vuc = util.get_nac_params(BORN_file, SCell, N1, N2, N3, tot_atoms_uc)
            C_nac = util.get_nac_C(kpoint_nac, Vuc, BORN, eps_inf, masses_uc, N1N2N3)
            K_corr_0K, K_corr_renorm = util.get_K_corr(K, C_nac), util.get_K_corr(K_renorm, C_nac)
        else:
            K_corr_0K, K_corr_renorm = K, K_renorm
            
        # Renormalised          
        D_renorm = util.get_D(k, K_corr_renorm,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_renorm, eigvecs_renorm, omegas_renorm = util.get_eigvals_eigvec(D_renorm)
        EIGVECS.append(eigvecs_renorm)
        if(np.any(np.all(np.isclose(k_scal,ks_scaled_path), axis=1))):
            EIGVECS_MD.append(eigvecs_renorm)
           
        # 0K dispersion
        D_0K = util.get_D(k, K_corr_0K,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_0K, eigvecs_0K, omegas_0K = util.get_eigvals_eigvec(D_0K)
        EIGVECS_0K.append(eigvecs_0K)
        frequencies[:,:,count_k] = omegas_renorm
        frequencies_disp[:,:,count_k] = omegas_0K 
        count_k = count_k + 1
# =============================================================================


# =============================================================================
    # this is for MD frequencies
    count_comm_k = 0
    frequencies_MD = np.zeros((2,tot_atoms_uc*3,len(ks_path)))
    ZQS = np.zeros((meta, 1+len(ks_path_many))) #for the DOS
    accepted_qpoints = []
    for i in range(len(ks_scaled_path)):
        qpoint = ks_scaled_path[i]
        if(np.any(np.all(np.equal(qpoint,ks_scaled_path[i]))) ): # e' un delirio questo ahaha, verifica che il qpoint trovato sia nel kpath
            to_skip = (4)*i
            to_skip_DOS = (1+meta)*i
            qpoint = np.genfromtxt(prefix+'quasiparticles'+appendix,skip_header=to_skip+0, max_rows=1)
            accepted_qpoints.append(qpoint.tolist())
            params = np.genfromtxt(prefix+'quasiparticles'+appendix,skip_header=to_skip+1, max_rows=3)
            omegas_gammas = params[0::2,:]
            frequencies_MD[:,:,count_comm_k] = omegas_gammas 
            if(np.allclose(qpoint, [0,0,0]) and NAC):
                # Renormalised          
                D_renorm_Gamma = util.get_D(qpoint, K_corr_renorm,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
                eigvals_renorm_Gamma, omegas_renorm_Gamma = util.get_eigvals(D_renorm_Gamma)
                frequencies_MD[0,:,count_comm_k] = omegas_renorm_Gamma
            count_comm_k = count_comm_k + 1
# =============================================================================

# =============================================================================
    # this is for the MD DOS
    ZQS = np.loadtxt('ZS'+appendix, usecols=(0,1))
    gaussian = 1/(sig*np.sqrt(2*np.pi)) * np.exp(-.5*((freq-mi)/sig)**2)                
    convolution = signal.fftconvolve(ZQS[:,1],gaussian, mode='same') / sum( gaussian)
    ZQS[:,1] = convolution
# =============================================================================
   
    # this is to reshape spectra according to real branches
    indexes, freqs_reshaped = util.get_real_branches(frequencies[0,:,:], EIGVECS, masses_uc, ks_path_many)
    indexes, freqs_disp_reshaped = util.get_real_branches(frequencies_disp[0,:,:], EIGVECS_0K, masses_uc, ks_path_many)
    indexes, freqs_MD_reshaped = util.get_real_branches(frequencies_MD[0,:,:], EIGVECS_MD, masses_uc, ks_path)
    frequencies_reshaped, frequencies_disp_reshaped , frequencies_MD_reshaped = np.copy(frequencies), np.copy(frequencies_disp), np.copy(frequencies_MD)
    frequencies_reshaped[0,:,:], frequencies_disp_reshaped[0,:,:], frequencies_MD_reshaped[0,:,:] = freqs_reshaped, freqs_disp_reshaped, freqs_MD_reshaped

    plot.plot40(distances_comm,  distances, frequencies_MD_reshaped, frequencies_disp_reshaped, frequencies_reshaped, ks_scaled_path, x_labels, ZQS, DOS_info, interp)

    
if(plot_type==5):
    print('Generating plot 5...')
    # take the path the user inputs and find all the k points you can plot, with interpolation
    ks_scal_path_many, ks_path_many, distances_many = util.get_kpath_many(ks_scaled_path, Hk, npoints=interp+1)
    num_modes = len(modes)
    K_renorm = np.loadtxt('K_renorm')

    freq = np.loadtxt('ZS'+appendix, usecols=0)
    meta = len(freq)
    
# =============================================================================        
    count_k = 0
    frequencies = np.zeros((tot_atoms_uc*3,len(ks_path_many)))
    frequencies_disp = np.zeros((tot_atoms_uc*3,len(ks_path_many)))
    EIGVECS, EIGVECS_0K = [], []
    for i in range(len(ks_path_many)):
        k = ks_path_many[i]
        print('\t processing path k-point:', i, ks_scal_path_many[i])
        
        # NAC
        if NAC:
            if(np.allclose(k, [0,0,0])):
                kpoint_nac = ks_path_many[i+1]
            else:
                kpoint_nac = k
            eps_inf, BORN, Vuc = util.get_nac_params(BORN_file, SCell, N1, N2, N3, tot_atoms_uc)
            C_nac = util.get_nac_C(kpoint_nac, Vuc, BORN, eps_inf, masses_uc, N1N2N3)
            K_corr_0K, K_corr_renorm = util.get_K_corr(K, C_nac), util.get_K_corr(K_renorm, C_nac)
        else:
            K_corr_0K, K_corr_renorm = K, K_renorm
            
        # Renormalised          
        D_renorm = util.get_D(k, K_corr_renorm,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_renorm, eigvecs_renorm, omegas_renorm = util.get_eigvals_eigvec(D_renorm)
        EIGVECS.append(eigvecs_renorm)
        
        # 0K dispersion
        D_0K = util.get_D(k, K_corr_0K,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_0K, eigvecs_0K, omegas_0K = util.get_eigvals_eigvec(D_0K)
        EIGVECS_0K.append(eigvecs_0K)
        
        frequencies[:,count_k] = omegas_renorm
        frequencies_disp[:,count_k] = omegas_0K 
        count_k = count_k + 1
# =============================================================================

# =============================================================================      
    count = 0
    ZQS = np.zeros((meta, len(ks_scaled_path)))
    ZQS_proj = np.zeros((meta, tot_atoms_uc*3, len(ks_scaled_path)))
    accepted_qpoints = []
    for i in range(Nqs_path):
        to_skip = (1+meta)*i
        to_skip2 = 4*i
        Params = np.genfromtxt(prefix+'quasiparticles'+appendix,skip_header=to_skip2+1, max_rows=3)
        qpoint = np.genfromtxt(prefix+'Zqs'+appendix,skip_header=to_skip+0, max_rows=1)
        for j in range(len(ks_scaled_path)):
            if(np.allclose(qpoint, ks_scaled_path[j]) and ((qpoint.tolist() not in accepted_qpoints) or i==j)): #è un completo delirio
                accepted_qpoints.append(qpoint.tolist())
                
                Zq = np.genfromtxt(prefix+'Zqs'+appendix,skip_header=to_skip+1, max_rows=meta)
                ZQS[:,count] = Zq[:,0]
                for b in range(tot_atoms_uc*3):
                    params = Params[:,b]

                    if(gaussian_smoothing != 0):
                        if(gaussian_smoothing < 0):
                            sig, mi = params[-1]/2, freq[int(len(freq)/2)]
                            if (sig == 0):
                                sig = 0.0001
                        else:
                            sig, mi = gaussian_smoothing, freq[int(len(freq)/2)]
                        
                        gaussian = util.norm_gaussian(freq, mi, sig)
                        convolution = signal.fftconvolve(Zq[:,b+1],gaussian, mode='same') / sum( gaussian)
                        ZQS_proj[:,b,i] = convolution
                    else:
                        ZQS_proj[:,b,i] = Zq[:,b+1]
        count = count + 1
# =============================================================================      


    #this is to reshape spectra according to real branches
    indexes, freqs_reshaped = util.get_real_branches(frequencies, EIGVECS, masses_uc, ks_path_many)
    indexes_0K, freqs_disp_reshaped = util.get_real_branches(frequencies_disp, EIGVECS_0K, masses_uc, ks_path_many)
    
    # #this is to reshape spectra according to real branches
    # indexes, freqs_disp_reshaped = util.aaa_get_real_branches(frequencies_disp, EIGVECS_0K, masses_uc, Hk, ks_scal_path_many)
    
    frequencies_reshaped, frequencies_disp_reshaped  = np.copy(frequencies), np.copy(frequencies_disp)
    frequencies_reshaped, frequencies_disp_reshaped = freqs_reshaped, freqs_disp_reshaped
    
    ZQS_proj_reshaped = np.zeros((meta, num_modes, len(ks_path)))
    for j in range(len(ks_path)):
        ZQS_proj_reshaped[:,:,j] = ZQS_proj[:,indexes[j,modes],j]
    freqs_from_spectrum = util.freqs_spectrum(freq,ZQS_proj_reshaped)
    
    if (interp>0):
        ZQS_proj_interp = util.interpol_spectrum(ks_path, freq, freqs_from_spectrum, distances_comm, distances_many, frequencies_reshaped[modes,:], EIGVECS, modes, ZQS_proj_reshaped)
    else:
        ZQS_proj_interp = ZQS_proj_reshaped[:,range(len(modes)),:]
        
    # if (interp>0):
    #     ZQS_proj_interp = util.aaa_interpol_spectrum(ks_path, freq, freqs_from_spectrum, EIGVECS_0K, modes, ZQS_proj_reshaped, interp)
    # else:
    #     ZQS_proj_interp = ZQS_proj_reshaped[:,range(len(modes)),:]
        
    plot.plot_k2(distances_comm, distances_many, frequencies_disp_reshaped, frequencies_reshaped, freq,ZQS,ZQS_proj_interp, x_labels,max_Z,modes)


if(plot_type==6):
    num_modes = len(modes)
    # ks_scal_path_many, ks_path_many, distances_many = util.get_kpath_many(ks_scaled_path, Hk, npoints=interp+1)
    K_renorm = np.loadtxt('K_renorm')
    
    freq = np.loadtxt('ZS'+appendix, usecols=0)
    meta = len(freq)
    accepted_qpoints = []
    
    for i in range(Nqs_path):
        k = ks_path[i]
        #NAC
        if (NAC and Nqs_path>1):
            if(np.allclose(k, [0,0,0])):
                kpoint_nac = ks_path[i+1]
            else:
                kpoint_nac = k
            eps_inf, BORN, Vuc = util.get_nac_params(BORN_file, SCell, N1, N2, N3, tot_atoms_uc)
            C_nac = util.get_nac_C(kpoint_nac, Vuc, BORN, eps_inf, masses_uc, N1N2N3)
            K_corr_0K, K_corr_renorm = util.get_K_corr(K, C_nac), util.get_K_corr(K_renorm, C_nac)
        else:
            K_corr_0K, K_corr_renorm = K, K_renorm
        
        D_0K = util.get_D(k, K_corr_0K,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_0K, eigvecs_0K, omegas_0K = util.get_eigvals_eigvec(D_0K)
        
        D_renorm = util.get_D(k, K_corr_renorm,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_renorm, eigvecs_renorm, omegas_renorm = util.get_eigvals_eigvec(D_renorm)
        
        to_skip = (1+meta)*i
        Zq = np.genfromtxt(prefix+'Zqs'+appendix,skip_header=to_skip+1, max_rows=meta)
        for b in range(len(modes)):
            mm = modes[b]
            ani = plot.plot6(freq,Zq[:,mm+1],Zq[:,0], k,eigvecs_0K[:,mm],omegas_0K[mm],mm,Ruc,masses_uc, max_Z, title='0K eigenvectors')
        for b in range(len(modes)):
            mm = modes[b]
            ani = plot.plot6(freq,Zq[:,mm+1],Zq[:,0], k,eigvecs_renorm[:,mm],omegas_renorm[mm],mm,Ruc,masses_uc, max_Z, title='finite T eigenvectors')
    
    
if(plot_type==7):
    print('WARNING: atm this only works for cubic crystals!')
    
    K_renorm = np.loadtxt('K_renorm')
    # take the path the user inputs and find all the k points you can plot
    # ks_path, x_labels, distances = read.read_path(kinput, Nqs_path, labels, Hk) 
    
    c_A_to_B = 1.88973 #conversion to Bohrs
    Hk = Hk/(2*np.pi) #if you use Thz as frequencies, you have to use 1/B as k, without 2 pi
    Hk = Hk*c_A_to_B #if you wanna use the 1/100 conv factor later, you need Angstrom
    
    #find the closest qpoints for EC
    dirs_C11 = [[1,0,0],[0,1,0],[0,0,1]]
    dirs_C12_C44 = [[1,1,0],[1,0,1],[0,1,1]]
    ampl = 10
    
    A1, A2, A3 = SCell[0,:], SCell[1,:], SCell[2,:]
    V = np.dot(A1, np.cross(A2,A3))
    print('The volume of the supercell is ', V, 'Bohr^3')
    print('NB: if you run a NPE simulation, you better use the average NPE volume!')
    conv_to_gcm3 = 11.2059 #convert amu/B^3 to g/cm^3
    M_tot = np.sum(masses)/3
    rho = M_tot/V*conv_to_gcm3
    print('The density is ',rho, ' g/cm^3\n')
    
    conv_factor = 1/100        
    
    accepted_qpoints = []
    for i in range(1,len(ks_path)-1):
        
        
        qpoint_sc = ks_scaled_path[i]
        qpoint_sc_prev = ks_scaled_path[i-1]
        k = ks_path[i]
        # Renormalised          
        D_renorm = util.get_D(k, K_renorm,N1,N2,N3,R0,masses_uc, tot_atoms_uc, SCell)
        eigvals_renorm, eigvec_q, omegas_renorm = util.get_eigvals_eigvec(D_renorm)
        
        
        direc = np.abs(np.dot(Hk, qpoint_sc - qpoint_sc_prev))
        direc_sc = np.round(direc/direc.max(),2)

            
        to_skip = (4)*i
        qpoint = np.genfromtxt(prefix+'quasiparticles'+appendix,skip_header=to_skip+0, max_rows=1)
        if(direc_sc.tolist() in dirs_C11 and (np.allclose(qpoint_sc_prev,[0,0,0]) or np.allclose(ks_path[i+1],[0,0,0]))):
            
            params = np.genfromtxt(prefix+'quasiparticles'+appendix,skip_header=to_skip+1, max_rows=3)
            omegas  = params[0,:]
            
            csi = np.linalg.norm(np.dot(Hk,qpoint))
            print('csi: ', csi)
            print()
            ##==============================================================================
            ## C11
            print('# =============================================================================')
            print('C11')
            freqs = []
            eigvecs_acou = eigvec_q[:,0:3]
            for j in range(0,3):
                freqs.append(omegas[j])
                
            
            j = -1
            freq = freqs[j]
            eigvec = eigvecs_acou[:,j]
            print('qpoint scaled: ', qpoint)
            print('qpoint:', np.round(np.dot(Hk,qpoint),3))
            print()
            print('freqs: ', np.round(freqs,3), ' taken ', np.round(freq,3))
            print('\neigenvec:')
            print(np.round(eigvec*ampl/np.sqrt(masses_uc),2).reshape(np.shape(Ruc)))
            print('# =============================================================================')
            print()
            C11 = rho * (freq/csi)**2 *conv_factor
            ##==============================================================================
            
            # =============================================================================
            # C44
            print('# =============================================================================')
            print('C44-1')
            freqs = []
            eigvecs_acou = eigvec_q[:,0:3]
            for j in range(0,3):
                freqs.append(omegas[j])
            j = 0
            freq = freqs[j]
            eigvec = eigvecs_acou[:,j]
            print('qpoint scaled: ', qpoint)
            print('qpoint: ',np.round(np.dot(Hk,qpoint),3))
            print()
            print(np.round(freqs,3), ' taken ', np.round(freq,3))
            print('\neigvec:')
            print(np.round(eigvec*ampl/np.sqrt(masses_uc),2))
            C44_1 = rho * (freq/csi)**2 *conv_factor
            print('# =============================================================================')
            print()
            # =============================================================================
            
            
        if(direc_sc.tolist() in dirs_C12_C44 and np.allclose(qpoint_sc_prev,[0,0,0]) or np.allclose(ks_path[i+1],[0,0,0])):
            params = np.genfromtxt(prefix+'quasiparticles'+appendix,skip_header=to_skip+1, max_rows=3)
            omegas  = params[0,:]
            
            #check that k = [csi, csi, 0]
            check = [np.allclose(x,csi) for x in np.dot(Hk,qpoint)] 
            if (check not in [[True, True, False],[True, False, True],[False, True, True]]):
                print('ERROR WARNING: the q point is not [csi, csi, 0] so everything is gonna be wrong')
            
            
            
            # =============================================================================
            # C44
            print('# =============================================================================')
            print('C44-2')
            freqs = []
            eigvecs_acou = eigvec_q[:,0:3]
            for j in range(0,3):
                freqs.append(omegas[j])
            j = 1
            freq = freqs[j]
            eigvec = eigvecs_acou[:,j]
            print('qpoint scaled: ', qpoint)
            print('qpoint:', np.dot(Hk,qpoint))
            print()
            print('freqs: ', freqs, ' taken ', freq)
            print('\neigenvec:')
            print(np.round(eigvec*ampl/np.sqrt(masses_uc),2).reshape(np.shape(Ruc)))
            print('# =============================================================================')
            print()
            C44_2 = .5* rho * (freq/csi)**2 *conv_factor
            # =============================================================
            
            
            #==============================================================================
            # C12
            print('# =============================================================================')
            print('C12-1')
            freqs = []
            eigvecs_acou = eigvec_q[:,0:3]
            for j in range(0,3):
                freqs.append(omegas[j])
                
            #csi = np.linalg.norm(np.dot(hr,qpoint_scaled))
            j = 0
            freq = freqs[j]
            eigvec = eigvecs_acou[:,j]
            print('qpoint scaled: ', qpoint)
            print('qpoint: ',np.round(np.dot(Hk,qpoint),3))
            print()
            print(np.round(freqs,3), ' taken ', np.round(freq,3))
            print('\neigvec:')
            print(np.round(eigvec*ampl/np.sqrt(masses_uc),2))
            A = rho * (freq/csi)**2 *conv_factor
            C12_1 =C11-A  #<- with freqs[0] # A - C11 -2*C44 #
            print('# =============================================================================')
            print()
            #==============================================================================
            
            #==============================================================================
            # C12
            print('# =============================================================================')
            print('C12-2')
            freqs = []
            eigvecs_acou = eigvec_q[:,0:3]
            for j in range(0,3):
                freqs.append(omegas[j])
                
            #csi = np.linalg.norm(np.dot(hr,qpoint_scaled))
            j = -1
            freq = freqs[j]
            eigvec = eigvecs_acou[:,j]
            print('qpoint: ', qpoint)
            print('qpoint:', np.dot(Hk,qpoint))
            print()
            print('freqs: ', freqs, ' taken ', freq)
            print('eigenvec:')
            print(np.round(eigvec*ampl/np.sqrt(masses_uc),2).reshape(np.shape(Ruc)))
            print('# =============================================================================')
            print()
            A = rho * (freq/csi)**2 *conv_factor
            C12_2 = A - C11 -2*C44_1 #C11-A  #<- with freqs[0] #
            C12_2_2 = A - C11 -2*C44_2
            #==============================================================================
            
            print()
            print('Elastic constants')
            print('C11 = ', np.round(C11,2), 'GPa')
            print('C44 using [100] = ', np.round(C44_1,2), 'GPa')
            print('C44 using [110] = ', np.round(C44_2,2), 'GPa')
            print('C12 using eq 1 = ', np.round(C12_1,2), 'GPa')
            print('C12 using eq 2 (C44[100])= ', np.round(C12_2,2), 'GPa')
            print('C12 using eq 2 (C44[110])= ', np.round(C12_2_2,2), 'GPa')
            
            print()
            print('Engineering elastic constants')
            ni = C12_2_2/(C11+C12_2_2)
            E = C11*(1+ni)*(1-2*ni)/(1-ni)
            print('E = ', np.round(E,2), 'GPa')
            print('ni = ', np.round(ni,2))
            print('G = ', np.round(C44_2,2), 'GPa')
    
    

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

