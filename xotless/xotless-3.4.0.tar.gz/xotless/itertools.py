#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import collections
from collections.abc import Sequence
from contextlib import contextmanager

from xotl.tools.symbols import Unset

from .pickablenv import EnvironmentData


def tail(iterable, n=1):  # pragma: no cover
    "Return an iterator over the last n items"
    # tail(3, 'ABCDEFG') --> E F G
    return iter(collections.deque(iterable, maxlen=n))


def last(iterable, default=Unset):  # pragma: no cover
    "Return the last item"
    try:
        return next(tail(iterable))
    except StopIteration:
        if default is not Unset:
            return default
        else:
            raise


class Line(Sequence):
    """An immutable list of objects arranged in a line.

    Negative indexes are not wrapped around:

      >>> l = Line(1, 2, 3)
      >>> l[-1]  # doctest: +ELLIPSIS
      Traceback (most recent call last):
      ...
      IndexError: Negative index is not supported

    The line starts at the beginning::

      >>> l.current
      1

    Empty lines are always at the beginning but have no current object::

      >>> l = Line()
      >>> l.beginning
      True

      >>> l.current
      Traceback (...)
      ...
      IndexError: ...

    The constructor allows a single keyword argument `start` so that you may
    place the line at a given position upon construction.  This argument
    supports negative indexes, even though the line itself does not.

    You may also provide the instances in the line as the keyword argument
    `instances` (invalid if any positional argument is provided).

    The inverse of a line is another line with the items in reverse order for
    which the current position gives the same object::

       >>> a = object()
       >>> b = object()
       >>> c = object()

       >>> l = Line(a, b, c)
       >>> l.current is (~l).current is a
       True

       >>> l.next() is a
       True

       >>> l.current is (~l).current is b
       True

    In fact, the function `back()` is defined as if performing a `next()` on
    the inverse and "translating" the change in position back from it.

    """

    START = 0

    def __init__(self, *instances, start=Unset):
        self.instances = instances
        if instances and start is not Unset:
            self.pos = start % len(instances)
        else:
            self.pos = self.START

    @classmethod
    def from_iterable(cls, iterable, start=Unset):
        return cls(*iterable, start=start)

    def __iter__(self):
        # Don't share `self` in iterations.
        return type(self)(*self.instances)

    def __getitem__(self, index):
        if index < 0:  # pragma: no cover
            raise IndexError("Negative index is not supported")
        return self.instances[index]

    def __len__(self):
        return len(self.instances)

    def __bool__(self):
        return len(self) > 0

    __nonzero__ = __bool__

    @property
    def current(self):
        return self[self.pos]

    def __next__(self):
        try:
            result = self.current
            self.pos += 1
            return result
        except IndexError:
            raise StopIteration

    next = __next__

    def __add__(self, other):
        from copy import copy

        result = copy(self)
        result.instances += tuple(other)
        return result

    def __radd__(self, other):
        from copy import copy

        result = copy(self)
        result.instances = tuple(other) + result.instances
        return result

    def __mul__(self, other):
        from copy import copy

        result = copy(self)
        result.instances *= other
        return result

    __rmul__ = __mul__

    def __contains__(self, what):
        return what in self.instances

    def __invert__(self):
        # If we represent a line like: [0, 1, *2, 3] were the * indicates
        # the current position.  Then its invert would be: [3, *2, 1, 0], the
        # position of the invert would that stays at the same element.
        result = type(self)(*reversed(self.instances))
        # We can't use the `start=` keyword argument here because `self.pos`
        # can be outside of the permitted range and since `start=` normalizes
        # it values it would result in a inconsistent state.  If self would be
        # just after the end (or just after the beginning) the inverse just be
        # just before the beginning (or just after the end).
        result.pos = len(self) - self.pos - 1
        return result

    def back(self):
        result = next(~self)
        self.pos -= 1
        return result

    def seek(self, what):
        """Puts the line at the first position where `what` is found.

        If `what` is not found, do nothing.

        """
        try:
            pos = self.instances.index(what)
        except ValueError:
            pass
        else:
            self.pos = pos

    @contextmanager
    def save_excursion(self):
        """A context manager that keeps the 'current' position.

        Example::

        >>> line = Line(1, 2, 3, 4)
        >>> line.seek(1)
        >>> line.current
        1

        >>> with line.save_excursion():
        ...    ahead = line.next()

        >>> with line.save_excursion():
        ...    previous = line.back()
        Traceback (...)
        ...
        StopIteration: ...

        >>> line.current, ahead
        (1, 2)

        """
        pos = self.pos
        try:
            yield self
        finally:
            self.pos = pos

    @property
    def beginning(self):
        """True if the line is at the beginning.

        When beginning is True, there will be no anterior item (IndexError).

        """
        return self.pos == 0

    @property
    def ending(self):
        """True if the line is at the ending.

        When ending is True, there will be no posterior item (IndexError).

        """
        return self.pos == len(self.instances) - 1

    @property
    def posterior(self):
        """The item that is posterior to the current one.

        If there's no posterior item, raise an IndexError.

        """
        with self.save_excursion():
            try:
                self.next()
                return self.next()
            except StopIteration:
                raise IndexError

    @property
    def anterior(self):
        """The item that is anterior to the current one.

        If there's no anterior item, raise an IndexError.

        """
        with self.save_excursion():
            try:
                self.back()
                return self.back()
            except StopIteration:
                raise IndexError


class ModelLine(Line):  # pragma: no cover
    """A line of Odoo models.

    Every item in the line must be an Odoo singleton recordset.

    .. warning:: Pickle support

       Model lines support pickling/unpickling, so you can *safely* put them
       in session-like objects.  However several words of caution are in
       order:

       You must perform all operations (expect pickling/unpickling) within a
       valid xoeuf.odoo.api.Environment manager.

       When you unpickle a model line we defer the actual browsing of Odoo
       recordsets until the first time you access any item.  This is because
       we expect that while loading the session data you may not have entered
       a managed Environment, but while accessing any item you're in your own
       code and, thus, an Environment is probably around.

    """

    EMPTY = {}  # type: ignore

    def __getstate__(self):
        if self.instances:
            envdata = {
                EnvironmentData.from_instance(instance)
                for instance in self.instances
            }
            assert len(envdata) == 1, envdata
            env = tuple(envdata)[0]
            state = {
                "pos": self.pos,
                "instances": [
                    ModelInstance(env, instance._name, instance.id)
                    for instance in self.instances
                ],
            }
            return state
        else:
            return self.EMPTY

    def __getitem__(self, index):
        self._resolve()
        return super(ModelLine, self).__getitem__(index)

    def _resolve(self):
        if len(self):
            result = super(ModelLine, self).__getitem__(0)
            if isinstance(result, ModelInstance):
                # This is the first time we get an item after we got unpickle,
                # we need to convert all to Odoo models now and we need to
                # find the environment.
                env = result.envdata.find()
                self.instances = tuple(
                    env[m._name].browse(m.id) for m in self.instances
                )

    def seek(self, what):
        self._resolve()
        return super(ModelLine, self).seek(what)


class CyclicInteger(int):
    """An integer within the Zn cyclic group.

    Since these integers exist in group with modulus n, you must provide the
    value and the modulus::

      >>> CyclicInteger(1, 10)
      CyclicInteger(1, 10)

    The value is automatically wrapped if needed::

      >>> CyclicInteger(10, 10)
      CyclicInteger(0, 10)

    A cyclic integer is an integer (or maybe a long if you're in Python 2).
    The difference is that when adding a cyclic integer to another number
    it will be confined to the Zn group::

      >>> CyclicInteger(9, 10) + 1
      CyclicInteger(0, 10)

    But this may not be true if the first operand is not a cyclic integer::

      >>> 1 + CyclicInteger(9, 10)
      10...

    """

    def __new__(cls, x, l):
        if l <= 0:
            raise TypeError(
                "Cyclic integers are only defined over strictly positive modulus."
            )
        res = super(CyclicInteger, cls).__new__(cls, x % l)
        res.l = l
        return res

    def __add__(self, y):
        return CyclicInteger(int(self) + y, self.l)

    def __sub__(self, y):
        return CyclicInteger(int(self) - y, self.l)

    def __repr__(self):
        return "CyclicInteger(%s, %s)" % (int(self), self.l)

    def __getnewargs__(self):
        return (int(self), self.l)


class CyclicIntegerDescriptor(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is not None:
            return instance.__dict__[self.name]
        else:
            return self

    def __set__(self, instance, value):
        instance.__dict__[self.name] = CyclicInteger(int(value), len(instance))


class CyclicLine(Line):
    """A line that is circular (or cyclic).

    Cyclic lines must contain at least an element::

       >>> CyclicLine()
       Traceback (...)
       ...
       TypeError: ...

    .. warning:: Calling `next()` will never raise a StopIteration so you
       should never blindly iterate over cyclic lines; they won't stop.

    """

    START = 0
    pos = CyclicIntegerDescriptor("pos")

    # In a cyclic line there's no concept of beginning or ending.  You can
    # always go to the next or previous item.

    @property
    def beginning(self):
        return False

    @property
    def ending(self):
        return False


class CyclicModelLine(CyclicLine, ModelLine):
    pass


class ModelInstance(object):  # pragma: no cover
    # Stands for the model within a ModelLine
    def __init__(self, envdata, model, id):
        self.envdata = envdata
        self._name = model
        self.id = id
