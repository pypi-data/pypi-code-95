#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import pickle
from datetime import datetime, timedelta

from hypothesis import strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, consumes, rule
from xotless.pickablenv import CURRENT_ENVIRONMENT
from xotless.tests.strategies.domains import numbers

from ... import create_program
from ...aggregators import SumAggregator
from ...predicates import AttributeInRangePredicate, Otherwise
from ...procedures import (
    BacktrackingBranchingProcedure,
    BranchingProcedure,
    FormulaProcedure,
    LoopProcedure,
    MapReduceProcedure,
    RoundProcedure,
    SetEnvProcedure,
    SetFallbackEnvProcedure,
)
from ...types import AttributeLocator
from . import base
from .structs import sensible_durations

try:
    from odoo.api import Environment as OdooEnvironment
except ImportError:

    class OdooEnvironment:  # type: ignore
        pass


_branches_types = st.sampled_from([BranchingProcedure, BacktrackingBranchingProcedure])
pickle_protocols = st.sampled_from(
    range(pickle.DEFAULT_PROTOCOL, pickle.HIGHEST_PROTOCOL + 1)
)

DATE_ATTR = AttributeLocator.of_demand("date", datetime)
START_DATE_ATTR = AttributeLocator.of_commodity("start_date", datetime)
QUANTITY_ATTR = AttributeLocator.of_request("quantity", float)
ATTR_DURATION = AttributeLocator.of_commodity("duration", timedelta)


class BasicProcedureMachine(RuleBasedStateMachine):
    """A machine that generates pricing programs.

    This machine performs only basic type-level checks.  So you should
    subclass it an create appropriate rules that check whatever you want.

    Also this machine doesn't have the 'env' to access Odoo models.
    Subclasses must provide it.  We promote the following way::

        class MySubClass(ProcedureMachine):
           # create new rules here

        class TestCaseX(TransactionCase):
           def test_the_machine(self):
              class _MySubClass(MySubClass):
                 env = self.env

              run_state_machine_as_test(_MySubClass)

    We have several Bundles:

    ``procedures``

        This bundle keeps all created procedures.  All generated procedures
        are kept in this bundle and also in another more specific type of
        bundle.

    ``basic_procedures``

        Procedures which take no other procedure as an argument.

    ``operational_procedures``

        Procedures that take a single procedure as an argument and perform a
        single operational (discounts, increases, compute margins etc) to the
        result.

    ``reducing_procedures``

        Procedures that take several procedures and reduce their values to a
        single value (sum all results, take the max, etc.).

    ``environ_procedures``

        Procedures that take a single procedure as an argument and manipulate
        the Environment.

    ``branching_procedures``

        Instances of BranchingProcedure or BacktrackingBranchingProcedure.  We
        made them so that they all use the same kind of predicate (except for
        the last on which uses Otherwise).
    """

    procedures = Bundle("procedures")  # type: ignore
    basic_procedures = Bundle("basic_procedures")  # type: ignore
    operational_procedures = Bundle("operational_procedures")  # type: ignore
    reducing_procedures = Bundle("reducing_procedures")  # type: ignore
    environ_procedures = Bundle("environ_procedures")  # type: ignore
    branching_procedures = Bundle("branching_procedures")  # type: ignore
    validity_branching_procedures = Bundle("validity_branching_procedures")  # type: ignore
    quantity_branching_procedures = Bundle("quantity_branching_procedures")  # type: ignore
    execution_branching_procedures = Bundle("execution_branching_procedures")  # type: ignore

    vars = Bundle("variables")  # type: ignore

    # This rule allows to check that we can pickle/unpickle procedures at any
    # time, and we use it to compute prices and as sub-procedures of other
    # bigger programs.
    @rule(target=procedures, proc=consumes(procedures), protocol=pickle_protocols)
    def go_throu_pickle_and_back(self, proc, protocol):
        env = getattr(self, "env", None)
        if isinstance(env, OdooEnvironment):
            with CURRENT_ENVIRONMENT(env):
                result = pickle.loads(pickle.dumps(proc, protocol))
        else:
            result = pickle.loads(pickle.dumps(proc, protocol))
        assert result == proc
        return result

    @rule(targets=(basic_procedures, procedures), proc=base.basic_procedures)
    def create_basic_procedure(self, proc):
        return proc

    @rule(
        targets=(procedures, operational_procedures),
        proc=procedures,
        Type=base.round_procedure_types,
    )
    def create_rounding_procedure(self, proc, Type):
        return Type(proc)

    @rule(
        targets=(procedures, operational_procedures),
        proc=procedures,
        digits=st.integers(min_value=2, max_value=6),
        method=st.sampled_from(["UP", "HALF-UP", "DOWN"]),
    )
    def create_rounding_procedure_with_method(self, proc, digits, method):
        return RoundProcedure(proc, digits, method)

    @rule(target=vars, varname=base.variables)
    def register_variable(self, varname):
        return varname

    @rule(
        targets=(procedures, environ_procedures),
        proc=procedures,
        varname=consumes(vars),
        value=numbers,
    )
    def create_setenv_procedure(self, proc, varname, value):
        return SetEnvProcedure({varname: value}, proc)

    @rule(
        targets=(procedures, environ_procedures),
        proc=procedures,
        varname=consumes(vars),
        value=numbers,
    )
    def create_setfallbackenv_procedure(self, proc, varname, value):
        return SetFallbackEnvProcedure({varname: value}, proc)

    @rule(
        targets=(procedures, branching_procedures, validity_branching_procedures),
        branches=st.integers(min_value=2, max_value=5)
        .flatmap(
            lambda n: st.tuples(
                base.validity_preds(many=n),
                # The size of the procedures must match the size of the
                # predicates
                st.lists(
                    ProcedureMachine.procedures.filter(lambda p: DATE_ATTR not in p.avm),
                    min_size=n,
                    max_size=n,
                ),
            )
        )
        .map(lambda args: list(zip(args[0], args[1]))),
        default_proc=procedures.filter(lambda p: DATE_ATTR not in p.avm) | st.just(None),
        BranchType=_branches_types,
    )
    def create_validity_branches(self, branches, default_proc, BranchType):
        if default_proc is not None:
            return BranchType(*branches, (Otherwise(), default_proc))
        else:
            return BranchType(*branches)

    @rule(
        targets=(procedures, branching_procedures, execution_branching_procedures),
        branches=st.integers(min_value=2, max_value=5)
        .flatmap(
            lambda n: st.tuples(
                base.execution_preds(many=n),
                # The size of the procedures must match the size of the
                # predicates
                st.lists(
                    ProcedureMachine.procedures.filter(
                        lambda p: START_DATE_ATTR not in p.avm
                    ),
                    min_size=n,
                    max_size=n,
                ),
            )
        )
        .map(lambda args: list(zip(args[0], args[1]))),
        default_proc=procedures.filter(lambda p: START_DATE_ATTR not in p.avm)
        | st.just(None),
        BranchType=_branches_types,
    )
    def create_execution_branches(self, branches, default_proc, BranchType):
        if default_proc is not None:
            return BranchType(*branches, (Otherwise(), default_proc))
        else:
            return BranchType(*branches)

    @rule(
        targets=(procedures, branching_procedures, quantity_branching_procedures),
        branches=st.integers(min_value=2, max_value=5)
        .flatmap(
            lambda n: st.tuples(
                base.quantity_preds(many=n),
                # The size of the procedures must match the size of the
                # predicates
                st.lists(
                    ProcedureMachine.procedures.filter(
                        lambda p: QUANTITY_ATTR not in p.avm
                    ),
                    min_size=n,
                    max_size=n,
                ),
            )
        )
        .map(lambda args: list(zip(args[0], args[1]))),
        default_proc=procedures.filter(lambda p: QUANTITY_ATTR not in p.avm)
        | st.just(None),
        BranchType=_branches_types,
    )
    def create_quantity_branches(self, branches, default_proc, BranchType):
        if default_proc is not None:
            return BranchType(*branches, (Otherwise(), default_proc))
        else:
            return BranchType(*branches)

    @rule(
        targets=(procedures, branching_procedures),
        branches_args=st.integers(min_value=2, max_value=5).flatmap(
            lambda n: st.tuples(
                st.lists(sensible_durations, unique=True, min_size=n + 1, max_size=n + 1),
                st.lists(
                    ProcedureMachine.procedures.filter(
                        lambda p: ATTR_DURATION not in p.avm
                    ),
                    min_size=n,
                    max_size=n,
                ),
            )
        ),
        default_proc=procedures.filter(lambda p: ATTR_DURATION not in p.avm)
        | st.just(None),
        BranchType=_branches_types,
    )
    def create_duration_in_ranges_branches(self, branches_args, default_proc, BranchType):
        boundaries, procedures = branches_args
        boundaries.sort()
        first, second, *rest = boundaries
        last = first + second
        predicates = [AttributeInRangePredicate(ATTR_DURATION.attr, first, last)]
        for next_ in rest:
            predicates.append(
                AttributeInRangePredicate(ATTR_DURATION.attr, last, last + next_)
            )
            last += next_
        branches = list(zip(predicates, procedures))
        if default_proc is not None:
            return BranchType(*branches, (Otherwise(), default_proc))
        else:
            return BranchType(*branches)

    @rule(targets=(procedures,), variable=base.variables)
    def create_var_formula_procedure(self, variable):
        result = FormulaProcedure(code=f"'{variable}'")
        assert result.evm == {variable: 0}
        return result

    @rule(proc=procedures)
    def check_all_procedures_have_len(self, proc):
        assert len(proc) > 0

    @rule(proc=procedures)
    def check_all_procedures_have_depth(self, proc):
        assert proc.depth > 0


class ProcedureMachine(BasicProcedureMachine):
    """A machine that generates pricing programs including loops.

    New bundles:

    ``loop_procedures``

        Instances of LoopProcedure.

    ``mapred_procedures``

        Instaces of MapReduceProcedure

    """

    procedures: Bundle = BasicProcedureMachine.procedures
    loop_procedures = Bundle("loop_procedures")  # type: ignore
    mapred_procedures = Bundle("mapred_procedures")  # type: ignore

    @rule(targets=(procedures, loop_procedures), proc=procedures)
    def create_loop_procedure(self, proc):
        # TODO: Aggregate by other means
        return LoopProcedure(proc, SumAggregator())

    @rule(
        targets=(procedures, mapred_procedures),
        proc=procedures,
        splitter=base.splitters,
        aggregator=base.aggregators,
    )
    def create_mapred_procedure(self, proc, splitter, aggregator):
        return MapReduceProcedure(splitter, proc, aggregator)


class BasicProgramMachine(BasicProcedureMachine):
    """A machine that creates `travertine.Program`:class: instances."""

    procedures = BasicProcedureMachine.procedures
    programs = Bundle("programs")  # type: ignore

    @rule(procedure=consumes(procedures), target=programs)
    def create_program(self, procedure):
        return create_program(procedure)


class ProgramMachine(ProcedureMachine):
    """A machine that creates `travertine.Program`:class: instances."""

    procedures = ProcedureMachine.procedures
    programs = Bundle("programs")  # type: ignore

    @rule(procedure=consumes(procedures), target=programs)
    def create_program(self, procedure):
        return create_program(procedure)
