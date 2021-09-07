"""This module contains the input model for the inverter."""


class InverterInputs:
    """Inverter inputs.

    This model does not inherit from the :class:`~.ModelInputs`,
    because those inputs are not required for the inverter.

    Attributes
    ----------
    p_in_kw : float
        Incoming (available) active power in [kW]
    p_set_kw : float
        Target active power in [kW]. Only used in the *'p_set'*,
        *'pq_set'*, and *'qp_set'* modes of the inverter.
    q_set_kw : float
        Target reactive power in [kVAr]. Only used in the *'q_set'*,
        *'pq_set'*, and *'qp_set'* modes of the inverter.
    cos_phi_set : float
        Target cos phi between 0 and 1. Only used in the
        *'cos_phi_set'* mode of the inverter.

    """

    def __init__(self):
        self.p_in_kw = None
        self.p_set_kw = None
        self.q_set_kvar = None
        self.cos_phi_set = None

    def reset(self):
        self.p_in_kw = None
        self.p_set_kw = None
        self.q_set_kvar = None
        self.cos_phi_set = None
