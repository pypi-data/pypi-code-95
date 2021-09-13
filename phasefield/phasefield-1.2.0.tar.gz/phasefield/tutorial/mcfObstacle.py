# Mean curvature flow with obstacle potential well and uniform refinement

from ufl import pi, sqrt, tanh
from phasefield import PhaseStepper, PhaseModel

from dune.fem.plotting import plotComponents

from dune.fem.function import integrate

class Mcf:
    """Sharp definition for mean curvature flow"""
    omega = [-2, -2], [2, 2], [3, 3]
    endTime = 0.125
    saveStep = 0.01
    fileBase = "McfObstacle"

    mobility = 1
    def initial(x):
        """ Initial conditions """
        r0 = 0.5
        epsilon = 0.02
        return [[0.5-0.5*tanh((1/epsilon)*(x[0]*x[0]+x[1]*x[1]-r0*r0)),
                 0.5+0.5*tanh((1/epsilon)*(x[0]*x[0]+x[1]*x[1]-r0*r0))]]

    def gamma(nu):
        """ Matrix of surface tensions """
        return [[0, 1], [1, 0]]

if __name__== "__main__":
    maxLevel = 15
    dt = 1e-4
    epsilon = 0.04

    phaseField = PhaseModel(Mcf, constrained=True, epsilon=epsilon, dt=dt)

    fempyBase = PhaseStepper(phaseField)

    fempyBase.defaultRefine = [1.4, 0.2, 4, maxLevel]
    fempyBase.gridSetup(13, maxLevel)

    while fempyBase.time < Mcf.endTime:
        print(fempyBase.time, flush=True)
        fempyBase.nextTime()
        fempyBase.adapt()
