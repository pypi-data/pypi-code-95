# ------------------------------------------------------------------------------
# Copyright (C) 2018-2019 Maximilian Stahlberg
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

"""Implementation of :class:`CPLEXSolver`."""

import time
from collections import namedtuple

import cvxopt

from ..apidoc import api_end, api_start
from ..constraints import (AffineConstraint, ConvexQuadraticConstraint,
                           DummyConstraint, RSOCConstraint, SOCConstraint)
from ..expressions import (CONTINUOUS_VARTYPES, AffineExpression,
                           BinaryVariable, IntegerVariable,
                           QuadraticExpression)
from ..modeling.footprint import Specification
from ..modeling.solution import (PS_FEASIBLE, PS_ILLPOSED, PS_INF_OR_UNB,
                                 PS_INFEASIBLE, PS_UNBOUNDED, PS_UNKNOWN,
                                 PS_UNSTABLE, SS_EMPTY, SS_FAILURE,
                                 SS_FEASIBLE, SS_INFEASIBLE, SS_OPTIMAL,
                                 SS_PREMATURE, SS_UNKNOWN)
from .solver import (ConflictingOptionsError, DependentOptionError, Solver,
                     UnsupportedOptionError)

_API_START = api_start(globals())
# -------------------------------


#: Maps CPLEX status code to PICOS status triples.
CPLEX_STATUS_CODES = {
    # primal status, dual status,   problem status
1:   (SS_OPTIMAL,    SS_OPTIMAL,    PS_FEASIBLE),    # CPX_STAT_OPTIMAL
2:   (SS_UNKNOWN,    SS_INFEASIBLE, PS_UNBOUNDED),   # CPX_STAT_UNBOUNDED
3:   (SS_INFEASIBLE, SS_UNKNOWN,    PS_INFEASIBLE),  # CPX_STAT_INFEASIBLE
4:   (SS_UNKNOWN,    SS_UNKNOWN,    PS_INF_OR_UNB),  # CPX_STAT_INForUNBD
5:   (SS_INFEASIBLE, SS_UNKNOWN,    PS_UNSTABLE),    # CPX_STAT_OPTIMAL_INFEAS
6:   (SS_UNKNOWN,    SS_UNKNOWN,    PS_UNSTABLE),    # CPX_STAT_NUM_BEST
    # 7—9 are not defined.
10:  (SS_PREMATURE,  SS_PREMATURE,  PS_UNKNOWN),     # CPX_STAT_ABORT_IT_LIM
11:  (SS_PREMATURE,  SS_PREMATURE,  PS_UNKNOWN),     # CPX_STAT_ABORT_TIME_LIM
12:  (SS_PREMATURE,  SS_PREMATURE,  PS_UNKNOWN),     # CPX_STAT_ABORT_OBJ_LIM
13:  (SS_PREMATURE,  SS_PREMATURE,  PS_UNKNOWN),     # CPX_STAT_ABORT_USER
    # 14—19 seem irrelevant (CPX_STAT_*_RELAXED_*).
20:  (SS_UNKNOWN,    SS_UNKNOWN,    PS_ILLPOSED),    # …_OPTIMAL_FACE_UNBOUNDED
21:  (SS_PREMATURE,  SS_PREMATURE,  PS_UNKNOWN),     # …_ABORT_PRIM_OBJ_LIM
22:  (SS_PREMATURE,  SS_PREMATURE,  PS_UNKNOWN),     # …_ABORT_DUAL_OBJ_LIM
23:  (SS_FEASIBLE,   SS_FEASIBLE,   PS_FEASIBLE),    # CPX_STAT_FEASIBLE
    # 24 irrelevant (CPX_STAT_FIRSTORDER).
25:  (SS_PREMATURE,  SS_PREMATURE,  PS_UNKNOWN),     # …_ABORT_DETTIME_LIM
    # 26—29 are not defined.
    # 30—39 seem irrelevant (CPX_STAT_CONFLICT_*).
    # 40—100 are not defined.
101: (SS_OPTIMAL,    SS_EMPTY,      PS_FEASIBLE),    # CPXMIP_OPTIMAL
102: (SS_OPTIMAL,    SS_EMPTY,      PS_FEASIBLE),    # CPXMIP_OPTIMAL_TOL
103: (SS_INFEASIBLE, SS_EMPTY,      PS_INFEASIBLE),  # CPXMIP_INFEASIBLE
104: (SS_PREMATURE,  SS_EMPTY,      PS_UNKNOWN),     # CPXMIP_SOL_LIM          ?
105: (SS_FEASIBLE,   SS_EMPTY,      PS_FEASIBLE),    # CPXMIP_NODE_LIM_FEAS
106: (SS_PREMATURE,  SS_EMPTY,      PS_UNKNOWN),     # CPXMIP_NODE_LIM_INFEAS
107: (SS_FEASIBLE,   SS_EMPTY,      PS_FEASIBLE),    # CPXMIP_TIME_LIM_FEAS
108: (SS_PREMATURE,  SS_EMPTY,      PS_UNKNOWN),     # CPXMIP_TIME_LIM_INFEAS
109: (SS_FEASIBLE,   SS_EMPTY,      PS_FEASIBLE),    # CPXMIP_FAIL_FEAS
110: (SS_FAILURE,    SS_EMPTY,      PS_UNKNOWN),     # CPXMIP_FAIL_INFEAS
111: (SS_FEASIBLE,   SS_EMPTY,      PS_FEASIBLE),    # CPXMIP_MEM_LIM_FEAS
112: (SS_PREMATURE,  SS_EMPTY,      PS_UNKNOWN),     # CPXMIP_MEM_LIM_INFEAS
113: (SS_FEASIBLE,   SS_EMPTY,      PS_FEASIBLE),    # CPXMIP_ABORT_FEAS
114: (SS_PREMATURE,  SS_EMPTY,      PS_UNKNOWN),     # CPXMIP_ABORT_INFEAS
115: (SS_INFEASIBLE, SS_EMPTY,      PS_UNSTABLE),    # CPXMIP_OPTIMAL_INFEAS
116: (SS_FEASIBLE,   SS_EMPTY,      PS_FEASIBLE),    # CPXMIP_FAIL_FEAS_NO_TREE
117: (SS_FAILURE,    SS_EMPTY,      PS_UNKNOWN),     # …_FAIL_INFEAS_NO_TREE
118: (SS_UNKNOWN,    SS_EMPTY,      PS_UNBOUNDED),   # CPXMIP_UNBOUNDED
119: (SS_UNKNOWN,    SS_EMPTY,      PS_INF_OR_UNB),  # CPXMIP_INForUNBD
    # 120—126 seem irrelevant (CPXMIP_*_RELAXED_*).
127: (SS_FEASIBLE,   SS_EMPTY,      PS_FEASIBLE),    # CPXMIP_FEASIBLE
128: (SS_OPTIMAL,    SS_EMPTY,      PS_FEASIBLE),    # …_POPULATESOL_LIM       ?
129: (SS_OPTIMAL,    SS_EMPTY,      PS_FEASIBLE),    # …_OPTIMAL_POPULATED     ?
130: (SS_OPTIMAL,    SS_EMPTY,      PS_FEASIBLE),    # …_OPTIMAL_POPULATED_TOL ?
131: (SS_FEASIBLE,   SS_EMPTY,      PS_FEASIBLE),    # CPXMIP_DETTIME_LIM_FEAS
132: (SS_PREMATURE,  SS_EMPTY,      PS_UNKNOWN),     # CPXMIP_DETTIME_LIM_INFEAS
}


class CPLEXSolver(Solver):
    """Interface to the CPLEX solver via its official Python interface.

    .. note ::
        Names are used instead of indices for identifying both variables and
        constraints since indices can change if the CPLEX instance is modified.
    """

    # NOTE: When making changes, also see the section in _solve that tells CPLEX
    #       the problem type.
    SUPPORTED = Specification(
        objectives=[
            AffineExpression,
            QuadraticExpression],
        constraints=[
            DummyConstraint,
            AffineConstraint,
            SOCConstraint,
            RSOCConstraint,
            ConvexQuadraticConstraint])

    NONCONVEX_QP = Specification(
        objectives=[QuadraticExpression],
        constraints=[DummyConstraint, AffineConstraint])

    @classmethod
    def supports(cls, footprint, explain=False):
        """Implement :meth:`~.solver.Solver.supports`."""
        result = Solver.supports(footprint, explain)
        if not result or (explain and not result[0]):
            return result

        # Support QPs and MIQPs with a nonconvex objective.
        # NOTE: SUPPORTED fully excludes nonconvex quadratic constraints. This
        #       further excludes QCQPs and MIQCQPs with a nonconvex objective.
        # TODO: See which of the excluded cases can be supported as well.
        if footprint.nonconvex_quadratic_objective \
        and footprint not in cls.NONCONVEX_QP:
            if explain:
                return (False, "(MI)QCQPs with nonconvex objective.")
            else:
                return False

        if footprint not in cls.SUPPORTED:
            if explain:
                return False, cls.SUPPORTED.mismatch_reason(footprint)
            else:
                return False

        return (True, None) if explain else True

    @classmethod
    def default_penalty(cls):
        """Implement :meth:`~.solver.Solver.default_penalty`."""
        return 0.0  # Commercial solver.

    @classmethod
    def test_availability(cls):
        """Implement :meth:`~.solver.Solver.test_availability`."""
        cls.check_import("cplex")

    @classmethod
    def names(cls):
        """Implement :meth:`~.solver.Solver.names`."""
        return "cplex", "CPLEX", "IBM ILOG CPLEX Optimization Studio"

    @classmethod
    def is_free(cls):
        """Implement :meth:`~.solver.Solver.is_free`."""
        return False

    CplexSOCC = namedtuple("CplexSOCC",
        ("LHSVars", "RHSVar", "LHSCons", "RHSCon", "quadCon"))

    CplexRSOCC = namedtuple("CplexRSOCC",
        ("LHSVars", "RHSVars", "LHSCons", "RHSCons", "quadCon"))

    def __init__(self, problem):
        """Initialize a CPLEX solver interface.

        :param ~picos.Problem problem: The problem to be solved.
        """
        super(CPLEXSolver, self).__init__(problem)

        self._cplexVarName = dict()
        """Maps PICOS variable indices to CPLEX variable names."""

        self._cplexLinConNames = dict()
        """Maps a PICOS (multidimensional) linear constraint to a collection of
        CPLEX (scalar) linear constraint names."""

        self._cplexQuadConName = dict()
        """Maps a PICOS quadratic or conic quadratic constraint to a CPLEX
        quadratic constraint name."""

        self._cplexSOCC = dict()
        """Maps a PICOS second order cone constraint to its CPLEX representation
        involving auxiliary variables and constraints."""

        self._cplexRSOCC = dict()
        """Maps a PICOS rotated second order cone constraint to its CPLEX
        representation involving auxiliary variables and constraints."""

        self.nextConstraintID = 0
        """Used to create unique names for constraints."""

    def __del__(self):
        if self.int is not None:
            self.int.end()

    def reset_problem(self):
        """Implement :meth:`~.solver.Solver.reset_problem`."""
        if self.int is not None:
            self.int.end()
        self.int = None
        self._cplexVarName.clear()
        self._cplexLinConNames.clear()
        self._cplexQuadConName.clear()
        self._cplexSOCC.clear()
        self._cplexRSOCC.clear()

    def _get_unique_constraint_id(self):
        ID = self.nextConstraintID
        self.nextConstraintID += 1
        return ID

    def _make_cplex_var_names(self, picosVar, localIndex=None):
        """Make CPLEX variable names.

        Converts a PICOS variable to a list of CPLEX variable names, each
        corresponding to one scalar variable contained in the PICOS variable.
        If localIndex is given, then only the name of the CPLEX variable
        representing the scalar variable with that offset is returned.
        The name format is "picosName[localIndex]".
        """
        # TODO: This function appears in multiple solvers, move it to the Solver
        #       base class as "_make_scalar_var_names".
        if localIndex is not None:
            return "{}[{}]".format(picosVar.name, localIndex)
        else:
            return [
                self._make_cplex_var_names(picosVar, localIndex)
                for localIndex in range(picosVar.dim)]

    def _import_variable(self, picosVar):
        import cplex

        dim = picosVar.dim

        # Create names.
        names = self._make_cplex_var_names(picosVar)

        # Retrieve types.
        if isinstance(picosVar, CONTINUOUS_VARTYPES):
            types = dim * self.int.variables.type.continuous
        elif isinstance(picosVar, IntegerVariable):
            types = dim * self.int.variables.type.integer
        elif isinstance(picosVar, BinaryVariable):
            types = dim * self.int.variables.type.binary
        else:
            assert False, "Unexpected variable type."

        # Retrieve bounds.
        lowerBounds = [-cplex.infinity]*dim
        upperBounds = [cplex.infinity]*dim
        lower, upper = picosVar.bound_dicts
        for i, b in lower.items():
            lowerBounds[i] = b
        for i, b in upper.items():
            upperBounds[i] = b

        # Import variable.
        # Note that CPLEX allows importing the objective function coefficients
        # for the new variables here, but that is done later to streamline
        # updates to the objective.
        self.int.variables.add(
            lb=lowerBounds, ub=upperBounds, types=types, names=names)

        # Map PICOS indices to CPLEX names.
        for localIndex in range(dim):
            self._cplexVarName[picosVar.id_at(localIndex)] = names[localIndex]

        if self._debug():
            cplexVar = {"names": names, "types": types,
                "lowerBounds": lowerBounds, "upperBounds": upperBounds}
            self._debug(
                "Variable imported: {} → {}".format(picosVar, cplexVar))

    def _remove_variable(self, picosVar):
        cplexVarNames = [self._cplexVarName.pop(picosVar.id_at(localIndex))
            for localIndex in range(picosVar.dim)]
        self.int.variables.delete(cplexVarNames)

    def _affinexp_pic2cpl(self, picosExpression):
        import cplex
        for names, coefficients, constant in picosExpression.sparse_rows(
                None, indexFunction=self._make_cplex_var_names):
            yield cplex.SparsePair(ind=names, val=coefficients), constant

    def _scalar_affinexp_pic2cpl(self, picosExpression):
        assert len(picosExpression) == 1
        return next(self._affinexp_pic2cpl(picosExpression))

    def _quadexp_pic2cpl(self, picosExpression):
        """Transform a quadratic expression from PICOS to CPLEX.

        :returns: :class:`SparseTriple <cplex.SparseTriple>` mapping a pair of
            CPLEX variable names to scalar constants.
        """
        import cplex

        assert isinstance(picosExpression, QuadraticExpression)

        cplexI, cplexJ, cplexV = [], [], []
        for (picosVar1, picosVar2), picosCoefficients \
                in picosExpression._sparse_quads.items():
            for sparseIndex in range(len(picosCoefficients)):
                localVar1Index = picosCoefficients.I[sparseIndex]
                localVar2Index = picosCoefficients.J[sparseIndex]
                localCoefficient = picosCoefficients.V[sparseIndex]
                cplexI.append(self._cplexVarName[picosVar1.id + localVar1Index])
                cplexJ.append(self._cplexVarName[picosVar2.id + localVar2Index])
                cplexV.append(localCoefficient)

        return cplex.SparseTriple(ind1=cplexI, ind2=cplexJ, val=cplexV)

    def _import_linear_constraint(self, picosConstraint):
        import cplex

        assert isinstance(picosConstraint, AffineConstraint)

        length = len(picosConstraint)

        # Retrieve left hand side and right hand side expressions.
        cplexLHS, cplexRHS = [], []
        for names, coefficients, constant in picosConstraint.sparse_Ab_rows(
                None, indexFunction=self._make_cplex_var_names):
            cplexLHS.append(cplex.SparsePair(ind=names, val=coefficients))
            cplexRHS.append(constant)

        # Retrieve senses.
        if picosConstraint.is_increasing():
            senses = length * "L"
        elif picosConstraint.is_decreasing():
            senses = length * "G"
        elif picosConstraint.is_equality():
            senses = length * "E"
        else:
            assert False, "Unexpected constraint relation."

        # Give unique names that are used to identify the constraint. This is
        # necessary as constraint indices can change if the problem is modified.
        conID = self._get_unique_constraint_id()
        names = ["{}:{}".format(conID, localConstraintIndex)
            for localConstraintIndex in range(length)]

        if self._debug():
            cplexConstraint = {"lin_expr": cplexLHS, "senses": senses,
                "rhs": cplexRHS, "names": names}
            self._debug(
                "Linear constraint imported: {} → {}".format(
                    picosConstraint, cplexConstraint))

        # Import the constraint.
        self.int.linear_constraints.add(
            lin_expr=cplexLHS, senses=senses, rhs=cplexRHS, names=names)

        return names

    def _import_quad_constraint(self, picosConstraint):
        assert isinstance(picosConstraint, ConvexQuadraticConstraint)

        # Retrieve
        # - CPLEX' linear term, which is the linear term of the affine
        #   expression in the PICOS constraint, and
        # - CPLEX' right hand side, which is the negated constant term of the
        #   affine expression in the PICOS constraint.
        cplexLinear, cplexRHS = \
            self._scalar_affinexp_pic2cpl(picosConstraint.le0.aff)
        cplexRHS = -cplexRHS

        # Retrieve CPLEX' quadratic term.
        cplexQuad = self._quadexp_pic2cpl(picosConstraint.le0)

        # Give a unique name that is used to identify the constraint. This is
        # necessary as constraint indices can change if the problem is modified.
        name = "{}:{}".format(self._get_unique_constraint_id(), 0)

        if self._debug():
            cplexConstraint = {"lin_expr": cplexLinear, "quad_expr": cplexQuad,
                "rhs": cplexRHS, "name": name}
            self._debug(
                "Quadratic constraint imported: {} → {}".format(
                    picosConstraint, cplexConstraint))

        # Import the constraint.
        self.int.quadratic_constraints.add(lin_expr=cplexLinear,
            quad_expr=cplexQuad, sense="L", rhs=cplexRHS, name=name)

        return name

    # TODO: Handle SOC → Quadratic via a reformulation.
    def _import_socone_constraint(self, picosConstraint):
        import cplex

        assert isinstance(picosConstraint, SOCConstraint)

        picosLHS = picosConstraint.ne
        picosRHS = picosConstraint.ub
        picosLHSLen = len(picosLHS)

        # Make identifying names for the auxiliary variables and constraints.
        conID = self._get_unique_constraint_id()
        cplexLHSVars = ["{}:V{}".format(conID, i) for i in range(picosLHSLen)]
        cplexRHSVar  = "{}:V{}".format(conID, picosLHSLen)
        cplexLHSCons = ["{}:C{}".format(conID, i) for i in range(picosLHSLen)]
        cplexRHSCon  = "{}:C{}".format(conID, picosLHSLen)
        cplexQuadCon = "{}:C{}".format(conID, picosLHSLen + 1)

        # Add auxiliary variables: One for every dimension of the left hand side
        # of the PICOS constraint and one for its right hand side.
        self.int.variables.add(
            names=cplexLHSVars, lb=[-cplex.infinity] * picosLHSLen,
            ub=[+cplex.infinity] * picosLHSLen,
            types=self.int.variables.type.continuous * picosLHSLen)
        self.int.variables.add(
            names=[cplexRHSVar], lb=[0.0], ub=[+cplex.infinity],
            types=self.int.variables.type.continuous)

        # Add constraints that identify the left hand side CPLEX auxiliary
        # variables with their slice of the PICOS left hand side expression.
        cplexLHSConsLHSs = []
        cplexLHSConsRHSs = []
        for localConIndex, (localLinExp, localConstant) in \
                enumerate(self._affinexp_pic2cpl(picosLHS)):
            localConstant = -localConstant
            localLinExp.ind.append(cplexLHSVars[localConIndex])
            localLinExp.val.append(-1.0)
            cplexLHSConsLHSs.append(localLinExp)
            cplexLHSConsRHSs.append(localConstant)
        self.int.linear_constraints.add(
            names=cplexLHSCons, lin_expr=cplexLHSConsLHSs,
            senses="E" * picosLHSLen, rhs=cplexLHSConsRHSs)

        # Add a constraint that identifies the right hand side CPLEX auxiliary
        # variable with the PICOS right hand side scalar expression.
        cplexRHSConLHS, cplexRHSConRHS = \
            self._scalar_affinexp_pic2cpl(-picosRHS)
        cplexRHSConRHS = -cplexRHSConRHS
        cplexRHSConLHS.ind.append(cplexRHSVar)
        cplexRHSConLHS.val.append(1.0)
        self.int.linear_constraints.add(
            names=[cplexRHSCon], lin_expr=[cplexRHSConLHS],
            senses="E", rhs=[cplexRHSConRHS])

        # Add a quadratic constraint over the auxiliary variables that
        # represents the PICOS second order cone constraint itself.
        quadIndices = [cplexRHSVar] + list(cplexLHSVars)
        quadExpr = cplex.SparseTriple(
            ind1=quadIndices, ind2=quadIndices, val=[-1.0] + [1.0]*picosLHSLen)
        self.int.quadratic_constraints.add(
            name=cplexQuadCon, quad_expr=quadExpr, sense="L", rhs=0.0)

        cplexMetaCon = self.CplexSOCC(LHSVars=cplexLHSVars, RHSVar=cplexRHSVar,
            LHSCons=cplexLHSCons, RHSCon=cplexRHSCon, quadCon=cplexQuadCon)

        if self._debug():
            cplexCons = {
                "LHSs of LHS auxiliary equalities": cplexLHSConsLHSs,
                "RHSs of LHS auxiliary equalities": cplexLHSConsRHSs,
                "LHS of RHS auxiliary equality": cplexRHSConLHS,
                "RHS of RHS auxiliary equality": cplexRHSConRHS,
                "Non-positive quadratic term": quadExpr}
            self._debug(
                "SOcone constraint imported: {} → {}, {}".format(
                    picosConstraint, cplexMetaCon, cplexCons))

        return cplexMetaCon

    # TODO: Handle RSOC → Quadratic via a reformulation.
    def _import_rscone_constraint(self, picosConstraint):
        import cplex

        assert isinstance(picosConstraint, RSOCConstraint)

        picosLHS = picosConstraint.ne
        picosRHS1 = picosConstraint.ub1
        picosRHS2 = picosConstraint.ub2
        picosLHSLen = len(picosLHS)

        # Make identifying names for the auxiliary variables and constraints.
        conID = self._get_unique_constraint_id()
        cplexLHSVars = ["{}:V{}".format(conID, i) for i in range(picosLHSLen)]
        cplexRHSVars = ["{}:V{}".format(conID, picosLHSLen + i) for i in (0, 1)]
        cplexLHSCons = ["{}:C{}".format(conID, i) for i in range(picosLHSLen)]
        cplexRHSCons = ["{}:C{}".format(conID, picosLHSLen + i) for i in (0, 1)]
        cplexQuadCon = "{}:C{}".format(conID, picosLHSLen + 2)

        # Add auxiliary variables: One for every dimension of the left hand side
        # of the PICOS constraint and two for its right hand side.
        self.int.variables.add(
            names=cplexLHSVars, lb=[-cplex.infinity] * picosLHSLen,
            ub=[+cplex.infinity] * picosLHSLen,
            types=self.int.variables.type.continuous * picosLHSLen)
        self.int.variables.add(
            names=cplexRHSVars, lb=[0.0, 0.0], ub=[+cplex.infinity] * 2,
            types=self.int.variables.type.continuous * 2)

        # Add constraints that identify the left hand side CPLEX auxiliary
        # variables with their slice of the PICOS left hand side expression.
        cplexLHSConsLHSs = []
        cplexLHSConsRHSs = []
        for localConIndex, (localLinExp, localConstant) in \
                enumerate(self._affinexp_pic2cpl(picosLHS)):
            localLinExp.ind.append(cplexLHSVars[localConIndex])
            localLinExp.val.append(-1.0)
            localConstant = -localConstant
            cplexLHSConsLHSs.append(localLinExp)
            cplexLHSConsRHSs.append(localConstant)
        self.int.linear_constraints.add(
            names=cplexLHSCons, lin_expr=cplexLHSConsLHSs,
            senses="E" * picosLHSLen, rhs=cplexLHSConsRHSs)

        # Add two constraints that identify the right hand side CPLEX auxiliary
        # variables with the PICOS right hand side scalar expressions.
        cplexRHSConsLHSs = []
        cplexRHSConsRHSs = []
        for picosRHS, cplexRHSVar in zip((picosRHS1, picosRHS2), cplexRHSVars):
            linExp, constant = self._scalar_affinexp_pic2cpl(-picosRHS)
            linExp.ind.append(cplexRHSVar)
            linExp.val.append(1.0)
            constant = -constant
            cplexRHSConsLHSs.append(linExp)
            cplexRHSConsRHSs.append(constant)
        self.int.linear_constraints.add(
            names=cplexRHSCons, lin_expr=cplexRHSConsLHSs,
            senses="E" * 2, rhs=cplexRHSConsRHSs)

        # Add a quadratic constraint over the auxiliary variables that
        # represents the PICOS rotated second order cone constraint itself.
        quadExpr = cplex.SparseTriple(
            ind1=[cplexRHSVars[0]] + list(cplexLHSVars),
            ind2=[cplexRHSVars[1]] + list(cplexLHSVars),
            val=[-1.0] + [1.0] * picosLHSLen)
        self.int.quadratic_constraints.add(
            name=cplexQuadCon, quad_expr=quadExpr, sense="L", rhs=0.0)

        cplexMetaCon = self.CplexRSOCC(
            LHSVars=cplexLHSVars, RHSVars=cplexRHSVars, LHSCons=cplexLHSCons,
            RHSCons=cplexRHSCons, quadCon=cplexQuadCon)

        if self._debug():
            cplexCons = {
                "LHSs of LHS auxiliary equalities": cplexLHSConsLHSs,
                "RHSs of LHS auxiliary equalities": cplexLHSConsRHSs,
                "LHSs of RHS auxiliary equalities": cplexRHSConsLHSs,
                "RHSs of RHS auxiliary equalities": cplexRHSConsRHSs,
                "Non-positive quadratic term": quadExpr}
            self._debug(
                "RScone constraint imported: {} → {}, {}".format(
                    picosConstraint, cplexMetaCon, cplexCons))

        return cplexMetaCon

    def _import_constraint(self, picosConstraint):
        # Import constraint based on type and keep track of the corresponding
        # CPLEX constraint and auxiliary variable names.
        if isinstance(picosConstraint, AffineConstraint):
            self._cplexLinConNames[picosConstraint] = \
                self._import_linear_constraint(picosConstraint)
        elif isinstance(picosConstraint, ConvexQuadraticConstraint):
            self._cplexQuadConName[picosConstraint] = \
                self._import_quad_constraint(picosConstraint)
        elif isinstance(picosConstraint, SOCConstraint):
            self._cplexSOCC[picosConstraint] = \
                self._import_socone_constraint(picosConstraint)
        elif isinstance(picosConstraint, RSOCConstraint):
            self._cplexRSOCC[picosConstraint] = \
                self._import_rscone_constraint(picosConstraint)
        else:
            assert isinstance(picosConstraint, DummyConstraint), \
                "Unexpected constraint type: {}".format(
                picosConstraint.__class__.__name__)

    def _remove_constraint(self, picosConstraint):
        if isinstance(picosConstraint, AffineConstraint):
            self.int.linear_constraints.delete(
                self._cplexLinConNames.pop(picosConstraint))
        elif isinstance(picosConstraint, ConvexQuadraticConstraint):
            self.int.quadratic_constraints.delete(
                self._cplexQuadConName.pop(picosConstraint))
        elif isinstance(picosConstraint, SOCConstraint):
            c = self._cplexSOCC.pop(picosConstraint)
            self.int.linear_constraints.delete(c.cplexLHSCons + [c.cplexRHSCon])
            self.int.quadratic_constraints.delete(c.cplexQuadCon)
            self.int.variables.delete(c.cplexLHSVars + [c.cplexRHSVar])
        elif isinstance(picosConstraint, RSOCConstraint):
            c = self._cplexRSOCC.pop(picosConstraint)
            self.int.linear_constraints.delete(c.cplexLHSCons + c.cplexRHSCons)
            self.int.quadratic_constraints.delete(c.cplexQuadCon)
            self.int.variables.delete(c.cplexLHSVars + c.cplexRHSVars)
        else:
            assert isinstance(picosConstraint, DummyConstraint), \
                "Unexpected constraint type: {}".format(
                picosConstraint.__class__.__name__)

    def _import_affine_objective(self, picosExpression):
        assert isinstance(picosExpression, AffineExpression)

        if picosExpression._constant_coef:
            offset = picosExpression._constant_coef[0]

            self.int.objective.set_offset(offset)

            if self._debug():
                self._debug("Constant part of objective imported: {} → {}"
                    .format(picosExpression.cst.string, offset))

        cplexExpression = []
        for picosVar, picosCoefficient in picosExpression._linear_coefs.items():
            assert picosCoefficient.size[0] == 1

            for localIndex in range(picosVar.dim):
                cplexCoefficient = picosCoefficient[localIndex]
                if not cplexCoefficient:
                    continue
                picosIndex = picosVar.id + localIndex
                cplexName = self._cplexVarName[picosIndex]
                cplexExpression.append((cplexName, cplexCoefficient))

        if cplexExpression:
            self.int.objective.set_linear(cplexExpression)

            if self._debug():
                self._debug("Linear part of objective imported: {} → {}"
                    .format(picosExpression.lin.string, cplexExpression))

    def _reset_affine_objective(self):
        self.int.objective.set_offset(0.0)

        linear = self.int.objective.get_linear()
        if any(linear):
            self.int.objective.set_linear(
                [(cplexVarIndex, 0.0) for cplexVarIndex, coefficient
                in enumerate(linear) if coefficient])

    def _import_quadratic_objective(self, picosExpression):
        assert isinstance(picosExpression, QuadraticExpression)

        # Import affine part of objective function.
        self._import_affine_objective(picosExpression.aff)

        # Import quadratic part of objective function.
        cplexQuadExpression = self._quadexp_pic2cpl(picosExpression)
        cplexQuadCoefficients = zip(
            cplexQuadExpression.ind1, cplexQuadExpression.ind2,
            [2.0 * coefficient for coefficient in cplexQuadExpression.val])
        self.int.objective.set_quadratic_coefficients(cplexQuadCoefficients)

        self._debug("Quadratic part of objective imported: {} → {}"
            .format(picosExpression.quad.string, cplexQuadCoefficients))

    def _reset_quadratic_objective(self):
        quadratics = self.int.objective.get_quadratic()
        if quadratics:
            self.int.objective.set_quadratic(
                [(sparsePair.ind, [0]*len(sparsePair.ind))
                for sparsePair in quadratics])

    def _import_objective(self):
        picosSense, picosObjective = self.ext.no

        # Import objective sense.
        if picosSense == "min":
            cplexSense = self.int.objective.sense.minimize
        else:
            assert picosSense == "max"
            cplexSense = self.int.objective.sense.maximize
        self.int.objective.set_sense(cplexSense)

        # Import objective function.
        if isinstance(picosObjective, AffineExpression):
            self._import_affine_objective(picosObjective)
        else:
            assert isinstance(picosObjective, QuadraticExpression)
            self._import_quadratic_objective(picosObjective)

    def _reset_objective(self):
        self._reset_affine_objective()
        self._reset_quadratic_objective()

    def _import_problem(self):
        import cplex

        # Create a problem instance.
        self.int = cplex.Cplex()

        # Import variables.
        for variable in self.ext.variables.values():
            self._import_variable(variable)

        # Import constraints.
        for constraint in self.ext.constraints.values():
            self._import_constraint(constraint)

        # Set objective.
        self._import_objective()

    def _update_problem(self):
        for oldConstraint in self._removed_constraints():
            self._remove_constraint(oldConstraint)

        for oldVariable in self._removed_variables():
            self._remove_variable(oldVariable)

        for newVariable in self._new_variables():
            self._import_variable(newVariable)

        for newConstraint in self._new_constraints():
            self._import_constraint(newConstraint)

        if self._objective_has_changed():
            self._reset_objective()
            self._import_objective()

    def _solve(self):
        import cplex

        # Reset options.
        self.int.parameters.reset()

        o = self.ext.options
        p = self.int.parameters

        continuous = self.ext.is_continuous()

        # TODO: Allow querying self.ext.objective directly.
        nonconvex_quad_obj = self.ext.footprint.nonconvex_quadratic_objective

        # verbosity
        verbosity = self.verbosity()
        if verbosity <= 0:
            # Note that this behaviour disables warning even with a verbosity of
            # zero but this is still better than having verbose output for every
            # option that is set.
            self.int.set_results_stream(None)
        else:
            p.barrier.display.set(min(2, verbosity))
            p.conflict.display.set(min(2, verbosity))
            p.mip.display.set(min(5, verbosity))
            p.sifting.display.set(min(2, verbosity))
            p.simplex.display.set(min(2, verbosity))
            p.tune.display.set(min(3, verbosity))
        self.int.set_error_stream(None)  # Already handled as exceptions.

        # abs_prim_fsb_tol
        if o.abs_prim_fsb_tol is not None:
            p.simplex.tolerances.feasibility.set(o.abs_prim_fsb_tol)

        # abs_dual_fsb_tol
        if o.abs_dual_fsb_tol is not None:
            p.simplex.tolerances.optimality.set(o.abs_dual_fsb_tol)

        # rel_prim_fsb_tol, rel_dual_fsb_tol, rel_ipm_opt_tol
        convergenceTols = [tol for tol in (o.rel_prim_fsb_tol,
            o.rel_dual_fsb_tol, o.rel_ipm_opt_tol) if tol is not None]
        if convergenceTols:
            convergenceTol = min(convergenceTols)
            p.barrier.convergetol.set(convergenceTol)
            p.barrier.qcpconvergetol.set(convergenceTol)

        # abs_bnb_opt_tol
        if o.abs_bnb_opt_tol is not None:
            p.mip.tolerances.absmipgap.set(o.abs_bnb_opt_tol)

        # rel_bnb_opt_tol
        if o.rel_bnb_opt_tol is not None:
            p.mip.tolerances.mipgap.set(o.rel_bnb_opt_tol)

        # integrality_tol
        if o.integrality_tol is not None:
            p.mip.tolerances.integrality.set(o.integrality_tol)

        # markowitz_tol
        if o.markowitz_tol is not None:
            p.simplex.tolerances.markowitz.set(o.markowitz_tol)

        # max_iterations
        if o.max_iterations is not None:
            maxit = o.max_iterations
            p.barrier.limits.iteration.set(maxit)
            p.simplex.limits.iterations.set(maxit)

        _lpm = {"interior": 4, "psimplex": 1, "dsimplex": 2}

        # lp_node_method
        if o.lp_node_method is not None:
            assert o.lp_node_method in _lpm, "Unexpected lp_node_method value."
            p.mip.strategy.subalgorithm.set(_lpm[o.lp_node_method])

        # lp_root_method
        if o.lp_root_method is not None:
            assert o.lp_root_method in _lpm, "Unexpected lp_root_method value."
            p.lpmethod.set(_lpm[o.lp_root_method])

        # timelimit
        if o.timelimit is not None:
            p.timelimit.set(o.timelimit)

        # treememory
        if o.treememory is not None:
            p.mip.limits.treememory.set(o.treememory)

        # Handle option conflict between "max_fsb_nodes" and "pool_size".
        if o.max_fsb_nodes is not None \
        and o.pool_size is not None:
            raise ConflictingOptionsError("The options 'max_fsb_nodes' and "
                "'pool_size' cannot be used in conjunction.")

        # max_fsb_nodes
        if o.max_fsb_nodes is not None:
            p.mip.limits.solutions.set(o.max_fsb_nodes)

        # pool_size
        if o.pool_size is not None:
            if continuous:
                raise UnsupportedOptionError("The option 'pool_size' can only "
                    "be used with mixed integer problems.")
            maxNumSolutions = max(1, int(o.pool_size))
            p.mip.limits.populate.set(maxNumSolutions)
        else:
            maxNumSolutions = 1

        # pool_relgap
        if o.pool_rel_gap is not None:
            if o.pool_size is None:
                raise DependentOptionError("The option 'pool_rel_gap' requires "
                    "the option 'pool_size'.")
            p.mip.pool.relgap.set(o.pool_rel_gap)

        # pool_abs_gap
        if o.pool_abs_gap is not None:
            if o.pool_size is None:
                raise DependentOptionError("The option 'pool_abs_gap' requires "
                    "the option 'pool_size'.")
            p.mip.pool.absgap.set(o.pool_abs_gap)

        # hotstart
        if o.hotstart:
            names, values = [], []
            for picosVar in self.ext.variables.values():
                if picosVar.valued:
                    for localIndex in range(picosVar.dim):
                        name = self._cplexVarName[picosVar.id_at(localIndex)]
                        names.append(name)
                        values.append(picosVar.internal_value[localIndex])
            if names:
                self.int.MIP_starts.add(
                    cplex.SparsePair(ind=names, val=values),
                    self.int.MIP_starts.effort_level.repair)

        # Set the optimality target now so that cplex_params may overwrite it.
        # This allows solving QPs and MIQPs with a nonconvex objective.
        if nonconvex_quad_obj:
            p.optimalitytarget.set(3)

        # Load a virtual machine config.
        if self.ext.options.cplex_vmconfig:
            self.int.copy_vmconfig(self.ext.options.cplex_vmconfig)

        # Handle CPLEX-specific options.
        for key, value in o.cplex_params.items():
            try:
                parameter = getattr(self.int.parameters, key)
            except AttributeError as error:
                self._handle_bad_solver_specific_option_key(key, error)

            try:
                parameter.set(value)
            except cplex.exceptions.errors.CplexError as error:
                self._handle_bad_solver_specific_option_value(key, value, error)

        # Handle options "cplex_upr_bnd_limit", "cplex_lwr_bnd_limit" and
        # "cplex_bnd_monitor" via a CPLEX callback handler.
        callback = None
        if o.cplex_upr_bnd_limit or o.cplex_lwr_bnd_limit \
        or o.cplex_bnd_monitor:
            from cplex.callbacks import MIPInfoCallback

            class PicosInfoCallback(MIPInfoCallback):
                def __call__(self):
                    v1 = self.get_incumbent_objective_value()
                    v2 = self.get_best_objective_value()
                    ub = max(v1, v2)
                    lb = min(v1, v2)
                    if self.bounds is not None:
                        elapsedTime = time.time() - self.startTime
                        self.bounds.append((elapsedTime, lb, ub))
                    if self.lbound is not None and lb >= self.lbound:
                        self.printer("The specified lower bound was reached, "
                            "so PICOS will ask CPLEX to stop the search.")
                        self.abort()
                    if self.ubound is not None and ub <= self.ubound:
                        self.printer("The specified upper bound was reached, "
                            "so PICOS will ask CPLEX to stop the search.")
                        self.abort()

            # Register the callback handler with CPLEX.
            callback = self.int.register_callback(PicosInfoCallback)

            # Pass parameters to the callback handler. Note that
            # callback.startTime will be set just before optimization begins.
            callback.printer = self._verbose
            callback.ubound = o.cplex_upr_bnd_limit
            callback.lbound = o.cplex_lwr_bnd_limit
            callback.bounds = [] if o.cplex_bnd_monitor else None

        # Inform CPLEX about the problem type.
        # This seems necessary, as otherwise LP can get solved as MIP, producing
        # misleading status output (e.g. "not integer feasible").
        conTypes = set(c.__class__ for c in self.ext.constraints.values())
        quadObj = isinstance(self.ext.no.function, QuadraticExpression)
        cplexTypes = self.int.problem_type

        if quadObj:
            if conTypes.issubset(set([DummyConstraint, AffineConstraint])):
                cplexType = cplexTypes.QP if continuous else cplexTypes.MIQP
            else:
                # Assume quadratic constraint types.
                cplexType = cplexTypes.QCP if continuous else cplexTypes.MIQCP
        else:
            if conTypes.issubset(set([DummyConstraint, AffineConstraint])):
                cplexType = cplexTypes.LP if continuous else cplexTypes.MILP
            else:
                # Assume quadratic constraint types.
                cplexType = cplexTypes.QCP if continuous else cplexTypes.MIQCP

        # Silence a warning explaining that optimality target 3 changes the
        # problem type from QP to MIQP by doing so manually.
        if nonconvex_quad_obj:
            # Enforce consistency with CPLEXSolver.supports.
            assert cplexType in (cplexTypes.QP, cplexTypes.MIQP)

            if p.optimalitytarget.get() == 3:  # User might have changed it.
                cplexType = cplexTypes.MIQP

        if cplexType is not None:
            self.int.set_problem_type(cplexType)

        # Attempt to solve the problem.
        if callback:
            callback.startTime = time.time()
        with self._header(), self._stopwatch():
            try:
                if maxNumSolutions > 1:
                    self.int.populate_solution_pool()
                    numSolutions = self.int.solution.pool.get_num()
                else:
                    self.int.solve()
                    numSolutions = 1
            except cplex.exceptions.errors.CplexSolverError as error:
                if error.args[2] == 5002:
                    self._handle_continuous_nonconvex_error(error)
                else:
                    raise

        solutions = []
        for solutionNum in range(numSolutions):
            # Retrieve primals.
            primals = {}
            if o.primals is not False:
                for picosVar in self.ext.variables.values():
                    try:
                        cplexNames = []

                        for localIndex in range(picosVar.dim):
                            picosIndex = picosVar.id + localIndex
                            cplexNames.append(self._cplexVarName[picosIndex])
                        if maxNumSolutions > 1:
                            value = self.int.solution.pool.get_values(
                                solutionNum, cplexNames)
                        else:
                            value = self.int.solution.get_values(cplexNames)
                        primals[picosVar] = value
                    except cplex.exceptions.errors.CplexSolverError:
                        primals[picosVar] = None

            # Retrieve duals.
            duals = {}
            if o.duals is not False and continuous:
                assert maxNumSolutions == 1

                for picosCon in self.ext.constraints.values():
                    if isinstance(picosCon, DummyConstraint):
                        duals[picosCon] = cvxopt.spmatrix(
                            [], [], [], picosCon.size)
                        continue

                    try:
                        if isinstance(picosCon, AffineConstraint):
                            cplexCons = self._cplexLinConNames[picosCon]
                            values = self.int.solution.get_dual_values(
                                cplexCons)
                            picosDual = cvxopt.matrix(values, picosCon.size)

                            # Flip sign based on constraint relation.
                            if not picosCon.is_increasing():
                                picosDual = -picosDual
                        elif isinstance(picosCon, SOCConstraint):
                            cplexMetaCon = self._cplexSOCC[picosCon]
                            lb = self.int.solution.get_dual_values(
                                cplexMetaCon.RHSCon)
                            z = self.int.solution.get_dual_values(
                                list(cplexMetaCon.LHSCons))
                            picosDual = -cvxopt.matrix([-lb] + z)
                        elif isinstance(picosCon, RSOCConstraint):
                            cplexMetaCon = self._cplexRSOCC[picosCon]
                            ab = [-x for x in self.int.solution.get_dual_values(
                                list(cplexMetaCon.RHSCons))]
                            z = self.int.solution.get_dual_values(
                                list(cplexMetaCon.LHSCons))
                            picosDual = -cvxopt.matrix(ab + z)
                        elif isinstance(picosCon, ConvexQuadraticConstraint):
                            picosDual = None
                        else:
                            assert False, "Unexpected constraint type."

                        # Flip sign based on objective sense.
                        if picosDual and self.ext.no.direction == "min":
                            picosDual = -picosDual
                    except cplex.exceptions.errors.CplexSolverError:
                        duals[picosCon] = None
                    else:
                        duals[picosCon] = picosDual

            # Retrieve objective value.
            try:
                if quadObj:
                    # FIXME: Retrieval of QP and MIQP objective value appears to
                    #        miss the quadratic part.
                    value = None
                elif maxNumSolutions > 1:
                    value = self.int.solution.pool.get_objective_value(
                        solutionNum)
                else:
                    value = self.int.solution.get_objective_value()
            except cplex.exceptions.errors.CplexSolverError:
                value = None

            # Retrieve solution status.
            code = self.int.solution.get_status()
            if code in CPLEX_STATUS_CODES:
                prmlStatus, dualStatus, probStatus = CPLEX_STATUS_CODES[code]
            else:
                prmlStatus = SS_UNKNOWN
                dualStatus = SS_UNKNOWN
                probStatus = PS_UNKNOWN

            info = {}
            if o.cplex_bnd_monitor:
                info["bounds_monitor"] = callback.bounds

            solutions.append(self._make_solution(value, primals, duals,
                prmlStatus, dualStatus, probStatus, info))

        if maxNumSolutions > 1:
            return solutions
        else:
            assert len(solutions) == 1
            return solutions[0]


# --------------------------------------
__all__ = api_end(_API_START, globals())
