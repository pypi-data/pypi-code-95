from ufl import conditional, sqrt, tanh
from phasefield import PhaseStepper, PhaseModel

from dune.fem.function import levelFunction, partitionFunction
from dune.grid import cartesianDomain
import math

epsilon = 0.01

class Iso3:
    omega = cartesianDomain([-0.2,-0.2],[0.2,0.2],[3,3])
    mobility = 10
    endTime = 0.5
    def gamma(nu):
        return [[0,1,1],[1,0,1],[1,1,0] ]
    def initial(x):
        circ = sqrt(x[0]*x[0]+x[1]*x[1])-0.1
        phase1 = 0.5+0.5*tanh( (2/epsilon)*conditional(circ<x[1],circ,x[1]))
        phase2 = 0.5-0.5*tanh( (2/epsilon)*x[1])
        phase3 = 1-phase1-phase2
        return [[phase1, phase2, phase3]]

from phasefield.auxfun import ConcaveConvex3p, Implicit3p
phaseField = PhaseModel(Iso3, epsilon, dt=1e-3)
phaseField.well = Implicit3p
# for a concave terms explicitly in time use
# phaseField.well = ConcaveConvex3p

solverParameters = {"tolerance": 1e-5,
                    "verbose": True,
                    "linear.tolerance": 1e-8,
                    "linear.preconditioning.method": "ilu",
                    "linear.preconditioning.iterations": 1,
                    "linear.preconditioning.relaxation": 1.2,
                    "linear.verbose": True}


fempyBase = PhaseStepper(phaseField, solverParameters)


fempyBase.gridSetup(12, 12)

vtk = fempyBase.gridView.sequencedVTK("iso3", pointdata=[fempyBase.solution],
                                      celldata=[levelFunction(fempyBase.gridView)])
vtk()

while fempyBase.time < Iso3.endTime:
    fempyBase.nextTime()
    fempyBase.adapt()
    print(fempyBase.time)
    vtk()
