#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 14:12:07 2019

@author: gc4217
"""
import numpy as np
import os, sys

def avg_vs_t(time,quantity):
    avg = []
    for i in range(1,len(time)):
        dt = time[i]-time[i-1]
        y = quantity[0:i]
        integral = np.sum(dt*y,axis=0)
        avg.append(1/(i*dt)*integral)
    avg = np.array(avg)
    return avg


N1, N2, N3 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
n_uc = int(sys.argv[4])
N1N2N3 = N1*N2*N3
N = N1*N2*N3*n_uc
DT = float(sys.argv[5])
flag  = sys.argv[6]

if(flag=='ASAP' or flag=='asap'):
    print('Hello, Im now converting the ASAP output files...\n')
    
    with open('Cartesian_0','r') as f:
        A = f.readlines()
    a = 0
    for i in range(0,len(A),N+1):
        del A[i-a]
        a = a + 1
        
    with open('pos','w') as g:
        g.writelines(A)
        
    Rall = np.loadtxt('pos',usecols=(1,2,3))
    
    Num_timesteps = int(len(Rall)/N)
    t = np.arange(Num_timesteps-1)*DT*2.418884254*1e-05 #conversion to picoseconds
    dt_ps = t[1]-t[0]
    
    Rt = []
    for i in range(0,len(Rall),N):
        if(i==N):
            continue
        #pos_first_Ba = Rall[i:i+1,:]
        #pos_cm = np.sum(Rall[i:i+N,:],axis=0)/N
        
        to_write = Rall[i:i+N:1] #- pos_cm
        Rt.append(to_write.flatten())
        
    Rt = np.array(Rt)
    #Vt = np.gradient(Rt,dt_ps,axis=0)  
    Vt = np.diff(Rt,axis=0)/dt_ps
    
    data_pos = np.hstack((t.reshape(len(t),1),Rt))
    runn_avg = avg_vs_t(t,Rt)
    data_avg = np.hstack((t[1::].reshape(len(t[1::]),1),runn_avg))
    
    np.savetxt('runn_avg_pos',data_avg)
    np.savetxt('data_pos',data_pos)
    
    
    data_vel = np.hstack((t[0:-1].reshape(len(t[0:-1]),1),Vt))
    runn_avg = avg_vs_t(t,Vt)
    data_avg = np.hstack((t[0:-1].reshape(len(t[0:-1]),1),runn_avg))
    
    np.savetxt('runn_avg_vel',data_avg)
    #np.savetxt('data_vel',data_vel)
    
    
    os.remove('pos')
    
    print('Finished. data_pos, data_vel, runn_avg_pos and runn_avg_vel created.\n\n')
    print('Please copy the file data_pos to your phonon DOS folder!')


if(flag=='QE' or flag=='qe'):
    name = sys.argv[6]
    
    print('Hello, Im now converting the QE output files...\n')
    
    with open(name+'.pos','r') as f:
        A = f.readlines()
    a = 0
    for i in range(0,len(A),N+1):
        del A[i-a]
        a = a + 1
        
    with open('pos','w') as g:
        g.writelines(A)
        
    Rall = np.loadtxt('pos')
    
    Num_timesteps = int(len(Rall)/N)
    t = np.arange(Num_timesteps-1)*DT*2.418884254*1e-05 #conversion to picoseconds
    
    R = []
    for i in range(0,len(Rall),N):
        if(i==N):
            continue
        #pos_first_Ba = Rall[i:i+1,:]
        #pos_cm = np.sum(Rall[i:i+N,:],axis=0)/N
        
        to_write = Rall[i:i+N:1] #- pos_cm
        R.append(to_write.flatten())
        
    R = np.array(R)
    
    data_pos = np.hstack((t.reshape(len(t),1),R))
    
    runn_avg = avg_vs_t(t,R)
    data_avg = np.hstack((t[1::].reshape(len(t[1::]),1),runn_avg))
    
    np.savetxt('runn_avg_pos',data_avg)
    np.savetxt('data_pos',data_pos)
    
    with open(name+'.vel','r') as f:
        A = f.readlines()
    a = 0
    for i in range(0,len(A),N+1):
        del A[i-a]
        a = a + 1
        
    with open('vel','w') as g:
        g.writelines(A)
        
    Vall = np.loadtxt('vel')
    
    Num_timesteps = int(len(Vall)/N)
    t = np.arange(Num_timesteps-1)*DT*2.418884254*1e-05 #conversion to picoseconds
    
    V = []
    for i in range(0,len(Vall),N):
        if(i==N):
            continue
        #pos_first_Ba = Rall[i:i+1,:]
        #pos_cm = np.sum(Rall[i:i+N,:],axis=0)/N
        
        to_write = Vall[i:i+N:1] #- pos_cm
        V.append(to_write.flatten())
        
    V = np.array(V)
    
    data_vel = np.hstack((t.reshape(len(t),1),V))
    
    runn_avg = avg_vs_t(t,V)
    data_avg = np.hstack((t[1::].reshape(len(t[1::]),1),runn_avg))
    
    np.savetxt('runn_avg_vel',data_avg)
    np.savetxt('data_vel',data_vel)
    
    
    os.remove('vel')
    
    
    
    print('Finished. data_pos, data_vel, runn_avg_pos and runn_avg_vel created.\n\n')
    print('Please copy the file data_pos to your phonon DOS folder!')


if(flag=='ASAP_pol' or flag=='asap_pol'):
    print('Hello, Im now converting the ASAP output files...\n')
    
    with open('Pol','r') as f:
        A = f.readlines()
    Num_timesteps = int(len(A)/(N1*N2*N3*n_uc+3))
    
    
    dipoles = np.zeros((Num_timesteps,n_uc*N1*N2*N3*3))
    for i in range(Num_timesteps):
        print(i)
        to_skip = i*(2+N1*N2*N3*n_uc+1)
        A = np.genfromtxt('Pol', skip_header=2+to_skip, max_rows=N1*N2*N3*n_uc)
        for j in range(n_uc):
            this_atom = int(A[j*N1N2N3,0]-1)
            dip_here = A[this_atom*N1*N2*N3:(this_atom+1)*N1*N2*N3,1:]
            dipoles[i,this_atom*N1*N2*N3*3:(this_atom+1)*N1*N2*N3*3] = dip_here.flatten()
    
    t = np.arange(Num_timesteps)*DT*2.418884254*1e-05 #conversion to picoseconds
    dt_ps = t[1]-t[0]
    
    
    data_dipoles = np.hstack((t.reshape(len(t),1),dipoles))
    runn_avg = avg_vs_t(t,dipoles)
    data_avg = np.hstack((t[1::].reshape(len(t[1::]),1),runn_avg))
    
    np.savetxt('runn_avg_dipoles',data_avg)
    np.savetxt('data_dipoles',data_dipoles)
    
    
    
    print('Finished. data_dipoles and runn_avg_dipoles created.\n\n')
    print('Please copy the file data_dipoles to your phonon DOS folder!')



















