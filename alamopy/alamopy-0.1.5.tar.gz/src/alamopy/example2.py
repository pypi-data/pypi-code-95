'''
Simple example to see if we can generate model for y = x**2 + z**2 + 1
'''
import numpy as np
from alamopy.almain import doalamo

xdata = np.random.rand(100, 3)
xdata[:, 0] *= 10  # Make x1 go from 0 to 10
xdata[:, 1] *= 5   # Make x2 go from 0 to 5

zdata = xdata[:, 0]**2 + xdata[:, 1]**2

def print_alamo():
    opts = doalamo(xdata, zdata, noutput=1, keep_alm_file=True, keep_lst_file=True,
               print_alm_output=True, monomialpower=[2, 3], crncustom=1,
               zlabels=["z"],
               customcon=["1 -z"])
    print(opts)

print_alamo()