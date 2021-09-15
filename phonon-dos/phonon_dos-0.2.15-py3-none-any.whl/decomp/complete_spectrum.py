#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 16:55:42 2019

@author: Gabriele Coiana
"""
import sys
import numpy as np
from decomp import cell, bz, plot, read, util

def corr(tall,X,tau,mode):
    M = len(tall)
    dt = tall[1] - tall[0]
    tmax = M - tau
    N = np.size(X[0])   
    X0 = X[0:tmax,:]
    X2 = 1/tmax*np.sum(X[0:tmax,:]*X[0:tmax,:])
    C = []
    for n in range(tau):
        Xjj = X[n:n+tmax,:]
        a = np.multiply(np.conjugate(X0),Xjj)
        b = 1/(tmax) * np.sum(a,axis=0)#/X2
        c = np.multiply(b,1)
        if (mode=='projected'):
            d = c
        else:
            d = np.sum(c)
        C.append(d)
    C = np.array(C)
    t = np.arange(0,tau)*dt
    freq = np.fft.fftfreq(tau,d=dt)
    Z = np.fft.fft(C,axis=0)
    return t, C, freq, Z


# =============================================================================
# Parameters
input_file = sys.argv[1]
a = read.read_parameters(input_file)[0]
Masses = read.read_parameters(input_file)[1]
n_atom_unit_cell = read.read_parameters(input_file)[2]
n_atom_conventional_cell = read.read_parameters(input_file)[3]
N1,N2,N3 = read.read_parameters(input_file)[4:7]
kinput = read.read_parameters(input_file)[7::][0]
file_eigenvectors = read.read_parameters(input_file)[8]
file_trajectory = read.read_parameters(input_file)[9]
file_initial_conf = read.read_parameters(input_file)[10]
system = read.read_parameters(input_file)[11]
DT = read.read_parameters(input_file)[12]
tau = read.read_parameters(input_file)[13]
T = read.read_parameters(input_file)[14]
branches = read.read_parameters(input_file)[15]
max_Z = read.read_parameters(input_file)[16]


tot_atoms_uc = int(np.sum(n_atom_unit_cell)) 
tot_atoms_conventional_cell = int(np.sum(n_atom_conventional_cell)) 
N1N2N3 = N1*N2*N3 # Number of cells
N = N1*N2*N3*tot_atoms_uc    # Number of atoms
masses, masses_for_animation = util.repeat_masses(Masses, n_atom_conventional_cell, n_atom_unit_cell, N1, N2, N3)
cH = 1.066*1e-6 # to [H]
cev = 2.902*1e-05 # to [ev]
kbH = 3.1668085639379003*1e-06# a.u. [H/K]
kbev = 8.617333262*1e-05 # [ev/K]
# =============================================================================

print('\nHello, lets start!\n')
print('Getting input parameters...')
print(' System: ', system)
print(' Masses: ', Masses)
print(' Number of atoms per unit cell', n_atom_unit_cell)
print(' Supercell: ', N1, N2, N3)
print(' k path: ', kinput)
print(' Temperature: ', T, ' K')
print()
print(' Number of timesteps chosen for correlation function: ', tau)
print(' Extent of timestep [ps]: ', DT*2.418884254*1e-05)
print(' Branches chosen: ', branches)
print(' Maximum correlation function value: ', max_Z)
print()
print('Now calculating velocities...')
Nqpoints, qpoints_scaled, ks, freqs, eigvecs = read.read_phonopy(file_eigenvectors, tot_atoms_uc)
#Nqpoints2, qpoints_scaled2, ks2, freqs2, eigvecs2 = read.read_phonopy('../qpoints_100K.yaml', tot_atoms_uc)
Ruc, R0 = read.read_SPOSCAR(file_initial_conf, N1N2N3, N,n_atom_conventional_cell,n_atom_unit_cell)                       #rhombo or avg R0

lista_freqs = []
lista_freqs.append(freqs[:,branches[0]:branches[1]])
#lista_freqs.append(freqs2)
#lista_freqs = np.array(lista_freqs)

Rt = np.loadtxt(file_trajectory)[:,1:]
Num_timesteps = int(len(Rt[:,0]))
print(' Number of timesteps of simulation: ', Num_timesteps, '\n')
tall = np.arange(Num_timesteps)*DT*2.418884254*1e-05 #conversion to picoseconds
dt_ps = tall[1]-tall[0]
meta = int(Num_timesteps/2)
Vt = np.diff(Rt,axis=0)/dt_ps*np.sqrt(masses)/np.sqrt(3*(N))

#you want the max frequency plotted be 25 Thz
max_freq = 0.5*1/dt_ps
if (max_freq < 25):
    meta = int(tau/2)
else:
    meta = int(tau/2*25/max_freq)
Vt = np.diff(Rt,axis=0)/dt_ps*np.sqrt(masses)/np.sqrt(3*(N))



## =============================================================================
## Decomposition
Zs = np.zeros((meta,Nqpoints))
Zs_projected = np.zeros((meta, branches[1]-branches[0], Nqpoints))
every_tot = int(tot_atoms_conventional_cell/tot_atoms_uc)
print('Now performing decomposition... ')
for i in range(Nqpoints):
    eigvec = eigvecs[i]
    k = ks[i]
    k_scaled = qpoints_scaled[i]
    freq_disp = freqs[i]
    print('\tkpoint scaled:  ',k_scaled)
    
    #Creating the collective variable based on the k point
    Vcoll = np.zeros((Num_timesteps-1,tot_atoms_conventional_cell*3),dtype=complex)  
    for j,h,l in zip(range(tot_atoms_conventional_cell*3),np.repeat(range(0,N),3)*N1N2N3*3,np.tile(range(0,3),tot_atoms_conventional_cell)):
        vels = np.array(Vt[:,h+l:h+N1N2N3*3:3],dtype=complex)
        poss = R0[h:h+N1N2N3*3:3,:]
        x = np.multiply(vels,np.exp(1j*np.dot(poss,k)))
        Vcoll[:,j] = np.sum(x,axis=1)
        
        
    Tkt = np.zeros((Num_timesteps-1,tot_atoms_uc*3), dtype=complex)
    for l,m in zip(range(0,tot_atoms_conventional_cell*3, every_tot*3),range(0,tot_atoms_uc*3,3)):
        Tkt[:,m:m+3] = Vcoll[:,l:l+3]
    eigvecH = np.conjugate(eigvec.T)
    Qkt = np.dot(eigvecH,Tkt.T).T#.reshape(Num_timesteps,1)
    
    
    # of the whole k point
    t, C, freq, G = corr(tall,Tkt,tau, ' ')
    Ztot = np.sqrt(np.conjugate(G)*G).real*cH/(kbH*T)
    print('\t\t kinetic energy of this kpoint: ',1/2*C.real[0]*cH, ' Hartree')
    print('\t\t kinetic according to eqp thm: ',1/2*kbH*T, ' Hartree')
    print('\t\t ratio: ', np.round((1/2*C.real[0]*cH)/(1/2*kbH*T)*100,2), ' %\n')
    
    # projected!
    t_proj, C_proj, freq_proj, G_proj = corr(tall,Qkt,tau, 'projected')
    Z = np.sqrt(np.conjugate(G_proj)*G_proj).real*cev/(kbev*T)
    
    for n in range(branches[0],branches[1]):
        Zs_projected[:,n-branches[0],i] = Z[0:meta,n]
    Zs[:,i] = Ztot[0:meta]
# =============================================================================

#np.savetxt('Zs_'+system,Zs)
#np.savetxt('freq',freq[0:meta])
plot.plot_k(freq[0:meta],Zs,Zs_projected, qpoints_scaled,lista_freqs,max_Z,branches,title=['freq from 0K dispersion','freq from finite K'])
