from __future__ import print_function
try:
    get_ipython().magic('matplotlib inline # can also use notebook or nbagg')
except:
    pass
from phase_stepper import PhaseStepper
from ufl_phasefield import UflPhasefield

from IPython.display import clear_output

import dune.fem as fem
#class for testing auto diff of nu argument
import pdb

from ufl import as_vector, atan, atan_2, conditional, dot, grad, pi, inner, sqrt, SpatialCoordinate, sqrt, tan


class SharpCrystal():
    # surface tension and mobility
    surfaceTension = 1
    mobility = 24

    omega = ([4, 4], [8, 8], [3, 3])
    endTime = 0.05

    def initial(x):
        r = sqrt( dot( x-as_vector([6,6]), x-as_vector([6,6])) )
        return  [conditional(r>0.3, 0, 1), -0.5]

    def gamma(nu):
        kappa1 = 0.9
        kappa2 = 20.
        c = 0.02
        N = 6.
        psi = pi/8.0 + atan_2(nu[1], nu[0])
        Phi = tan(N / 2.0 * psi)
        beta = (1.0 - Phi*Phi) / (1.0 + Phi*Phi)
        dbeta_dPhi = -2.0 * N * Phi / (1.0 + Phi * Phi)
        fac = 1.0 + c * beta
        # extension to make 1 homogeneous
        ext = sqrt(inner(nu,nu))
        #return [[0, fac*ext], [fac*ext, 0]]
        return [[0, fac], [fac, 0]]

    def a(u, un):
        kappa1 = 0.9
        kappa2 = 20
        gamma = kappa1/pi
        return [0,200 * gamma * atan(kappa2* u[0])]

    def distE(u):
        #here K is the latent heat at the interface
        return [[u[0]-1, u[0]]]

    def distQ(u):
        Td = 2.25
        return [[-Td*grad(u[0]), -Td*grad(u[0])]]

    def distF(u, un):
        return [[0, 0]]

