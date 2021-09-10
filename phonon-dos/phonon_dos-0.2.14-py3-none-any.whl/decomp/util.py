#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 14:33:25 2019

@author: gc4217
"""
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy import signal
import numpy as np
import os

def get_power_spectrum(time_quantity, constant):
    Tkw = np.fft.fft(time_quantity, axis=0)
    S = (np.sum(np.conjugate(Tkw)*Tkw, axis=1)).real*constant
    return S

def get_power_spectrum_proj(time_quantity, constant):
    Tkw = np.fft.fft(time_quantity, axis=0)
    S = (np.conjugate(Tkw)*Tkw).real*constant
    return S

def get_power_spectrum2(time_quantity, dt_ps, constant, Nb):
    Num_timesteps = len(time_quantity)
    tau = int(Num_timesteps/Nb)
    S = np.zeros(tau)
    for b in range(Nb):
        tkt = time_quantity[b*tau:(b+1)*tau]
        tw = np.fft.fft(tkt, axis=0)
        S = S + (np.sum(np.conjugate(tw)*tw, axis=1)).real*constant/tau*dt_ps
    freq = np.fft.fftfreq(tau, dt_ps)
    return tau, freq, S/Nb

def get_power_spectrum_proj2(time_quantity, dt_ps, constant, Nb):
    Num_timesteps = len(time_quantity)
    ndofs = len(time_quantity[0,:])
    tau = int(Num_timesteps/Nb)
    S = np.zeros((tau, ndofs))
    for b in range(Nb):
        tkt = time_quantity[b*tau:(b+1)*tau]
        tw = np.fft.fft(tkt, axis=0)
        S = S + (np.conjugate(tw)*tw).real*constant/tau*dt_ps
    freq = np.fft.fftfreq(tau, dt_ps)
    return tau, freq, S/Nb






def get_commensurate_kpath(file, N1,N2,N3, N1_FC,N2_FC,N3_FC, kinput_scaled, labels):
    # =============================================================================
    #   Brilloin zone 
    conv = np.genfromtxt(file, skip_header=1, max_rows=1)
    h = np.genfromtxt(file,skip_header=2, max_rows=3)
    S = np.genfromtxt(file, skip_header=8)
    
    #your default units are Bohrs, but phonopy's are A
    if (conv==1.0 or conv==1):
        conv_factor = 1.88973
    else:
        conv_factor = 1
        
    f1, f2, f3 = N1_FC/N1, N2_FC/N2, N3_FC/N3
    a1,a2,a3 = h[0]*conv_factor/N1,h[1]*conv_factor/N2,h[2]*conv_factor/N3
    c = 2*np.pi
    
    V = np.dot(a1,np.cross(a2,a3))
    b1 = c*np.cross(a2,a3)/V
    b2 = c*np.cross(a3,a1)/V
    b3 = c*np.cross(a1,a2)/V
    Hk = np.vstack((b1,b2,b3))
    
    b1_mod = np.linalg.norm(b1)
    b2_mod = np.linalg.norm(b2)
    b3_mod = np.linalg.norm(b3)
    b_mod = [b1_mod,b2_mod,b3_mod]
    kinput_real = np.multiply(b_mod,np.array(kinput_scaled))
    #Compute all possible k points
    x1 = np.arange(0,N1_FC+1)/N1_FC
    x2 = np.arange(0,N2_FC+1)/N2_FC
    x3 = np.arange(0,N3_FC+1)/N3_FC
    comb = np.array(np.meshgrid(x1,x2,x3)).T.reshape(-1,3)
    #a1 = np.multiply(comb,b1)
    #a2 = np.multiply(comb,b2)
    #a3 = np.multiply(comb,b3)
    #kpoints = a1+a2+a3
    allkpoints_scaled = comb
    allkpoints = np.multiply(b_mod,comb)
    # =============================================================================
    
    
    # =============================================================================
    # Compute directions <x y z>
    directions_scaled = []
    directions = []
    for i in range(0,len(kinput_scaled)-1):
        if(kinput_scaled[i] not in allkpoints_scaled):
            print('The k point '+str(kinput_scaled[i])+' provided is not compatible with the supercell. \nTry again :)')
        num = 1/np.max(np.abs(kinput_scaled[i]-kinput_scaled[i+1]))
        mod = np.linalg.norm(kinput_scaled[i]-kinput_scaled[i+1])
        directions_scaled.append((kinput_scaled[i]-kinput_scaled[i+1])*num)
        directions.append((kinput_scaled[i]-kinput_scaled[i+1])/mod)
    # =============================================================================
    
    # =============================================================================
    # Remove kpoints already input
    indexes = []
    for i in range(len(allkpoints_scaled)):
        for kpoint in kinput_scaled:
            if(np.array_equal(allkpoints_scaled[i],kpoint)):
                indexes.append(i)
    allkpoints_scaled_no = np.delete(allkpoints_scaled,indexes,axis=0)
    # =============================================================================
    
    # =============================================================================
    # Look for other k points in the same path
    kdef = kinput_real
    kdef_scaled = kinput_scaled
    x_labels = labels
    count = 0
    for index in range(0,len(directions)): #iterating over directions
        count = count+1
        direction = directions[index]
        
        if (all(direction <= np.array([0,0,0]))):
            for kpoint in allkpoints_scaled_no:
                diff = kinput_scaled[index]-kpoint
                mod = np.linalg.norm(diff)
                actual_direction = diff/mod
                if(np.array_equal(np.round(actual_direction,9),np.round(direction,9)) and all(np.abs(diff)<=np.abs(kinput_scaled[index+1]-kinput_scaled[index]))):
#                    kdef = np.insert(kdef,count,np.dot(h,kpoint),axis=0)   
                    kdef_scaled = np.insert(kdef_scaled,count,kpoint,axis=0)
                    x_labels = np.insert(x_labels,count,' ')
                    count = count+1 
        else:
            for kpoint in allkpoints_scaled_no[::-1]:
                diff = kinput_scaled[index]-kpoint
                mod = np.linalg.norm(diff)
                actual_direction = diff/mod
                if(np.array_equal(np.round(actual_direction,9),np.round(direction,9)) and all(np.abs(diff)<=np.abs(kinput_scaled[index+1]-kinput_scaled[index]))):
#                    kdef = np.insert(kdef,count,np.dot(h,kpoint),axis=0)
                    kdef_scaled = np.insert(kdef_scaled,count,kpoint,axis=0)
                    x_labels = np.insert(x_labels,count,' ')
                    count = count+1 

    # =============================================================================
    
    kdef_scaled = np.array(kdef_scaled)
    kdef = np.dot(Hk,kdef_scaled.T).T
    Nqpoints = len(kdef)
    
    # =============================================================================
    #  fake k points only for plotting, projection
    directionsdef = []
    for i in range(0,len(kdef_scaled)-1):
        directionsdef.append((kdef[i]-kdef[i+1]))
    kk = np.zeros(len(kdef_scaled))
    for i in range(1,len(kk)):
        kk[i] = kk[i-1]+(np.linalg.norm(directionsdef[i-1]))
    # =============================================================================
    
    return Nqpoints, kdef, kdef_scaled, kk, x_labels, Hk

def get_kpath_many(kinput, Hk, npoints=20):
    ks_scal = np.array([0,0,0])
    distances, dist = [], 0
    for i in range(len(kinput)-1):
        this_k = kinput[i]
        next_k = kinput[i+1]
        diff = next_k - this_k
        increment = diff/npoints
        kpoints_in_between = np.outer(increment, np.arange(npoints+1)).T + this_k
        distance = np.linalg.norm(np.dot(Hk,(kpoints_in_between-this_k).T).T, axis=1) + dist
        dist = distance[-1]
        distances.append(distance[0:-1])
        ks_scal = np.vstack((ks_scal,kpoints_in_between[:-1,:]))
        
        
    ks_scal = np.vstack((ks_scal, kinput[-1]))
    ks_scal = ks_scal[1::,:]
    
    distances = np.array(distances).flatten()
    distances = np.concatenate((distances, [distance[-1]]))

    
    ks = np.dot(Hk, ks_scal.T).T
    return ks_scal, ks, distances

def get_kgrid(N1k, N2k, N3k, Hk):
    x,y,z = np.linspace(0,1,N1k+1)[0:-1], np.linspace(0,1,N2k+1)[0:-1], np.linspace(0,1,N3k+1)[0:-1]
    kpoints_scal = np.array(np.meshgrid(x,y,z)).T.reshape(-1,3)
    kpoints = np.dot(Hk,kpoints_scal.T).T
    return kpoints_scal, kpoints

def check_is_symm(k_scal, ks_scal_path):
    permutations = np.array([[[0,1,0],[1,0,0],[0,0,1]], 
                             [[0,0,1],[0,1,0],[1,0,0]], 
                             [[1,0,0],[0,0,1],[0,1,0]],
                             [[0,1,0],[0,0,1],[1,0,0]],
                             [[0,0,1],[1,0,0],[0,1,0]]])
    accepted_ks = []

    #first check: is this irr k within the k path input?
    for j in range(len(permutations)):
        matrix = permutations[j]
        k_permutated = np.dot(matrix, k_scal)
        if (np.any(np.all(np.isclose(k_permutated-ks_scal_path,0), axis=1)) and (k_permutated.tolist() not in accepted_ks) ):
            accepted_ks.append(k_permutated.tolist())
            
    #second check: is this irr k in the k path outside the 1st BZ?
    for s in range(1,3): #3 è un numero a caso, se l'utente va oltre 3 BZ di distanza è proprio un coglione!
        shift = np.eye(3)*s
        ks_outside_BZ = shift + k_scal
        for k in range(3):
            k_outside_BZ = ks_outside_BZ[k,:]
            if (np.any(np.all(np.isclose(k_outside_BZ-ks_scal_path,0), axis=1))):
                accepted_ks.append(k_outside_BZ)
            
    accepted_ks = np.array(accepted_ks)  
    return accepted_ks

def get_irr_ks(ks, ks_scaled):
    Nks = len(ks)
    permutations = np.array([[[0,1,0],[1,0,0],[0,0,1]], 
                             [[0,0,1],[0,1,0],[1,0,0]], 
                             [[1,0,0],[0,0,1],[0,1,0]],
                             [[0,1,0],[0,0,1],[1,0,0]],
                             [[0,0,1],[1,0,0],[0,1,0]]])
    
    accepted_same_ks_overall, index_irr_ks, weights, permutations_types = np.array([]), [], [], []
    for i in range(Nks):
        if(i in accepted_same_ks_overall.tolist()):
            # print('non irr k') #found non irreducible kpoint
            continue
        this_k = ks[i]
        # print(this_k)
        same_ks_thisk = []
        for j in range(len(permutations)):
            matrix = permutations[j]
            exchanged_rows = np.dot(matrix, ks.T).T
            diff = exchanged_rows-this_k
            w = np.all(np.isclose(diff,0), axis=1)# * 1
            same_ks_index = np.argwhere(w==True).flatten()
            same_ks_thisk.append(same_ks_index.tolist())

        same_ks_thisk = (np.array(same_ks_thisk).flatten())
        # print(same_ks_thisk)
        indexes_without_thisk = np.argwhere(same_ks_thisk != i).flatten()
        same_ks_thisk = same_ks_thisk[indexes_without_thisk]
        permutations_thisk = np.arange(5, dtype=int)[indexes_without_thisk]
        accepted_same_ks_thisk, indexes = np.unique(same_ks_thisk, return_index=True)
        
        # print(accepted_same_ks_thisk)
        accepted_permutations = permutations_thisk[indexes]
        
        
        # print(ks[accepted_same_ks_thisk])
        # print(accepted_permutations)
        # print()
        
        weights.append(1 + len(accepted_same_ks_thisk))
        index_irr_ks.append(i)
        permutations_types.append(accepted_permutations.tolist())
        accepted_same_ks_overall = np.concatenate((accepted_same_ks_overall,accepted_same_ks_thisk))

    
    irr_ks_scal = ks_scaled[index_irr_ks,:]
    irr_ks = ks[index_irr_ks,:]
    
    return irr_ks, irr_ks_scal, np.array(weights), permutations_types


def get_eigvals_eigvec(D):
    eigvals, eigvecs = np.linalg.eigh(D)
    idx = np.argsort(eigvals)
    eigvals, eigvecs = eigvals[idx], eigvecs[:,idx]
    omegas = np.sqrt(eigvals, dtype=complex)/(2*np.pi)
    omegas = omegas.real - omegas.imag
    return eigvals, eigvecs, omegas

def get_eigvals(D):
    eigvals = np.linalg.eigvalsh(D)
    idx = np.argsort(eigvals)
    eigvals = eigvals[idx]
    omegas = np.sqrt(eigvals, dtype=complex)/(2*np.pi)
    omegas = omegas.real - omegas.imag
    return eigvals, omegas
    

def repeat_masses(Masses, n_atom_conventional_cell, n_atom_primitive_cell, N1, N2, N3):
    repeated_masses = np.array([])
    repeated_masses_for_ani = np.array([])
    for i in range(len(Masses)):
        mass = Masses[i]

        n = n_atom_conventional_cell[i]
        nprim = n_atom_primitive_cell[i]
        
        m = np.repeat(mass, N1*N2*N3*3*n)
        m_ani = np.repeat(mass,nprim*3)
        
        repeated_masses = np.concatenate((repeated_masses,m))
        repeated_masses_for_ani = np.concatenate((repeated_masses_for_ani,m_ani))
        
    masses = np.array(repeated_masses).flatten()
    masses_for_animation = np.array(repeated_masses_for_ani).flatten()
    
    return masses, masses_for_animation

def corr(tall,X,Y,tau,mode):
    M = len(tall)
    dt = tall[1] - tall[0]
    tmax = M - tau
    N = np.size(X[0]) 
    X0 = X[0:tmax,:]
    X2 = 1/tmax*np.sum(X[0:tmax,:]*X[0:tmax,:])
    C = []
    for n in range(tau):
        print(n)
        Xjj = Y[n:n+tmax,:]
        a = np.multiply(np.conjugate(X0),Xjj)
        b = 1/(tmax) * np.sum(a,axis=0)#/X2
        if (mode=='projected'):
            c = b
        else:
            c = np.sum(b)
        C.append(c)
    C = np.array(C)
    t = np.arange(0,tau)*dt
    freq = np.fft.fftfreq(tau,d=dt)
    Z = np.fft.fft(C,axis=0)
    return t, C, freq, Z

def lorentzian(x, x0, A, gamma):
    y = 1/np.pi *  A * 1/2*gamma / ((x - x0)**2 + (1/2*gamma)**2)
    return y

def save(filename, data):
    filename2 = filename
    if os.path.isfile(filename):
        n_of_files = len([name for name in os.listdir('.') if (os.path.isfile(name) and 
                                                               (name==filename or name in [filename+'_'+str(n) for n in range(10)] ) )]) #AHAHAHAHAHAHAHAHAHAHAHAH
        filename2 = filename+'_'+str(n_of_files)
        print(filename, ' already present. Saving it as ', filename2)
    np.savetxt(filename2,data) 
    return

def save_quasiparticles(filename, quasiparticle_kpoints, quasiparticle_info):
    filename2 = filename
    if os.path.isfile(filename):
        n_of_files = len([name for name in os.listdir('.') if (os.path.isfile(name) and 
                                                               (name==filename or name in [filename+'_'+str(n) for n in range(10)] ) )]) #AHAHAHAHAHAHAHAHAHAHAHAH
        filename2 = filename+'_'+str(n_of_files)
        print(filename, ' already present. Saving it as ', filename2)
        
    Nqs = len(quasiparticle_kpoints)  
    file = open(filename2,'ab')
    for i in range(Nqs):
        data1 = quasiparticle_kpoints[i].reshape(1,3)
        data2 = quasiparticle_info[i,:,:]
        np.savetxt(file,data1)
        np.savetxt(file,data2)
    file.close()
    return

def save_append(filename, data1, data2):
    filename2 = filename
#    if os.path.isfile(filename):
#        n_of_files = len([name for name in os.listdir('.') if (os.path.isfile(name) and name==filename)])
#        filename2 = filename+'_'+str(n_of_files)
#        print(filename, ' already present. Saving it as ', filename2)
        
    file = open(filename2,'ab')
    np.savetxt(file,data1)
    np.savetxt(file,data2)
    file.close()
    return

def max_freq(dt_ps, tau):
    #you want the max frequency plotted be 25 Thz
    max_freq = 0.5*1/dt_ps
    if (max_freq < 25):
        meta = int(tau/2)
    else:
        meta = int(tau/2*25/max_freq)
    return meta

def fit_to_lorentzian(x_data, y_data, k, n):
    try:
        if(n in [0,1,2] and np.allclose(k, [0,0,0])): #if acoustic modes at Gamma, don't fit anything
                popt, pcov = np.array([0.0001, 0, 0.0001]), np.zeros((3,3))
        else:
            popt, pcov = curve_fit(lorentzian, x_data, y_data)
    except RuntimeError:
        print('\t\tWasnt able to fit to Lorentzian mode '+str(n)+'\n\n')
        x0 = x_data[np.argwhere(y_data==y_data.max())]
        y0 = y_data.max()
        popt, pcov = np.array([x0,y0,0.0001]), np.zeros((3,3))
    perr = np.sqrt(np.diag(pcov))
    return popt, perr

def odd_num_steps(Num_timesteps):
    if((Num_timesteps-1)%2 == 0): 
        Num_steps = Num_timesteps -1
    return Num_steps

def create_Tkt(Num_timesteps, tot_atoms_uc, N1N2N3, Vt, R0, k):
    N = tot_atoms_uc*N1N2N3
    Vcoll = np.zeros((Num_timesteps,tot_atoms_uc*3),dtype=complex)  
    for j,h,l in zip(range(tot_atoms_uc*3),np.repeat(range(0,N),3)*N1N2N3*3,np.tile(range(0,3),tot_atoms_uc)):
        vels = np.array(Vt[:,h+l:h+N1N2N3*3:3],dtype=complex)
        poss = R0[h:h+N1N2N3*3:3,:]
        x = np.multiply(vels,np.exp(-1j*np.dot(poss,k)))
        Vcoll[:,j] = np.sum(x,axis=1)
    Tkt = Vcoll  
    return Tkt


def pair_distr(file_initial_conf, Rt, Nsteps, dr):
    N = len(Rt[0,0::3])
    ang_to_bohr = 1.8897259886
    SCell = np.genfromtxt(file_initial_conf, skip_header=2, max_rows=3)*ang_to_bohr
    A1, A2, A3 = SCell[0,:], SCell[1,:], SCell[2,:]
    V = np.dot(A1, np.cross(A2, A3))
    L = V**(1/3)
#    dr = .01 #[B] 
    r = np.arange(0,L/2,dr)
    Nbins = len(r)-1
    
    HIST = np.zeros(Nbins)
    for t in range(Nsteps):
        print(t)
        hist = np.zeros(Nbins)
        Rx, Ry, Rz = Rt[t,0::3], Rt[t,1::3], Rt[t,2::3]
#        vtx, vty, vtz = Vt[t,0::3],  Vt[t,1::3], Vt[t,2::3]
    #    R0x, R0y, R0z = R0[::3,0], R0[::3,1], R0[::3,2]
    
        Rmatx, Rmaty, Rmatz = np.tile(Rx,(N,1)).T, np.tile(Ry,(N,1)).T, np.tile(Rz,(N,1)).T
        Rijx, Rijy, Rijz = Rmatx - Rx, Rmaty - Ry, Rmatz - Rz
    
    
        for i in range(N):
    #        vi = np.sqrt(vtx[i]**2+vty[i]**2+vtz[i]**2)
            for j in range(N):
    #            vj = np.sqrt(vtx[j]**2+vty[j]**2+vtz[j]**2) 
                if(i==j):
                    continue
                rijx, rijy, rijz = Rijx[i,j], Rijy[i,j], Rijz[i,j]
                rij = np.sqrt(rijx**2+rijy**2+rijz**2)
                BIN = int(rij/dr) 
                if (BIN < Nbins):
                    hist[BIN] = hist[BIN] + 3 #3*vi*vj 
        HIST = HIST + hist
                        
    const = 4/3 * np.pi* N/V  
    g = np.zeros(Nbins)
    for b in range(Nbins):
        rlower = b*dr
        rupper = (b+1)*dr
        nid = const*(rupper**3-rlower**3)
        g[b] = HIST[b]/N/Nsteps/nid
        
    return r[0:-1], g


def get_real_branches(freqs, eigvecs, masses, ks):
    """
    This code finds the phonon bands based on the eigenvectors. 
    It is equivalent to Phonopy's band connection = .true.
    It is quite hard to read, to be honest I think I don't know myself!
    """
    num_ks = len(ks)
    num_branches = len(freqs[:,0])    
        
    new_indexes = range(num_branches) #you have to start from something, you assume the first kpoint is in order
    all_indexes = [new_indexes]
    
    for k in range(0,num_ks-1):
        kpoint = ks[k]
        next_kpoint = ks[k+1]

        this_eigvecs_T = eigvecs[k].T/np.sqrt(masses)
        norm_this_eigvecs = np.linalg.norm(this_eigvecs_T,axis=1)
        this_eigvecs_norm = this_eigvecs_T.T /norm_this_eigvecs
        
        next_eigvecs_T = eigvecs[k+1].T/np.sqrt(masses)
        norm_next_eigvecs = np.linalg.norm(next_eigvecs_T,axis=1)
        next_eigvecs_norm = next_eigvecs_T.T /norm_next_eigvecs
        
        indexes = []
        
        # for l in new_indexes:
        #     print(l)
        #     eig  = this_eigvecs_norm[:,l]
        #     # print(np.round(eig,2))
        #     dot = np.abs(np.dot(next_eigvecs_norm.T, eig))
        #     print(np.round(dot,2))
        #     index = int(np.argwhere(dot == dot.max()))
        #     if (index in indexes): #case of degeneracy
        #         dot[index] = 0
        #         index = int(np.argwhere(dot==dot.max()))
        #     indexes.append(index)
            
        this_eigvecs_reshaped = this_eigvecs_norm[:, new_indexes]
        
        dot = np.abs(np.dot(this_eigvecs_reshaped.conj().T, next_eigvecs_norm)) #* (np.dot(next_eigvecs_norm.T, this_eigvecs_reshaped)).conj()
        for i in range(num_branches):
            row = dot[i,:]
            max_index, max_row = int(np.argwhere(row == max(row))), max(row)
            for j in range(num_branches):
                if(i==j):
                    continue
                this_row = dot[j,:]
                max_index_this_row, max_this_row = int(np.argwhere(this_row == max(this_row))), max(this_row)
                if(max_index_this_row == max_index):
                    if(max_row > max_this_row):
                        dot[j,max_index_this_row] = 0
                    else:
                        dot[i,max_index] = 0
                            

        maxima = np.max(dot, axis=1)
        for l in range(num_branches):
            index = int(np.argwhere(dot[l,:] == maxima[l]))
            indexes.append(index)
            new_indexes = indexes #update new indexes
            
        all_indexes.append(indexes)    

    freqs_sorted = np.copy(freqs)
    for j in range(1,num_ks):
        freqs_sorted[:,j] = freqs[all_indexes[j],j]
    
    return np.array(all_indexes), freqs_sorted


def get_real_branches_old(freqs, eigvecs, masses, ks):
    num_ks = len(ks)
    num_branches = len(freqs[:,0])    
    
    freqs_until_now = freqs[:,0]
    indexes = np.tile(np.arange(num_branches), (2,1))
    new_indexes = np.arange(num_branches)
    
    for k in range(1):#(1,num_ks-1):
        kpoint = ks[k]
        next_kpoint = ks[k+1]
        
        # if(np.allclose(next_kpoint,[0,0,0])):
        #     next_kpoint = [0,0,0]
        # else:
        #     next_kpoint = next_kpoint/np.linalg.norm(next_kpoint)
#        print(k,qpoints_scaled[k], np.round(next_kpoint,2))

        this_eigvecs = eigvecs[k].T/np.sqrt(masses)*10
        next_eigvecs = eigvecs[k+1].T/np.sqrt(masses)*10
        next_eigvecs = next_eigvecs/np.linalg.norm(next_eigvecs, axis=0)

#        print(np.round(next_eigvecs[0::],2))

        temp = new_indexes#np.arange(num_branches)
        for j,l in zip(range(num_branches), new_indexes):
            eig = this_eigvecs[l,:]
            eig = eig/np.linalg.norm(eig)
#            print(l,np.round(eig,2), freqs[l,k])
            dot_prod = np.abs(np.dot(next_eigvecs,eig))
            print(np.round(dot_prod,2))


            new_index = np.argwhere([dot_prod.max()-0.0000000000001 <= dd <= dot_prod.max() for dd in dot_prod])
            degenerate = len(new_index)
#            print(new_index)
            if (len(new_index) > 1):
#                print('two are degenerate')
#                next_eigvecs_deg = next_eigvecs[new_index,:]
#                dot_nexteigvecs_nextk = np.dot(next_eigvecs_deg.reshape(degenerate*2,3), next_kpoint)
#                dot_nexteigvecs_nextk = np.abs(dot_nexteigvecs_nextk.reshape(degenerate,2))
#                dot_nexteigvecs_nextk = dot_nexteigvecs_nextk/np.linalg.norm(dot_nexteigvecs_nextk)
#                dot_thiseig_nextk = np.abs(np.dot(eig.reshape(1*2,3), next_kpoint))
#                dot_thiseig_nextk = dot_thiseig_nextk/np.linalg.norm(dot_thiseig_nextk)
#                diff = np.abs(dot_thiseig_nextk - dot_nexteigvecs_nextk)
#                diff_sum = np.sum(diff, axis=1)
#                print(np.round(dot_nexteigvecs_nextk,2))
#                print(np.round(dot_thiseig_nextk,2))
#                print('diffsum', np.round(diff_sum,2))
                a=0
                if(a==10):#(np.isclose(dot_nexteigvecs_nextk, 1,  rtol=0.2, atol=0.2).any()):
                    #you have a longitudinal branch
                    print('theres a longitudinal')
#                    isclose = np.isclose(dot_nexteigvecs_nextk, dot_thiseig_nextk, rtol=0.2, atol=.2)
#                    true_long = np.all(isclose, axis=1)
#                    arg_long = np.argwhere(true_long)
#                    new_index = new_index[arg_long]
#                    print(new_index)
#                    
                else:
#                    c = np.argwhere(diff_sum==diff_sum.min())
                    new_index = l#new_index[c]
                    print(new_index)

                
                
            if (new_index in temp[0:j]): #it happens at Gamma where TA modes are degenerate
#                print('aaaa')
                new_index = l

            temp[j] = new_index
#            print()
        new_indexes = temp.astype(int)
#        print(new_indexes)
#        print()



        indexes = np.vstack((indexes,new_indexes))
        
    indexes = indexes.astype(int)
#    print(indexes)
    freqs_sorted = []
    for j in range(num_ks):
        freqs_sorted.append(freqs[indexes[j],j])   
        
    return indexes, np.array(freqs_sorted).T


#fig,ax = plt.subplots()
#    
#masses = np.array([24.305 ,  24.305  , 24.305 ,  15.9994 , 15.9994  ,15.9994])
#xd = np.copy(freqs_disp.T)
#s=get_real_branches(xd, eigvecs_phonopy, masses, Hk,  qpoints_scaled)
#print(np.shape(freqs_disp))
#
#kk = np.arange(len(freqs_disp[:,2]))
#for i in range(6):
#    ax.scatter(kk,freqs_disp[:,i], c='black')
##
##ax.plot(np.arange(len(s[0,:])),s[0,:].flatten())
##ax.plot(np.arange(len(s[0,:])),s[1,:].flatten())
##ax.plot(np.arange(len(s[0,:])),s[2,:].flatten())
#
#ax.plot(np.arange(len(s[0,:])),s[3,:].flatten())
#ax.plot(np.arange(len(s[0,:])),s[4,:].flatten())
#ax.plot(np.arange(len(s[0,:])),s[5,:].flatten())
    
def freqs_spectrum(freq,ZQS):
    num_modes = len(ZQS[0,:,0])
    num_ks = len(ZQS[0,0,:])
#    fig,ax = plt.subplots()
    freqs_from_spectrum = np.zeros((num_modes, num_ks))
    for i in range(num_ks):
        for j in range(num_modes):
            phonon = ZQS[:,j,i]
            if (-.001<phonon.max()<.001):
                continue
#            ax.plot(freq, phonon)
            freq_max = freq[np.argwhere(phonon==phonon.max())]
            freqs_from_spectrum[j,i] = freq_max
#    ax.plot(np.arange(2540), ZQS[:,0,1])
#    ax.plot(np.arange(2540), ZQS[:,0,2])
#    ax.plot(np.arange(2540), ZQS[:,0,3])
    return freqs_from_spectrum.T

def find_Gammas(ks_path):
    ks_path = np.array(ks_path)
    num_ks = len(ks_path)
    kk = np.linspace(0,1,num_ks)
    indexes_Gammas = np.argwhere(np.all(np.isclose(ks_path,[0,0,0]), axis=1)).flatten()
    if(indexes_Gammas[-1]==len(kk)):
        indexes_Gammas_withboundaries = indexes_Gammas
    else:
        indexes_Gammas_withboundaries = indexes_Gammas
        indexes_Gammas_withboundaries = np.concatenate((indexes_Gammas_withboundaries,[len(kk)-1]))
    num_Gammas = len(indexes_Gammas)
    return num_Gammas, indexes_Gammas, indexes_Gammas_withboundaries

def gaussian(x,A, B, c):
#    y = 1/(sig*np.sqrt(2*np.pi)) * np.exp(-.5*((x-mi)/sig)**2)
    y = A * np.exp(-B*(x-c)**2) 
    return y

def norm_gaussian(x, mi, sig):
    y = 1/(sig*np.sqrt(2*np.pi)) * np.exp(-.5*((np.subtract.outer(x,mi))/sig)**2)
    return y

def get_Force_Constants(eigvecs, freqs_spectrum, ks, R0):
    num_ks = len(freqs_spectrum[0,:])
    num_modes = len(freqs_spectrum[:,0])
    tot_atoms_uc = int(num_modes/3)
    N = len(R0[:,0])
    N1N2N3 = int(N/tot_atoms_uc)
    Dyna_matrixes = np.zeros((num_modes,num_modes, num_ks))
    K = np.zeros((num_modes,N*3))
    summa = 0
    print(np.shape(ks))
    for k in range(1):
        this_k = ks[k,:]
        this_eig = eigvecs[k]
        lamda = np.diag(freqs_spectrum[:,k])
        D = np.dot(np.dot(this_eig,lamda),this_eig.T)
        Dyna_matrixes[:,:,k] = D
    
    for a in range(tot_atoms_uc):
        R_origin = R0[a*N1N2N3,:]
        for b in range(tot_atoms_uc):
            somma = np.zeros((3,3))
            for k in range(num_ks):
                j = k + N1N2N3*a
                R_next = R0[j,:]
                diffR = R_next - R_origin
                kdotr = np.dot(this_k, diffR)
                D = Dyna_matrixes[:,:,k]
                Da = D[a*3:a*3+3, b*3:b*3+3]
                
                somma = somma + Da*np.exp(1j*kdotr)
  
        
    return

def all_kpoints(N1,N2,N3, Hk):
    N1N2N3 = N1*N2*N3
    #Compute all possible k points
    x1 = np.arange(0,N1)/N1
    x2 = np.arange(0,N2)/N2
    x3 = np.arange(0,N3)/N3
    comb = np.array(np.meshgrid(x1,x2,x3)).T.reshape(-1,3)
    allkpoints_scaled = comb.T
    allkpoints = np.dot(Hk,allkpoints_scaled)
    return allkpoints_scaled.T, allkpoints.T

def get_K_renorm_old(tot_atoms_uc, N1, N2, N3, H, R0, kpoints, Ds):
    """
    old getK_renorm, without exploiting irreducible ks
    """
    N1N2N3 = N1*N2*N3
    N1N2N3_k = len(kpoints)
    N = N1N2N3 * tot_atoms_uc
    R_mat = R_matrix(N1,N2,N3,tot_atoms_uc, R0, H)

    K_renorm = np.zeros((tot_atoms_uc*3, N*3), dtype=complex)
    for i in range(0,tot_atoms_uc*3,3):
        atom_ref_i = int(i/3)
        count = 1
        for j in range(N1N2N3*tot_atoms_uc):
            atom_ref_j = int(j/N1N2N3)
            R = R_mat[i,j*3:j*3+3]
            KR = sum_Dqs_old(R,kpoints,Ds, N1N2N3_k)
            K_renorm[i:i+3,j*3:j*3+3] = KR[i:i+3,atom_ref_j*3:atom_ref_j*3+3]
    return  K_renorm.real/(0.964*10**(4))


def sum_Dqs_old(R,kpoints,Ds, N1N2N3):
    """
    old sum Dqs, without exploiting irr ks
    """
    kpoints2 = -kpoints
    # kpoints = np.vstack((kpoints,kpoints2))
    Ds2 = np.conjugate(Ds[:,:,:])
    # Ds = np.concatenate((Ds, Ds2), axis=0)
    kdotR = np.dot(kpoints,R)

    cs = np.exp(1j*kdotR).reshape(N1N2N3,1,1)


    A = 1/N1N2N3*np.multiply(cs,Ds)
    Kr = np.sum(A, axis=0)
    return Kr

def get_K_renorm(tot_atoms_uc, N1, N2, N3, H, R0, irr_ks, permutations_types, Ds):
    N1N2N3_k = len(Ds[:,0,0])
    N1N2N3 = N1*N2*N3
    N = N1N2N3 * tot_atoms_uc
    R_mat = R_matrix(N1,N2,N3,tot_atoms_uc, R0, H)
    
    K_renorm = np.zeros((tot_atoms_uc*3, N*3), dtype=complex)
    for i in range(0,tot_atoms_uc*3,3):
        atom_ref_i = int(i/3)
        count = 1
        for j in range(N1N2N3*tot_atoms_uc):
            atom_ref_j = int(j/N1N2N3)
            R = R_mat[i,j*3:j*3+3]
            KR = sum_Dqs(R,irr_ks, permutations_types, Ds, N1N2N3)
            K_renorm[i:i+3,j*3:j*3+3] = KR[i:i+3,atom_ref_j*3:atom_ref_j*3+3]
    K_renorm = K_renorm/(0.964*10**(4)) #/0.529177249
    print('Maximum imaginary part of renorm FORCE CONSTANTS:', np.max(K_renorm.imag), '[ev/B]')
    return  K_renorm.real

def sum_Dqs(R,irr_kpoints, permutations_types, Ds, N1N2N3):
    N1N2N3_irr = len(irr_kpoints)
    permutations = np.array([[[0,1,0],[1,0,0],[0,0,1]], 
                             [[0,0,1],[0,1,0],[1,0,0]], 
                             [[1,0,0],[0,0,1],[0,1,0]],
                             [[0,1,0],[0,0,1],[1,0,0]],
                             [[0,0,1],[1,0,0],[0,1,0]]])
    shape_D = np.shape(Ds[0,:,:])
    tot_atoms_uc = int(shape_D[0]/3)
    
# =============================================================================
# irreducible part
    #              this is in case you wanna force it real
    # irr_kpoints2 = -irr_kpoints
    # irr_kpoints_doubled = np.vstack((irr_kpoints,irr_kpoints2))
    # Ds2 = np.conjugate(Ds[:,:,:])
    # Ds = np.concatenate((Ds, Ds2), axis=0)
    
    kdotR = np.dot(irr_kpoints,R)
    cs = np.exp(1j*kdotR).reshape(N1N2N3_irr,1,1)
    A = 1/N1N2N3*np.multiply(cs,Ds)
    Kr_irr = np.sum(A, axis=0)
# =============================================================================

# =============================================================================
# other non irreducible kpoints
    Ds_non_irr, ks_non_irr = [], []
    for i in range(len(irr_kpoints)):
        this_irr_k = irr_kpoints[i]
        D_irr_k = Ds[i]
        this_permutations = permutations_types[i]
        for permut in this_permutations:
            matrix_perm = permutations[permut]
            non_irr_k = np.dot(matrix_perm, this_irr_k)
            ks_non_irr.append(non_irr_k)
            non_irr_D = np.zeros(shape_D, dtype=complex)
            for l in range(tot_atoms_uc):
                for m in range(tot_atoms_uc):
                    D_3by3 = D_irr_k[l*3:l*3+3, m*3:m*3+3]
                    non_irr_D[l*3:l*3+3, m*3:m*3+3] = np.dot(np.dot(matrix_perm, D_3by3), matrix_perm.T)
            Ds_non_irr.append(non_irr_D)   
    Ds_non_irr = np.array(Ds_non_irr)
    ks_non_irr = np.array(ks_non_irr)
    N1N2N3_non_irr = len(ks_non_irr)
    
    #              this is in case you wanna force it real
    # non_irr_kpoints2 = -ks_non_irr
    # non_irr_kpoints = np.vstack((ks_non_irr,non_irr_kpoints2))
    # Ds_non_irr2 = np.conjugate(Ds_non_irr[:,:,:])
    # Ds_non_irr = np.concatenate((Ds_non_irr, Ds_non_irr2), axis=0)
    
    kdotR_non_irr = np.dot(ks_non_irr,R)
    cs_non_irr = np.exp(1j*kdotR_non_irr).reshape(N1N2N3_non_irr,1,1)
    A_non_irr = 1/N1N2N3*np.multiply(cs_non_irr,Ds_non_irr)
    Kr_non_irr = np.sum(A_non_irr, axis=0)
# =============================================================================

    Kr = Kr_irr + Kr_non_irr

    
    return Kr




def get_Ds(N1,N2,N3,Hk, K, R0, masses_uc, tot_atoms_uc, H):
    """
    old, doesn't renormalise
    """
    x,y,z = np.linspace(0,1,N1+1)[0:-1], np.linspace(0,1,N2+1)[0:-1], np.linspace(0,1,N3+1)[0:-1]
    k_scal = np.array(np.meshgrid(x,y,z)).T.reshape(-1,3)
    kpoints = np.dot(Hk,k_scal.T).T
    Ds = []
    for k in kpoints:
        D = get_D(k, K,N1,N2,N3,R0,masses_uc, tot_atoms_uc, H)
        Ds.append(D)
    Ds = np.array(Ds)
    return kpoints, Ds








def get_R_FC(N1o, N2o, N3o, N1,N2,N3,tot_atoms_uc, Suc, SCell):
    N1N2N3 = N1*N2*N3
    N = N1N2N3*tot_atoms_uc
    
    N1N2N3o = N1o*N2o*N3o
    if(N1N2N3 != N1N2N3o):
        conv_factor = np.array([N1o/N1, N2o/N2, N3o/N3])
    else:
        conv_factor=1
    h = SCell/conv_factor
    

    COMB = np.zeros((tot_atoms_uc*N1N2N3,3))
    for atom in range(tot_atoms_uc):
        x0,y0,z0 = Suc[atom,0],Suc[atom,1],Suc[atom,2]
        x,y,z = np.linspace(0,1,N1+1)[0:-1], np.linspace(0,1,N2+1)[0:-1], np.linspace(0,1,N3+1)[0:-1]
        comb = np.array(np.meshgrid(x+x0/N1,y+y0/N2,z+z0/N3)).T.reshape(-1,3)
        COMB[atom*N1N2N3:(atom+1)*N1N2N3,:] = comb
    
    R_FC_normal = np.dot(h, COMB.T).T
    R_FC = np.zeros((tot_atoms_uc*3,N*3))  
    count = 0
    
    for atom in range(tot_atoms_uc):
        r_fc = np.dot(h,COMB.T).T
        x0,y0,z0 = Suc[atom,0],Suc[atom,1],Suc[atom,2]
        atom_origin = np.dot(h,[x0/N1,y0/N2,z0/N3])
        
        row = (r_fc-atom_origin).flatten()
        repeated_row = np.tile(row,(3,1))
        R_FC[count:count+3,:] = repeated_row
        count =  count + 3

    return h, R_FC_normal, R_FC

def get_Scells(H, R0):
    N = len(R0)
    x1 = np.arange(-1,2)
    comb = np.array(np.meshgrid(x1,x1,x1)).T.reshape(-1,3)
    displ = np.dot(H, comb.T).T
    Scells = np.zeros((27, N, 3))
    for c in range(27):
        Scells[c] = R0 + displ[c]     
    return Scells

def R_matrix2(N1,N2,N3,tot_atoms_uc,R0):
    """
    returns the R matrix
    """
    N1N2N3 = N1 * N2 * N3
    N = len(R0[:,0])
    
    R_matrix = np.zeros((tot_atoms_uc*3,N*3))
    count = 0
    for i in range(tot_atoms_uc):
        atom_origin = R0[i*N1N2N3]
        row = (R0[:,:]-atom_origin).flatten()
        repeated_row = np.tile(row,(3,1))
        R_matrix[count:count+3,:] = repeated_row
        count =  count + 3
        
    return R_matrix#*0.529177249

def R_matrix(N1,N2,N3,tot_atoms_uc,R0, H):
    """
    returns the R matrix
    """
    N1N2N3 = N1 * N2 * N3
    N = len(R0[:,0])
    Scells = get_Scells(H, R0)
    
    
    R_matrix = np.zeros((tot_atoms_uc*3,N*3))
    count = 0
    for i in range(tot_atoms_uc):
        atom_origin = R0[i*N1N2N3]
        row = []
        for j in range(N):
            dist_Scells_vec = Scells[:,j,:] - atom_origin
            dist_Scells = np.linalg.norm(dist_Scells_vec, axis=1)
            found_min_dist = np.argwhere(dist_Scells == np.min(dist_Scells, axis=0))
            found_min_dist_0 = found_min_dist[0]
            row.append((Scells[found_min_dist_0,j,:] - atom_origin).flatten())
        row = np.array(row)
        
        repeated_row = np.tile(row.flatten(),(3,1))
        R_matrix[count:count+3,:] = repeated_row
        count =  count + 3
        
    return R_matrix#*0.529177249

def get_D(k, K,N1,N2,N3,R0,masses,tot_atoms_uc, H):
    """
    builds the dynamical matrix
    expects forces in 1/amu * ev / A**2
    returns Thz**2
    """
    N1N2N3 = N1 * N2 * N3
    N = N1N2N3*tot_atoms_uc
    
    R = R_matrix(N1,N2,N3,tot_atoms_uc, R0, H)
    #prepare kdotr
    kdotr = np.zeros((tot_atoms_uc*3,N*3))
    for i in range(tot_atoms_uc*3):
        for j in range(0,N*3,3):
            kdotr[i,j] = np.dot(k,R[i,j:j+3])
            kdotr[i,j+1] = np.dot(k,R[i,j:j+3])
            kdotr[i,j+2] = np.dot(k,R[i,j:j+3])
    
    D = np.zeros((tot_atoms_uc*3,tot_atoms_uc*3),dtype=complex)
    for i in range(tot_atoms_uc*3):
        # for j in range(1):
        for j,h in zip(range(tot_atoms_uc*3),np.repeat(range(0,N),3)):
#            print(i,j,h)
            mass_coeff = complex(1/(masses[i]*masses[j])**(0.5))
            exp = 0*1j
            # h = 0
            for l in range(j+h*3*(N1N2N3-1),j+h*3*(N1N2N3-1)+(N1N2N3)*3,3):
                # print(i,l,np.round(np.exp(1j*kdotr[i,l]),2),K[i,l])
                exp = exp + K[i,l]*np.exp(1j*kdotr[i,l])
#            print()
            D[i,j] = mass_coeff*exp
    return (D+D.conj().transpose())/2*0.964*10**(4)#, np.exp(1j*kdotr)#, R



def voigt_eq(n, k, freq, Z, sig):
    if(n in [0,1,2] and np.allclose(k, [0,0,0])): #if acoustic modes at Gamma, don't fit anything
        popt, pcov = np.array([0, 0, 0]), np.zeros((3,3))
        return popt[0], popt[-1]
    
    mi = freq[int(len(freq)/2)]
    gaussian = norm_gaussian(freq, mi, sig)                
    convolution = signal.fftconvolve(Z,gaussian, mode='same') / sum( gaussian)
    
    
    f_max = int(np.argwhere(convolution==convolution.max()))
    conv_sx, conv_dx = convolution[0:f_max], convolution[f_max::]
    if(len(np.argwhere(conv_sx < convolution.max()/2)) > 0):
        sx, dx = np.argwhere(conv_sx < convolution.max()/2)[-1], np.argwhere(conv_dx < convolution.max()/2)[0] + f_max
        fv = (freq[dx] - freq[sx])[0]
    else:
        dx = np.argwhere(conv_dx < convolution.max()/2)[0] + f_max
        fv = freq[dx][0]*2
    fg = 2*sig*np.sqrt(2*np.log(2))
    a, b, c = 0.0692, -1.0692*fv, -fg**2+fv**2
    fl = (-b/2-np.sqrt((b/2)**2-a*c))/a 
#   www = (-fv**2+fg**2)/(-fv)
    return freq[f_max], fl






def all_freqs(N1,N2,N3, Hk, Num_timesteps, tot_atoms_uc, Vt):
    N1N2N3 = N1*N2*N3
    meta = int(len(freq)/2)
    freq_meta = freq[0:meta]
    #Compute all possible k points
    x1 = np.arange(0,N1+1)/N1
    x2 = np.arange(0,N2+1)/N2
    x3 = np.arange(0,N3+1)/N3
    comb = np.array(np.meshgrid(x1,x2,x3)).T.reshape(-1,3)
    #a1 = np.multiply(comb,b1)
    #a2 = np.multiply(comb,b2)
    #a3 = np.multiply(comb,b3)
    #kpoints = a1+a2+a3
    allkpoints_scaled = comb.T
    allkpoints = np.dot(Hk,allkpoints_scaled)
    
    import matplotlib.pyplot as plt
    from scipy import signal
    for k in range(1,2):
        fig,ax = plt.subplots()
        #Creating the collective variable based on the k point
        kpoint = allkpoints[:,k]
        Tkt = create_Tkt(Num_timesteps-1, tot_atoms_uc, N1N2N3, Vt, R0, kpoint)
        Tkw = np.fft.fft(Tkt, axis=0)
        Sq = (np.sum(np.conjugate(Tkw)*Tkw, axis=1)).real*cev/(kbev*T)/Num_timesteps*dt_ps
        sig, mi = .1/2, freq[int(meta/2)]
        gaussian = 1/(sig*np.sqrt(2*np.pi)) * np.exp(-.5*((freq_meta-mi)/sig)**2)
        convolution = signal.fftconvolve(Sq[0:meta],gaussian, mode='same') / sum( gaussian)
        print(convolution)
        ax.plot(freq_meta,Sq[0:meta], freq_meta, convolution)
        area_q = np.trapz(Sq, freq[0:meta])
        print('\t DOS for this kpoint: ', area_q)
    return allkpoints_scaled

#SSS= all_freqs(10,10,10, Hk, Num_timesteps, tot_atoms_uc, Vt)
#R = R0[0::3,:]
#get_Force_Constants(eigvecs_phonopy, freqs_from_spectrum.T, ks, R)

def get_nac_params(BORN_file, SCell, N1, N2, N3, tot_atoms_uc):
    eps_inf, BORN = np.genfromtxt(BORN_file, skip_header=1, max_rows=1).reshape(3,3), np.genfromtxt(BORN_file, skip_header=2, max_rows=tot_atoms_uc).reshape(tot_atoms_uc*3,3)
    a1, a2, a3 = SCell[0]/N1, SCell[1]/N2, SCell[2]/N3
    Vuc = np.dot(a1, np.cross(a2,a3))
    return eps_inf, BORN, Vuc

def get_nac_C(kpoint,Vuc, BORN, eps_inf, masses, N1N2N3):
    const = 11.78*1e+06/(2*np.pi) #3.4191*1e+02 #1.18*1e+07
    constevA2 = 1.222*1e+03 / (2*np.pi)
    num = np.outer(np.dot(kpoint,BORN.T) , np.dot(BORN,kpoint))
    den = np.dot(kpoint.T,np.dot(eps_inf,kpoint))
    Mij = np.sqrt(np.outer(masses,masses))
    Cna = 4*np.pi/Vuc * num/den *constevA2 /N1N2N3 
    return Cna

def get_K_corr(K, C_nac):
    K2 = np.copy(K)
    dofs = len(C_nac)
    tot_atoms_uc = int(dofs/3)
    N1N2N3 = int(len(K[0,:])/tot_atoms_uc/3)
    for i in range(tot_atoms_uc):
        this_Cnac = C_nac[:,i*3:i*3+3]
        A = np.tile(this_Cnac,N1N2N3)
        K2[:,i*N1N2N3*3:(i+1)*N1N2N3*3] += A
    return K2







def interpol_spectrum(ks_path, freq, freqs_from_spectrum, kk, kk_many, frequencies, eigvecs, modes, ZQS):
    num_ks = len(ks_path)
    num_modes = len(freqs_from_spectrum[0,:])
    num_freqs = len(ZQS[:,0,0])
    df = freq[1] - freq[0]

    
    ZQS_interp = np.zeros((num_freqs,num_modes, len(kk_many)))
    
    
    ktot = 0
    for k in range(num_ks-1):
        count_k_in_between = 0
        for j in range(num_modes):  
            this_gaussian = ZQS[:,j,k]
            next_gaussian = ZQS[:,j,k+1]
            
            # import matplotlib.pyplot as plt
            # fig,ax = plt.subplots()
#            #to comment
#            popt_this, pcov_this = curve_fit(gaussian, freq, this_gaussian)
#            popt_next, pcov_next = curve_fit(gaussian, freq, next_gaussian)
            
            this_max = freqs_from_spectrum[k,j]
            next_max = freqs_from_spectrum[k+1,j]
            diff_maxima = next_max - this_max
            
            if(diff_maxima >= 0):
                this_gaussian_interp = interp1d(freq, this_gaussian, bounds_error=False, fill_value=0)
                next_gaussian_interp = interp1d(freq, next_gaussian, bounds_error=False, fill_value=0)
                this_gaussian_fit = this_gaussian_interp(freq-diff_maxima)
                next_gaussian_fit = next_gaussian_interp(freq)
                shift_interp = -next_max
            else:
                this_gaussian_interp = interp1d(freq, this_gaussian, bounds_error=False, fill_value=0)
                next_gaussian_interp = interp1d(freq, next_gaussian, bounds_error=False, fill_value=0)
                this_gaussian_fit = this_gaussian_interp(freq)
                next_gaussian_fit = next_gaussian_interp(freq+diff_maxima)
                shift_interp = -this_max
            
#            area_this_gaussian = np.trapz(this_gaussian_fit, freq)
#            area_next_gaussian = np.trapz(next_gaussian_fit, freq)

            this_k = kk[k]
            next_k = kk[k+1]
            indexes_sx, indexes_dx = np.argwhere(this_k<=kk_many).flatten(), np.argwhere(kk_many<next_k).flatten()
            indexes = np.intersect1d(indexes_sx, indexes_dx)
            interm_k = kk_many[indexes]

            # interp = INTERP[sector+j*num_Gammas]
            intermediate_maxima = frequencies[j,indexes]
            count_k_in_between = 0
            for m in range(len(interm_k)):
                mi = intermediate_maxima[m]
                x = (interm_k[m] - interm_k[0])/(next_k-interm_k[0])
#                area_factor = area_this_gaussian+(area_next_gaussian-area_this_gaussian)*x
                interp_gaussian = this_gaussian_fit+(next_gaussian_fit-this_gaussian_fit)*x
                interp_gaussian_interp = interp1d(freq, interp_gaussian,bounds_error=False, fill_value=0)
                
                interp_gaussian_fit = interp_gaussian_interp(freq-(shift_interp+mi))
                ZQS_interp[:,j,ktot+count_k_in_between] = interp_gaussian_fit
                count_k_in_between = count_k_in_between + 1
                

#                popt = popt_this + (popt_next-popt_this)*x
#                interp_gaussian_fit = gaussian(freq, *popt)#1/(sig*np.sqrt(2*np.pi)) * np.exp(-.5*((freq-mi)/sig)**2) *area_factor

#                 ax.plot(freq, interp_gaussian_fit, label='interp')
#             ax.plot(freq, this_gaussian, label='real this')
#             ax.plot(freq,next_gaussian, label='real next')
# #            ax.plot(freq, this_gaussian_fit, label='real this fit')
# #            ax.plot(freq,next_gaussian_fit, label='real next fit')
#             ax.legend()
            
        ktot = ktot + count_k_in_between
    ZQS_interp[:,:,-1] = ZQS[:,:,-1]
    return ZQS_interp







