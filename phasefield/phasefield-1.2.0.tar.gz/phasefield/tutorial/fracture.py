"""
Fracture model computed with a coupled scheme
"""
from phasefield.auxfun import InterpolateOne
from phasefield import PhaseStepper, PhaseModel

from dune.fem.function import levelFunction, partitionFunction
from dune.fem.utility import pointSample

from ufl import as_vector, conditional, Identity, dot, inner, grad, tr, transpose


#************ HELP FUNCTIONS *****************************
def eps(u):
    return 0.5*(grad(u)+transpose(grad(u)))

def sigma(u):
    lam = mu = 563.2
    geodim = 2
    return lam*tr(eps(u))*Identity(geodim) + 2*mu*eps(u)
#*********************************************************

class Fracture:
    # second parameter is the dimension of the domain
    omega = ("data/crack2.dgf", 2)
    endTime = 0.1
    saveStep = 0.01

    mobility = 3e-4

    def dirichlet(t, x):
        return {2: [0, 0], 3: [None, 0]}
    def neuman(t,x):
        return as_vector([0,conditional(x[1]>75-1e-8,-t*6,0)])

    tipCenter = [25,0]
    tipRadius = 0.01

    def initial(x):
        tipCenter = as_vector(Fracture.tipCenter)
        tipRadius = Fracture.tipRadius
        crack = 1 - conditional(x[1] > tipRadius, 0, 1) * conditional(x[0] > tipCenter[0], 0, 1)
        return [[crack], [0, 0]]

    def gamma(nu):
        return [[0.5]]

    def a(u, gradu):
        return [0.5*inner(sigma(u), eps(u))]

    def distE(u):
        return [[0], [0]]

    def distQ(u):
        return [[sigma(u)[0, :]], [sigma(u)[1, :]]]

    def distF(u, x):
        return [[0], [0]]

def compute(sim,maxLevel,epsilon,dt):
    uflModel = PhaseModel(Fracture, constrained=True, epsilon=epsilon, dt=dt)

    uflModel.bulkSmoothdict['Q', 0] = lambda phi, phin: [phin[0] * phin[0]]
    uflModel.bulkSmoothdict['Q', 1] = lambda phi, phin: [phin[0] * phin[0]]

    uflModel.interpolate = InterpolateOne

    fempyBase = PhaseStepper(uflModel,
                         preBulk = [0,1],
                         solver="cg")
    solution = fempyBase.solution
    fempyBase.indicator = 1-solution[0]
    fempyBase.defaultRefine = [3e-1, 1e-1, 8, maxLevel]
    fempyBase.gridSetup(10,maxLevel)

    dx = 0.5
    point = Fracture.tipCenter
    point[0] += dx/2
    arrivalTimes = []

    while True: # fempyBase.time < Fracture.endTime:
        fempyBase.nextTime()
        fempyBase.adapt()
        value = pointSample(solution,point)
        if value[0] < 0.05:
            arrivalTimes += [[point[0],fempyBase.time]]
            if point[0] > 5:
                break
            point[0] += dx
            print(fempyBase.time,fempyBase.gridView.size(0),point[0],value,"arrival time",flush=True)
        else:
            print(fempyBase.time,fempyBase.gridView.size(0),point[0],value,flush=True)
    return arrivalTimes

if __name__== "__main__":
  compute("",16,0.1,1e-4)
