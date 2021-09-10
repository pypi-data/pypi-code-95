#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 14:40:14 2020

@author: gc4217
"""

import numpy as np
import os, sys
from decomp import plot, read


## =============================================================================
## Parameters
input_file = sys.argv[1]
mode = read.read_post_proc(input_file)[0]
n_atom_unit_cell = read.read_post_proc(input_file)[1]
file_eigenvectors = read.read_post_proc(input_file)[2]
max_Z = read.read_post_proc(input_file)[3]
kinput = read.read_post_proc(input_file)[4::][0]
labels = read.read_post_proc(input_file)[5]
modes = read.read_post_proc(input_file)[6]
temperatures_folders = read.read_post_proc(input_file)[7]



Ruc, masses_for_animation = 0,0

tot_atoms_uc = int(np.sum(n_atom_unit_cell)) 
Nqpoints, qpoints_scaled, ks, freqs_disp, eigvecs, distances = read.read_phonopy(file_eigenvectors, tot_atoms_uc)
#### =============================================================================

if(mode==0):
    namedir = plot.create_folder('')
    freq = np.loadtxt('freq')
    meta = len(freq)
    for i in range(Nqpoints):
        to_skip = (1+meta)*i
        ZZ = np.genfromtxt('Zqs',skip_header=to_skip+1, max_rows=meta)
        Z_q = ZZ[:,0]
        Z = ZZ[:,1:]
        to_skip2 = 4*i
        Params = np.genfromtxt('quasiparticles',skip_header=to_skip2+1, max_rows=3)
        
        k_scaled = qpoints_scaled[i]
        eigvec = eigvecs[i]
        freq_disp = freqs_disp[i]
        print(' Creating plots for k point = ', k_scaled)
        for n in range(tot_atoms_uc*3):
            params = Params[:,n]
            plot.save_proj(freq,Z[:,n],Z_q, qpoints_scaled[i], Ruc, eigvec[:,n],freq_disp[n],n,namedir,masses_for_animation, params,max_Z)


if(mode==1):
    freq = np.loadtxt('freq')
    meta = len(freq)
    ZQS = [np.zeros(meta)]
    count = 1
    accepted_qpoints = []
    accepted_labels = []
    for i in range(Nqpoints):
        to_skip = (1+meta)*i
        qpoint = np.genfromtxt('Zqs',skip_header=to_skip+0, max_rows=1)
        for j in range(len(kinput)):
            if(np.allclose(qpoint, kinput[j]) and (qpoint.tolist() not in accepted_qpoints)):
                accepted_qpoints.append(qpoint.tolist())
                accepted_labels.append(labels[j])
                Zq = np.genfromtxt('Zqs',skip_header=to_skip+1, max_rows=meta)
                ZQS.append(Zq[:,0])
                count = count + 1
            
                #    Ztot = np.genfromtxt('ZS',usecols=0)
    ZQS = np.array(ZQS).T
    ZQS[:,0] = np.sum(ZQS[:,1::],axis=1)
    plot.plot1(freq,ZQS, accepted_labels)
    
    
if(mode==2): 
    freq = np.loadtxt('freq')
    meta = len(freq)
    ZQS = np.zeros((meta, tot_atoms_uc*3+1, len(kinput)))
    count = 0
    accepted_qpoints = []
    accepted_labels = []
    freqs_from_disp = np.zeros((tot_atoms_uc*3,len(kinput)))
    for i in range(Nqpoints):
        to_skip = (1+meta)*i
        qpoint = np.genfromtxt('Zqs',skip_header=to_skip+0, max_rows=1)

        for j in range(len(kinput)):
            if(np.allclose(qpoint, kinput[j]) and (qpoint.tolist() not in accepted_qpoints)):
                accepted_qpoints.append(qpoint.tolist())
                accepted_labels.append(labels[j])

                for m in range(Nqpoints):
                    if(np.allclose(qpoint,qpoints_scaled[m])):
                        freqs_from_disp[:,count] = freqs_disp[m]
                        break
                
                
                Zq = np.genfromtxt('Zqs',skip_header=to_skip+1, max_rows=meta)
                ZQS[:,:,count] = Zq[:,:]
                count = count + 1
                
    
    plot.plot2(freq,ZQS, modes, accepted_labels, freqs_from_disp)
    
    
if(mode==3):
    subdirectories = [x[1] for x in os.walk(temperatures_folders)][0]
    subdirectories.sort(key= lambda x: float(x.strip('K')))
    Ts = [int(x.strip('K')) for x in subdirectories]
    frequencies = np.zeros((2,tot_atoms_uc*3,len(kinput),len(Ts)))
    count_T = 0
    for subdir in subdirectories:
        count_q = 0
        accepted_qpoints = []
        accepted_labels = []

        for i in range(Nqpoints):
            to_skip = (4)*i
            qpoint = np.genfromtxt(subdir+'/quasiparticles',skip_header=to_skip+0, max_rows=1)
            for j in range(len(kinput)):
                if(np.allclose(qpoint, kinput[j]) and (qpoint.tolist() not in accepted_qpoints)):
                    accepted_qpoints.append(qpoint.tolist())
                    accepted_labels.append(labels[j])
                    omegas_gammas = np.genfromtxt(subdir+'/quasiparticles',skip_header=to_skip+1, max_rows=3)
                    frequencies[:,:,count_q, count_T] = omegas_gammas[0::2,:]
                    count_q = count_q + 1
        count_T = count_T + 1
    
    diff =len(frequencies[0,0,:,0]) -  len(accepted_labels) 
    if(diff != 0): #this is to eliminate repetitive kpoints if present
        for h in range(diff):
            frequencies = np.delete(frequencies, -1, axis=2)
    plot.plot3(Ts, frequencies, modes, accepted_labels)

   
if(mode==4):
    # take the path the user inputs and find all the k points you can plot
    ks_path, x_labels = read.read_path(kinput, Nqpoints, labels)
    frequencies = np.zeros((2,tot_atoms_uc*3,len(ks_path)))
    for i in range(Nqpoints):
        to_skip = (4)*i
        qpoint = np.genfromtxt('quasiparticles',skip_header=to_skip+0, max_rows=1)
        if(np.any(np.all(np.equal(qpoint,ks_path), axis=1))): # e' un delirio questo ahaha, verifica che il qpoint trovato sia nel kpath
            params = np.genfromtxt('quasiparticles',skip_header=to_skip+1, max_rows=3)
            omegas_gammas = params[0::2,:]
            frequencies[:,:,i] = omegas_gammas
    plot.plot4(distances, frequencies, ks_path, x_labels)
    

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

