# ------------------------------------------------------------------------------
# Copyright (C) 2019 Maximilian Stahlberg
# Based on the original picos.expressions module by Guillaume Sagnol.
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

"""Implements :class:`SumExponentials`."""

import math
import operator
from collections import namedtuple

import cvxopt
import numpy

from .. import glyphs
from ..apidoc import api_end, api_start
from ..caching import cached_property, cached_unary_operator
from ..constraints import LogSumExpConstraint, SumExponentialsConstraint
from .data import convert_and_refine_arguments, convert_operands, cvx2np
from .exp_affine import AffineExpression
from .expression import Expression, refine_operands, validate_prediction

_API_START = api_start(globals())
# -------------------------------


class SumExponentials(Expression):
    r"""Sum of elementwise exponentials of an affine expression.

    :Definition:

    Let :math:`x` be an :math:`n`-dimensional real affine expression.

    1.  If no additional expression :math:`y` is given, this is the sum of
        elementwise exponentials

        .. math::

            \sum_{i = 1}^n \exp(\operatorname{vec}(x)_i).

    2.  If an additional affine expression :math:`y` of same shape as :math:`x`
        is given, this is the sum of elementwise perspectives of exponentials

        .. math::

            \sum_{i = 1}^n \operatorname{vec}(y)_i \exp\left(
            \frac{\operatorname{vec}(x)_i}{\operatorname{vec}(y)_i}\right).

    .. warning::

        When you pose an upper bound :math:`t` on a sum of elementwise
        exponentials, then PICOS enforces :math:`t \geq 0` through an auxiliary
        constraint during solution search. When an additional expression
        :math:`y` is given, PICOS enforces :math:`y \geq 0` as well.
    """

    # --------------------------------------------------------------------------
    # Initialization and factory methods.
    # --------------------------------------------------------------------------

    @convert_and_refine_arguments("x", "y", allowNone=True)
    def __init__(self, x, y=None):
        """Construct a :class:`SumExponentials`.

        :param x: The affine expression :math:`x`.
        :type x: ~picos.expressions.AffineExpression
        :param y: An additional affine expression :math:`y`. If necessary, PICOS
            will attempt to reshape or broadcast it to the shape of :math:`x`.
        :type y: ~picos.expressions.AffineExpression
        """
        if not isinstance(x, AffineExpression):
            raise TypeError("Can only sum the elementwise exponentials of a "
                "real affine expression, not of {}.".format(x.string))

        if y is not None:
            if not isinstance(y, AffineExpression):
                raise TypeError("The additional parameter y must be a real "
                    "affine expression, not {}.".format(y.string))
            elif x.shape != y.shape:
                y = y.reshaped_or_broadcasted(x.shape)

            if y.is1:
                y = None

        self._x = x
        self._y = y

        if len(x) == 1:
            if y is None:
                typeStr = "Exponential"
                symbStr = glyphs.exp(x.string)
            else:
                typeStr = "Exponential Perspective"
                symbStr = glyphs.mul(
                    y.string, glyphs.exp(glyphs.div(x.string, y.string)))
        else:
            if y is None:
                typeStr = "Sum of Exponentials"
                symbStr = glyphs.make_function("sum", "exp")(x.string)
            else:
                typeStr = "Sum of Exponential Perspectives"
                symbStr = glyphs.sum(glyphs.mul(glyphs.slice(y.string, "i"),
                    glyphs.exp(glyphs.div(glyphs.slice(x.string, "i"),
                    glyphs.slice(y.string, "i")))))

        Expression.__init__(self, typeStr, symbStr)

    # --------------------------------------------------------------------------
    # Abstract method implementations and method overridings, except _predict.
    # --------------------------------------------------------------------------

    def _get_refined(self):
        if self._x.constant and (self._y is None or self._y.constant):
            return AffineExpression.from_constant(self.value, 1, self._symbStr)
        else:
            return self

    Subtype = namedtuple("Subtype", ("argdim", "y"))

    def _get_subtype(self):
        return self.Subtype(len(self._x), self._y is not None)

    def _get_value(self):
        x = numpy.ravel(cvx2np(self._x._get_value()))

        if self._y is None:
            s = numpy.sum(numpy.exp(x))
        else:
            y = numpy.ravel(cvx2np(self._y._get_value()))
            s = y.dot(numpy.exp(x / y))

        return cvxopt.matrix(s)

    @cached_unary_operator
    def _get_mutables(self):
        if self._y is None:
            return self._x._get_mutables()
        else:
            return self._x._get_mutables().union(self._y.mutables)

    def _is_convex(self):
        return True

    def _is_concave(self):
        return False

    def _replace_mutables(self, mapping):
        return self.__class__(self._x._replace_mutables(mapping),
            None if self._y is None else self._y._replace_mutables(mapping))

    def _freeze_mutables(self, freeze):
        return self.__class__(self._x._freeze_mutables(freeze),
            None if self._y is None else self._y._freeze_mutables(freeze))

    # --------------------------------------------------------------------------
    # Python special method implementations, except constraint-creating ones.
    # --------------------------------------------------------------------------

    @convert_operands(scalarRHS=True)
    @refine_operands()
    def __add__(self, other):
        if isinstance(other, AffineExpression):
            if not other.constant:
                raise NotImplementedError("You may only add a constant term to "
                    "a nonconstant PICOS sum of exponentials.")

            value = other.value

            if value < 0:
                raise NotImplementedError("You may only add a nonnegative term "
                    "to a nonconstant PICOS sum of exponentials.")

            if value == 0:
                # NOTE: We could return self here, but this is more consistent
                #       with other expressions' __add__ methods.
                sumexp = SumExponentials(self._x)
            elif self._y is None:
                sumexp = SumExponentials(self._x // math.log(value))
            else:
                sumexp = SumExponentials(self._x // value, self._y // 1)

            sumexp._typeStr = "Offset " + sumexp._typeStr
            sumexp._symbStr = glyphs.clever_add(self.string, other.string)

            return sumexp
        elif isinstance(other, SumExponentials):
            if self._y is None and other._y is None:
                sumexp = SumExponentials(self._x.vec // other._x.vec)
            elif self._y is not None and other._y is None:
                one = AffineExpression.from_constant(1.0, (other.n, 1))
                sumexp = SumExponentials(
                    self._x.vec // other._x.vec, self._y.vec // one)
            elif self._y is None and other._y is not None:
                one = AffineExpression.from_constant(1.0, (self.n, 1))
                sumexp = SumExponentials(
                    self._x.vec // other._x.vec, one // other._y.vec)
            else:
                sumexp = SumExponentials(
                    self._x.vec // other._x.vec, self._y.vec // other._y.vec)

            sumexp._symbStr = glyphs.clever_add(self.string, other.string)

            return sumexp
        else:
            return NotImplemented

    @convert_operands(scalarRHS=True)
    @refine_operands()
    def __radd__(self, other):
        if isinstance(other, (AffineExpression, SumExponentials)):
            sumexp = self.__add__(other)
            # NOTE: __add__ always creates a fresh expression.
            sumexp._symbStr = glyphs.clever_add(other.string, self.string)
            return sumexp
        else:
            return NotImplemented

    @convert_operands(scalarRHS=True)
    @refine_operands()
    def __mul__(self, other):
        if isinstance(other, AffineExpression):
            if not other.constant:
                raise NotImplementedError("You may only multiply a nonconstant "
                    "PICOS sum of exponentials with a constant term.")

            value = other.value

            if value < 0:
                raise NotImplementedError("You may only multiply a nonconstant "
                    "PICOS sum of exponential with a nonnegative term.")

            if value == 0:
                return AffineExpression.zero()

            if self._y is None:
                sumexp = SumExponentials(self._x + math.log(value))
            else:
                sumexp = SumExponentials(self._x * value, self._y * value)

            sumexp._typeStr = "Scaled " + sumexp._typeStr
            sumexp._symbStr = glyphs.clever_mul(self.string, other.string)

            return sumexp
        else:
            return NotImplemented

    @convert_operands(scalarRHS=True)
    @refine_operands()
    def __rmul__(self, other):
        if isinstance(other, AffineExpression):
            sumexp = self.__mul__(other)
            # NOTE: __mul__ always creates a fresh expression.
            sumexp._symbStr = glyphs.clever_mul(other.string, self.string)
            return sumexp
        else:
            return NotImplemented

    @convert_operands(scalarRHS=True)
    @refine_operands()
    def __truediv__(self, other):
        if isinstance(other, AffineExpression):
            if not other.constant:
                raise NotImplementedError("You may only divide a nonconstant "
                    "PICOS sum of exponentials by a constant term.")

            value = other.value

            if value <= 0:
                raise NotImplementedError("You may only divide a nonconstant "
                    "PICOS sum of exponential by a positive term.")

            sumexp = self * (1.0 / value)
            # NOTE: __mul__ always creates a fresh expression.
            sumexp._symbStr = glyphs.div(self.string, other.string)
        else:
            return NotImplemented

    # --------------------------------------------------------------------------
    # Methods and properties that return expressions.
    # --------------------------------------------------------------------------

    @property
    def x(self):
        """The expression :math:`x`."""
        return self._x

    @property
    def y(self):
        """The additional expression :math:`y`, or :obj:`None`."""
        return self._y

    @cached_property
    def log(self):
        """The logarithm of the expression."""
        from . import LogSumExp

        if self._y is not None:
            raise NotImplementedError("May only take the logarithm of a sum of"
                " exponentials, not of a sum of exponential perspectives.")

        return LogSumExp(self._x)

    # --------------------------------------------------------------------------
    # Methods and properties that describe the expression.
    # --------------------------------------------------------------------------

    @property
    def n(self):
        """Length of :attr:`x`."""
        return len(self._x)

    # --------------------------------------------------------------------------
    # Constraint-creating operators, and _predict.
    # --------------------------------------------------------------------------

    @classmethod
    def _predict(cls, subtype, relation, other):
        assert isinstance(subtype, cls.Subtype)

        if relation == operator.__le__:
            if issubclass(other.clstype, AffineExpression) \
            and other.subtype.dim == 1:
                return SumExponentialsConstraint.make_type(
                    argdim=subtype.argdim,
                    lse_representable=(not subtype.y and other.subtype.nonneg))
            elif issubclass(other.clstype, SumExponentials):
                if subtype.y or other.subtype.y:
                    return NotImplemented

                if other.subtype.argdim != 1:
                    return NotImplemented

                return LogSumExpConstraint.make_type(argdim=subtype.argdim)

        return NotImplemented

    @convert_operands(scalarRHS=True)
    @validate_prediction
    @refine_operands()
    def __le__(self, other):
        from . import LogSumExp

        if isinstance(other, AffineExpression):
            return SumExponentialsConstraint(self, other)
        elif isinstance(other, SumExponentials):
            if self._y is not None or other._y is not None:
                raise NotImplementedError("Comparing two sums of exponentials "
                    "is not supported if either expression has the additional "
                    "perspectives parameter y set.")

            if other.n != 1:
                raise NotImplementedError("You may only upper bound a sum of "
                    "exponentials by a single exponential, not by another sum.")

            return LogSumExp(self._x) <= other._x
        else:
            return NotImplemented


# --------------------------------------
__all__ = api_end(_API_START, globals())
