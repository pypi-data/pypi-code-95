from ufl import as_vector, atan, atan_2, cos, conditional, dot, grad, pi, sqrt, zero

from phasefield import PhaseStepper, PhaseModel, Obstacle, ConcaveConvex

from dune.fem import parameter

class Tumour:
    omega = [0,0], [12.5, 12.5], [30, 30]
    endTime = 10.0
    saveStep = 0.1

    mobility = 0

    def dirichlet(t, x):
        return {x[0]*x[1]>1e-12: [None, 1]}

    def initial(x):
        r = sqrt(dot(x, x))
        theta = atan_2(x[1],x[0]) + conditional(x[1] < 0, 2*pi, 0)
        rTheta = 2 + 0.1 * cos(2*theta)
        return [conditional(r > rTheta, 0, 1), conditional(r < rTheta, 0, 1)], [0, 1]

    def gamma(nu):
        beta = 0.1
        gamma = pi/2
        return [[0, beta*gamma], [beta*gamma, 0]]

    def a(u, gradu, un, gradun):
        chi = 5
        return [0, 2*u[0] + 2*chi*un[1]]

    def distE(u):
        return [[1, 0], [0, 0]]

    def distQ(u):
        D = 1
        return [[-grad(u[0]), zero(2)], [grad(u[1]), grad(u[1])]]

    def distF(u, x, un):
        lam = 0
        P = 0.1
        C = 2
        A = 0
        return [[ P *( un[1] + lam) - A, 0], [C *( u[1] + lam ), 0.]]

if __name__ == "__main__":

    parameter.append( {"fem.verboserank": -1} )
    solverParameters = {"newton.verbose": True,
                        "newton.linear.verbose": True,
                        "newton.linear.tolerance": 1e-9,
                        "newton.linear.preconditioning.method": "ilu",
                        "newton.linear.preconditioning.iterations": 1,
                        "newton.linear.preconditioning.relaxation": 1.2,
                        "newton.lineSearch": "simple",
                        "newton.tolerance": 1e-6}

    uflModel = PhaseModel(Tumour, epsilon=0.01, dt=0.001)
    uflModel.bulkSmoothdict['Q',0] = lambda phi, phiN: [phiN[0] * phiN[0], phiN[1] * phiN[1]]
    fempyBase = PhaseStepper(uflModel, postBulk = [1],
                             solver="gmres", solverParameters=solverParameters)
    fempyBase.defaultRefine = [1.5, 0.15, 0, 16]
    fempyBase.gridSetup(8,18)
    while fempyBase.time < Tumour.endTime:
        print(fempyBase.time, fempyBase.spc.size, flush=True)
        fempyBase.nextTime()
        fempyBase.adapt()
