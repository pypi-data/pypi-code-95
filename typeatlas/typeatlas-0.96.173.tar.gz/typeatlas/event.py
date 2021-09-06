# -*- coding: utf-8 -*-
#
#    TypeAtlas Event / Observer Pattern Signals
#    Copyright (C) 2018-2021 Milko Krachounov
#
#    This file is part of TypeAtlas
#
#    TypeAtlas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TypeAtlas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TypeAtlas.  If not, see <http://www.gnu.org/licenses/>.
#
#                                 ***
#
#    Alternatively, you may use this file (part of TypeAtlas libraries)
#    under the terms of the X11/MIT license as follows:
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following
#    conditions:
#
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#    OTHER DEALINGS IN THE SOFTWARE.
#


"""Signal implementation that is similar (but different) from Qt (PySide/PyQt)
signals.

The module also provides NoisySequence, NoisyMapping, and OrderedNoisyMapping.

The signals here are not generally compatible with Qt signals, but in
a limited subset of their use they can be used interchangeably, provided:

1. Only methods are used (a Slot decorator is provided, for compatibility, not needed).
2. Types known to Qt are passed to Signal() only (e.g. other Signal features are ignored)
3. Only positional arguments are passed to signals (that's recommended anyway)
4. No bare functions are used as callbacks (unless the behaviour is changed to default
   to hardref=True for non-methods).
5. No Qt signals are connected to these signals directly.

   Qt supports callbacks with less arguments that the signal. We currently do
   support such use case too, but only for Python methods, and that may incur
   minor performance penalty, which can be taxing if there are a lot of signals call.
   You may consider not relying on it, as it makes optimizing the module easily
   (remove f.__code__.co_argcount code, etc.)

It is preferable to use Qt signals in the Qt part of the code, and this signals
in the non-Qt part of the code, except for performance reasons.
"""

# FIXME: Cannot connect with .emit of Qt signals unless they are
# connected with hardref=True

import os
import sys
import types
import weakref
import traceback
import functools
from collections import defaultdict, OrderedDict
from collections.abc import MutableMapping, MutableSequence
from collections.abc import Mapping, Callable, Hashable
from inspect import CO_VARARGS, CO_VARKEYWORDS

try:
    from typing import Optional
except ImportError:
    Optional = None


SIGNAL_TRACE = bool(os.environ.get('TYPEATLAS_DEBUG_SIGNAL_TRACE'))
SIGNAL_DEBUG = SIGNAL_TRACE


_empty_dict = {}


def _unpack_method(func: Callable) -> tuple:

    """Extract method as a tuple. If this is a method, this
    returns a tuple of self, the function implementing the method,
    if it is a regular function, it returns a tuple of the function
    and None."""

    try:
        return func.__self__, func.__func__
    except AttributeError:
        return func, None


class ObWeakRef(weakref.ref):

    """A weak reference to an object that is hashable, using object
    identity as hash and equality. This allows to store metadata for
    any objects with __weakref__ that is automatically cleared when
    the object is collected."""

    __slots__ = "_oid",

    def __new__(type, ob, callback=None):
        self = weakref.ref.__new__(type, ob, callback)
        self._oid = id(ob)

        return self

    def __eq__(self, other):

        if isinstance(other, ObWeakRef):

            if self is other:
                return True

            selfob = self()
            otherob = other()

            if selfob is not otherob:
                return False

            if selfob is None:
                return self._oid == other._oid

            return True

        return NotImplemented

    def __ne__(self, other):
        value = self.__eq__(other)

        if value is NotImplemented:
            return NotImplemented

        return not value

    def __hash__(self):
        return hash(self._oid)


class ObRef(weakref.ref):

    """A hard reference to an object that is hashable, using object
    identity as hash and equality. This can be used the reference
    created by ObWeakRef to be hard, and the object to never be
    collected."""

    __slots__ = ("ob", "_oid")

    def __init__(self, ob, callback=None):
        self.ob = ob
        self._oid = id(ob)

    def __eq__(self, other):

        if isinstance(other, ObRef):
            return self.ob is other.ob

        if isinstance(other, ObWeakRef):
            return self.ob is other() is not None

        return NotImplemented

    def __ne__(self, other):
        value = self.__eq__(other)

        if value is NotImplemented:
            return NotImplemented

        return not value

    def __hash__(self):
        return hash(self._oid)


class SignalMethod(object):

    """A signal bound to an instance of a class."""

    def __init__(self, signal: 'Signal', instance: object):
        self.signal = signal
        self.instance = instance

    def connect(self, *args, **kwargs):
        """Connect this signal from this instance of the class to a
        callable (usually a method, called a Slot in Qt vernacular).

        See Signal.connect() for signature; the instance is passed
        automatically."""

        self.signal.connect(self.instance, *args, **kwargs)

    def connect_wrapped(self, *args, **kwargs):
        """Connect a callable wrapping a method.

        See Signal.connect_wrapped() for what that means and for
        a signature."""

        self.signal.connect_wrapped(self.instance, *args, **kwargs)

    def disconnect(self, *args, **kwargs):
        """Disconnect a callable from the instance's signal."""
        self.signal.disconnect(self.instance, *args, **kwargs)

    def __call__(*args, **kwargs):
        """Emit the signal with the given arguments. This can be
        called as both signal.emit() for compatibility with Qt,
        and with signal() to allow connecting signals to signals, or
        to use them as drop-in replacements of methods.

        All callbacks are called. Any exceptions are printed on stderr.

        The callbacks need to have the same signature as the signal,
        unless pass_self=True is passed, which provides as an extra arguments.
        Similarly to Qt, a Python function with less arguments will receive
        less than arguments than the signal. Using this would prevent
        optimizing this module by stripping that code out (it has
        not been timed).
        """

        self = args[0]
        args = args[1:]

        if SIGNAL_TRACE:
            owner = type(self.instance)
            name = self.signal.__name__
            if not name or name == '<signal>':
                for attr in dir(owner):
                    if getattr(owner, attr, None) is self.signal:
                        self.signal.__name__ = name = attr
                        break

            print('[DEBUG] signal: %s.%s(%s) @ %r' % (
                        owner.__name__, self.signal.__name__,
                        ', '.join([repr(arg) for arg in args] +
                                  ['%s=%r' % (key, arg)
                                   for key, arg in kwargs.items()]),
                        self.instance),
                  file=sys.stderr)

        return self.signal(self.instance, *args, **kwargs)

    emit = __call__

    @property
    def __func__(self):
        return self.signal

    @property
    def __self__(self):
        return self.instance
    

class Signal(object):

    """A signal descriptor that can be added to a class so that the class can emit
    signals of that type.

    For partial compatibility with Qt, you can pass accepted types as positional
    arguments (they are also used in the documentation for the signal). The types
    can be strings for forward references.

    When partial compatibility with Qt is not required, you can pass doc,
    name and signature_func arguments, which are presently used only for
    documentation purposes. If inherit_func_name=True is passed, that
    means that the signal is exactly like the signal (we inherit name, doc).

    You can use alternative construction Signal.from_function to decorate
    a function and have the arguments, types and documentation introspected
    from it.
    """

    SIGNAL_ASSIGNMENTS = [attr for attr in functools.WRAPPER_ASSIGNMENTS
                          if attr not in ['__name__', '__doc__',
                                          '__qualname__']]

    SIGNAL_UPDATES = [attr for attr in functools.WRAPPER_UPDATES
                           if attr not in ['__dict__']]

    def __init__(self, *typelist, name: str=None,
                                  doc: str=None,
                                  signature_func: types.FunctionType=None,
                                  inherit_func_name: bool=False):

        # An ordered dict allows us to order the items, and to
        # add some extra metadata for the items that is not part of the key
        self.callbacks = defaultdict(OrderedDict)
        self.types = types

        self.__name__ = name or '<signal>'
        self.__doc__ = doc or ''

        if signature_func is not None:
            if inherit_func_name:
                functools.update_wrapper(self, signature_func)
            else:
                self.__qualname__ = (signature_func.__name__.rpartition('.')[0]
                                     + '.' + self.__name__)
                functools.update_wrapper(self, signature_func,
                                         self.SIGNAL_ASSIGNMENTS,
                                         self.SIGNAL_UPDATES)

        #arg_tuple = '*args'
        arg_tuple = ', '.join('<' + getattr(t, __name__, '') or repr(t)  + '>'
                              for t in typelist)

        self.__doc__ += ('\n\n' if self.__doc__ else '') + (
            'You can connect to this signal with self.{0}.connect(ob.method), \n'
            'and it can be emitted with self.{0}.emit({1}) or \n'
            'self.{0}({1}). Usually the class is responsible \n'
            'for emitting the signal, unless noted otherwise.'
                            .format(self.__name__, arg_tuple))

    def connect(self, instance: object, callback: Callable,
                      pass_self: bool=False, hardref: bool=False,
                      receiver: object=None,
                      pass_receiver: bool=True, pass_class: bool=False):

        """Connect a method, callback or, in Qt vernacular, slot to this
        signal for a given instance. The bound signals pass the instance
        automatically, as self is for a method.

        You should pass a callable, which is preferred to be a builtin
        bound method of an instantiated object. In that case, a weak reference
        to the object is kept, and the signal is automatically disconnected
        when the instance is deleted. Other callables are also weakly referenced,
        which may not work (the default behaviour may be altered in the future).
        The provided callable needs to have the same signature as the signal,
        although for Python function arguments not accepted by the callable
        can be omitted for compatibility with Qt signals.

        If you pass hardref=True, the callback uses a hard reference, and is not
        automatically disconnected.

        If you pass pass_self=True, the instance is also passed to the callback.
        In Qt, one would use self.sender() to get the sender of the signal,
        since this isn't supported by typeatlas signals, passing the instance
        explicitly is the only way to get the sender.

        You can manually pass a receiver of a signal, a function (unbound method).
        That way, the function will be called as the receiver as self (first argument),
        and the signal disconnected when the receiver is collected.

        Then, you can disabling the passing of the receiver by pass_receiver=False,
        or pass the class of the receiver with pass_class=True.
        """

        if receiver is not None:
            ob = receiver
            if pass_class:
                method = classmethod(callback)
            elif pass_receiver:
                method = callback
            else:
                method = staticmethod(callback)
        else:
            ob, method = _unpack_method(callback)


        # Support missing arguments in receiver methods, like Qt
        # Only for Python functions, inspect.signature() is too slow.
        argnames = argcount = None

        if method is None:
            try:
                argnames = ob.__code__.co_varnames
                argcount = ob.__code__.co_argcount
                flags = ob.__code__.co_flags

            except AttributeError:
                pass

            else:
                if flags & CO_VARARGS:
                    argcount = None
                else:
                    if pass_self:
                        argcount = max(argcount - 1, 0)

                if flags & CO_VARKEYWORDS:
                    argnames = None

        else:
            try:
                argnames = method.__code__.co_varnames
                argcount = method.__code__.co_argcount
                flags = method.__code__.co_flags

            except AttributeError:
                pass

            else:
                if flags & CO_VARARGS:
                    argcount = None
                else:
                    argcount -= 1
                    if pass_self:
                        argcount -= 1
                    argcount = max(argcount, 0)

                if flags & CO_VARKEYWORDS:
                    argnames = None
                else:
                    argnames = argnames[1:]

        def remove(ignored=None):
            cbs = self.callbacks[instanceref]
            cbs.pop((obref, method, pass_self), None)
            if not cbs:
                del self.callbacks[instanceref]

        def remove_all(ignored=None):
            self.callbacks.pop(instanceref, None)

        if hardref:
            obref = ObRef(ob)
        else:
            obref = ObWeakRef(ob, remove)

        instanceref = ObWeakRef(instance, remove_all)

        self.callbacks[instanceref][obref, method,
                                    pass_self] = (argcount, argnames)

    def disconnect(self, instance: object, callback: Callable,
                         pass_self: bool=False,
                         receiver: object=None,
                         pass_receiver: bool=True, pass_class: bool=False):

        """Disconnect a signal. You need to pass the same arguments as for
        connect, expect hardref."""

        if receiver is not None:
            ob = receiver
            if pass_class:
                method = classmethod(callback)
            elif pass_receiver:
                method = callback
            else:
                method = staticmethod(callback)

        else:
            ob, method = _unpack_method(callback)

        obref = ObWeakRef(ob)
        instanceref = ObWeakRef(instance)

        cbs = self.callbacks[instanceref]
        del cbs[obref, method, pass_self]
        if not cbs:
            del self.callbacks[instanceref]

    def __call__(*args, **kwargs):
        """Emit the signal with the given arguments. This can be
        called as both signal.emit() for compatibility with Qt,
        and with signal() to allow connecting signals to signals, or
        to use them as drop-in replacements of methods.

        All callbacks are called. Any exceptions are printed on stderr.

        Calling from the bound signal instance, you only provide the arguments.
        If you need to call Signal().emit(), you need to provider the instance
        of the sender of the signal as first argument.

        The callbacks need to have the same signature as the signal,
        unless pass_self=True is passed, which provides as an extra arguments.
        Similarly to Qt, a Python function with less arguments will receive
        less than arguments than the signal. Using this would prevent
        optimizing this module by stripping that code out (it has
        not been timed).
        """
        self, instance = args[0:2]
        args = args[2:]

        instanceref = ObWeakRef(instance)

        callback_tuples = list(self.callbacks.get(instanceref,
                                                  _empty_dict).items())

        for ((obref, method, pass_self),
             (argcount, argnames)) in callback_tuples:

            ob = obref()

            if ob is None:
                continue

            if method is None:
                callback = ob
            else:
                callback = method.__get__(ob, type(ob))

            passargs = args
            passkwargs = kwargs

            # Support functions with less arguments, like Qt.
            if argcount is not None:
                passargs = passargs[:argcount]

            # Rare usage?
            if argnames is not None and passkwargs:
                passkwargs = {arg: passkwargs[arg]
                              for arg in argnames if arg in passkwargs}

            try:
                if pass_self:
                    callback(instance, *passargs, **passkwargs)
                else:
                    callback(*passargs, **passkwargs)
            except:
                traceback.print_exc()

    emit = __call__

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return SignalMethod(self, instance)

    def connect_wrapped(self, instance: object,
                              callback: Callable,
                              wrapper: Callable=None,
                              *args, **kwargs) -> 'Optional[Callable]':
        """If you want to wrap a callback that you will call once your
        wrapper has been called, use this function, which will either
        return a decorator connecting your wrapper (if not provided),
        or connect it directly.

        The callback is provided to your wrapper as first argument.

        This cannot be disconnected manually, only automatically.
        """

        def decorator(wrapper):
            ob, method = _unpack_method(callback)

            def helper(*args, **kwargs):
                if method is None:
                    original_callback = ob
                else:
                    original_callback = method.__get__(ob, type(ob))

                return wrapper(original_callback, *args, **kwargs)

            self.connect(instance, helper, receiver=ob, *args, **kwargs)

        if wrapper is not None:
            return decorator(wrapper)
        return decorator

    @classmethod
    def from_function(cls, *typelist, **kwargs) -> Callable:
        def decorator(func: types.FunctionType) -> 'Signal':
            return cls(*typelist, signature_func=func, inherit_func_name=True,
                       **kwargs)
        return decorator


def Slot(*args) -> Callable:
    """For drop-in compatibility with Qt's Slot/Signal,
    return a do-nothing decorator.."""

    def decorator(func: Callable) -> Callable:
        return func

    return decorator


class NoisyMapping(MutableMapping):

    """A noisy mapping implementation that emits signals when modified.

    You can also proxy an tentatively immutable dictionary with the
    NoisyMapping.proxy() alternative constructor.

    The factory attribute defines what will be used to implement the
    dictionary that will be wrapped here. The temporary_factory
    is used as a temporary dictionary factory when e.g. replacing
    the proxied dictionary.

    Signals are defined at the bottom.
    """

    factory = dict
    temporary_factory = OrderedDict

    is_noisy_collection = True

    _unfreeze = None

    def __init__(self, *args, **kwargs):
        self._values = self.factory(*args, **kwargs)

    @classmethod
    def proxy(cls, values: Mapping=None, unfreeze: Callable=None):
        """Create a proxy for some dictionary. If unfreeze is passed,
        dictionary will be converted to a mutable one using it on the first
        modification."""
        self = cls()
        self.replace_proxied(values, unfreeze)
        return self

    def replace_proxied(self, values: Mapping=None, unfreeze: Callable=None):
        """Change the dictionary being proxied. If unfreeze is passed,
        dictionary will be converted to a mutable one using it on the first
        modification."""
        if values is None:
            values = {}

        # Use a temporary dictionary to emit signals for the replacement
        self._values = self.temporary_factory(self._values)
        self.clear()
        self.update(values)

        self._values = values
        self._unfreeze = unfreeze

    def __getitem__(self, key):
        return self._values[key]

    def __delitem__(self, key):
        if self._unfreeze is not None:
            self._values = self._unfreeze(self._values)
            self._unfreeze = None

        value = self._values[key]

        self.delete_pending(key, value)
        del self._values[key]
        self.deleted(key, value)

    def __setitem__(self, key: Hashable, value: object):
        if self._unfreeze is not None:
            self._values = self._unfreeze(self._values)
            self._unfreeze = None

        existing = key in self._values
        if existing:
            old_value = self._values[key]
            self.value_change_pending(key, value, old_value)
        else:
            self.add_pending(key, value)

        self._values[key] = value

        if existing:
            self.value_changed(key, value, old_value)
        else:
            self.added(key, value)

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, dict(self._values))

    delete_pending = Signal(Hashable, object,
                            name='delete_pending', signature_func=__setitem__,
                            doc="A key with a given value is about to be deleted")
    add_pending = Signal(Hashable, object,
                         name='add_pending', signature_func=__setitem__,
                         doc="A key with a given value is about to be added")

    deleted = Signal(Hashable, object,
                     name='deleted', signature_func=__setitem__,
                     doc="A key with a given value was just deleted")
    added = Signal(Hashable, object,
                   name='added', signature_func=__setitem__,
                   doc="A key with a given value was just added")

    def _value_changed_signature(self, key: Hashable,
                                       value: object, old_value: object):
        pass

    value_change_pending = Signal(Hashable, object, object,
                                  name='value_change_pending',
                                  signature_func=_value_changed_signature,
                                  doc="A key is about to be changed to a "
                                      "given value from another value")
    value_changed = Signal(Hashable, object, object,
                           name='value_changed',
                           signature_func=_value_changed_signature,
                           doc="A key was changed to a given from another "
                               "value")

    del _value_changed_signature


class OrderedNoisyMapping(NoisyMapping):

    """An ordered version of a noisy mapping"""

    factory = OrderedDict

    def __eq__(self, other):
        return self._values == other

    def __reversed__(self):
        return reversed(self._values)

    def move_to_end(self, key, last=True):
        """Move the key to end. This does not emit signal, because
        no value is added or removed."""
        self._values.move_to_end(key, last=last)

    def popitem(self, last=True):

        try:
            key = next(reversed(self)) if last else next(iter(self))
        except StopIteration:
            raise KeyError('popitem(): dictionary is empty')

        value = self[key]
        del self[key]

        return key, value


class NoisySequence(MutableSequence):

    """A noisy sequence implementation that emits signals when modified.

    You can also proxy an tentatively immutable list with the
    NoisySequence.proxy() alternative constructor.

    The factory attribute defines what will be used to implement the
    list that will be wrapped here. The temporary_factory
    is used as a temporary list y factory when e.g. replacing
    the proxied sequency.

    Signals are defined at the bottom.
    """

    factory = list
    temporary_factory = list

    is_noisy_collection = True

    _unfreeze = None

    def __init__(self, *args, **kwargs):
        self._values = self.factory(*args, **kwargs)

    @classmethod
    def proxy(cls, values=None, unfreeze=None):
        """Create a proxy for some sequence. If unfreeze is passed,
        sequence will be converted to a mutable one using it on the first
        modification."""
        self = cls()
        self.replace_proxied(values, unfreeze)
        return self

    def replace_proxied(self, values=None, unfreeze=None):
        """Change the sequence being proxied. If unfreeze is passed,
        sequence will be converted to a mutable one using it on the first
        modification."""
        if values is None:
            values = {}

        # Use a temporary sequence to emit signals for the replacement
        self._values = self.temporary_factory(self._values)
        del self[:]
        self[:] = values

        self._values = values
        self._unfreeze = unfreeze

    def __delitem__(self, index):
        if self._unfreeze is not None:
            self._values = self._unfreeze(self._values)
            self._unfreeze = None

        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            indices = range(start, stop, step)
            if step > 0:
                indices = reversed(indices)
            for i in indices:
                del self[i]
            return

        value = self._values[index]
        self.remove_pending(index, value)
        del self._values[index]
        self.removed(index, value)

    def __getitem__(self, index):
        return self._values[index]

    def __len__(self):
        return len(self._values)

    def __setitem__(self, index: int, value: object):
        if self._unfreeze is not None:
            self._values = self._unfreeze(self._values)
            self._unfreeze = None

        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))

            if step != 1:
                value = list(value)
                if len(value) != len(range(start, stop, step)):
                    raise ValueError('attempt to assign sequence of size {} '
                                     'to extended slice of size {}'.format(
                                            len(value),
                                            len(range(start, stop, step))))

            iterator = iter(value)

            for i in range(start, stop, step):
                self[i] = next(iterator)

            for i, v in enumerate(iterator, stop):
                assert step != 1, "impossible code reached"
                self.insert(i, v)
            return

        old_value = self._values[index]
        self.value_change_pending(index, value, old_value)
        self._values[index] = value
        self.value_changed(index, value, old_value)

    def insert(self, index, value):
        if self._unfreeze is not None:
            self._values = self._unfreeze(self._values)
            self._unfreeze = None

        self.insert_pending(index, value)
        self._values.insert(index, value)
        self.inserted(index, value)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, list(self._values))

    def _item_sig(self, index: int, value: object):
        pass

    remove_pending = Signal(int, object,
                            name='remove_pending', signature_func=_item_sig,
                            doc="An index with a given value is about to be "
                                "removed")
    insert_pending = Signal(int, object,
                            name='insert_pending', signature_func=_item_sig,
                            doc="At a given index a given value is about to be "
                                "inserted")

    removed = Signal(int, object,
                     name='removed', signature_func=_item_sig,
                     doc="An index with a given value was removed")
    inserted = Signal(int, object,
                      name='inserted', signature_func=_item_sig,
                      doc="At a given index a given value was inserted")

    def _value_changed_signature(self, index: int,
                                       value: object, old_value: object):
        pass

    value_change_pending = Signal(int, object, object,
                                  name='value_change_pending',
                                  signature_func=_value_changed_signature,
                                  doc="At a given index the value is about to "
                                      "be changed to the given value from the "
                                      "given value")
    value_changed = Signal(int, object, object,
                           name='value_changed',
                           signature_func=_value_changed_signature,
                           doc="At a given index the value was changed "
                               "to the given value from the given "
                               "value")

    del _item_sig, _value_changed_signature


def isnoisy(collection: object) -> bool:
    """Return true if this is a noisy collection."""
    return bool(getattr(collection, 'is_noisy_collection', False))
