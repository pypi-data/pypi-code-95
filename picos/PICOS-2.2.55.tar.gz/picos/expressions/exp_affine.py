# ------------------------------------------------------------------------------
# Copyright (C) 2019-2020 Maximilian Stahlberg
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

"""Implements affine expression types."""

import operator
from collections import namedtuple

import numpy

from .. import glyphs
from ..apidoc import api_end, api_start
from ..caching import cached_property, cached_unary_operator
from ..constraints import (AffineConstraint, ComplexAffineConstraint,
                           ComplexLMIConstraint, Constraint, LMIConstraint)
from .data import convert_operands, cvx2np, load_data, sparse_quadruple
from .exp_biaffine import BiaffineExpression
from .expression import (Expression, ExpressionType, refine_operands,
                         validate_prediction)

_API_START = api_start(globals())
# -------------------------------


class ComplexAffineExpression(BiaffineExpression):
    """A multidimensional (complex) affine expression.

    Base class for the real :class:`AffineExpression`.
    """

    # --------------------------------------------------------------------------
    # Abstract method implementations for Expression.
    # --------------------------------------------------------------------------

    Subtype = namedtuple("Subtype", ("shape", "constant", "nonneg"))
    Subtype.dim = property(lambda self: self.shape[0] * self.shape[1])

    def _get_subtype(self):
        """Implement :meth:`~.expression.Expression._get_subtype`."""
        nonneg = self.constant and self.isreal \
            and all(x >= 0 for x in self.value_as_matrix)

        return self.Subtype(self._shape, self.constant, nonneg)

    # --------------------------------------------------------------------------
    # Method overridings for Expression.
    # --------------------------------------------------------------------------

    @cached_unary_operator
    def _get_refined(self):
        """Implement :meth:`~.expression.Expression._get_refined`."""
        if self.isreal:
            return AffineExpression(self._symbStr, self._shape, self._coefs)
        else:
            return self

    @convert_operands(sameShape=True, allowNone=True)
    def _set_value(self, value):
        """Override :meth:`~.expression.Expression._set_value`."""
        if value is None:
            for var in self._linear_coefs:
                var.value = None
            return

        # Since all variables are real-valued, prevent NumPy from finding
        # complex-valued solutions that do not actually work.
        (self.real // self.imag).renamed(self.string).value \
            = (value.real // value.imag)

    # --------------------------------------------------------------------------
    # Abstract method implementations for BiaffineExpression.
    # --------------------------------------------------------------------------

    @classmethod
    def _get_bilinear_terms_allowed(cls):
        """Implement for :class:`~.exp_biaffine.BiaffineExpression`."""
        return False

    @classmethod
    def _get_parameters_allowed(cls):
        """Implement for :class:`~.exp_biaffine.BiaffineExpression`."""
        return False

    @classmethod
    def _get_basetype(cls):
        """Implement :meth:`~.exp_biaffine.BiaffineExpression._get_basetype`."""
        return ComplexAffineExpression

    @classmethod
    def _get_typecode(cls):
        """Implement :meth:`~.exp_biaffine.BiaffineExpression._get_typecode`."""
        return "z"

    # --------------------------------------------------------------------------
    # Method overridings for BiaffineExpression: Binary operators.
    # --------------------------------------------------------------------------

    @convert_operands(sameShape=True)
    @refine_operands(stop_at_affine=True)
    def __or__(self, other):
        """Extend :meth:`~.exp_biaffine.BiaffineExpression.__or__`.

        The scalar product of two nonconstant (complex) affine expressions is in
        general a :class:`~.exp_quadratic.QuadraticExpression`.
        """
        from .exp_quadratic import QuadraticExpression
        from .exp_sqnorm import SquaredNorm

        if isinstance(other, ComplexAffineExpression) \
        and not self.constant and not other.constant:
            # Create a squared norm if possible.
            # NOTE: Must not check self.equals(other) here; see SquaredNorm.
            # TODO: Consider creating a helper function for __or__ that always
            #       returns a QuadraticExpression instead of a SquaredNorm to be
            #       used within SquaredNorm. Then equals would be possible here.
            if self is other:
                return SquaredNorm(self)

            string = glyphs.clever_dotp(
                self.string, other.string, other.complex, self.scalar)

            # Handle the complex case: Conjugate the right hand side.
            other = other.conj

            Cs, Co = self._constant_coef, other._constant_coef

            # Compute the affine part of the product.
            affString = glyphs.affpart(string)
            affCoefs = {(): Cs.T * Co}
            for var in self.variables.union(other.variables):
                if var not in other._linear_coefs:
                    affCoefs[var] = Co.T * self._linear_coefs[var]
                elif var not in self._linear_coefs:
                    affCoefs[var] = Cs.T * other._linear_coefs[var]
                else:
                    affCoefs[var] = Co.T * self._linear_coefs[var] + \
                        Cs.T * other._linear_coefs[var]
            affPart = self._common_basetype(other)(affString, (1, 1), affCoefs)

            # Compute the quadratic part of the product.
            quadPart = {(v, w): self._linear_coefs[v].T * other._linear_coefs[w]
                for v in self._linear_coefs for w in other._linear_coefs}

            # Don't create quadratic expressions without a quadratic part.
            if not any(quadPart.values()):
                affPart._symbStr = string
                return affPart

            # Remember a factorization into two real scalars if applicable.
            # NOTE: If the user enters a multiplication a*b of two scalar affine
            #       expressions, then we have, at this point, self == a.T == a
            #       and other == b.conj.conj == b.
            if len(self) == 1 and len(other) == 1 \
            and self.isreal and other.isreal:
                factors = (self.refined, other.refined)
            else:
                factors = None

            return QuadraticExpression(
                string, quadPart, affPart, scalarFactors=factors)
        else:
            return BiaffineExpression.__or__(self, other)

    @convert_operands(rMatMul=True)
    @refine_operands(stop_at_affine=True)
    def __mul__(self, other):
        """Extend :meth:`~.exp_biaffine.BiaffineExpression.__mul__`.

        The matrix product of two nonconstant scalar (complex) affine
        expressions is a :class:`~.exp_quadratic.QuadraticExpression`.
        """
        if isinstance(other, ComplexAffineExpression) \
        and not self.constant and not other.constant:
            # If the result is scalar, allow for quadratic terms.
            if self._shape[0] == 1 and other._shape[1] == 1 \
            and self._shape[1] == other._shape[0]:
                result = self.T.__or__(other.conj)

                # NOTE: __or__ always creates a fresh expression.
                result._symbStr = glyphs.clever_mul(self.string, other.string)

                return result
            else:
                raise NotImplementedError(
                    "PICOS does not support multidimensional quadratic "
                    "expressions at this point. More precisely, one factor must"
                    " be constant or the result must be scalar.")
        else:
            return BiaffineExpression.__mul__(self, other)

    @convert_operands(sameShape=True)
    @refine_operands(stop_at_affine=True)
    def __xor__(self, other):
        """Extend :meth:`~.exp_biaffine.BiaffineExpression.__xor__`.

        The hadamard product of two nonconstant scalar (complex) affine
        expressions is a :class:`~.exp_quadratic.QuadraticExpression`.
        """
        if isinstance(other, ComplexAffineExpression) \
        and not self.constant and not other.constant:
            # If the result is scalar, allow for quadratic terms.
            if self._shape == (1, 1):
                result = self.__or__(other.conj)

                # NOTE: __or__ always creates a fresh expression.
                result._symbStr = glyphs.hadamard(self.string, other.string)

                return result
            else:
                raise NotImplementedError(
                    "PICOS does not support multidimensional quadratic "
                    "expressions at this point. More precisely, one factor must"
                    " be constant or the result must be scalar.")
        else:
            return BiaffineExpression.__xor__(self, other)

    # TODO: Create a quadratic expression from a scalar Kronecker prod.

    # --------------------------------------------------------------------------
    # Method overridings for BiaffineExpression: Unary operators.
    # --------------------------------------------------------------------------

    @cached_property
    def real(self):
        """Override :meth:`~.exp_biaffine.BiaffineExpression.real`.

        The result is returned as an :meth:`AffineExpression`.
        """
        return AffineExpression(glyphs.real(self.string), self._shape,
            {vars: coef.real() for vars, coef in self._coefs.items()})

    @cached_property
    def imag(self):
        """Override :meth:`~.exp_biaffine.BiaffineExpression.imag`.

        The result is returned as an :meth:`AffineExpression`.
        """
        return AffineExpression(glyphs.imag(self.string), self._shape,
            {vars: coef.imag() for vars, coef in self._coefs.items()})

    # --------------------------------------------------------------------------
    # Additional unary operators.
    # --------------------------------------------------------------------------

    @cached_unary_operator
    def __abs__(self):
        """Denote the Euclidean or Frobenius norm of the expression."""
        from . import Norm

        return Norm(self)

    # --------------------------------------------------------------------------
    # Constraint-creating operators, and _predict.
    # --------------------------------------------------------------------------

    @classmethod
    def _predict(cls, subtype, relation, other):
        assert isinstance(subtype, cls.Subtype)

        from .set import Set

        if relation == operator.__eq__:
            if issubclass(other.clstype, ComplexAffineExpression):
                return ComplexAffineConstraint.make_type(dim=subtype.dim)
        elif relation == operator.__lshift__:
            if issubclass(other.clstype, ComplexAffineExpression):
                return ComplexLMIConstraint.make_type(int(subtype.dim**0.5))
            elif issubclass(other.clstype, Set):
                other_type = ExpressionType(cls, subtype)
                return other.predict(operator.__rshift__, other_type)
        elif relation == operator.__rshift__:
            if issubclass(other.clstype, ComplexAffineExpression):
                return ComplexLMIConstraint.make_type(int(subtype.dim**0.5))

        return NotImplemented

    @convert_operands(sameShape=True)
    @validate_prediction
    @refine_operands()
    def __eq__(self, other):
        if isinstance(other, ComplexAffineExpression):
            return ComplexAffineConstraint(self, other)
        else:
            return NotImplemented

    # Since we define __eq__, __hash__ is not inherited. Do this manually.
    __hash__ = Expression.__hash__

    def _lshift_implementation(self, other):
        if isinstance(other, ComplexAffineExpression):
            return ComplexLMIConstraint(self, Constraint.LE, other)
        else:
            return NotImplemented

    def _rshift_implementation(self, other):
        if isinstance(other, ComplexAffineExpression):
            return ComplexLMIConstraint(self, Constraint.GE, other)
        else:
            return NotImplemented

    # --------------------------------------------------------------------------
    # Interface for PICOS-internal use.
    # --------------------------------------------------------------------------

    def sparse_rows(
            self, varOffsetMap, lowerTriangle=False, upperTriangle=False,
            indexFunction=None):
        """Return a sparse list representation of the expression.

        The method is intended for internal use: It simplifies passing affine
        constraints to solvers that support only scalar constraints. The idea is
        to pose the constraint as a single (multidimensional) affine expression
        bounded by zero, and use the coefficients and the constant term of this
        expression to fill the solver's constraint matrix (with columns
        representing scalar variables and rows representing scalar constraints).

        :param dict varOffsetMap: Maps variables to column offsets.
        :param bool lowerTriangle: Whether to return only the lower triangular
            part of the expression.
        :param bool upperTriangle: Whether to return only the upper triangular
            part of the expression.
        :param indexFunction: Instead of adding the local variable index to the
            value returned by varOffsetMap, use the return value of this
            function, that takes as argument the variable and its local index,
            as the "column index", which need not be an integer. When this
            parameter is passed, the parameter varOffsetMap is ignored.

        :returns: A list of triples (J, V, c) where J contains column indices
            (representing scalar variables), V contains coefficients for each
            column index and c is a constant term.
        """
        if lowerTriangle and upperTriangle:
            lowerTriangle = False
            upperTriangle = False

        rows = []
        numRows = len(self)
        m = self.size[0]

        for row in range(numRows):
            i, j = row % m, row // m

            if lowerTriangle and i < j:
                rows.append(None)
            elif upperTriangle and j < i:
                rows.append(None)
            else:
                rows.append([[], [], 0.0])

        for var, coef in self._linear_coefs.items():
            V, I, J, _ = sparse_quadruple(coef)

            for localCoef, localConIndex, localVarIndex in zip(V, I, J):
                row = rows[localConIndex]

                if not row:
                    continue

                # TODO: Use a single parameter for both types.
                if indexFunction:
                    row[0].append(indexFunction(var, localVarIndex))
                else:
                    row[0].append(varOffsetMap[var] + localVarIndex)

                row[1].append(localCoef)

        for localConIndex in range(numRows):
            row = rows[localConIndex]

            if not row:
                continue

            row[2] = self._constant_coef[localConIndex]

        return [row for row in rows if row]


class AffineExpression(ComplexAffineExpression):
    """A multidimensional real affine expression."""

    # --------------------------------------------------------------------------
    # Method overridings for BiaffineExpression.
    # --------------------------------------------------------------------------

    @property
    def isreal(self):
        """Always true for :class:`AffineExpression` instances."""  # noqa
        return True

    @property
    def real(self):
        """The :class:`AffineExpression` as is."""  # noqa
        return self

    @cached_property
    def imag(self):
        """A zero of same shape as the :class:`AffineExpression`."""  # noqa
        return self._basetype.zero(self._shape)

    @property
    def conj(self):
        """The :class:`AffineExpression` as is."""  # noqa
        return self

    @property
    def H(self):
        """The regular transpose of the :class:`AffineExpression`."""  # noqa
        return self.T

    # --------------------------------------------------------------------------
    # Method overridings for ComplexAffineExpression.
    # --------------------------------------------------------------------------

    @classmethod
    def _get_basetype(cls):
        return AffineExpression

    @classmethod
    def _get_typecode(cls):
        return "d"

    def _get_refined(self):
        return self

    @convert_operands(sameShape=True, allowNone=True)
    def _set_value(self, value):
        if value is None:
            for var in self._linear_coefs:
                var.value = None
            return

        if not isinstance(value, AffineExpression) or not value.constant:
            raise TypeError("Cannot set the value of {} to {}: Not real or not "
                "a constant.".format(repr(self), repr(value)))

        if self.constant:
            raise TypeError("Cannot set the value on a constant expression.")

        y = cvx2np(value._constant_coef)

        A = []
        for var, coef in self._linear_coefs.items():
            A.append(cvx2np(coef))
        assert A

        A = numpy.hstack(A)
        b = y - cvx2np(self._constant_coef)

        try:
            solution, residual, _, _ = numpy.linalg.lstsq(A, b, rcond=None)
        except numpy.linalg.LinAlgError as error:
            raise RuntimeError("Setting a value on {} by means of a least-"
                "squares solution failed.".format(self.string)) from error

        if not numpy.allclose(residual, 0):
            raise ValueError("Setting a value on {} failed: No exact solution "
                "to the associated linear system found.".format(self.string))

        offset = 0
        for var in self._linear_coefs:
            var.internal_value = solution[offset:offset+var.dim]
            offset += var.dim

    # --------------------------------------------------------------------------
    # Additional unary operators.
    # --------------------------------------------------------------------------

    @cached_property
    def exp(self):
        """The exponential function applied to the expression."""  # noqa
        from . import SumExponentials
        return SumExponentials(self)

    @cached_property
    def log(self):
        """The Logarithm of the expression."""  # noqa
        from . import Logarithm
        return Logarithm(self)

    # --------------------------------------------------------------------------
    # Constraint-creating operators, and _predict.
    # --------------------------------------------------------------------------

    @classmethod
    def _predict(cls, subtype, relation, other):
        assert isinstance(subtype, cls.Subtype)

        if relation in (operator.__eq__, operator.__le__, operator.__ge__):
            if issubclass(other.clstype, AffineExpression):
                return AffineConstraint.make_type(
                    dim=subtype.dim, eq=(relation is operator.__eq__))
        elif relation == operator.__lshift__:
            if issubclass(other.clstype, AffineExpression):
                return LMIConstraint.make_type(int(subtype.dim**0.5))
            elif issubclass(other.clstype, ComplexAffineExpression):
                return ComplexLMIConstraint.make_type(int(subtype.dim**0.5))
        elif relation == operator.__rshift__:
            if issubclass(other.clstype, AffineExpression):
                return LMIConstraint.make_type(int(subtype.dim**0.5))
            elif issubclass(other.clstype, ComplexAffineExpression):
                return ComplexLMIConstraint.make_type(int(subtype.dim**0.5))

        return NotImplemented

    @convert_operands(sameShape=True)
    @validate_prediction
    @refine_operands()
    def __le__(self, other):
        if isinstance(other, AffineExpression):
            return AffineConstraint(self, Constraint.LE, other)
        else:
            return NotImplemented

    @convert_operands(sameShape=True)
    @validate_prediction
    @refine_operands()
    def __ge__(self, other):
        if isinstance(other, AffineExpression):
            return AffineConstraint(self, Constraint.GE, other)
        else:
            return NotImplemented

    @convert_operands(sameShape=True)
    @validate_prediction
    @refine_operands()
    def __eq__(self, other):
        if isinstance(other, AffineExpression):
            return AffineConstraint(self, Constraint.EQ, other)
        else:
            return NotImplemented

    # Since we define __eq__, __hash__ is not inherited. Do this manually.
    __hash__ = Expression.__hash__

    def _lshift_implementation(self, other):
        if isinstance(other, AffineExpression):
            return LMIConstraint(self, Constraint.LE, other)
        elif isinstance(other, ComplexAffineExpression):
            return ComplexLMIConstraint(self, Constraint.LE, other)
        else:
            return NotImplemented

    def _rshift_implementation(self, other):
        if isinstance(other, AffineExpression):
            return LMIConstraint(self, Constraint.GE, other)
        elif isinstance(other, ComplexAffineExpression):
            return ComplexLMIConstraint(self, Constraint.GE, other)
        else:
            return NotImplemented


def Constant(name_or_value, value=None, shape=None):
    """Create a constant PICOS expression.

    Loads the given numeric value as a constant
    :class:`~picos.expressions.ComplexAffineExpression` or
    :class:`~picos.expressions.AffineExpression`, depending on the value.
    Optionally, the value is broadcasted or reshaped according to the shape
    argument.

    :param str name_or_value: Symbolic string description of the constant. If
        :obj:`None` or the empty string, a string will be generated. If this is
        the only positional parameter (i.e.``value`` is not given), then this
        position is used as the value argument instead!
    :param value: The numeric constant to load.

    See :func:`~.data.load_data` for supported data formats and broadcasting and
    reshaping rules.

    :Example:

    >>> from picos import Constant
    >>> Constant(1)
    <1×1 Real Constant: 1>
    >>> Constant(1, shape=(2, 2))
    <2×2 Real Constant: [1]>
    >>> Constant("one", 1)
    <1×1 Real Constant: one>
    >>> Constant("J", 1, (2, 2))
    <2×2 Real Constant: J>
    """
    if value is None:
        value = name_or_value
        name  = None
    else:
        name  = name_or_value

    value, valStr = load_data(value, shape)

    if value.typecode == "z":
        cls = ComplexAffineExpression
    else:
        cls = AffineExpression

    return cls(name if name else valStr, value.size, {(): value})


# --------------------------------------
__all__ = api_end(_API_START, globals())
