#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from collections.abc import Mapping
from functools import partial
from typing import Type

import immutables

from .pickablenv import PickableRecordset

# I won't depend on Odoo, but if it installed ImmutableWrapper will be
# intelligent about it.
try:
    from odoo import models

    BaseModel: Type = models.BaseModel
except ImportError:

    class BaseModel:  # type: ignore
        pass


class ImmutableWrapper:
    """Wraps a `target` object so that it can be used immutably.

    Some external objects (most likely Odoo recordsets) are used within the
    pricing programs immutably but *copies* of such objects are created (e.g
    by splitters) while updating or changing some of its attributes.

    Example usage:

    .. code-block:: python

       >>> Commodity = self.env['operation.commodity']                         # doctest: +SKIP
       >>> target = Commodity.search([('start_date', '!=', False)], limit=1)   # doctest: +SKIP

       >>> wrapped = ImmutableWrapper(target)                                  # doctest: +SKIP
       >>> new = wrapped.replace(start_date=target.start_date + timedelta(1),  # doctest: +SKIP
       ...                       duration=timedelta(1))

       >>> assert new.start_date == target.start_date + timedelta(1)           # doctest: +SKIP

    Immutable wrappers are always flattened.  If the `target` object is
    another instance of ImmutableWrapper, we extract its enclosed object and
    "inherit" the overrides:

    .. code-block:: python

       >>> class new:
       ...     pass

       >>> target = new()
       >>> wrapper = ImmutableWrapper(target, overrides=dict(a="a", c="c"))
       >>> wrapper2 = ImmutableWrapper(wrapper, overrides=dict(b="b"))

       >>> wrapper2._ImmutableWrapper__target is target
       True

       >>> wrapper2.a, wrapper2.b, wrapper2.c
       ('a', 'b', 'c')

    Trying to mutate an attribute raises a TypeError:

    .. code-block:: python

       >>> wrapper2.a = 1
       Traceback (most recent call last):
       ...
       TypeError: Cannot mutate an immutable wrapped object...

    If `wrap_callables` is True, then calling method on the target will
    receive the wrapper (see also ``sudo`` below).

    If `wrap_descriptors` is True, the method ``__get__`` of descriptors in
    the target will receive the wrapper.  This allows properties to work with
    overridden values.

    ImmutableWrapper implements ``__getitem__``.  Any error raised by the
    target is not handled.  The result of __getitem__ might be rewrapped (for
    Odoo recordsets) in another ImmutableWrapper that inherits overrides and
    the value of `wrap_callables` and `wrap_descriptors`.

    ImmutableWrapper implements ``__bool__`` trying to call the underlying's
    type ``__bool__`` with the wrapper as self.  If a TypeError occurrs while
    calling the target's type ``__iter__``, fallback to ``bool(target)``.

    ImmutableWrapper implements a method ``sudo`` specially to support targets
    which are Odoo models.  If the target is an Odoo model, the it simply
    rewraps the result of calling ``sudo`` to the target.  This is done
    despite the value of `wrap_callables` and in this case we don't pass the
    wrapper to the underlying method.  If the target is not an Odoo model, we
    simply try to call a method `sudo` and this time `wraps_callable` is taken
    into account.

    .. versionchanged:: 1.2.0  Add argument `wrap_descriptors`.

    .. versionchanged:: 1.8.0  Add support for ``__getitem__``.

    .. versionchanged:: 2.1.0  Implement ``__bool__``.

    .. versionchanged:: 3.3.0 Add method ``sudo``.

    """

    def __new__(
        self,
        target,
        *,
        overrides=None,
        wrap_callables=False,
        wrap_descriptors=False,
    ):
        if overrides is None:
            overrides = {}
        if isinstance(target, PickableRecordset):
            target = target.instance
        if isinstance(target, ImmutableWrapper):
            attrs = dict(target.__overrides, **overrides)
            target = target.__target
        else:
            attrs = overrides
        result = super().__new__(self)
        # Avoid calling __setattr__ which would fail
        result.__dict__["_ImmutableWrapper__target"] = target
        result.__dict__["_ImmutableWrapper__overrides"] = immutables.Map(attrs)
        result.__dict__["_ImmutableWrapper__cache"] = {}
        result.__dict__["_ImmutableWrapper__wrap_callables"] = wrap_callables
        result.__dict__[
            "_ImmutableWrapper__wrap_descriptors"
        ] = wrap_descriptors
        return result

    def __getitem__(self, key):
        item = self.__target[key]  # let errors go
        return self.__maybe_rewrap(self, item, keep_overrides=True)

    def __getattr__(self, attr):
        from xotl.tools.symbols import Unset

        res = self.__overrides.get(attr, Unset)
        if res is Unset:
            res = self.__cache.get(attr, Unset)
        if res is Unset and self.__wrap_descriptors:
            descriptor = getattr(type(self.__target), attr, None)
            if descriptor is not None:
                fget = getattr(descriptor, "__get__", None)
                if fget is not None:
                    try:
                        res = fget(self, type(self.__target))
                    except TypeError:
                        res = Unset
        if res is Unset:
            res = getattr(self.__target, attr)
        res = self.__maybe_rewrap(self, res, keep_overrides=False)
        self.__cache[attr] = res
        return res

    def __bool__(self):
        if type(self.__target) not in (int, float):
            # int and float will raise a TypeError, so avoid the call.
            method = getattr(type(self.__target), "__bool__", None)
        else:
            method = None
        if method:
            try:
                return method(self)
            except TypeError:
                pass
        return bool(self.__target)

    def __setattr__(self, attr, value):
        raise TypeError(
            "Cannot mutate an immutable wrapped object.  Use method 'replace'."
        )

    def replace(self, **attrs):
        """Return a new wrapper of the same object with updates."""
        overrides = dict(self.__overrides, **attrs)
        return ImmutableWrapper(
            self.__target,
            overrides=overrides,
            wrap_callables=self.__wrap_callables,
            wrap_descriptors=self.__wrap_descriptors,
        )

    @classmethod
    def __maybe_rewrap(cls, self, res, keep_overrides):
        if (
            self.__wrap_callables
            and callable(res)
            and getattr(res, "__self__", None) is self.__target
        ):
            # If `res` a bound method of __target, extract the underlying
            # fuction so that `self` in the method is the ImmutableWrapper.
            res = partial(res.__func__, self)
        if isinstance(res, BaseModel):
            if not keep_overrides:
                res = ImmutableWrapper(
                    res,
                    wrap_callables=self.__wrap_callables,
                    wrap_descriptors=self.__wrap_descriptors,
                )
            else:
                res = ImmutableWrapper(
                    res,
                    overrides=self.__overrides,
                    wrap_callables=self.__wrap_callables,
                    wrap_descriptors=self.__wrap_descriptors,
                )
        return res

    # IMPORTANT: The __cache can't be part of the hash nor of eq because is
    # just an optimization and not a part of the *identity* of the object.
    #
    # Also, there's a minor problem in __eq__ which allows to compare an
    # ImmutableWrapper with the underlying object; this means that instances
    # of ImmutableWrapper and the target object will hash differently despite
    # being equal.  This is only an issue if you mix ImmutableWrappers with
    # wrapped objects in the same collection (set, dict, etc...)
    def __hash__(self):
        if self.__overrides:
            return hash((self.__target, self.__overrides))
        else:
            return hash(self.__target)

    def __eq__(self, other):
        if isinstance(other, ImmutableWrapper):
            return (
                self.__target == other.__target
                and self.__overrides == other.__overrides
            )
        elif isinstance(other, type(self.__target)):
            # We allow for a wrapper to be equal to its underlying target
            # object, but only if there are no overrides.
            return not self.__overrides and self.__target == other
        else:
            return NotImplemented

    def __repr__(self):
        return (
            f"<ImmutableWrapper of '{self.__target!r}' with {self.__overrides}; "
            f"cache: {self.__cache}; wrap_callables: {self.__wrap_callables}>"
        )

    def __getnewargs__(self):
        if isinstance(self.__target, BaseModel):
            return (PickableRecordset.from_recordset(self.__target),)
        else:
            return (self.__target,)

    def __getstate__(self):
        cache = self.__cache
        overrides = self.__overrides
        return (overrides, cache)

    def __setstate__(self, state):
        overrides, cache = state
        self.__dict__["_ImmutableWrapper__overrides"] = overrides
        self.__dict__["_ImmutableWrapper__cache"] = cache

    # Odoo gets special treatment for the method `sudo`, since it changes the
    # Environment into which the target is in being called we cannot rely on
    # `wrap_callables` (it passes the wrapper instance to the method), instead
    # we're rewrapping the result of calling sudo, in such cases.
    #
    # Notice that this method exists only when both xotless and odoo are
    # installed, and this rewrapping only works for Odoo models, otherwise we
    # fallback calling `sudo` from the target despite the value of
    # `wrap_callables`.
    def sudo(self, *args, **kwargs):  # pragma: no cover
        cls = type(self)
        if isinstance(self.__target, BaseModel):
            return cls(
                self.__target.sudo(*args, **kwargs),
                overrides=self.__overrides,
                wrap_callables=self.__wrap_callables,
                wrap_descriptors=self.__wrap_descriptors,
            )
        else:
            get = cls.__getattr__
            return get(self, "sudo")(*args, **kwargs)


class ImmutableChainMap(Mapping):  # noqa
    def __init__(self, *maps):
        self.maps = maps
        self._cache = None

    def _fill_cache(self):
        if self._cache is None:
            self._cache = cache = {}
            for mapping in reversed(self.maps):
                cache.update(mapping)

    def __hash__(self):
        return hash(tuple(hash(mapping) for mapping in self.maps))

    def __eq__(self, other):
        if isinstance(other, ImmutableChainMap):
            other._fill_cache()
            self._fill_cache()
            return self._cache == other._cache
        else:
            return NotImplemented

    def __getitem__(self, key):
        self._fill_cache()
        return self._cache[key]

    def __len__(self):
        self._fill_cache()
        return len(self._cache)

    def __iter__(self):
        self._fill_cache()
        return iter(self._cache)

    def __getstate__(self):
        return self.maps

    def __setstate__(self, state):
        self.__init__(*state)
