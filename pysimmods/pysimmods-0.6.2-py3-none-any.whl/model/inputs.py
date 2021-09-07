"""This module contains the base class for all model inputs."""
from datetime import datetime
from pysimmods.util.dateformat import GER


class ModelInputs:
    """Base class for model inputs.

    Attributes
    ----------
    p_set_kw : float
        Target electrical activate power in [kW].
    q_set_kvar : float
        Target electrical reactive power in [kVAr].
    step_size : int
        Step size for the net step in [s].

    """

    def __init__(self):
        self.p_set_kw = None
        self.q_set_kvar = None
        self.step_size = None
        self._now = None

    @property
    def now(self):
        return self._now

    @now.setter
    def now(self, value):
        """Set the current time.

        Parameters
        ----------
        value : datetime.datetime
            The time to set. If *value* is an UTC ISO 8601 time string
            or an unix timestamp, it will be converted to datetime.

        Raises
        ------
        ValueError
            If *value* is neither datetime.datetime nor an UTC ISO 8601
            time string nor an unix timestamp.

        """

        if isinstance(value, str):
            self._now = datetime.strptime(value, GER)
        elif isinstance(value, int):
            self._now = datetime.utcfromtimestamp(value)
        elif isinstance(value, datetime):
            self._now = value
        else:
            raise ValueError(f"Unknown date format: {type(value)}")

    def reset(self):
        """To be called at the end of each step."""
        for attr in self.__dict__.keys():
            setattr(self, attr, None)
