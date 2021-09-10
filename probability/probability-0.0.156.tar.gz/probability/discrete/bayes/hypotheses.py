from typing import Callable, Any

from probability.discrete._old.joint import Joint


class Hypotheses(object):

    def __init__(self, prior: Joint,
                 likelihood: Callable[[Any, str], float],
                 ):
        """
        Create a new collection of hypotheses to solve problems using Bayes'
        rule.

        :param prior: Prior probability of each hypothesis. 1d Joint
                      containing 1 value for each hypothesis name.
        :param likelihood: Method to call with (data, hypothesis name)
        """
        self._prior: Joint = prior
        self._likelihood: Callable[[Any, str], float] = likelihood

    def update(self, data: float):

        for hypothesis in self._prior.variables:
            pass

