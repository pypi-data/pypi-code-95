"""This module contains the base class for all model states."""


class ModelState:
    """Base class for model states.

    Parameters
    ----------
    inits : dict
        A *dict* containing the state variables.

    Attributes
    ----------
    p_kw : float
        Current (or last) electrical active power in [kW].
    q_kvar : float
        Current (or last) electrical reactive power in [kVAr].
    """

    def __init__(self, inits):
        self.p_kw = inits.get("p_kw", 0)
        self.q_kvar = inits.get("q_kvar", 0)
