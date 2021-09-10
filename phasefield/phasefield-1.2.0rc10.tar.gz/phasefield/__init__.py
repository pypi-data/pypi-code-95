import os

from phasefield.stepper import PhaseStepper as PhaseStepper
from phasefield.ufl_phasefield import UflPhasefield as PhaseModel
from phasefield.auxfun import *

try:
    import phasefield.useDune
except ImportError:
    pass

def get_tutorial():
    path = os.path.join( os.path.dirname(__file__), "tutorial" )
    execute  = "cp -r " + path + " "
    execute += __name__ + "_tutorial"
    status = os.system(execute)
    if status != 0: raise RuntimeError(status)
