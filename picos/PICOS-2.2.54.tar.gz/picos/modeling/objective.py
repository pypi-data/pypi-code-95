# ------------------------------------------------------------------------------
# Copyright (C) 2019-2021 Maximilian Stahlberg
#
# This file is part of PICOS.
#
# PICOS is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PICOS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------

"""Implementation of :class:`Objective`."""

from .. import expressions, glyphs
from ..apidoc import api_end, api_start
from ..caching import cached_property
from ..expressions.uncertain import IntractableWorstCase, UncertainExpression

_API_START = api_start(globals())
# -------------------------------


class Objective:
    """An optimization objective composed of search direction and function.

    :Example:

    >>> from picos import Objective, RealVariable
    >>> x = RealVariable("x")
    >>> obj = Objective("min", x); obj
    <Objective: minimize x>
    >>> obj + x**2  # Add a term to the objective function.
    <Objective: minimize x + x²>
    >>> obj/2 + 2*obj  # Scale and combine two objectives.
    <Objective: minimize x/2 + 2·x>
    >>> -obj  # Flip the optimization direction.
    <Objective: maximize -x>
    """

    #: Short string denoting a feasibility problem.
    FIND = "find"

    #: Short string denoting a minimization problem.
    MIN  = "min"

    #: Short string denoting a maximization problem.
    MAX  = "max"

    def __init__(self, direction=None, function=None):
        """Construct an optimization objective.

        :param str direction:
            Case insensitive search direction string. One of

            - ``"min"`` or ``"minimize"``,
            - ``"max"`` or ``"maximize"``,
            - ``"find"`` or :obj:`None` (for a feasibility problem).

        :param ~picos.expressions.Expression function:
            The objective function. Must be :obj:`None` for a feasibility
            problem.
        """
        if direction is None:
            direction = self.FIND
        else:
            if not isinstance(direction, str):
                raise TypeError("Search direction must be given as a string.")

            lower = direction.lower()
            if lower == "find":
                direction = self.FIND
            elif lower.startswith("min"):
                direction = self.MIN
            elif lower.startswith("max"):
                direction = self.MAX
            else:
                raise ValueError(
                    "Invalid search direction '{}'.".format(direction))

        if function is None:
            if direction != self.FIND:
                raise ValueError("Missing an objective function.")
        else:
            if direction == self.FIND:
                raise ValueError("May not specify an objective function for a "
                    "feasiblity problem.")

            if not isinstance(function, expressions.Expression):
                raise TypeError(
                    "Objective function must be a PICOS expression.")

            if len(function) != 1:
                raise TypeError("Objective function must be scalar.")

            function = function.refined

            if isinstance(function, expressions.ComplexAffineExpression) \
            and function.complex:
                raise TypeError("Objective function may not be complex.")

        self._direction = direction
        self._function = function

    def __str__(self):
        if self._function is None:
            return "find an assignment"
        else:
            minimize = self._direction == self.MIN
            dir_str = "minimize" if minimize else "maximize"

            if self._function.uncertain:
                obj_str = self._function.worst_case_string(
                    "max" if minimize else "min")
            else:
                obj_str = self._function.string

            return "{} {}".format(dir_str, obj_str)

    def __repr__(self):
        return glyphs.repr1("Objective: {}".format(self))

    def __iter__(self):
        yield self._direction
        yield self._function

    def __eq__(self, other):
        if not isinstance(other, Objective):
            return False

        if self._direction != other._direction:
            return False

        if self._direction == self.FIND:
            return True

        try:
            return self._function.equals(other._function)
        except AttributeError:
            # TODO: Allow all expressions to be equality-checked?
            return self._function is other._function

    def __pos__(self):
        return self

    def __neg__(self):
        if self._direction == self.FIND:
            return self
        elif self._direction == self.MIN:
            return Objective(self.MAX, -self._function)
        else:
            return Objective(self.MIN, -self._function)

    def __add__(self, other):
        if self.feasibility:
            if isinstance(other, Objective):
                return other
            else:
                raise TypeError(
                    "May only add another objective to a feasiblity objective.")
        elif isinstance(other, Objective):
            if other.feasibility:
                return self
            elif self._direction == other._direction:
                return self + other._function
            else:
                return self - (-other._function)
        else:
            try:
                function = self._function + other
            except TypeError as error:
                raise TypeError("Failed to add to objective.") from error
            else:
                return Objective(self._direction, function)

    def __sub__(self, other):
        if self.feasibility:
            if isinstance(other, Objective):
                return -other
            else:
                raise TypeError("May only subtract another objective from a "
                    "feasiblity objective.")
        elif isinstance(other, Objective):
            if other.feasibility:
                return self
            elif self._direction == other._direction:
                return self - other._function
            else:
                return self + (-other._function)
        else:
            try:
                function = self._function - other
            except TypeError as error:
                raise TypeError("Failed to subtract from objective.") from error
            else:
                return Objective(self._direction, function)

    def _mul(self, other, reverse):
        if self.feasibility:
            return self
        elif isinstance(other, Objective):
            raise TypeError("You may only add or subtract two objectives, not "
                "multiply or divide them.")
        else:
            try:
                if reverse:
                    function = other * self._function
                else:
                    function = self._function * other
            except TypeError as error:
                raise TypeError("Failed to multiply objective.") from error
            else:
                return Objective(self._direction, function)

    def __mul__(self, other):
        return self._mul(other, False)

    def __rmul__(self, other):
        return self._mul(other, True)

    def __truediv__(self, other):
        if self.feasibility:
            return self
        elif isinstance(other, Objective):
            raise TypeError("You may only add or subtract two objectives, not "
                "multiply or divide them.")
        else:
            try:
                function = self._function / other
            except TypeError as error:
                raise TypeError("Failed to divide objective.") from error
            else:
                return Objective(self._direction, function)

    @property
    def feasibility(self):
        """Whether the objective is "find an assignment"."""
        return self._function is None

    @property
    def pair(self):
        """Search direction and objective function as a pair."""
        return self._direction, self._objective

    @property
    def direction(self):
        """Search direction as a short string."""
        return self._direction

    @property
    def function(self):
        """Objective function."""
        return self._function

    @cached_property
    def normalized(self):
        """The objective but with feasiblity posed as "minimize 0".

        >>> from picos import Objective
        >>> obj = Objective(); obj
        <Objective: find an assignment>
        >>> obj.normalized
        <Objective: minimize 0>
        """
        if self._function is None:
            return Objective(self.MIN, expressions.AffineExpression.zero())
        else:
            return self

    @property
    def value(self):
        """Value of the objective function.

        In the case of an uncertain objective, this is the worst-case (expected)
        objective value.

        :raises picos.uncertain.IntractableWorstCase:
            When computing the worst-case (expected) value of an uncertain
            objective is not supported.
        """
        if self._function is None:
            return None
        elif isinstance(self._function, UncertainExpression):
            if self._direction == self.MIN:
                bad_direction = self.MAX
            elif self._direction == self.MAX:
                bad_direction = self.MIN
            else:
                bad_direction = self.FIND

            try:
                return self._function.worst_case_value(bad_direction)
            except IntractableWorstCase as error:
                raise IntractableWorstCase("Failed to compute the worst-case "
                    "value of the objective function {}: {} Maybe evaluate the "
                    "nominal objective function instead?"
                    .format(self._function.string, error)) from None
        else:
            return self._function.value

    def __index__(self):
        if self._function is None:
            raise TypeError("A feasiblity objective cannot be used as an index "
                "because there is no objective function to take the value of.")

        value = self.value

        if value is None:
            raise expressions.NotValued(
                "Cannot use unvalued objective function {} as an index."
                .format(self._function.string))

        assert isinstance(value, (float, int))

        if not value.is_integer():
            raise ValueError(
                "Cannot use the objective function {} as an index as its value "
                "of {} is not integral.".format(self._function.string, value))

        return int(value)

    def _casting_helper(self, theType):
        assert theType in (int, float, complex)

        if self._function is None:
            raise TypeError("A feasiblity objective cannot be cast as {} "
                "because there is no objective function to take the value of."
                .format(theType.__name__))

        value = self.value

        if value is None:
            raise expressions.NotValued(
                "Cannot cast unvalued objective function {} as {}."
                .format(self._function.string, theType.__name__))

        return theType(value)

    def __int__(self):
        return self._casting_helper(int)

    def __float__(self):
        return self._casting_helper(float)

    def __complex__(self):
        return self._casting_helper(complex)

    def __round__(self, ndigits=None):
        return round(float(self), ndigits)


# --------------------------------------
__all__ = api_end(_API_START, globals())
