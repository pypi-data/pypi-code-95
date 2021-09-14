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

"""Implementation of :class:`GurobiSolver`."""

from collections import namedtuple

import cvxopt

from ..apidoc import api_end, api_start
from ..constraints import (AffineConstraint, ConvexQuadraticConstraint,
                           DummyConstraint, RSOCConstraint, SOCConstraint)
from ..expressions import (CONTINUOUS_VARTYPES, AffineExpression,
                           BinaryVariable, IntegerVariable,
                           QuadraticExpression)
from ..modeling.footprint import Specification
from ..modeling.solution import (PS_FEASIBLE, PS_INF_OR_UNB, PS_INFEASIBLE,
                                 PS_UNBOUNDED, PS_UNKNOWN, PS_UNSTABLE,
                                 SS_EMPTY, SS_FEASIBLE, SS_INFEASIBLE,
                                 SS_OPTIMAL, SS_PREMATURE, SS_UNKNOWN)
from .solver import Solver

_API_START = api_start(globals())
# -------------------------------


class GurobiSolver(Solver):
    """Interface to the Gurobi solver via its official Python interface."""

    # TODO: Allow nonconvex quadratic constraints in the integer case?
    # TODO: Don't support (conic) quadratic constraints when duals are
    #       requested because their precision is bad and can't be controlled.
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

    @classmethod
    def supports(cls, footprint, explain=False):
        """Implement :meth:`~.solver.Solver.supports`."""
        result = Solver.supports(footprint, explain)
        if not result or (explain and not result[0]):
            return result

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
        cls.check_import("gurobipy")

    @classmethod
    def names(cls):
        """Implement :meth:`~.solver.Solver.names`."""
        return "gurobi", "Gurobi", "Gurobi Optimizer"

    @classmethod
    def is_free(cls):
        """Implement :meth:`~.solver.Solver.is_free`."""
        return False

    GurobiSOCC = namedtuple("GurobiSOCC",
        ("LHSVars", "RHSVar", "LHSCons", "RHSCon", "quadCon"))

    GurobiRSOCC = namedtuple("GurobiRSOCC",
        ("LHSVars", "RHSVars", "LHSCons", "RHSCons", "quadCon"))

    def __init__(self, problem):
        """Initialize a Gurobi solver interface.

        :param ~picos.Problem problem: The problem to be solved.
        """
        super(GurobiSolver, self).__init__(problem)

        self._gurobiVar = dict()
        """Maps PICOS variable indices to Gurobi variables."""

        self._gurobiLinearConstraints = dict()
        """Maps a PICOS (multidimensional) linear constraint to a collection of
        Gurobi (scalar) linear constraints."""

        self._gurobiQuadConstraint = dict()
        """Maps a PICOS quadratic constraint to a Gurobi quadr. constraint."""

        self._gurobiSOCC = dict()
        """Maps a PICOS second order cone constraint to its Gurobi
        representation involving auxiliary variables and constraints."""

        self._gurobiRSOCC = dict()
        """Maps a PICOS rotated second order cone constraint to its Gurobi
        representation involving auxiliary variables and constraints."""

    def reset_problem(self):
        """Implement :meth:`~.solver.Solver.reset_problem`."""
        self.int = None

        self._gurobiVar.clear()
        self._gurobiLinearConstraints.clear()
        self._gurobiQuadConstraint.clear()
        self._gurobiSOCC.clear()
        self._gurobiRSOCC.clear()

    def _import_variable(self, picosVar):
        import gurobipy as gurobi

        dim = picosVar.dim

        # Retrieve types.
        if isinstance(picosVar, CONTINUOUS_VARTYPES):
            gurobiVarType = gurobi.GRB.CONTINUOUS
        elif isinstance(picosVar, IntegerVariable):
            gurobiVarType = gurobi.GRB.INTEGER
        elif isinstance(picosVar, BinaryVariable):
            gurobiVarType = gurobi.GRB.BINARY
        else:
            assert False, "Unexpected variable type."

        # Retrieve bounds.
        lowerBounds = [-gurobi.GRB.INFINITY]*dim
        upperBounds = [gurobi.GRB.INFINITY]*dim
        lower, upper = picosVar.bound_dicts
        for i, b in lower.items():
            lowerBounds[i] = b
        for i, b in upper.items():
            upperBounds[i] = b

        # Import variable.
        # Note that Gurobi allows importing the objective function coefficients
        # for the new variables here, but that is done later to streamline
        # updates to the objective.
        gurobiVars = self.int.addVars(dim, lb=lowerBounds, ub=upperBounds,
            vtype=gurobiVarType, name=picosVar.name)

        # Map PICOS variable indices to Gurobi variables.
        for localIndex in range(dim):
            self._gurobiVar[picosVar.id_at(localIndex)] = gurobiVars[localIndex]

    def _remove_variable(self, picosVar):
        gurobiVars = [self._gurobiVar.pop(picosVar.id_at(localIndex))
            for localIndex in range(picosVar.dim)]
        self.int.remove(gurobiVars)

    def _import_variable_values(self):
        for picosVar in self.ext.variables.values():
            if picosVar.valued:
                value = picosVar.internal_value

                for localIndex in range(picosVar.dim):
                    gurobiVar = self._gurobiVar[picosVar.id_at(localIndex)]
                    gurobiVar.Start = value[localIndex]

    def _reset_variable_values(self):
        import gurobipy as gurobi

        for gurobiVar in self._gurobiVar.values():
            gurobiVar.Start = gurobi.GRB.UNDEFINED

    def _affinexp_pic2grb(self, picosExpression):
        import gurobipy as gurobi

        for gurobiVars, coefficients, constant in picosExpression.sparse_rows(
                None, indexFunction=lambda picosVar, localIndex:
                self._gurobiVar[picosVar.id_at(localIndex)]):
            gurobiExpression = gurobi.LinExpr(coefficients, gurobiVars)
            gurobiExpression.addConstant(constant)
            yield gurobiExpression

    def _scalar_affinexp_pic2grb(self, picosExpression):
        """Transform a scalar affine expression from PICOS to Gurobi.

        :returns: A :class:`LinExpr <gurobipy.LinExpr>`.
        """
        assert len(picosExpression) == 1
        return next(self._affinexp_pic2grb(picosExpression))

    def _quadexp_pic2grb(self, picosExpression):
        import gurobipy as gurobi

        assert isinstance(picosExpression, QuadraticExpression)

        # Import affine part of expression.
        gurobiExpression = gurobi.QuadExpr(
            self._scalar_affinexp_pic2grb(picosExpression.aff))

        # Import quadratic form.
        gurobiI, gurobiJ, gurobiV = [], [], []
        for (picosVar1, picosVar2), picosCoefficients \
                in picosExpression._sparse_quads.items():
            for sparseIndex in range(len(picosCoefficients)):
                localVar1Index = picosCoefficients.I[sparseIndex]
                localVar2Index = picosCoefficients.J[sparseIndex]
                localCoefficient = picosCoefficients.V[sparseIndex]
                gurobiI.append(self._gurobiVar[picosVar1.id_at(localVar1Index)])
                gurobiJ.append(self._gurobiVar[picosVar2.id_at(localVar2Index)])
                gurobiV.append(localCoefficient)
        gurobiExpression.addTerms(gurobiV, gurobiI, gurobiJ)

        return gurobiExpression

    def _import_linear_constraint(self, picosConstraint):
        import gurobipy as gurobi

        assert isinstance(picosConstraint, AffineConstraint)

        # Retrieve sense.
        if picosConstraint.is_increasing():
            gurobiSense = gurobi.GRB.LESS_EQUAL
        elif picosConstraint.is_decreasing():
            gurobiSense = gurobi.GRB.GREATER_EQUAL
        elif picosConstraint.is_equality():
            gurobiSense = gurobi.GRB.EQUAL
        else:
            assert False, "Unexpected constraint relation."

        # Append scalar constraints.
        gurobiCons = []
        for localConIndex, (gurobiLHS, gurobiRHS) in enumerate(zip(
                self._affinexp_pic2grb(picosConstraint.lhs),
                self._affinexp_pic2grb(picosConstraint.rhs))):
            if picosConstraint.name:
                gurobiName = "{}:{}".format(picosConstraint.name, localConIndex)
            else:
                gurobiName = ""

            gurobiCons.append(self.int.addConstr(
                gurobiLHS, gurobiSense, gurobiRHS, gurobiName))

        return gurobiCons

    def _import_quad_constraint(self, picosConstraint):
        import gurobipy as gurobi

        assert isinstance(picosConstraint, ConvexQuadraticConstraint)

        gurobiLHS = self._quadexp_pic2grb(picosConstraint.le0)
        gurobiRHS = -gurobiLHS.getLinExpr().getConstant()
        if gurobiRHS:
            gurobiLHS.getLinExpr().addConstant(gurobiRHS)

        return self.int.addQConstr(
            gurobiLHS, gurobi.GRB.LESS_EQUAL, gurobiRHS)

    # TODO: Handle SOC → Quadratic via a reformulation.
    def _import_socone_constraint(self, picosConstraint):
        import gurobipy as gurobi

        assert isinstance(picosConstraint, SOCConstraint)

        picosLHS = picosConstraint.ne
        picosRHS = picosConstraint.ub
        picosLHSLen = len(picosLHS)

        # Add auxiliary variables: One for every dimension of the left hand side
        # of the PICOS constraint and one for its right hand side.
        gurobiLHSVarsIndexed = self.int.addVars(
            picosLHSLen, lb=-gurobi.GRB.INFINITY, ub=gurobi.GRB.INFINITY)
        gurobiLHSVars = gurobiLHSVarsIndexed.values()
        gurobiRHSVar = self.int.addVar(lb=0.0, ub=gurobi.GRB.INFINITY)

        # Add constraints that identify the left hand side Gurobi auxiliary
        # variables with their slice of the PICOS left hand side expression.
        gurobiLHSSlices = dict()
        for dimension, slice in enumerate(self._affinexp_pic2grb(picosLHS)):
            gurobiLHSSlices[dimension] = slice
        gurobiLHSCons = self.int.addConstrs(
            (gurobiLHSSlices[dimension] - gurobiLHSVarsIndexed[dimension] == 0
            for dimension in range(picosLHSLen))).values()

        # Add a constraint that identifies the right hand side Gurobi auxiliary
        # variable with the PICOS right hand side scalar expression.
        gurobiRHSExp = self._scalar_affinexp_pic2grb(picosRHS)
        gurobiRHSCon = self.int.addConstr(
            gurobiRHSVar - gurobiRHSExp, gurobi.GRB.EQUAL, 0)

        # Add a quadratic constraint over the auxiliary variables that
        # represents the PICOS second order cone constraint itself.
        quadExpr = gurobi.QuadExpr()
        quadExpr.addTerms([1.0] * picosLHSLen, gurobiLHSVars, gurobiLHSVars)
        gurobiName = picosConstraint.name if picosConstraint.name else ""
        gurobiQuadCon = self.int.addQConstr(quadExpr, gurobi.GRB.LESS_EQUAL,
            gurobiRHSVar * gurobiRHSVar, gurobiName)

        gurobiMetaCon = self.GurobiSOCC(
            LHSVars=gurobiLHSVars, RHSVar=gurobiRHSVar, LHSCons=gurobiLHSCons,
            RHSCon=gurobiRHSCon, quadCon=gurobiQuadCon)

        return gurobiMetaCon

    # TODO: Handle RSOC → Quadratic via a reformulation.
    def _import_rscone_constraint(self, picosConstraint):
        import gurobipy as gurobi

        assert isinstance(picosConstraint, RSOCConstraint)

        picosLHS = picosConstraint.ne
        picosRHS1 = picosConstraint.ub1
        picosRHS2 = picosConstraint.ub2
        picosLHSLen = len(picosLHS)

        # Add auxiliary variables: One for every dimension of the left hand side
        # of the PICOS constraint and one for its right hand side.
        gurobiLHSVarsIndexed = self.int.addVars(
            picosLHSLen, lb=-gurobi.GRB.INFINITY, ub=gurobi.GRB.INFINITY)
        gurobiLHSVars = gurobiLHSVarsIndexed.values()
        gurobiRHSVars = self.int.addVars(
            2, lb=0.0, ub=gurobi.GRB.INFINITY).values()

        # Add constraints that identify the left hand side Gurobi auxiliary
        # variables with their slice of the PICOS left hand side expression.
        gurobiLHSSlices = dict()
        for dimension, slice in enumerate(self._affinexp_pic2grb(picosLHS)):
            gurobiLHSSlices[dimension] = slice
        gurobiLHSCons = self.int.addConstrs(
            (gurobiLHSSlices[dimension] - gurobiLHSVarsIndexed[dimension] == 0
            for dimension in range(picosLHSLen))).values()

        # Add two constraints that identify the right hand side Gurobi auxiliary
        # variables with the PICOS right hand side scalar expressions.
        gurobiRHSExps = \
            self._scalar_affinexp_pic2grb(picosRHS1), \
            self._scalar_affinexp_pic2grb(picosRHS2)
        gurobiRHSCons = self.int.addConstrs(
            (gurobiRHSVars[i] - gurobiRHSExps[i] == 0 for i in (0, 1))).values()

        # Add a quadratic constraint over the auxiliary variables that
        # represents the PICOS second order cone constraint itself.
        quadExpr = gurobi.QuadExpr()
        quadExpr.addTerms([1.0] * picosLHSLen, gurobiLHSVars, gurobiLHSVars)
        gurobiName = picosConstraint.name if picosConstraint.name else ""
        gurobiQuadCon = self.int.addQConstr(quadExpr, gurobi.GRB.LESS_EQUAL,
            gurobiRHSVars[0] * gurobiRHSVars[1], gurobiName)

        gurobiMetaCon = self.GurobiRSOCC(
            LHSVars=gurobiLHSVars, RHSVars=gurobiRHSVars, LHSCons=gurobiLHSCons,
            RHSCons=gurobiRHSCons, quadCon=gurobiQuadCon)

        return gurobiMetaCon

    def _import_constraint(self, picosConstraint):
        # Import constraint based on type.
        if isinstance(picosConstraint, AffineConstraint):
            self._gurobiLinearConstraints[picosConstraint] = \
                self._import_linear_constraint(picosConstraint)
        elif isinstance(picosConstraint, ConvexQuadraticConstraint):
            self._gurobiQuadConstraint[picosConstraint] = \
                self._import_quad_constraint(picosConstraint)
        elif isinstance(picosConstraint, SOCConstraint):
            self._gurobiSOCC[picosConstraint] = \
                self._import_socone_constraint(picosConstraint)
        elif isinstance(picosConstraint, RSOCConstraint):
            self._gurobiRSOCC[picosConstraint] = \
                self._import_rscone_constraint(picosConstraint)
        else:
            assert isinstance(picosConstraint, DummyConstraint), \
                "Unexpected constraint type: {}".format(
                picosConstraint.__class__.__name__)

    def _remove_constraint(self, picosConstraint):
        if isinstance(picosConstraint, AffineConstraint):
            self.int.remove(
                self._gurobiLinearConstraints.pop(picosConstraint))
        elif isinstance(picosConstraint, ConvexQuadraticConstraint):
            self.int.remove(
                self._gurobiQuadConstraint.pop(picosConstraint))
        elif isinstance(picosConstraint, SOCConstraint):
            c = self._gurobiSOCC.pop(picosConstraint)
            self.int.remove(c.gurobiLHSCons + [c.gurobiRHSCon]
                + [c.gurobiQuadCon] + c.gurobiLHSVars + [c.gurobiRHSVar])
        elif isinstance(picosConstraint, RSOCConstraint):
            c = self._gurobiRSOCC.pop(picosConstraint)
            self.int.remove(c.gurobiLHSCons + c.gurobiRHSCons
                + [c.gurobiQuadCon] + c.gurobiLHSVars + c.gurobiRHSVars)
        else:
            assert isinstance(picosConstraint, DummyConstraint), \
                "Unexpected constraint type: {}".format(
                picosConstraint.__class__.__name__)

    def _import_objective(self):
        import gurobipy as gurobi

        picosSense, picosObjective = self.ext.no

        # Retrieve objective sense.
        if picosSense == "min":
            gurobiSense = gurobi.GRB.MINIMIZE
        else:
            assert picosSense == "max"
            gurobiSense = gurobi.GRB.MAXIMIZE

        # Retrieve objective function.
        if isinstance(picosObjective, AffineExpression):
            gurobiObjective = self._scalar_affinexp_pic2grb(picosObjective)
        else:
            assert isinstance(picosObjective, QuadraticExpression)
            gurobiObjective = self._quadexp_pic2grb(picosObjective)

        self.int.setObjective(gurobiObjective, gurobiSense)

    def _import_problem(self):
        import gurobipy as gurobi

        # Create a problem instance.
        if self._license_warnings:
            self.int = gurobi.Model()
        else:
            with self._enforced_verbosity():
                self.int = gurobi.Model()

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
            self._import_objective()

    def _solve(self):
        import gurobipy as gurobi

        # Reset options.
        # NOTE: OutputFlag = 0 prevents resetParams from printing to console.
        self.int.Params.OutputFlag = 0
        self.int.resetParams()

        # verbosity
        self.int.Params.OutputFlag = 1 if self.verbosity() > 0 else 0

        # abs_prim_fsb_tol
        if self.ext.options.abs_prim_fsb_tol is not None:
            self.int.Params.FeasibilityTol = self.ext.options.abs_prim_fsb_tol

        # abs_dual_fsb_tol
        if self.ext.options.abs_dual_fsb_tol is not None:
            self.int.Params.OptimalityTol = self.ext.options.abs_dual_fsb_tol

        # rel_ipm_opt_tol
        if self.ext.options.rel_ipm_opt_tol is not None:
            self.int.Params.BarConvTol = self.ext.options.rel_ipm_opt_tol

            # HACK: Work around low precision (conic) quadratic duals.
            self.int.Params.BarQCPConvTol = \
                0.01 * self.ext.options.rel_ipm_opt_tol

        # abs_bnb_opt_tol
        if self.ext.options.abs_bnb_opt_tol is not None:
            self.int.Params.MIPGapAbs = self.ext.options.abs_bnb_opt_tol

        # rel_bnb_opt_tol
        if self.ext.options.rel_bnb_opt_tol is not None:
            self.int.Params.MIPGap = self.ext.options.rel_bnb_opt_tol

        # integrality_tol
        if self.ext.options.integrality_tol is not None:
            self.int.Params.IntFeasTol = self.ext.options.integrality_tol

        # markowitz_tol
        if self.ext.options.markowitz_tol is not None:
            self.int.Params.MarkowitzTol = self.ext.options.markowitz_tol

        # max_iterations
        if self.ext.options.max_iterations is not None:
            self.int.Params.BarIterLimit = self.ext.options.max_iterations
            self.int.Params.IterationLimit = self.ext.options.max_iterations

        _lpm = {"interior": 2, "psimplex": 0, "dsimplex": 1}

        # lp_node_method
        if self.ext.options.lp_node_method is not None:
            value = self.ext.options.lp_node_method
            assert value in _lpm, "Unexpected lp_node_method value."
            self.int.Params.SiftMethod = _lpm[value]

        # lp_root_method
        if self.ext.options.lp_root_method is not None:
            value = self.ext.options.lp_root_method
            assert value in _lpm, "Unexpected lp_root_method value."
            self.int.Params.Method = _lpm[value]

        # timelimit
        if self.ext.options.timelimit is not None:
            self.int.Params.TimeLimit = self.ext.options.timelimit

        # max_fsb_nodes
        if self.ext.options.max_fsb_nodes is not None:
            self.int.Params.SolutionLimit = self.ext.options.max_fsb_nodes

        # hotstart
        if self.ext.options.hotstart:
            self._import_variable_values()
        else:
            self._reset_variable_values()

        # Handle Gurobi-specific options.
        for key, value in self.ext.options.gurobi_params.items():
            if not self.int.getParamInfo(key):
                self._handle_bad_solver_specific_option_key(key)

            try:
                self.int.setParam(key, value)
            except TypeError as error:
                self._handle_bad_solver_specific_option_value(key, value, error)

        # Handle unsupported options.
        self._handle_unsupported_option("treememory")

        # Extend functionality for continuous problems.
        if self.ext.is_continuous():
            # Compute duals also for QPs and QC(Q)Ps.
            if self.ext.options.duals is not False:
                self.int.setParam(gurobi.GRB.Param.QCPDual, 1)

            # Allow nonconvex quadratic objectives.
            # TODO: Allow querying self.ext.objective directly.
            if self.ext.footprint.nonconvex_quadratic_objective:
                self.int.setParam(gurobi.GRB.Param.NonConvex, 2)

        # Attempt to solve the problem.
        with self._header(), self._stopwatch():
            try:
                self.int.optimize()
            except gurobi.GurobiError as error:
                if error.errno == gurobi.GRB.Error.Q_NOT_PSD:
                    self._handle_continuous_nonconvex_error(error)
                else:
                    raise

        # Retrieve primals.
        primals = {}
        if self.ext.options.primals is not False:
            for picosVar in self.ext.variables.values():
                try:
                    value = []
                    for localIndex in range(picosVar.dim):
                        gurobiVar = self._gurobiVar[picosVar.id_at(localIndex)]
                        scalarValue = gurobiVar.getAttr(gurobi.GRB.Attr.X)
                        value.append(scalarValue)
                except AttributeError:
                    primals[picosVar] = None
                else:
                    primals[picosVar] = value

        # Retrieve duals.
        duals = {}
        if self.ext.options.duals is not False and self.ext.is_continuous():
            Pi = gurobi.GRB.Attr.Pi

            for picosCon in self.ext.constraints.values():
                if isinstance(picosCon, DummyConstraint):
                    duals[picosCon] = cvxopt.spmatrix([], [], [], picosCon.size)
                    continue

                # HACK: Work around gurobiCon.getAttr(gurobi.GRB.Attr.Pi)
                #       printing a newline to console when it raises an
                #       AttributeError and OutputFlag is enabled. This is a
                #       WONTFIX on Gurobi's end (PICOS #264, Gurobi #14248).
                oldOutput = self.int.Params.OutputFlag
                self.int.Params.OutputFlag = 0

                try:
                    if isinstance(picosCon, AffineConstraint):
                        gurobiCons = self._gurobiLinearConstraints[picosCon]
                        gurobiDuals = []
                        for gurobiCon in gurobiCons:
                            gurobiDuals.append(gurobiCon.getAttr(Pi))
                        picosDual = cvxopt.matrix(gurobiDuals, picosCon.size)

                        # Flip sign based on constraint relation.
                        if not picosCon.is_increasing():
                            picosDual = -picosDual
                    elif isinstance(picosCon, SOCConstraint):
                        gurobiMetaCon = self._gurobiSOCC[picosCon]
                        lb = gurobiMetaCon.RHSCon.getAttr(Pi)
                        z = [-constraint.getAttr(Pi)
                            for constraint in gurobiMetaCon.LHSCons]
                        picosDual = cvxopt.matrix([lb] + z)
                    elif isinstance(picosCon, RSOCConstraint):
                        gurobiMetaCon = self._gurobiRSOCC[picosCon]
                        ab = [constraint.getAttr(Pi)
                            for constraint in gurobiMetaCon.RHSCons]
                        z = [-constraint.getAttr(Pi)
                            for constraint in gurobiMetaCon.LHSCons]
                        picosDual = cvxopt.matrix(ab + z)
                    elif isinstance(picosCon, ConvexQuadraticConstraint):
                        picosDual = None
                    else:
                        assert isinstance(picosCon, DummyConstraint), \
                            "Unexpected constraint type: {}".format(
                            picosCon.__class__.__name__)

                    # Flip sign based on objective sense.
                    if picosDual and self.ext.no.direction == "min":
                        picosDual = -picosDual
                except AttributeError:
                    duals[picosCon] = None
                else:
                    duals[picosCon] = picosDual

                # HACK: See above. Also: Silence Gurobi while enabling output.
                if oldOutput != 0:
                    with self._enforced_verbosity(noStdOutAt=float("inf")):
                        self.int.Params.OutputFlag = oldOutput

        # Retrieve objective value.
        try:
            value = self.int.getAttr(gurobi.GRB.Attr.ObjVal)
        except AttributeError:
            value = None

        # Retrieve solution status.
        statusCode = self.int.getAttr(gurobi.GRB.Attr.Status)
        if statusCode   == gurobi.GRB.Status.LOADED:
            raise RuntimeError("Gurobi claims to have just loaded the problem "
                "while PICOS expects the solution search to have terminated.")
        elif statusCode == gurobi.GRB.Status.OPTIMAL:
            primalStatus   = SS_OPTIMAL
            dualStatus     = SS_OPTIMAL
            problemStatus  = PS_FEASIBLE
        elif statusCode == gurobi.GRB.Status.INFEASIBLE:
            primalStatus   = SS_INFEASIBLE
            dualStatus     = SS_UNKNOWN
            problemStatus  = PS_INFEASIBLE
        elif statusCode == gurobi.GRB.Status.INF_OR_UNBD:
            primalStatus   = SS_UNKNOWN
            dualStatus     = SS_UNKNOWN
            problemStatus  = PS_INF_OR_UNB
        elif statusCode == gurobi.GRB.Status.UNBOUNDED:
            primalStatus   = SS_UNKNOWN
            dualStatus     = SS_INFEASIBLE
            problemStatus  = PS_UNBOUNDED
        elif statusCode == gurobi.GRB.Status.CUTOFF:
            # "Optimal objective for model was proven to be worse than the value
            # specified in the Cutoff parameter. No solution information is
            # available."
            primalStatus   = SS_PREMATURE
            dualStatus     = SS_PREMATURE
            problemStatus  = PS_UNKNOWN
        elif statusCode == gurobi.GRB.Status.ITERATION_LIMIT:
            primalStatus   = SS_PREMATURE
            dualStatus     = SS_PREMATURE
            problemStatus  = PS_UNKNOWN
        elif statusCode == gurobi.GRB.Status.NODE_LIMIT:
            primalStatus   = SS_PREMATURE
            dualStatus     = SS_EMPTY  # Applies only to mixed integer problems.
            problemStatus  = PS_UNKNOWN
        elif statusCode == gurobi.GRB.Status.TIME_LIMIT:
            primalStatus   = SS_PREMATURE
            dualStatus     = SS_PREMATURE
            problemStatus  = PS_UNKNOWN
        elif statusCode == gurobi.GRB.Status.SOLUTION_LIMIT:
            primalStatus   = SS_PREMATURE
            dualStatus     = SS_PREMATURE
            problemStatus  = PS_UNKNOWN
        elif statusCode == gurobi.GRB.Status.INTERRUPTED:
            primalStatus   = SS_PREMATURE
            dualStatus     = SS_PREMATURE
            problemStatus  = PS_UNKNOWN
        elif statusCode == gurobi.GRB.Status.NUMERIC:
            primalStatus   = SS_UNKNOWN
            dualStatus     = SS_UNKNOWN
            problemStatus  = PS_UNSTABLE
        elif statusCode == gurobi.GRB.Status.SUBOPTIMAL:
            # "Unable to satisfy optimality tolerances; a sub-optimal solution
            # is available."
            primalStatus   = SS_FEASIBLE
            dualStatus     = SS_FEASIBLE
            problemStatus  = PS_FEASIBLE
        elif statusCode == gurobi.GRB.Status.INPROGRESS:
            raise RuntimeError("Gurobi claims solution search to be 'in "
                "progress' while PICOS expects it to have terminated.")
        elif statusCode == gurobi.GRB.Status.USER_OBJ_LIMIT:
            # "User specified an objective limit (a bound on either the best
            # objective or the best bound), and that limit has been reached."
            primalStatus   = SS_FEASIBLE
            dualStatus     = SS_EMPTY  # Applies only to mixed integer problems.
            problemStatus  = PS_FEASIBLE
        else:
            primalStatus   = SS_UNKNOWN
            dualStatus     = SS_UNKNOWN
            problemStatus  = PS_UNKNOWN

        return self._make_solution(
            value, primals, duals, primalStatus, dualStatus, problemStatus)


# --------------------------------------
__all__ = api_end(_API_START, globals())
