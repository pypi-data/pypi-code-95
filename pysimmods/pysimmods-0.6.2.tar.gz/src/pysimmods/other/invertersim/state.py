"""This module contains the state model of the inverter."""

from pysimmods.model.state import ModelState


class InverterState(ModelState):
    """Inverter state

    Parameters
    ----------
    inits : dict
        A *dict* containing initialization parameters of the inverter.

    Attributes
    ----------
    cos_phi : float
        The cosinus of the phase angle used in the last step.

    """

    def __init__(self, inits):
        super().__init__(inits)

        self.cos_phi = inits.get("cos_phi", 0.9)
