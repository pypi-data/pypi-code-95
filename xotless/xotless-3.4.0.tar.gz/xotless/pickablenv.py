#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import logging
from dataclasses import dataclass
from typing import Tuple

logger = logging.getLogger(__name__)


@dataclass(init=False)
class EnvironmentData:
    """A pickable object to represent Odoo's Environment.

    Odoo's Environment holds a connection to the DB and is not pickable.  This
    object holds only data that is pickable, and when required finds the right
    Environment in the Odoo's local data.

    .. warning:: When using the method `find()` you must be sure there's a
       right environment in Odoo's local data.

    .. deprecated:: 1.8.0

    """

    dbname: str
    uid: int
    context: dict  # We expect this to be immutable

    @classmethod
    def from_instance(cls, instance):
        res = getattr(instance, "envdata", None)
        if res is not None:
            return res
        else:
            return cls(instance.env)

    def __init__(self, env):
        if isinstance(env, EnvironmentData):
            self.dbname = env.dbname
        else:
            self.dbname = env.cr.dbname
        self.uid = env.uid
        self.context = dict(env.context)

    def __hash__(self):
        return hash(
            (
                self.dbname,
                self.uid,
                frozenset(
                    self.context
                ),  # Consider only the keys to avoid unhashable values
            )
        )

    def find(self, ignore_user=False, ignore_context=False):
        """Find (in the context) a suitable Odoo environment.

        If both `ignore_user` and `ignore_context` are True any environment
        that matches dbname will be a match.

        In the context of `CURRENT_ENVIRONMENT`:func:, return the given
        environment, but only if its of the same db.

        In the context of `FORCED_ENVIRONMENT`:func:, return the forced
        environment.

        """
        # This is a little dirty trick to avoid creating a new environment for
        # self's db name.  Creating a new Environment requires to open a new
        # cursor to the DB and it won't be the same other modules are using and
        # it'd be leaked.
        from odoo.api import Environment
        from xotl.tools.context import context

        forced = context[_FORCED_ENVIRONMENT].get("env", None)
        if isinstance(forced, Environment):
            return forced

        current = context[_CURRENT_ENVIRONMENT].get("env", None)
        if (
            isinstance(current, Environment)
            and current.cr.dbname == self.dbname
        ):
            return current

        try:
            from odoo.http import request

            env = request.env
            if env and (self.dbname != env.cr.dbname):
                env = None
        except Exception:
            env = None

        envs = list(getattr(Environment._local, "environments", []))
        if env and env in envs:  # Installing addons clears the envs
            return env
        env = None
        while not env and envs:
            env = envs.pop(0)
            if env and (
                self.dbname != env.cr.dbname
                or (self.uid != env.uid and not ignore_user)
                or (self.context != dict(env.context) and not ignore_context)
            ):
                env = None
        if env:
            return env
        else:
            args = (self.dbname, self.uid, self.context)
            envs = list(getattr(Environment._local, "environments", []))
            logger.warning(
                "Could not find a proper environment for %r.  Environments: %r",
                args,
                envs,
            )
            raise MissingEnvironment(*args)


@dataclass
class PickableRecordset:
    """A pickable object to represent Odoo's recordsets.

    .. deprecated:: 1.8.0

    """

    model: str
    ids: Tuple[int]
    envdata: EnvironmentData

    @classmethod
    def from_recordset(cls, recordset):
        result = cls(
            recordset._name,
            tuple(recordset.ids),
            EnvironmentData.from_instance(recordset),
        )
        return result

    @property
    def instance(self):
        return self.envdata.find()[self.model].browse(self.ids)

    def find_instance(self, ignore_env_user=False, ignore_env_context=False):
        return self.envdata.find(
            ignore_user=ignore_env_user, ignore_context=ignore_env_context
        )[self.model].browse(self.ids)

    # Recordset are equal regardless of the Environment full data.  I don't
    # want to rely on Odoo's implementation of Model's __eq__ and __hash__
    # because they assume (actually know) inter-database is not possible.  But
    # since this a pickable record we may get an instance of a DB in the
    # context of another.
    def __eq__(self, other):
        if isinstance(other, PickableRecordset):
            return (
                self.model == other.model
                and set(self.ids) == set(other.ids)
                and self.envdata.dbname == other.envdata.dbname
            )
        else:
            return NotImplemented

    def __hash__(self):
        return hash((self.model, frozenset(self.ids), self.envdata.dbname))

    def __getstate__(self):
        return self.model, self.ids, self.envdata

    def __setstate__(self, state):
        self.model, self.ids, self.envdata = state


class MissingEnvironment(RuntimeError):
    pass


_FORCED_ENVIRONMENT = object()


def FORCED_ENVIRONMENT(env):
    """A context manager to force a given environment while unpickling."""
    from odoo.api import Environment
    from xotl.tools.context import context

    assert isinstance(env, Environment)
    return context(_FORCED_ENVIRONMENT, env=env)


_CURRENT_ENVIRONMENT = object()


def CURRENT_ENVIRONMENT(env):
    """A context manager to use a given environment while unpickling."""
    from odoo.api import Environment
    from xotl.tools.context import context

    assert isinstance(env, Environment)
    return context(_CURRENT_ENVIRONMENT, env=env)
