from __future__ import print_function
try:
    get_ipython().magic('matplotlib inline # can also use notebook or nbagg')
except:
    pass

# import phasefield.useDune
import phasefield.useFenics
from phasefield import PhaseStepper, PhaseModel
from ufl import as_vector, atan, atan_2, conditional, dot, grad, pi, inner, sqrt, SpatialCoordinate, tan

class SharpCrystal():
    #### mynote: the inspection doesn't work for fenics...
    #### can't one get this information easier from the initial conditions?
    dimRangePhase = 1
    imRangeBalance = 1

    # surface tension and mobility
    mobility = 24

    omega = [[4, 4], [8, 8], [3, 3]]
    endTime = 0.05

    def initial(x):
        r = sqrt( dot( x-as_vector([6,6]), x-as_vector([6,6])) )
        return [[conditional(r>0.3, 0, 1), conditional(r<0.3, 0, 1)], [-0.5]]

    # probably should put this in properly needed for inspection to deduce
    # anisotropy in acOperator
    def gamma(nu):
        return [[0, inner(nu, nu)], [inner(nu, nu), 0]]

    def a(u,nablau):
        kappa1 = 0.9
        kappa2 = 20
        gamma = kappa1/pi
        return [0, 200 * gamma * atan(kappa2 * u[0])]

    def distE(u):
        #here K is the latent heat at the interface
        return [[u[0]-1, u[0]]]

    def distQ(u):
        Td = 2.25
        return [[-Td*grad(u[0]), -Td*grad(u[0])]]

    def distF(u):
        return [[0, 0]]


class TimeDis(PhaseModel):
    """
    Best way to change part of the time discretisation put it in a separate class
    and inherit from UflPhasefield
    """
    def diffusionTerm(self, phi, phin, v):
        c = 0.02
        N = 6.
        psi = pi/8.0 + atan_2(grad(phin[0])[1], (grad(phin[0])[0]))
        Phi = tan(N / 2.0 * psi)
        beta = (1.0 - Phi*Phi) / (1.0 + Phi*Phi)
        dbeta_dPhi = -2.0 * N * Phi / (1.0 + Phi * Phi)
        fac = 1.0 + c * beta
        diag = fac * fac
        offdiag = -fac * c * dbeta_dPhi
        d0 = as_vector([diag, offdiag])
        d1 = as_vector([-offdiag, diag])
        return -self.eps * 18 * (inner(dot(d0, grad(phi[0])), grad(v)[0]) + inner(dot(d1, grad(phi[0])), grad(v)[1]))

phaseField = TimeDis(SharpCrystal, epsilon = 0.015, dt = 0.0005)
fempyBase = PhaseStepper(phaseField)

fempyBase.gridSetup(12,12)
plotComponents(fempyBase.solution)
while fempyBase.t < SharpCrystal.endTime:
    print(fempyBase.t)
    fempyBase.nextTime()
    fempyBase.adapt()
plotComponents(fempyBase.solution)
