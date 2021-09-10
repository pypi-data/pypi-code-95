#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 18:35:54 2018

@author: Gabriele Coiana
"""
import numpy as np


def getk_fcc(a,N1,N2,N3,kinput_scaled):
    # =============================================================================
    #   Brilloin zone for FCC
    c = 2*np.pi/a
    b1 = c*np.array([-1,1,1])#/np.sqrt(3)
    b2 = c*np.array([1,-1,1])#/np.sqrt(3)
    b3 = c*np.array([1,1,-1])#/np.sqrt(3)
    b = np.linalg.norm(b1)
    kinput_real = np.array(kinput_scaled)*b
    #Compute all possible k points
    x1 = np.arange(0,N1+1)/N1
    x2 = np.arange(0,N2+1)/N2
    x3 = np.arange(0,N3+1)/N3
    comb = np.array(np.meshgrid(x1,x2,x3)).T.reshape(-1,3)
    #a1 = np.multiply(comb,b1)
    #a2 = np.multiply(comb,b2)
    #a3 = np.multiply(comb,b3)
    #kpoints = a1+a2+a3
    allkpoints_scaled = comb
    allkpoints = comb*b
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
                    kdef = np.insert(kdef,count,kpoint*b,axis=0)
                    kdef_scaled = np.insert(kdef_scaled,count,kpoint,axis=0)
                    count = count+1 
        else:
            for kpoint in allkpoints_scaled_no[::-1]:
                diff = kinput_scaled[index]-kpoint
                mod = np.linalg.norm(diff)
                actual_direction = diff/mod
                if(np.array_equal(np.round(actual_direction,9),np.round(direction,9)) and all(np.abs(diff)<=np.abs(kinput_scaled[index+1]-kinput_scaled[index]))):
                    kdef = np.insert(kdef,count,kpoint*b,axis=0)
                    kdef_scaled = np.insert(kdef_scaled,count,kpoint,axis=0)
                    count = count+1 
            
    # =============================================================================
    
    # =============================================================================
    #  fake k points only for plotting, projection
    directionsdef_scaled = []
    for i in range(0,len(kdef_scaled)-1):
        directionsdef_scaled.append((kdef_scaled[i]-kdef_scaled[i+1]))
    kk = np.zeros(len(kdef_scaled))
    for i in range(1,len(kk)):
        kk[i] = kk[i-1]+(np.linalg.norm(directionsdef_scaled[i-1]))
    # =============================================================================
           
    return kdef, kdef_scaled, kk


def getk(file_UPOSCAR, N1,N2,N3,kinput_scaled):
    # =============================================================================
    #   Brilloin zone 
    A = np.genfromtxt(file_UPOSCAR,skip_header=2, skip_footer=8)
    to_bohr = 0.5291772108 
    a1,a2,a3 = A[0]*to_bohr/N1,A[1]*to_bohr/N2,A[2]*to_bohr/N3
    c = 2*np.pi
    
    V = np.dot(a1,np.cross(a2,a3))
    b1 = c*np.cross(a2,a3)/V
    b2 = c*np.cross(a3,a1)/V
    b3 = c*np.cross(a1,a2)/V
    h = np.vstack((b1,b2,b3))
    
    b1_mod = np.linalg.norm(b1)
    b2_mod = np.linalg.norm(b2)
    b3_mod = np.linalg.norm(b3)
    b_mod = [b1_mod,b2_mod,b3_mod]
    kinput_real = np.multiply(b_mod,np.array(kinput_scaled))
    #Compute all possible k points
    x1 = np.arange(0,N1+1)/N1
    x2 = np.arange(0,N2+1)/N2
    x3 = np.arange(0,N3+1)/N3
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
                    count = count+1 
        else:
            for kpoint in allkpoints_scaled_no[::-1]:
                diff = kinput_scaled[index]-kpoint
                mod = np.linalg.norm(diff)
                actual_direction = diff/mod
                if(np.array_equal(np.round(actual_direction,9),np.round(direction,9)) and all(np.abs(diff)<=np.abs(kinput_scaled[index+1]-kinput_scaled[index]))):
#                    kdef = np.insert(kdef,count,np.dot(h,kpoint),axis=0)
                    kdef_scaled = np.insert(kdef_scaled,count,kpoint,axis=0)
                    count = count+1 
            
    # =============================================================================
    
    # =============================================================================
    #  fake k points only for plotting, projection
    directionsdef_scaled = []
    for i in range(0,len(kdef_scaled)-1):
        directionsdef_scaled.append((kdef_scaled[i]-kdef_scaled[i+1]))
    kk = np.zeros(len(kdef_scaled))
    for i in range(1,len(kk)):
        kk[i] = kk[i-1]+(np.linalg.norm(directionsdef_scaled[i-1]))
    # =============================================================================
    
    kdef = np.dot(h,kdef_scaled.T).T
    return kdef, kdef_scaled, kk

## =============================================================================
## Parameters
#a = params.get_parameters()[0]
#mba, mti, mo = params.get_parameters()[1:4]
#N1,N2,N3 = params.get_parameters()[4:7]
#kinput = params.get_parameters()[7::][0]
#interp = params.get_parameters()[8]
#savefreq = params.get_parameters()[9]
#
#N1N2N3 = N1*N2*N3 # Number of cells
#N = N1*N2*N3*5    # Number of atoms
## =============================================================================
#a1 = np.array([0,1,1])*a/2
#a2 = np.array([1,0,1])*a/2
#a3 = np.array([1,1,0])*a/2
#kdef, kdef_scaled, kk = getk(a1,a2,a3,N1,N2,N3,kinput)
#kdef_fcc, kdef_fcc_scaled, kk_fcc = getk_fcc(a,N1,N2,N3,kinput)
