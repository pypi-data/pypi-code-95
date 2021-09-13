import numpy as np
import math
from numpy import linalg as LG


pi = math.pi

# Our general class will read a Current file and a Voltages file to output a Dirichlet to Neumann map.
# Variables: 
# r - radius of body (assumed symmetrical for now) 
# AE -  area of the electrodes
# L - Number of Electrodes
class read_data:

    # The Current and Voltage file should be in the format: L-1 lines with values for the L electrodes.
    def __init__(self, Current, Voltage, r, AE, L):
        self.L = L
        self.r = r
        self.AE = AE
        self.Current = Current.transpose() # Matrix L x L-1
        self.Voltage = Voltage.transpose() # Matrix L x L-1
        self.DNmap = np.zeros((L-1, L-1))
        self.load()
        
    def load(self):
        S=0
        for n in range(self.L-1):
            S = np.sum(self.Voltage[:, n])
            self.Voltage[:, n] = (self.Voltage[:, n]-np.ones(self.L)*S/self.L)/LG.norm(self.Current[:, n], 2)
            self.Current[:, n] = self.Current[:, n]/LG.norm(self.Current[:, n], 2)
            
        for n in range(self.L-1):
            for m in range(self.L-1):
                C = self.Current[:, n]
                V = self.Voltage[:, m]
                self.DNmap[n, m] = np.inner(C, V)
                
        self.DNmap = (self.AE/self.r)*LG.inv(self.DNmap)
        
