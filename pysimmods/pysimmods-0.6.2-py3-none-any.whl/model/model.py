"""This module contains the base class for all pysimmods models."""
import copy
from abc import ABC, abstractmethod


class Model(ABC):
    """Base class for pysimmods models.

    Parameters
    ----------
    params : dict
        A *dict* containing configuration parameters.
    inits : dict
        A *dict* containing the state variables.

    Attributes
    ----------
    config : pysimmods.model.config:Config
        A config object holding all the configuration parameters of
        this model. These do not change during simulation.
    state : pysimmods.model.state:State
        A state object holding all variable parameters of this model.
        These values normally change during each step.
    inputs : pysimmods.model.inputs:Inputs
        An inputs object defining the inputs for this model. In each
        step, all the inputs need to be provided.

    """

    def __init__(self, params, inits):
        self.config = None
        self.state = None
        self.inputs = None

    @abstractmethod
    def step(self):
        """Perform a simulation step."""
        raise NotImplementedError

    def get_state(self):
        """Return the current state of the model

        Returns
        -------
        dict
            The current state of the model in form of a dictionary
            containing entries for all state variables. Returned dict
            can be assigned to the *inits* argument when creating a new
            model instance.

        """

        try:
            return {
                attr: getattr(self.state, attr)
                for attr in self.state.__slots__
            }
        except AttributeError:
            return copy.deepcopy(self.state.__dict__)

    def set_state(self, state):
        """Set the current state of the model.

        Parameters
        ----------
        state : dict
            A *dict* containing entries for all state variables.

        """
        for attr, value in state.items():
            setattr(self.state, attr, value)

    @property
    def p_max_kw(self):
        return self.config.p_max_kw

    @property
    def p_min_kw(self):
        return self.config.p_min_kw

    @property
    def p_kw(self):
        return self.state.p_kw

    @property
    def q_max_kvar(self):
        return self.config.q_max_kvar

    @property
    def q_min_kvar(self):
        return self.config.q_min_kvar

    @property
    def q_kvar(self):
        return self.state.q_kvar

    @property
    def set_percent(self):
        raise NotImplementedError

    @set_percent.setter
    def set_percent(self, set_percent):
        raise NotImplementedError

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
        return self.config.default_schedule
