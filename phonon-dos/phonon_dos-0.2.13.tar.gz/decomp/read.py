# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 11:05:28 2018

@author: Gabriele Coiana
"""

import numpy as np
import yaml, os
#yaml.warnings({'YAMLLoadWarning': False})

def read_parameters(input_file):
    """
    This function takes the input parameters from the file input.txt 
    and applies the right types to the variables
    """
    lista = []
    f = open(input_file, 'r')
    A = f.readlines()
    for string in A:
        index = string.find('=')+2
        lista.append(string[index:-1])
        

    m = lista[1]
    Masses = np.fromstring(m, dtype=np.float, sep=',')
    
    ns = lista[2]
    n_atom_unit_cell = np.fromstring(ns, dtype=np.int, sep=',')
    
    N = lista[3]
    n = np.fromstring(N, dtype=np.int, sep=',')
    N1,N2,N3 = n[0],n[1],n[2]
    
    band = lista[4]
    a = np.fromstring(band, dtype=np.float, sep=',')
    num = len(a)/3
    ks = np.split(a,num)
    
    file_FC = str(lista[5])
    
    file_trajectory = str(lista[6])
    
    file_initial_conf = str(lista[7])
    
    DT = float(lista[8])
    
    Nb = int(lista[9])
    
    

            
#    brchs = lista[14]
#    branches = np.fromstring(brchs, dtype=np.int, sep=',')
#    
#    max_Z = float(lista[15])
    
    f.close()
    return  Masses, n_atom_unit_cell, N1,N2,N3, ks, file_FC, file_trajectory, file_initial_conf, DT, Nb





def read_post_proc(input_file):
    lista = []
    f = open(input_file, 'r')
    A = f.readlines()
    for string in A:
        index = string.find('=')+2
        lista.append(string[index:-1])
    
    plot_types = int(lista[1])#np.fromstring(lista[1], dtype=np.int, sep=',')
    
    m = lista[2]
    Masses = np.fromstring(m, dtype=np.float, sep=',')
    
    ns = lista[3]
    n_atom_unit_cell = np.fromstring(ns, dtype=np.int, sep=',')
    
    N = lista[4]
    n = np.fromstring(N, dtype=np.int, sep=',')
    N1,N2,N3 = n[0],n[1],n[2]
    
    file_forces = str(lista[5])
    
    file_SPOSCAR = lista[6]
    
    max_Z = float(lista[7])
    
    gaussian_smoothing = lista[8]
    if(gaussian_smoothing=='auto'):
        gaussian_smoothing = -1
    else:
        gaussian_smoothing = float(lista[8])
    
    interp = int(lista[9])
    
    ks = lista[10]
    a = np.fromstring(ks, dtype=np.float, sep=',')
    num = len(a)/3
    kpoints = np.split(a,num)
    
    labs = lista[11]
    labels = labs.split(',')
    
    modes = np.fromstring(lista[12], dtype=np.int, sep=',')
    
    temperature_folders = lista[13]
    
    NAC = bool(int(lista[14]))
    
    appendix = lista[15].strip()

    return plot_types, Masses, n_atom_unit_cell, N1, N2, N3, file_forces, file_SPOSCAR, max_Z, gaussian_smoothing, interp, kpoints, labels, modes, temperature_folders, NAC, appendix



def read_SPOSCAR_and_masses(file, n_atom_primitive_cell, Masses, N1, N2, N3):
    conv = np.genfromtxt(file, skip_header=1, max_rows=1)
    h = np.genfromtxt(file,skip_header=2, max_rows=3)
    S = np.genfromtxt(file, skip_header=8)
    
    N = len(S[:,0])
    tot_atoms_primitive = int(np.sum(n_atom_primitive_cell))

    N1N2N3 = int(N/tot_atoms_primitive)
    
    #your default units are Bohrs
    if (conv==1.0 or conv==1):
        conv_factor = 1.88973
    else:
        conv_factor = 1
            
    
    R0 = np.dot(h,S.T).T*conv_factor
    
    Ruc = np.zeros((tot_atoms_primitive,3))
    huc = h/np.array([N1,N2,N3])*conv_factor
    c = 0
    for i in range(len(n_atom_primitive_cell)):
        n = n_atom_primitive_cell[i]
        for j in range(n):
            Ruc[c+j] = R0[(c+j)*N1N2N3]
        c = c + j+1
    Suc = np.dot(np.linalg.inv(huc), Ruc.T).T
    R0_repeat = np.repeat(R0,3,axis=0)
    
    
    repeated_masses = np.array([])
    repeated_masses_for_ani = np.array([])
    for i in range(len(Masses)):
        mass = Masses[i]

        n = n_atom_primitive_cell[i]
        nprim = n_atom_primitive_cell[i]
        
        m = np.repeat(mass, N1N2N3*3*n)
        m_ani = np.repeat(mass,nprim*3)
        
        repeated_masses = np.concatenate((repeated_masses,m))
        repeated_masses_for_ani = np.concatenate((repeated_masses_for_ani,m_ani))
        
    masses = np.array(repeated_masses).flatten()
    masses_for_animation = np.array(repeated_masses_for_ani).flatten()
    
    return h*conv_factor, Ruc, Suc, R0, R0_repeat, S, masses, masses_for_animation

#h, Ruc, R0, masses, masses_for_animation = read_SPOSCAR_and_masses('../SPOSCAR_primitive', [1,1], [1,1], [1,1])
#Cell = h/10
#a1, a2, a3 = Cell[0,:], Cell[1,:], Cell[2,:]
#
#
#b1 = 2*np.pi * np.cross(a2,a3) / np.dot(a1, np.cross(a2,a3))
#b2 = 2*np.pi * np.cross(a3,a1) / np.dot(a2, np.cross(a3,a1))
#b3 = 2*np.pi * np.cross(a1,a2) / np.dot(a3, np.cross(a1,a2))
#
#print(b1/2/np.pi)
#print(b2)
#print(b3)







def read_FC(file):
    tot_atoms_uc, N = np.genfromtxt(file,max_rows=1, dtype=int)
    K = np.zeros((tot_atoms_uc*3,N*3))
    
    to_skip = 2
    for i in range(tot_atoms_uc):
        for j in range(N):
            forces = np.genfromtxt(file,skip_header=to_skip, max_rows=3)
            K[i*3:i*3+3,j*3:j*3+3] = forces
            to_skip = to_skip+1+3
    # ASAP's displacement is in Bohrs, but phonopy thinks they are A, so you do
    # FC = Force / displ = (ev / A) / Bohr = ev / A**2 /0.52917
    return K/0.529177249






