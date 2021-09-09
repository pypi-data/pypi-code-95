#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from dataclasses import dataclass
from typing import Iterable

from .topo import topological_sort
from .types import Procedure

from ._impl import (  # noqa  isort:skip
    __doc__,
    ExternalObject,
    NullDemand,
    Program,
    UnitaryDemand,
)

NULL_DEMAND = NullDemand()


def create_program(
    procedure: Procedure, capacity: int = None, base_program: Program = None
) -> Program:
    """Creates a program with the entire `procedure` added.

    This function follows a topological sort of the procedure graph so that it
    complies with the API of `Program`:class:.

    The `capacity` should be a close estimate of the number of procedures in
    the program.  You should strive to produce a number as low as possible to
    avoid consuming too much memory.  If unsure leave it as None.

    If `base_program` is not None, extend it without creating a new one.  This
    is useful in combination with `ProgramPseudoProcedure`:class:.  If this
    case, `capacity` is ignored.

    .. warning:: We don't make a copy of the `base_program`, so it gets
       modified.

    .. versionchanged:: 0.6.0  Added parameter `base_program`.

    """
    if base_program is None:
        program = Program(capacity)
    else:
        program = base_program
    for proc in topological_sort(procedure):
        proc.add_to_travertine_program(program)
    return program


@dataclass(init=False)
class ProgramPseudoProcedure:
    """Wraps a program as if it were a procedure.

    This class allows to extend programs in stages.  You can build and store a
    cache of base programs and later wrap them to introduce modifiers.

    Example:

       .. code-block:: python

          from travertine import create_program, ProgramPseudoProcedure
          from travertine.procedures import ConstantProcedure, FormulaProcedure
          from travertine.topo import topological_sort

          base_procedure = ConstantProcedure(10)  # Just imagine this is a big graph of procedures
          program = create_program(base_procedure)

          # Now you'd like to apply a modifying formula over the base
          # procedure but don't like to perform the entire suff.
          ref = ProgramPseudoProcedure(program)
          proc = FormulaProcedure(ref, code="#1 + 100")

          new_program = create_program(proc, base_program=program.clone())

    Instances of this class are not complete procedures: they fail to compute
    the AVM, to be callable and other requirements of `procedures
    <Procedure>`:class:.  They are only useful to create pseudo-procedures
    only meant to be translated to `travertine.Program`:class:.

    .. warning:: You can't mix several programs together using this class.

       That could lead to both unexpected results -- the program behaving
       unpredictably: segfaulting, running without halting, and in the best of
       cases `create_program` would raise ValueError.

    You SHOULD pass the original `base_procedure`, or you MUST ensure it stays
    alive for as long as the `program` is also alive.  Otherwise, Python may
    reclaim the procedure's memory and the indexes in the program would be up
    to being reused.  So adding more procedures to the program could lead to
    ValueError.

    .. versionadded:: 0.6.0

    """

    __slots__ = ("procedure_index", "program", "procedure")

    def __init__(self, program: Program, base_procedure: Procedure = None) -> None:
        self.program = program
        self.procedure = base_procedure
        # The `program.procedure_index` can change after this procedure is
        # added to the program.  So don't trust users will clone the original
        # program when calling `create_program` and store the index.
        self.procedure_index = program.procedure_index

    def __iter__(self) -> Iterable[Procedure]:
        # We don't want to yield 'self.procedure' as a sub-procedure: We
        # simply allow it to hold a reference to the procedure so that the
        # `id` won't be wiped out of memory.
        return
        yield

    def add_to_travertine_program(self, program: Program):
        program.add_identity_procedure(id(self), self.procedure_index)
