import phasefield.useFenics
from phasefield import PhaseStepper, PhaseModel
from ufl import as_vector, conditional, SpatialCoordinate
from fenics import plot, File, project
import matplotlib.pyplot as plt

class Mcf:
    """Sharp definition for mean curvature flow."""
    omega = [-2, -2], [2, 2], [300, 300]
    endTime = 0.125
    saveStep = 0.001

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

    fempyBase = PhaseStepper(phaseField, solver = ("direct"))
    solution = fempyBase.solution

    fempyBase.gridSetup(13, 13)

    vtkfile = File('mcf.pvd')
    vtkfile << project(solution[0])

    while fempyBase.time < Mcf.endTime:
        fempyBase.nextTime()
        fempyBase.adapt()
        print(fempyBase.time)

    vtkfile << project(solution[0])
