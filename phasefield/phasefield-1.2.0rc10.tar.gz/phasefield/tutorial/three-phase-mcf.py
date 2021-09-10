import math
import numpy as np
import matplotlib.pyplot as plt
import ufl
from ufl import conditional, sqrt, tanh, pi, sqrt
from phasefield import PhaseStepper, PhaseModel

from dune.fem.function import levelFunction, partitionFunction
from dune.grid import cartesianDomain
from dune.fem.plotting import plotComponents
from dune.grid import cartesianDomain
from dune.fem.function import integrate

from phasefield import PhaseStepper, PhaseModel, ConcaveConvex, ConcaveConvex3p, Implicit3p

def compute(baseName, maxLevel, epsilon, dt):
    r0 = 0.5

    class Iso3:
        omega = cartesianDomain([-2,-2],[2,2],[3,3])
        mobility = 1
        saveStep = 1e-3
        endTime = 0.125
        fileBase = "mcftpmcf"

        r0 = 0.5
        def gamma(nu):
            return [[0,1,1],[1,0,1],[1,1,0] ]

        def initial(x):
            return [[0.5-0.5*ufl.tanh((1/epsilon)*(x[0]*x[0]+x[1]*x[1]-r0*r0)),
                     0.5+0.5*ufl.tanh((1/epsilon)*(x[0]*x[0]+x[1]*x[1]-r0*r0)),0]]


    phaseField = PhaseModel(Iso3, epsilon=epsilon, dt=dt)
    phaseField.well = Implicit3p

    fempyBase = PhaseStepper(phaseField)

    fempyBase.gridSetup(13, maxLevel)
    fempyBase.defaultRefine = [1.4, 1.2, 4, maxLevel]

    solution = fempyBase.solution
    radiusVec = []
    while fempyBase.time < Iso3.endTime:
        if fempyBase.saveTime is not None and fempyBase.saveTime <= fempyBase.time +dt:
            radius = sqrt(integrate(fempyBase.gridView,solution,4)[0]/pi)
            radiusVec.append(radius)
        fempyBase.nextTime()
        fempyBase.adapt()
    return radiusVec

maxLevel = 13
dt = 1e-3

# carry out a sequence of simulations with different value for epsilon
# for a given 'epsilon' the result is stored in a dictonary for later postprocessing

try:
    myDict = np.load('Iso3IMsim.npy', allow_pickle='TRUE').item()
except FileNotFoundError:
    print("Creating a new dictionary for saving")
    myDict = {}
    t = 0
    exactList = []
    while t < 0.125:
        exactList.append(sqrt(0.5*0.5-2*t))
        t += dt
    myDict['exact'] = exactList

for eps in np.linspace(0.05, 0.01, 9):
    if (maxLevel, eps, dt) in myDict:
        print("sim found in dict using old value")
    else:
        print("sim not found in dict running")
        try:
            myDict[(maxLevel, eps, dt)] = compute("cc", maxLevel, eps, dt)
            np.save('Iso3IMsim.npy', myDict)
        except Exception as e:
            print(e)
            myDict[(maxLevel, eps, dt)] = False
            print("simulation", (maxLevel, eps, dt), "failed")

for key, value in myDict.items():
    if value != False:
        plt.plot(value, label=key)

plt.legend()
plt.show()
