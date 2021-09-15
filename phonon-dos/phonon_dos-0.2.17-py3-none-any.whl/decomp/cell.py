#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 25 12:00:17 2018

@author: Gabriele Coiana
"""
import numpy as np


class BaTiO3:
    def __init__(self,a):
        self.a = a
        self.mBa = 250331.80714328878 #[atomic units]
        self.mTi = 87256.20316855246 #[atomic units]
        self.mO = 29164.392890585812#[atomic units]
        return
        
    def phaseI(self):
        #self.Ti = np.array(np.meshgrid(np.arange(0.5,0.5+self.N1*self.a,self.a), np.arange(0.5,0.5+self.N2*self.a,self.a), np.arange(0.5,0.5+self.N3*self.a,self.a)))
        self.Ti = self.a*np.array([[0.5,0.5,0.5]])
        self.O = self.a*np.array([[0.5,0.5,0], [0.5,0,0.5], [0,0.5,0.5]])
        self.Ba = self.a*np.array([[0,0,0]])
        return
    
    def supercell(self, N1, N2, N3):
        self.N1, self.N2, self.N3 = N1, N2, N3
        xx,yy,zz = np.meshgrid(np.arange(0.5*self.a,0.5+self.N1*self.a,self.a), np.arange(0.5*self.a,0.5+self.N2*self.a,self.a), np.arange(0.5*self.a,0.5+self.N3*self.a,self.a))
        xx, yy, zz = xx.reshape(1,N1*N2*N3)[0], yy.reshape(1,N1*N2*N3)[0], zz.reshape(1,N1*N2*N3)[0]
        self.Ti = np.dstack((zz,xx,yy))[0]
        
        xx,yy,zz = np.meshgrid(np.arange(0.0,0.0+self.N1*self.a,self.a), np.arange(0.0,0.0+self.N2*self.a,self.a), np.arange(0.0,0.0+self.N3*self.a,self.a))
        xx, yy, zz = xx.reshape(1,N1*N2*N3)[0], yy.reshape(1,N1*N2*N3)[0], zz.reshape(1,N1*N2*N3)[0]
        self.Ba = np.dstack((zz,xx,yy))[0]
        
        xx,yy,zz = np.meshgrid(np.arange(0.5*self.a,0.5+self.N1*self.a,self.a), np.arange(0.5*self.a,0.5+self.N2*self.a,self.a), np.arange(0.0,0.0+self.N3*self.a,self.a))
        xx, yy, zz = xx.reshape(1,N1*N2*N3)[0], yy.reshape(1,N1*N2*N3)[0], zz.reshape(1,N1*N2*N3)[0]
        self.O3 = np.dstack((zz,xx,yy))[0]
        
        xx,yy,zz = np.meshgrid(np.arange(0.5*self.a,0.5+self.N1*self.a,self.a), np.arange(0.0,0.0+self.N2*self.a,self.a), np.arange(0.5*self.a,0.5+self.N3*self.a,self.a))
        xx, yy, zz = xx.reshape(1,N1*N2*N3)[0], yy.reshape(1,N1*N2*N3)[0], zz.reshape(1,N1*N2*N3)[0]
        self.O1 = np.dstack((zz,xx,yy))[0]
        
        xx,yy,zz = np.meshgrid(np.arange(0.0,0.0+self.N1*self.a,self.a), np.arange(0.5*self.a,0.5+self.N2*self.a,self.a), np.arange(0.5*self.a,0.5+self.N3*self.a,self.a))
        xx, yy, zz = xx.reshape(1,N1*N2*N3)[0], yy.reshape(1,N1*N2*N3)[0], zz.reshape(1,N1*N2*N3)[0]
        self.O2 = np.dstack((zz,xx,yy))[0]
        return 
    
    def get_supercell(self, a, N1, N2, N3):
        bati = BaTiO3(a)
        bati.supercell(N1,N2,N3)
        Rba,Rti,Ro1,Ro2,Ro3 = bati.Ba,bati.Ti,bati.O1,bati.O2,bati.O3
        R = np.vstack((Rba,Rti,Ro1,Ro2,Ro3))
        R = np.repeat(R,3,axis=0)
        return R
        



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
#bati = BaTiO3(4)
#bati.supercell(2,2,2)
#print(bati.O3)



#Kr, a, epsilon, sigma, m = 15.18, 7.551345593761988, 0.00485678, 4.5, 1451.0
#const = (Kr, a, epsilon, sigma)
#R0 = np.concatenate((bati.Ba, bati.Ti, bati.O1, bati.O2, bati.O3))
#dt, nSteps, T0, gamma, N = 1, 20, 300, 0.0, 5*8

#Rtot, Vtot, Utot, Ktot, Etot, R2tot  = moleculardynamics.langevin(R0, dt, nSteps, T0, m, gamma, N, *const)

#plot.plot(bati)
