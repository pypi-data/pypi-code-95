import math
from dune.fem.plotting import plotComponents

from phasefield import PhaseStepper, PhaseModel, SimpleInterpolate

from ufl import conditional, grad

class Ms:
    omega = [0, 0], [2, 2], [3, 3]
    endTime = 0.05
    saveStep = 0.005
    mobility = 0.

    def initial(x):
        return [[conditional(9*(x[0]-1)*(x[0]-1)+(x[1]-1)*(x[1]-1) > 0.5, 1, 0),
                 conditional(9*(x[0]-1)*(x[0]-1)+(x[1]-1)*(x[1]-1) > 0.5, 0, 1)], [1]]

    def gamma(nu):
        surface = 0.8/9
        return [[0, 0.8/9], [0.8/9, 0]]

    def a(u):
        return [0,2*u[0]]

    def distE(u):
        return [[1, 0]]

    def distQ(u):
        return [[-2*grad(u[0]), -2*grad(u[0])]]

    def distF(u, x):
        return [[0, 0]]


solverParameters = {"fem.solver.newton.tolerance": 1e-9,
                    "newton.verbose": True,
                    "newton.linear.tolerance": 1e-8,
                    "newton.linear.preconditioning.method": "ilu",
                    "newton.linear.preconditioning.iterations": 1,
                    "newton.linear.preconditioning.relaxation": 1.2,
                    "newton.linear.verbose": True}

phaseField = PhaseModel(Ms, epsilon=0.15*math.sqrt(3/4), dt=1e-4)

phaseField.interpolate = SimpleInterpolate

fempyBase = PhaseStepper(phaseField, solverParameters)

fempyBase.gridSetup(12, 12)

while fempyBase.time < Ms.endTime:
    print(fempyBase.time)
    fempyBase.nextTime()
    fempyBase.adapt()

plotComponents(fempyBase.solution)
