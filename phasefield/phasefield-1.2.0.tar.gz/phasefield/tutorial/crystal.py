# # Crystal Demo
# This is a demonstration of the crystallation on the surface due to coolings. For more details see http://www.ctcms.nist.gov/fipy/examples/phase/generated/examples.phase.anisotropy.html . This is an sharp interface adapation of https://gitlab.dune-project.org/dune-fem/dune-fempy/blob/master/notebooks/crystal.py .

try:
    get_ipython().magic('matplotlib inline # can also use notebook or nbagg')
except:
    pass

import phasefield.useDune
from phasefield.auxfun import SmoothStep
from phasefield import PhaseStepper, PhaseModel
from ufl import as_vector, atan, atan_2, conditional, dot, grad, pi, inner, sqrt, SpatialCoordinate, tan
from dune.fem.plotting import plotComponents


class Crystal:

    omega = [4, 4], [8, 8], [3, 3]
    endTime = 0.1
    mobility = 24
    saveStep = 0.001
    fileBase = "crystal"

    def initial(x):
        r = sqrt( dot( x-as_vector([6,6]), x-as_vector([6,6])) )
        return [[conditional(r>0.3, 0, 1), conditional(r<0.3, 0, 1)], [-0.5]]

    def gammaTheta(theta):
        c = 0.02
        N = 6.
        psi = pi/8.0 + theta
        Phi = tan(N / 2.0 * psi)
        beta = (1.0 - Phi*Phi) / (1.0 + Phi*Phi)
        dbeta_dPhi = -2.0 * N * Phi / (1.0 + Phi * Phi)
        return sqrt(18) * (1.0 + c * beta)

    def a(u,nablau):
        kappa1 = 0.9
        kappa2 = 20
        gamma = kappa1/pi
        return [400 * gamma * atan(kappa2 * u[0]),0]

    def distE(u):
        lam = 1
        return [[u[0]-lam, u[0]]]

    def distQ(u):
        alpha = 2.25
        return [[-alpha*grad(u[0]), -alpha*grad(u[0])]]

    def distF(u, x):
        return [[0, 0]]

# Finally setup the grid and timeloop.
if __name__ == "__main__":
    solverParameters = {
            "newton.tolerance": 1e-8,
            "newton.linear.tolerance": 1e-10,
            "newton.verbose": True,
            "newton.linear.verbose": True
        }

    phaseField = PhaseModel(Crystal, epsilon = 0.015, dt = 0.0005, thetaSemi = True)
    phaseField.interpolate = SmoothStep
    fempyBase = PhaseStepper(phaseField, solverParameters)

    fempyBase.gridSetup(12,12)
    plotComponents(fempyBase.solution)
    while fempyBase.time < Crystal.endTime:
        print(fempyBase.time)
        fempyBase.nextTime()
        fempyBase.adapt()
    plotComponents(fempyBase.solution)
