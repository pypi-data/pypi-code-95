"""
Well and smoothstep classes for definitions of potential wells and interpolation
"""
import math
import ufl
import numpy as np

def Obstacle(phaseModel, phi, phiK):
    gamma = phaseModel.sharpCls.gamma

    if phaseModel.inspectDict['numPhases'] == 1:
        return (1/2)*(gamma(ufl.grad(phi[0]))[0][0])*(1-phi[0])*(1-phi[0])
    else:
        return gamma(ufl.grad(phi[0]))[0][1]*(16/(math.pi*math.pi))*phi[0]*(1-phi[0])

def Implicit(phaseModel, phi, phiK):
    """
    If the energy is isoptric multiply the well by that number if it is anisotropic don't do anything
    """
    assert phaseModel.inspectDict['numPhases'] > 1

    if phaseModel.inspectDict['isotropic'] == True:
        gamma = phaseModel.sharpCls.gamma
        return 9*gamma(ufl.grad(phi[0]))[0][1]*phi[0]*phi[0]*(1-phi[0])*(1.0-phi[0])
    else:
        return 9*phi[0]*phi[0]*(1-phi[0])*(1.0-phi[0])

def Default(phaseModel, phi, phiK):
    """
    If the energy is isoptric multiply the well by that number if it is anisotropic
    don't do anything
    """
    if phaseModel.inspectDict['numPhases'] == 1:
        return Obstacle(phaseModel,phi,phiK)
    else:
        return Implicit(phaseModel,phi,phiK)

def ConcaveConvex(phaseModel, phi, phiK):
    gamma = phaseModel.sharpCls.gamma

    return 9*gamma(ufl.grad(phi[0]))[0][1] * ((phi[0]-0.5)*(phi[0]-0.5)*(phi[0]-0.5)*(phi[0]-0.5)-0.5*phiK[0]*(phiK[0]-1))

def Implicit3p(phaseModel, phi, phiK):
    def f(x):
        return x*x*(1-x)*(1-x)

    return 9/2*(phaseModel.surfaceVec()[0]*f(phi[0])+ phaseModel.surfaceVec()[1]*f(phi[1])+ phaseModel.surfaceVec()[2]*f(phi[2]))

def ConcaveConvex3p(phaseModel, phi, phiK):
    def fplus(x):
        return (x-0.5)*(x-0.5)*(x-0.5)*(x-0.5)

    def fminus(x):
        return (1/16)*(1-2*(2*x-1)*(2*x-1))

    sigmaPlus = np.maximum(phaseModel.surfaceVec(), np.zeros(3))
    sigmaMinus = -np.minimum(phaseModel.surfaceVec(), np.zeros(3))

    convex = 0.5*(sigmaPlus[0]*fplus(phi[0]) + sigmaPlus[1]*fplus(phi[1]) +
                  sigmaPlus[2]*fplus(phi[2]) - sigmaMinus[0]*fminus(phi[0]) -
                  sigmaMinus[1]*fminus(phi[1]) - sigmaMinus[1]*fminus(phi[1]))

    concave = 0.5*(sigmaPlus[0]*fminus(phiK[0]) + sigmaPlus[1]*fminus(phiK[1]) +
                   sigmaPlus[2]*fminus(phiK[2]) - sigmaMinus[0]*fplus(phiK[0]) -
                   sigmaMinus[1]*fplus(phiK[1]) - sigmaMinus[1]*fplus(phiK[1]))

    return 9*(convex+concave)

def SmoothStep(phi, phiK, a):
    """
    Given two arguments which are ufl forms returns a ufl form which is the
    derivative of the function with respect to phi
    this is smoothstep interpolation
    https://en.wikipedia.org/wiki/Smoothstep
    f(x,a) = a + (b-a)*(3*x**2 - 2*x**3)
    """
    return a[1] + (a[0]-a[1])*(3*phi[0]*phi[0]-2*phi[0]*phi[0]*phi[0])

def SimpleInterpolate(phi, phiK, a):
    """
    A simplified interpolation does not work well in a lot of cases unless one has
    degenerate mobility to kill bulk terms instead of this function
    corresponding to x*a + (1-x)*b
    """
    return sum(phi[i]*a[i] for i in range(0,phi.ufl_shape[0]))

def InterpolateOne(phi, phiK, a):
    """
    Interpolation function used when there is only one phase present more degenerate
    """
    return phi[0]*phi[0]*a[0]
