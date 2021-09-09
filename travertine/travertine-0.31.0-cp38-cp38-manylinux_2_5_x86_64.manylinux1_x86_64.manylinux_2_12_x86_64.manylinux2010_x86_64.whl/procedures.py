#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Standard procedures.

The procedure are the basic unit of computation while computing a price.  Each
class in this module is NOT a procedure, but its instances are.

The classes here allow to compose pricing computations and to return a result
with a detailed account of the process.


"""
import logging
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import immutables
from xotl.tools.context import context
from xotl.tools.symbols import Unset
from xotless.immutables import ImmutableChainMap
from xotless.trees import Cell, IntervalTree
from xotless.types import EqTypeClass, OrdTypeClass

from .avm import BranchingAVM, FilteringAVM, merge_avms
from .floats import float_round
from .formulae import FormulaProcedureType, parse, transpile
from .formulae.ast import Substep, Variable
from .i18n import _
from .meta import MemoizedType
from .predicates import Otherwise
from .structs import LazyCall, LazyResults, PriceResult
from .types import (
    AVM,
    EVM,
    MATCH,
    RANGE,
    Aggregator,
    AttributeLocator,
    Branch,
    Demand,
    Environment,
    NamedProcedureType,
    Predicate,
    PriceResultType,
    Procedure,
    Result,
    Splitter,
    SupportsPartialDefinition,
    TypedAttribute,
    Undefined,
)

logger = logging.getLogger(__name__)


class BaseProcedure(metaclass=MemoizedType):  # pragma: no cover
    pass


# We regard all procedures as immutable (and hashable), but we don't enforce
# immutability (with frozen=True) to avoid a worthless rewrite of the
# attributes.  So it's best to simply have a custom hash.
#
# Other structures needed also to be immutable and hashable (demands,
# requests, commodities -- at least in the context of a single computation they
# are so, aggregators, predicates and splitters).
@dataclass(unsafe_hash=True)
class NamedProcedure(BaseProcedure):
    title: str


def build_result(
    proc: NamedProcedureType,
    result: Result,
    demand: Demand,
    env: Environment,
    *subres: PriceResultType,
    title=None,
) -> PriceResultType:
    return PriceResult(title or proc.title, proc, result, demand, env, *subres)


class BoundsError(TypeError):
    "A type error on the arguments of a procedure requiring min/max args."
    pass


class Composer:
    # Marks procedures that compose the result of others; e.g SumProcedure,
    # Max, etc.

    # The minimum and maximum amount required to instantiate the procedure.
    # `min_args` must be a number and it defaults to 0.  `max_args` can be
    # either an int; or None to indicate no upper limit.
    #
    # Sub classes must enforce this requirements by calling
    # `_check_args_limits`.
    min_args: ClassVar[int] = 0
    max_args: ClassVar[Optional[int]] = None

    @classmethod
    def _check_args_limits(cls, args):
        count = len(args)
        if count < cls.min_args:
            raise BoundsError(
                f"{cls.__name__} requires at least {cls.min_args} arguments"
            )
        if cls.max_args is not None and cls.max_args < count:
            raise BoundsError(f"{cls.__name__} takes at most {cls.max_args} arguments")


class FinalProcedureMixin:
    "A mixin for procedures which don't require sub-procedures."

    @property
    def avm(self):
        return EMPTY_AVM

    @property
    def evm(self):
        return {}

    def __len__(self):
        return 1

    @property
    def depth(self):
        return 1

    def __iter__(self) -> Iterator[Procedure]:
        return
        yield


@dataclass(init=False, unsafe_hash=True)
class UndefinedProcedure(NamedProcedure, FinalProcedureMixin):
    """Return Undefined.

    A procedure that always returns Undefined.  The `title` of the procedure
    is used as trace in the result.

    """

    def __init__(self, *, title: str = None) -> None:
        self.title = title or _("Price is not defined")

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        return build_result(self, Undefined, demand, env)

    def add_to_travertine_program(self, program):
        program.add_undefined_procedure(id(self), self.title)


@dataclass(init=False, unsafe_hash=True)
class ConstantProcedure(NamedProcedure, FinalProcedureMixin):
    "Return a constant value."

    result: Result

    __slots__ = ("title", "result")

    def __init__(self, result: Result = 0, *, title: str = None) -> None:
        self.result = result
        self.title = title or _("Constant price")

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        return build_result(self, self.result, demand, env)

    def add_to_travertine_program(self, program):
        if self.result is not Undefined:
            program.add_constant_procedure(id(self), float(self.result))
        else:
            program.add_undefined_procedure(id(self), None)


@dataclass(init=False, unsafe_hash=True)
class GetAttributeProcedure(NamedProcedure, FinalProcedureMixin):
    """Return the value of an attribute.

    If the demand contains many requests we return the value of single one.
    So be sure to make demands with a single request.

    If the request does not have the attribute, return Undefined.  If the
    demand has no requests, return Undefined.

    """

    # If the demand contains many requests we return the value of single one.
    # So be sure to make demands with a single request.
    #
    # If the request does not have the attribute, return Undefined.  If the
    # demand has no requests, return Undefined.

    attr: TypedAttribute
    title: str

    __slots__ = ("title", "attr")

    def __init__(self, attr: TypedAttribute, *, title: str = None) -> None:
        self.title = title or _("The value of %s") % attr.name
        self.attr = attr

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        commodities = list(demand.get_commodities())
        if commodities:
            result = getattr(commodities[0], self.attr.name, Undefined)
        else:
            result = Undefined
        return build_result(self, result, demand, env)

    # NOTE on AVM: self.attr is a traversable chain, not actually an
    # attribute.  The **result** is the value of the attribute chain, but the
    # attribute is not used to decide anything.

    def add_to_travertine_program(self, program):
        program.add_getattr_procedure(id(self), self.attr.name)


@dataclass(init=False, unsafe_hash=True)
class VarnameProcedure(NamedProcedure, FinalProcedureMixin):
    """Value of a variable name.

    A procedure that returns the value of a name from the environment.

    """

    varname: str
    default: Result

    __slots__ = ("title", "varname", "default")

    def __init__(self, varname: str, default: Result, *, title: str = None) -> None:
        self.varname = varname
        self.title = title or _("Value of %s") % varname
        self.default = default

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        return build_result(self, env.get(self.varname, self.default), demand, env)

    @property
    def evm(self) -> EVM:
        return {self.varname: self.default}

    def add_to_travertine_program(self, program):
        if self.default is not Undefined:
            program.add_varname_procedure(id(self), self.varname, float(self.default))
        else:
            program.add_varname_procedure(id(self), self.varname, 0.0)


class OperationalProcedureMixin:
    """A mixin for procedures that simply transform another one."""

    @property
    def avm(self):
        return self.proc.avm

    @property
    def evm(self):
        return self.proc.evm

    def __len__(self):
        return len(self.proc) + 1

    @property
    def depth(self):
        return self.proc.depth + 1

    def __iter__(self) -> Iterator[Procedure]:
        yield self.proc  # type: ignore


@dataclass(unsafe_hash=True)
class _RoundingProcedureBase(BaseProcedure, OperationalProcedureMixin):
    proc: Procedure

    def __call__(self, demand: Demand, environment: Environment) -> PriceResultType:
        price = self.proc(demand, environment)
        result = price.result
        if not isinstance(result, type(Undefined)):
            price = price.replace(result=self._round(result))  # type: ignore
        return price

    def _round(self, number: Union[float, int]) -> Union[float, int]:
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__!s}({self.proc!r})"

    def __len__(self):
        return len(self.proc) + 1

    @property
    def depth(self):
        return self.proc.depth + 1


class CeilRoundingProcedure(_RoundingProcedureBase):
    __slots__ = ("proc",)

    def _round(self, number):
        import math

        return math.ceil(number)

    def add_to_travertine_program(self, program):
        program.add_ceil_procedure(id(self), id(self.proc))


class FloorRoundingProcedure(_RoundingProcedureBase):
    __slots__ = ("proc",)

    def _round(self, number):
        import math

        return math.floor(number)

    def add_to_travertine_program(self, program):
        program.add_floor_procedure(id(self), id(self.proc))


@dataclass(init=False, unsafe_hash=True)
class RoundProcedure(_RoundingProcedureBase):
    __slots__ = ("proc", "digits", "method")

    def __init__(self, proc: Procedure, digits: int = 2, method: str = "HALF-UP"):
        method = method.upper()
        assert method in ("UP", "DOWN", "HALF-UP")
        self.proc = proc
        self.digits = digits
        self.method = method

    def _round(self, number):
        return float_round(
            number, precision_digits=self.digits, rounding_method=self.method
        )

    def __repr__(self):
        return f"{self.__class__.__name__!s}({self.proc!r}, {self.digits!r}, {self.method!r})"

    def add_to_travertine_program(self, program):
        program.add_round_procedure(id(self), self.digits, self.method, id(self.proc))


# These are never part of a PriceResult, but since we're testing that every
# procedure must be pickable, and generate programs that contains these, we
# must allow for a sane __eq__
@dataclass(init=False, unsafe_hash=True)
class BaseEnvProcedure(BaseProcedure, OperationalProcedureMixin):
    baseenv: immutables.Map
    proc: Procedure

    __slots__ = ("proc", "baseenv")

    def __init__(self, baseenv: Environment, proc: Procedure) -> None:
        self.baseenv = immutables.Map(baseenv)
        self.proc = proc

    def __repr__(self):
        env = dict(self.baseenv)
        return f"{self.__class__.__name__!s}({env!r}, {self.proc!r})"


class SetEnvProcedure(BaseEnvProcedure):
    """Set values for variables into the environment.

    The values set by this procedure take precedence over the values already
    in the environment.  If a name x is in the calling `env` and in the
    `baseenv`, the value in `baseenv` takes priority.

    """

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        return self.proc(demand, ImmutableChainMap(self.baseenv, env))

    def add_to_travertine_program(self, program):
        # FIXME: Detect the real cause we're getting invalid keys
        env = {
            k: v
            for k, v in self.baseenv.items()
            if isinstance(k, str) and isinstance(v, (float, int))
        }
        program.add_setenv_procedure(id(self), env, id(self.proc))


class SetFallbackEnvProcedure(BaseEnvProcedure):
    """Set default values for variables into the environment.

    The values set by this procedure take lesser precedence over the
    values already in the environment.  If a name X is in the calling
    `env` and in the `baseenv`, the value in `env` takes priority.

    """

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        return self.proc(demand, ImmutableChainMap(env, self.baseenv))

    def add_to_travertine_program(self, program):
        # FIXME: Detect the real cause we're getting invalid keys
        env = {
            k: v
            for k, v in self.baseenv.items()
            if isinstance(k, str) and isinstance(v, (float, int))
        }
        program.add_setfallback_procedure(id(self), env, id(self.proc))


@dataclass(init=False, unsafe_hash=True)
class MapReduceProcedure(NamedProcedure):
    """Map and reduce.

    A procedure that aggregates the result of a base procedure called several
    times according to a splitter.

    When called, this procedures splits each request with the `split` function
    and calls `base_proc` on a new demand using this requests.  Then it passes
    all the results to the `aggregate` function to get a single result.

    Notice that if the original demand has many requests the base procedure is
    called once per request; each time with a demand restricted to the
    sub-requests returned by the splitter per original request.

    """

    split: Splitter
    aggregate: Aggregator
    base_proc: Procedure

    __slots__ = ("title", "split", "aggregate", "base_proc")

    def __init__(
        self,
        splitter: Splitter,
        base_procedure: Procedure,
        aggregator: Aggregator,
        *,
        title: str = None,
    ) -> None:
        self.split = splitter
        self.aggregate = aggregator
        self.base_proc = base_procedure
        self.title = title or _("Aggregated over items")

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        # TODO: Should I leave this to splitters?  Sometime ago, splitters
        # would divide the requests, so no requests meant no values to divide
        # into.
        #
        # For now, let's assume empty demands are somehow ill-formed and
        # should not happen.  However, some other components are creating
        # empty demands.  So let's be nice.
        if demand.requests:
            demands = self.split(demand, env)
        else:
            demands = []
        results = LazyResults(LazyCall(self.base_proc, demand, env) for demand in demands)
        return self.aggregate(results, self.title, demand, env, self)

    @property
    def avm(self) -> AVM:
        return self.base_proc.avm

    @property
    def evm(self) -> EVM:
        return self.base_proc.evm

    def __len__(self):
        return len(self.base_proc) + 1

    @property
    def depth(self):
        return self.base_proc.depth + 1

    def __iter__(self) -> Iterator[Procedure]:
        yield self.base_proc

    def add_to_travertine_program(self, program):
        program.add_identity_procedure(id(self), id(self.base_proc))


@dataclass(init=False, unsafe_hash=True)
class LoopProcedure(NamedProcedure):
    """Loop procedure.

    Aggregates the result of a base procedure called several times: one per
    request.

    This is equivalent to Map and Reduce using the
    `~travertine.splitters.RequestSplitter`:class:.

    """

    aggregate: Aggregator
    base_proc: Procedure

    __slots__ = ("title", "aggregate", "base_proc")

    def __init__(
        self, base_proc: Procedure, aggregator: Aggregator, *, title: str = None
    ) -> None:
        self.aggregate = aggregator
        self.base_proc = base_proc
        self.title = title or _("Aggregated over items")

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        results = LazyResults(
            LazyCall(self.base_proc, demand.replace(requests=(request,)), env)
            for request in demand.requests
        )
        return self.aggregate(results, self.title, demand, env, self)

    @property
    def avm(self) -> AVM:
        return self.base_proc.avm

    @property
    def evm(self) -> EVM:
        return self.base_proc.evm

    def __len__(self):
        return len(self.base_proc) + 1

    @property
    def depth(self):
        return self.base_proc.depth + 1

    def __iter__(self) -> Iterator[Procedure]:
        yield self.base_proc

    def add_to_travertine_program(self, program):
        program.add_identity_procedure(id(self), id(self.base_proc))


@dataclass(init=False, unsafe_hash=True)
class _BranchProcedure(NamedProcedure, Composer):
    min_args: ClassVar[int] = 0  # FIXME: This should be 1 -- git blame
    branches: Sequence[Branch]
    otherwise_procedure: Optional[Procedure]

    __slots__ = (
        "title",
        "branches",
        "otherwise_procedure",
        "match_table",
        "interval_tree",
        "attribute_locator",
        "_avm",
    )

    def __init__(self, *branches: Branch, title: str = None) -> None:
        self._check_args_limits(branches)
        # i18n: title of the branching procedures (with/out backtracking)
        self.title = title or _("Matched from sub-procedures")
        otherwise, branches = self._extract_otherwise_branch(branches)
        self.branches = branches
        self.otherwise_procedure = otherwise
        (
            self.match_table,
            self.interval_tree,
            self.attribute_locator,
        ) = self._prepare_lookup_tables(branches)
        self._avm = None

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        if self.match_table is not None:
            return self._call_single_lookup(demand, env)
        elif self.interval_tree is not None:
            return self._call_range_lookup(demand, env)
        else:
            return ILL_TYPED_PROCEDURE(demand, env)

    def _call_single_lookup(self, demand: Demand, env: Environment) -> PriceResultType:
        attr: Optional[AttributeLocator] = self.attribute_locator
        assert attr is not None
        assert self.match_table is not None
        # Predicate semantics indicates that *all* requests, commodities must
        # match the performed test; so we must get the same value from the
        # locator or this won't be a match.
        values = set(value for value in attr.lookup(demand, Unset) if value is not Unset)
        if len(values) == 1:
            value = values.pop()
            procedures = self.match_table.get(value, (self.nomatch,))
        else:
            procedures = (self.nomatch,)
        return self._call_with_procedures(demand, env, procedures)

    def _call_range_lookup(self, demand: Demand, env: Environment) -> PriceResultType:
        attr: Optional[AttributeLocator] = self.attribute_locator
        assert attr is not None
        assert self.interval_tree is not None
        values = set(value for value in attr.lookup(demand, Unset) if value is not Unset)
        if values:
            value = values.pop()
            cells = self.interval_tree.get(value)
            #  Take for instance two distinct values 1 and 2 and branches like
            #  this:
            #
            #               1         2
            #               |         |
            #         [-----x---------x----]
            #   [-----------x---]     |
            #             [-x---------x-------]
            #
            #  Only the ranges in first and third branch will be valid for all
            #  the values.  So only procedures for those branches will be able
            #  to be considered.  But if a third value should lie outside of
            #  all the three branches, none would match.
            #
            #  So we need to shrink the cells to the ones that contains all
            #  the values in the demand.
            while values and cells:
                value = values.pop()
                candidates = self.interval_tree.get(value)
                cells = tuple(cell for cell in cells if cell in candidates)
            if cells:
                cells_in_branch_order = sorted(
                    tuple(cell for cell in cells), key=lambda c: c.data[0]
                )
                procedures = tuple(cell.data[1] for cell in cells_in_branch_order)
            else:
                procedures = (self.nomatch,)
        else:
            procedures = (self.nomatch,)
        return self._call_with_procedures(demand, env, procedures)

    def _call_with_procedures(
        self, demand: Demand, env: Environment, procedures: Sequence[Procedure]
    ) -> PriceResultType:
        raise NotImplementedError

    @property
    def nomatch(self) -> Procedure:
        raise NotImplementedError

    @property
    def evm(self) -> EVM:
        return {
            varname: val for _, proc in self.branches for varname, val in proc.evm.items()
        }

    def __len__(self):
        return sum(len(proc) for _, proc in self.branches) + 1

    @property
    def depth(self):
        if self.branches:
            return max(proc.depth for _, proc in self.branches) + 1
        else:
            return 1

    def __iter__(self) -> Iterator[Procedure]:
        for _pred, proc in self.branches:
            yield proc
        if self.otherwise_procedure:
            yield self.otherwise_procedure

    def _extract_otherwise_branch(
        self, branches: Tuple[Branch, ...]
    ) -> Tuple[Optional[Procedure], Tuple[Branch, ...]]:
        """Extract the branch a Otherwise predicate.

        Return a pair of `(procedure, branches)`, where `procedure` is either
        None or the procedure matching the Otherwise predicate.  The
        `branches` is the sequence of all branches which are not otherwise.

        Pre-conditions:

        - there's a single Otherwise predicate and it is the last branch; or

        - there's no Otherwise at all.

        """
        if not branches:
            return None, ()
        pred, otherwise_procedure = branches[-1]
        if isinstance(pred, Otherwise):
            branches = branches[:-1]
            assert all(not isinstance(pred, Otherwise) for pred, _proc in branches)
            return otherwise_procedure, branches
        else:
            assert all(not isinstance(pred, Otherwise) for pred, _proc in branches)
            return None, branches

    def _prepare_lookup_tables(
        self, branches: Sequence[Branch]
    ) -> Tuple[
        Optional[Mapping[EqTypeClass, Sequence[Procedure]]],
        Optional[IntervalTree[Tuple[int, Procedure], OrdTypeClass]],
        Optional[AttributeLocator],
    ]:
        """Prepare the look dictionaries to perform fast branching.

        Returns a triplet of:

        - match_table; which is only filled if the predicates perform a
          comparison of type MATCH (e.g MatchesAttributePredicate).

        - interval_tree; which is only filled if the predicates perform
          a comparison of type RANGE (e.g AttributeInRangePredicate,
          QuantityPredicate, etc.)

        - attribute_locator; which is not None only if either the of previous
          is also not None, and contains the AttributeLocator to find the
          values of the attribute to test.

        -

        """
        if not branches:
            return None, None, None
        first_predicate: Predicate = branches[0][0]
        pred_kind = first_predicate.get_kind()
        if pred_kind is None:
            # We can't prepare for a predicate of an unknown attribute or
            # comparison type.
            return None, None, None
        single_lookup: Dict[EqTypeClass, List[Procedure]] = {}
        cells: List[Cell[Tuple[int, Procedure], OrdTypeClass]] = []
        i, well_typed = 0, True
        while well_typed and i < len(branches):
            pred, proc = branches[i]
            i += 1
            well_typed = pred_kind.same_kind(pred.get_kind())
            if well_typed:
                pred_kind = pred.get_kind()
                comparison_kind = pred_kind.comparison_kind
                if isinstance(comparison_kind, RANGE):
                    cell = Cell.from_bounds(
                        comparison_kind.lower, comparison_kind.upper, (i, proc)
                    )
                    cells.append(cell)
                elif isinstance(comparison_kind, MATCH):
                    procedures = single_lookup.setdefault(comparison_kind.value, [])
                    procedures.append(proc)
                else:
                    well_typed = False
        if well_typed:
            if isinstance(pred_kind.comparison_kind, RANGE):
                return (None, IntervalTree.from_cells(cells), pred_kind.attr)
            else:
                assert isinstance(pred_kind.comparison_kind, MATCH)
                return (single_lookup, None, pred_kind.attr)
        else:
            return None, None, None

    def add_to_travertine_program(self, program):
        from .predicates import (
            AttributeInRangePredicate,
            ExecutionPredicate,
            MatchesAttributePredicate,
            QuantityPredicate,
            ValidityPredicate,
        )

        if not self.branches:
            if self.otherwise_procedure:
                program.add_identity_procedure(id(self), id(self.otherwise_procedure))
            else:
                program.add_undefined_procedure(
                    id(self), f"Undefined because {self.title} is not completely defined"
                )
        else:
            first_pred, _ = self.branches[0]
            if isinstance(first_pred, ValidityPredicate):
                method = program.add_branching_procedure_with_validity_pred
            elif isinstance(first_pred, ExecutionPredicate):
                method = program.add_branching_procedure_with_execution_pred
            elif isinstance(first_pred, QuantityPredicate):
                method = program.add_branching_procedure_with_quantity_pred
            elif isinstance(first_pred, MatchesAttributePredicate):
                method = program.add_branching_procedure_with_match_attr_pred
            elif isinstance(first_pred, AttributeInRangePredicate):
                method = program.add_branching_procedure_with_attr_in_range_pred
            else:
                raise AssertionError
            branches = [pred.get_args() + (id(proc),) for pred, proc in self.branches]
            method(
                id(self),
                branches,
                id(self.otherwise_procedure) if self.otherwise_procedure else None,
                isinstance(self, BacktrackingBranchingProcedure),
            )

    # We need to exclude the AVM from the pickle state, because AVM may not be
    # pickable.
    def __getstate__(self):
        return (
            self.branches,
            self.otherwise_procedure,
            self.title,
            self.match_table,
            self.interval_tree,
        )

    def __setstate__(self, state):
        branches, otherwise_procedure, title, match_table, interval_tree = state
        self.branches = branches
        self.otherwise_procedure = otherwise_procedure
        self.title = title
        self.match_table = match_table
        self.interval_tree = interval_tree
        # AttributeLocator is not pickable, so recontruct it from the first
        # predicate.
        if match_table is not None or interval_tree is not None:
            first_predicate, _prod = branches[0]
            self.attribute_locator = first_predicate.get_attr_locator()
        else:
            self.attribute_locator = None
        self._avm = None


class BranchingProcedure(_BranchProcedure):
    """Conditional execution (branch procedure).

    A procedure that executes another based on conditions.

    Each branch is a pair of a `~travertine.types.Predicate`:class: and
    another `~travertine.types.Procedure`:class:.  Only the first branch that
    matches is executed.  If no branch matches return the result Undefined
    annotated with 'Undefined because not branch matched'.

    """

    @property
    def nomatch(self) -> Procedure:
        if self.otherwise_procedure is None:
            return UndefinedProcedure(
                title=_('Undefined because not branch matched in "%s"') % self.title
            )
        else:
            return self.otherwise_procedure

    def _call_with_procedures(
        self, demand: Demand, env: Environment, procedures: Sequence[Procedure]
    ) -> PriceResultType:
        return procedures[0](demand, env)

    @property
    def avm(self) -> AVM:
        res: AVM = self._avm  # type: ignore
        if res is None:
            self._avm = res = BranchingAVM(
                (pred.avm, proc.avm) for pred, proc in self.branches
            )
        return res

    def __repr__(self):
        branches = ", ".join(f"{branch!r}" for branch in self.branches)
        return f"BranchingProcedure({branches!s}, title={self.title!r})"


class BacktrackingBranchingProcedure(_BranchProcedure):
    """Conditional execution with backtracking (Experimental).

    The difference with `BranchingProcedure`:class: is that when no branch
    matches this procedure may backtrack to the next branch of another
    BacktrackingBranchinProcedure.  In the following diagram::

        [Backtracking 1]
           Branch 1  ----------- other procs ----------> [Backtracking 2]
                                                             Branch 5 ...
           Branch 2 -- ...
           Branch 3 -- ...
           ...

    If the procedure ``Backtracking 2`` finds no match, it backtracks
    (following the call stack) to the next matching branch of a calling
    backtracking procedure.  In the example, it will try first ``Branch 2``.
    This creates kind of an AND logical combinator between the predicates of
    ``Branch 1`` and ``Branch 5``.

    If the procedure finds no matches and there's no backtracking procedure is
    in the call stack, return Undefined.

    """

    @property
    def nomatch(self) -> Procedure:
        if self.otherwise_procedure is not None:
            return self.otherwise_procedure

        return_undefined = UndefinedProcedure(
            title=_('Undefined because not branch matched in "%s"') % self.title
        )

        def result(demand, env):
            if context[BACK_TRACKING_EXECUTION]:
                raise NoMatchingBranchError
            else:
                return return_undefined(demand, env)

        return result  # type: ignore

    def _call_with_procedures(
        self, demand: Demand, env: Environment, procedures: Sequence[Procedure]
    ) -> PriceResultType:
        """Return the first result that doesn't perform backtracking."""
        result: Optional[PriceResultType] = None
        pos = 0
        while result is None and pos < len(procedures):
            prod = procedures[pos]
            pos += 1
            with context(BACK_TRACKING_EXECUTION):
                try:
                    result = prod(demand, env)
                except NoMatchingBranchError:
                    result = None
        if result is not None:
            return result
        else:
            return self.nomatch(demand, env)

    @property
    def avm(self) -> AVM:
        res: AVM = self._avm  # type: ignore
        if res is None:
            # WARNING: There's no way to represent the complexity of
            # backtracking in an AVM.  Backtracking performs logical OR when
            # the chain of conditions fail at a point.  So the CascadingAVM we
            # do to compute BranchingAVM is not suitable for a
            # BacktrackingBranchingProcedure.
            #
            # The best thing is to merge each branch separately.
            self._avm = res = merge_avms(
                FilteringAVM(pred.avm, proc.avm) for pred, proc in self.branches
            )
        return res


BACK_TRACKING_EXECUTION = object()


class NoMatchingBranchError(RuntimeError):
    pass


@dataclass(init=False, unsafe_hash=True)
class FormulaProcedure(NamedProcedure, Composer):
    """Compute a simple formula.

    This procedure allows to express simple arithmetical formulae in a
    single step.  This allows the user to have more meaningful formulae
    without having to split it in several procedures.

    The formulae are targeted to return float/int values.  You can use
    variables names by enclosing them in quotes::

       'Variable 1' * ('Variable 2' - 4)

    The result of sub-procedures is referenced with ``#i``, where ``i`` is the
    index of the sub-procedure, starting at 1.  A formula procedure is
    ill-defined is there are less sub-procedures than required by the maximum
    reference in the code.

    """

    procs: Tuple[Procedure, ...]
    code: str
    title: str

    __slots__ = ("procs", "code", "title", "_avm", "compiled", "parsed")

    # We need to put the 'code' after the *procs, because at the moment that's
    # the order in the property 'base_procedure' in Steps.
    def __init__(self, *procs: Procedure, code: str, title: str = None) -> None:
        self._check_args_limits(procs)
        self.code = code
        self.procs = procs
        self.title = title or f"Result of formula {code}"
        self.parsed = parsed = parse(code)
        if parsed:
            self.compiled: Optional[FormulaProcedureType] = transpile(
                parsed, name=f"<{self.title}>"
            )
        else:
            self.compiled = None
        self._avm = None

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        if not self.compiled:
            return build_result(
                self,
                Undefined,
                demand,
                env,
                title=_("Undefined because the formula contained errors"),
            )
        # To the get sub-results we do a little trick by looking the
        # Substep index in the memoization cache for the sub-procedures.
        # This way we don't perform any extra computation needlessly.
        cls, nodes = type(self), list(self.parsed.walk())
        with cls._computation_context() as memory:
            try:
                result = self.compiled(demand, env, self.procs)
            except IndexError:
                logger.warning("IndexError while computing formula '%s'", self.title)
                result = Undefined
            subresults = []
            seen_procs = set()
            seen_vars = set()
            for node in nodes:
                if isinstance(node, Substep):
                    index = node.index - 1
                    if 0 <= index < len(self.procs) and index not in seen_procs:
                        seen_procs.add(index)
                        proc = self.procs[index]
                        subres = memory.get((proc, id(demand), id(env)), None)
                        if subres:
                            subresults.append(subres)
                elif isinstance(node, Variable):
                    varname = node.varname
                    if varname not in seen_vars:
                        seen_vars.add(varname)
                        subresults.append(
                            PriceResult(
                                varname,
                                None,
                                env.get(varname, Undefined),
                                demand,
                                env,
                            )
                        )
        return build_result(self, result, demand, env, *subresults)

    @property
    def evm(self):
        return dict(
            self.parsed.evm,
            **{varname: val for proc in self.procs for varname, val in proc.evm.items()},
        )

    @property
    def avm(self):
        res: AVM = self._avm
        if res is None:
            self._avm = res = merge_avms(proc.avm for proc in self.procs)
        return res

    def __getstate__(self):
        return self.code, self.procs, self.title

    def __setstate__(self, state):
        code, procs, title = state
        self.__init__(*procs, code=code, title=title)

    @property
    def completely_defined(self):
        """False iff there references to unexisting substeps."""
        max_substep_index = self.parsed.max_substep_index
        return max_substep_index <= len(self.procs)

    def __len__(self):
        return sum(len(proc) for proc in self.procs) + 1

    @property
    def depth(self):
        if self.procs:
            return max(proc.depth for proc in self.procs) + 1
        else:
            return 1

    def __iter__(self) -> Iterator[Procedure]:
        yield from iter(self.procs)

    def add_to_travertine_program(self, program):
        program.add_formula_procedure(
            id(self), self.code, [id(proc) for proc in self.procs]
        )


EMPTY_AVM: AVM = {}
EMPTY_EVM: EVM = {}
ILL_TYPED_PROCEDURE = UndefinedProcedure(
    title=_("Undefined because the procedure was ill-typed")
)


if TYPE_CHECKING:

    def check_partials(who: SupportsPartialDefinition) -> None:
        pass

    check_partials(FormulaProcedure(code="$1"))
