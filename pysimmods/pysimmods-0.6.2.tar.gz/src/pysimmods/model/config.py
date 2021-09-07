"""This module contains the base config for each model."""


class ModelConfig:
    """The base config for all models.

    Parameters
    ----------
    params : dict
        A *dict* containing configuration parameters. See *Attributes*
        for detailed information

    Attributes
    ----------
    sign_convention : str
        Should be defined in *params* and can have the values
        *'passive'* or *'active'*. Passive sign convention aka load
        reference arrow system is normally used and leads to positive
        consumption and negative generation power flows.
    psc : bool
        Is *True* if passive sign convention is used.
    asc : bool
        Is *True* if active sign convention is used.
    gsign : int
        The generator sign depending on the sign convention. Will be
        set to *-1* if passive sign convention is used and to *1*
        otherwise.
    lsign : int
        The load sign depending on the sign convention. Will be set to
        *1* is passive sign convention is used and to *-1* otherwise.

    """

    def __init__(self, params):

        self.sign_convention = params.get("sign_convention", "passive")
        assert self.sign_convention in ["active", "passive"]

        self.psc = self.sign_convention == "passive"
        self.asc = self.sign_convention == "active"

        if self.sign_convention == "active":
            self.gsign = 1
            self.lsign = -1
        else:
            self.gsign = -1
            self.lsign = 1

        self._default_schedule = [50] * 24

    @property
    def p_max_kw(self):
        raise NotImplementedError()

    @property
    def p_min_kw(self):
        raise NotImplementedError()

    @property
    def q_max_kvar(self):
        raise NotImplementedError()

    @property
    def q_min_kvar(self):
        raise NotImplementedError()

    @property
    def default_schedule(self):
        """Return the default schedule.

        Returns
        -------
        list
            A *list* containing a default schedule with percentage
            power for each hour of the day (i.e.,
            len(default_schedule) == 24). This is used if no other *p*
            or *q* input is provided.

        """
        return self._default_schedule
