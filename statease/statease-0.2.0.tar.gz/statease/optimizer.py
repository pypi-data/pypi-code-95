from enum import Enum
import json

class Goal(Enum):
    """An enumeration representing the different types of goals a Criteria can have."""

    NONE = 0
    MAXIMIZE = 1
    MINIMIZE = 2
    TARGET = 3
    IN_RANGE = 4
    EQUAL_TO = 5
    CPK = 6

    def __str__(self):
        return self.name

class Optimizer:
    """The Optimizer class is used to set criteria on one or more Analyses,
    then use those criteria to find the optimal parameters.
    """

    def __init__(self, client):
        self._client = client

        result = self._client.send_payload({
            "method": "GET",
            "uri": "optimizer",
        })

        self._criteria = []
        self._solutions = tuple()

    def __str__(self):
        out = ''
        for c in self._criteria:
            if c.goal != Goal.NONE:
                out += '{}\n'.format(c)
        out += "Found {} solutions:".format(len(self._solutions))
        for s in self._solutions:
            out += '{}\n'.format(s)
        return out

    def have_criteria(self):
        for c in self._criteria:
            if c.goal != Goal.NONE:
                return True
        return False

    def add_criteria(self, criteria):
        self._criteria.append(criteria)

    @property
    def solutions(self):
        return self._solutions

    def optimize(self):
        """ Runs the optimization routine. Must have one or more Criteria specified. """

        if not self.have_criteria():
            raise ValueError("Can't run optimization - no criteria specified!")

        result = self._client.send_payload({
            "method": "POST",
            "uri": "optimizer",
            "criteria": [ c.to_json() for c in self._criteria ],
        })
        self._solutions = tuple(result['payload']['solutions'])

class Criteria:
    """The Criteria class is used by the optimizer to calculate a desirability score
    for a given point in the design space, which is then used to search for an optimal point.

    Each Analysis and Factor can have a Criteria (e.g. you might maximize the output of an Analysis,
    and target a certian value of a Factor).
    """

    def __init__(self, factor=None, analysis=None):
        """ Create a Criteria for a Factor or Analysis. """

        if (not analysis and not factor) or (analysis and factor):
            raise ValueError("You must pass in either an analysis or factor.")

        self._analysis = analysis
        self._factor = factor

        self._goal = Goal.NONE
        self._target = 0
        self._lower_limit = 0
        self._upper_limit = 0
        self._lower_weight = 1
        self._upper_weight = 1
        self._importance = 3

    def __str__(self):
        name = ''
        if self._analysis:
            name += self._analysis.name
        if self._factor:
            name += self._factor.name
        return "Criteria for {} -> Goal: {} Target: {} Lower Limit: {} Upper Limit: {} Lower Weight: {} Upper Weight: {} Importance: {}".format(
            name,
            self._goal,
            self._target,
            self._lower_limit,
            self. _upper_limit,
            self._lower_weight,
            self._upper_weight,
            self._importance,
        )

    @property
    def goal(self):
        """ The goal of this Criteria (e.g. Goal.MAXIMIZE). """
        return self._goal

    @goal.setter
    def goal(self, goal):
        self._goal = goal

    @property
    def target(self):
        """ The target for this Criteria, if using Goal.EQUAL_TO or Goal.TARGET """
        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    @property
    def lower_limit(self):
        """ The lower limit for this Criteria. """
        return self._lower_limit

    @lower_limit.setter
    def lower_limit(self, lower_limit):
        self._lower_limit = lower_limit

    @property
    def upper_limit(self):
        """ The upper limit for this Criteria. """
        return self._upper_limit

    @upper_limit.setter
    def upper_limit(self, upper_limit):
        self._upper_limit = upper_limit

    @property
    def lower_weight(self):
        """ The lower weight for this Criteria. """
        return self._lower_weight

    @lower_weight.setter
    def lower_weight(self, lower_weight):
        self._lower_weight = lower_weight

    @property
    def upper_weight(self):
        """ The upper weight for this Criteria. """
        return self._upper_weight

    @upper_weight.setter
    def upper_weight(self, upper_weight):
        self._upper_weight = upper_weight

    @property
    def importance(self):
        """ The importance of this Criteria, relative to other Criteria. """
        return self._importance

    @importance.setter
    def importance(self, importance):
        self._importance = importance

    def to_json(self):
        out_dict = {
            'analysis': self._analysis.name if self._analysis else None,
            'factor': self._factor.name if self._factor else None,
            'goal': str(self._goal),
        }

        # the rest of the members are primitives
        for k, v in self.__dict__.items():
            key = k[1:] # strip off leading underscore
            if key in out_dict.keys():
                continue
            out_dict[key] = v
        return out_dict
