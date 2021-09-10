# Mean curvature flow computation with implicit potential well.

from ufl import conditional
from phasefield import PhaseStepper, PhaseModel

from dune.fem.plotting import plotComponents

class Mcf:
    """Sharp definition for mean curvature flow."""
    omega = [-2, -2], [2, 2], [3, 3]
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

    fempyBase = PhaseStepper(phaseField, solver = ("direct"))

    fempyBase.gridSetup(13, 13)

    plotComponents(fempyBase.solution)

    while fempyBase.time < Mcf.endTime:
        fempyBase.nextTime()
        fempyBase.adapt()
        print(fempyBase.time)

    plotComponents(fempyBase.solution)
