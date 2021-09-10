# Mean curvature flow computation with implicit potential well on a circular domain

from ufl import conditional
from phasefield import PhaseStepper, PhaseModel

from dune.fem.plotting import plotComponents
from dune.grid import reader

import numpy

def domain(radius,boundaryPoints):
    vertices = numpy.zeros((2*boundaryPoints+1, 2))
    vertices[0] = [0, 0]
    for i in range(0, boundaryPoints):
        vertices[i+1] = [numpy.cos(2*numpy.pi*i/boundaryPoints)*radius,
                         numpy.sin(2*numpy.pi*i/boundaryPoints)*radius]
    for i in range(0, boundaryPoints):
        vertices[boundaryPoints+i+1] = [numpy.cos(2*numpy.pi*(i+0.5)/boundaryPoints)*radius*0.65,
                                        numpy.sin(2*numpy.pi*(i+0.5)/boundaryPoints)*radius*0.65]
    dgf = """DGF
VERTEX
"""
    for v in vertices:
        dgf += str(v[0]) + " " + str(v[1]) + "\n"
    dgf += """#
SIMPLEX
"""
    for i in range(boundaryPoints):
        dgf += "0 " + str(i%boundaryPoints+1) + " " + str(i%boundaryPoints+boundaryPoints+1) + "\n"
        dgf += "0 " + str((i+1)%boundaryPoints+1) + " " + str(i%boundaryPoints+boundaryPoints+1) + "\n"
        dgf += str(i%boundaryPoints+1) + " " + str(i%boundaryPoints+boundaryPoints+1) + " " +str((i+1)%boundaryPoints+1) + "\n"
    dgf += """#
PROJECTION
"""
    dgf += "function p(x) = " + str(radius) + " * x / |x|\n"
    for i in range(boundaryPoints):
        dgf += "segment " + str(i%boundaryPoints+1) + " " + str((i+1)%boundaryPoints+1) + " p\n"
    dgf += """#"""
    return dgf

def domainDict(radius,boundaryPoints,area):
    import triangle
    theta = numpy.linspace(0, 2 * numpy.pi, boundaryPoints, endpoint=False)
    pts = numpy.stack([numpy.cos(theta), numpy.sin(theta)], axis=1)
    A = dict(vertices=pts)
    B = triangle.triangulate(A, 'qa'+str(area))
    return (B,2)

class Mcf:
    """Sharp definition for mean curvature flow."""
    omega =  ((reader.dgfString, domain(1.,6)),2) # use dgf

    endTime = 0.125
    saveStep = 0.01

    mobility = 1
    def initial(x):
        """
        Initial conditions
        """
        return [[conditional(x[0]*x[0]+x[1]*x[1] < 0.25, 1, 0),
                 conditional(x[0]*x[0]+x[1]*x[1] > 0.25, 1, 0)]]

    def gamma(nu):
        """
        Matrix of surface tensions
        """
        return [[0, 1], [1, 0]]

if __name__ == "__main__":

    phaseField = PhaseModel(Mcf, epsilon=0.03, dt=0.001)

    fempyBase = PhaseStepper(phaseField, solver = "direct")

    fempyBase.gridSetup(5, 13)

    plotComponents(fempyBase.solution)

    while fempyBase.time < Mcf.endTime:
        fempyBase.nextTime()
        fempyBase.adapt()
        print(fempyBase.time)

    plotComponents(fempyBase.solution)
