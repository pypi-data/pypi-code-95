# -*- coding: utf-8 -*-
#
#    TypeAtlas Font Filtering
#    Copyright (C) 2019-2021 Milko Krachounov
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


"""Font filter implementation.

Objects whose accept(font) method determines if a font is acceptable
or not.

Includes conjuctive and disjunctive groups, and multitude of views
allowing the filter tree or parts of it to displayed in a variety of
widgets.
"""


# FIXME: The retaining of default kwargs should be handled by change() azjaidyhd7b

import re
import abc
import bisect
import inspect
import operator
import os
import fnmatch
import numbers
from operator import attrgetter, itemgetter
from collections import defaultdict
from collections.abc import MutableMapping, MutableSet, Mapping
from collections.abc import Collection, Set, Sequence, Callable, Iterable
from collections.abc import Hashable
from itertools import count
from functools import partial
from typeatlas import opentype, annotations, fontlist, datastore
from typeatlas.event import Signal, NoisyMapping, NoisySequence
from typeatlas.event import isnoisy
from typeatlas.util import OrderedSet, classproperty, warnmsgf
from typeatlas.util import generic_type, namespace_resolve, MaybeLazy
from typeatlas.util import STRIKE
from typeatlas.langutil import _, N_, H_, textlang
from typeatlas.langutil import LanguageDatabase
from typeatlas.langutil import NATIVE_NAME, ENGLISH_NAME

Optional = generic_type('Optional')
Union = generic_type('Union')
TupleOf = generic_type('Tuple')
SequenceOf = generic_type('Sequence')
IteratorOf = generic_type('Iterator')
IterableOf = generic_type('Iterable')
SetOf = generic_type('Set')


PRIO_TOTAL_CUTOFF = -200
PRIO_MAJOR_CUTOFF = -100
PRIO_DEFAULT = 0
PRIO_MINOR_CUTOFF = 210

COST_FAST = -10
COST_DEFAULT = 0
COST_SLOW = 110

PREFERRED = 'preferred-value'
ANY = 'any-value'


_filter_nums = count(0)


# These contain the constructors and arguments for the default keys of
# the standard filter mappings.
#
# Restore order warning: The restore using the default keys for some
# filters needs to happen in a specific order. For example, all PANOSE
# and IBM subclasses and properties need to be restores before the
# *classes* (families for PANOSE) as the filter depends on the
# family to function, and a GUI requires the family to decide which
# checkbox/combobox it corresponds to.
#
# In addition, file path/name are restored after names, as that might
# help a GUI that uses one textbox for all, with checkboxes for the path/name.
# The current GUI implementation should theoretically work without such
# help, but it is provided nonetheless.
_default_keys = {}
_default_kwargs = {}
_restore_order = {}

_NOTHING = object()

CHANGED = 'changed'
ADDED = 'added'
REMOVED = 'removed'
REPLACED = 'replaced'


KeyTupleType = TupleOf[Optional[str], ...]


## For debuggining purposes, this ensures children filters
## are checked.
SLOW_FILTERS = False

if os.environ.get('TYPEATLAS_DEBUG_TYPECHECK'):
    SLOW_FILTERS = True


## TODO:
#            # FIXME
#            if value in self.group.filters:
#                self.group.remove(value)


# FIXME: [fixed?] Unclassified seems to be None, which we don't like here.
# FIXME: [fixed?] IBM classes don't work
# FIXME: [ok] IBM subclass could depend on the family? Currently manually handled

def register(default_key: str, *,
             restore_order: numbers.Real=0, **kwargs):
    """Return a decorator registering the filter's class for a default key.

    The restore_order keyword argument allows some filter to be loaded after
    others by passing values larger than 0. That includes IBM/PANOSE
    subclass and properties, which depend on the class/family to function.

    Any other kwargs will be passed to the constructor when building a
    default instance for that key.
    """

    def decorator(cls):
        _default_keys[default_key] = cls
        _restore_order[default_key] = restore_order
        if kwargs:
            _default_kwargs[default_key] = kwargs
        cls.default_key = default_key
        if 'default_keys' not in vars(cls):
            cls.default_keys = OrderedSet()
        else:
            cls.default_keys.add(default_key)
        return cls

    return decorator


_cmdline_processor = None
_cmdline_queue = []

def register_cmdline(*options: str, **kwargs):
    """Register the filter for command line use."""
    def decorator(cls):
        if _cmdline_processor is not None:
            _cmdline_processor(cls, *options, **kwargs)
        else:
            _cmdline_queue.append((cls, options, kwargs))
        return cls

    return decorator

def set_cmdline_processor(func: Callable):
    """Set which function to use to process command line arguments. This can
    be called after register_cmdline has been called."""
    _cmdline_processor = func
    for cls, options, kwargs in _cmdline_queue:
        _cmdline_processor(cls, *options, **kwargs)
    _cmdline_queue.clear()



def make_standard_filter(key: str, *args, **kwargs) -> 'Optional[Filter]':
    """Make a standard named filter.

    The factory of the filter is selected by key, and all
    provided arguments are provided to the make() class method
    of the factory."""
    default_kwargs = _default_kwargs.get(key)
    if default_kwargs:
        multiple = kwargs.keys() & default_kwargs.keys()
        if multiple:
            raise TypeError("got multiple values for arguments %s"
                            ', '.join(map(repr, multiple)))

        kwargs = dict(default_kwargs,
                      empty_kwargs=not kwargs,
                      **kwargs)
    return _default_keys[key].make(*args, **kwargs)


def would_make_standard_filter(key: str, *args, **kwargs) -> bool:
    """Return False if the standard filter would not be made, or would be
    removed, with the given arguments.

    The factory of the filter is selected by key, and all
    provided arguments are provided to the would_make() class method
    of the factory.
    """
    default_kwargs = _default_kwargs.get(key)
    if default_kwargs:
        multiple = kwargs.keys() & default_kwargs.keys()
        if multiple:
            raise TypeError("got multiple values for arguments %s"
                            ', '.join(map(repr, multiple)))

        kwargs = dict(default_kwargs,
                      empty_kwargs=not kwargs,
                      **kwargs)
    return _default_keys[key].would_make(*args, **kwargs)


class BranchChange(object):

    """A change in a branch the filter tree. When viewed from a certain
    filter, each change to it or a subfilter is a linked list of objects,
    with the main filter being represented by the outermost BranchChange
    object containing the next one (if it exists) as a 'child' attribute.

    The de-facto change is the innermost change, which can be obtained
    with leaf() or the filter with leading_filter(), but all filters
    along the linked list have their behaviour altered.

    The branch changes are keyed with the keys of their filter. The root
    filter usually is keyless (having a key of None), and the inner
    filters usually have a string key. This means that for a branch change
    from the root, one needs to remove the first element of the tuple to
    get the filter key in order to get the qualified filter key that
    can access the filters in depth.

    These are emitted from branch_changed().
    """

    _key_tuple = None
    _cached_branch_key = _NOTHING

    def __init__(self, filter: 'Filter', replacing: 'Filter'=None,
                       action: str=CHANGED, child: 'BranchChange'=None):
        self.filter = filter
        self.replacing = replacing
        self.action = action
        self.child = child

    def is_leaf(self) -> bool:
        """Return True if this is the innermost change in the branch."""
        return self.child is None

    def leaf(self) -> 'BranchChange':
        """Return the innermost change in the branch."""
        if self.child is None:
            return self
        return self.child.leaf()

    def leading_filter(self) -> 'Filter':
        """Return the innermost filter participating in the branch."""
        return self.leaf().filter

    def changes(self) -> 'IteratorOf[BranchChange]':
        """Yield all the changes along the branch, outermost to innermost."""
        yield self
        if self.child is not None:
            yield from self.child.changes()

    def filters(self, previous: bool=False) -> 'IteratorOf[Filter]':
        """Yield all the filters changed along the branch, outermost to
        innermost.

        If previous=True is passed, the old (replaced) filter is returned
        when a filter was removed and a new one was added, instead of
        the new one.
        """
        if previous and self.replacing is not None:
            yield self.previous
        else:
            yield self.filter

        if self.child is not None:
            yield from self.child.filters(previous)

    def filter_keys(self) -> 'IteratorOf[Optional[str]]':
        """Yield the keys of the filters changed along the branch, outermost to
        innermost."""
        for filter in self.filters():
            yield filter.key

    def key_tuple(self) -> KeyTupleType:
        """Return a tuple of the keys of the filters changed along the branch,
        outermost to innermost.

        By slicing away the first element of the tuple - key_tuple[1:] - one
        can obtain the key used to lookup the innermost filter from the root.
        The reason that it needs to be sliced is that the root is included in
        the tuple.
        """
        result = self._key_tuple
        if result is None:
            self._key_tuple = result = tuple(self.filter_keys())
        return result

    def _branch_key(self) -> str:
        """For debug only, for now. Return the key_tuple as a dotted string."""
        result = self._cached_branch_key
        if result is _NOTHING:
            keys = []
            for key in self.filter_keys():
                #if key is None:
                #    result = None
                #    break
                keys.append(key or '?')
            else:
                result = '.'.join(keys)
            self._cached_branch_key = result
        return result

    def extended(self, *args, action: str=None, **kwargs) -> 'BranchChange':
        """Return a copy of the change with a new child at the bottom.

        This can be used when deleting a whole branch of filters: their
        children aren't changed per se (as they don't exist at all),
        but are still deleted.

        This is used by find_lower_descendants() to simplify dealing with
        changed of children that are of interest.
        """

        if self.child is None:
            if action is None:
                action = self.action
            child = type(self)(*args, action=action, **kwargs)
        else:
            child = self.child.extended(*args, action=action, **kwargs)

        return type(self)(self.filter, self.replacing, self.action, child)

    def find_lower_descendants(self, recursive: bool=False
                               ) -> 'IteratorOf[BranchChange]':
        """Return an iterable of changes covering the changes to
        one level below the deepest direct change.

        When a whole branch is removed, this can deal with the childen
        as it yields branch changes for all those implicitly removed children.
        The children aren't directly removed themsleves, so there is
        no explicit BranchChange for them, and most code watching a
        filter root should guess that the children have been removed.

        However, this method allows an explicit BranchChange to be generated,
        e.g. to rely on the same code for explicit and implicit removals, or
        to more easily locate a removed filter if stored in flat dictionary.
        """

        if recursive:
            for change in self.find_lower_descendants():
                yield change
                yield from change.find_lower_descendants(recursive=True)
            return

        leaf = self.leaf()
        if leaf.action == REPLACED:
            if leaf.replacing.is_group:
                for filter in leaf.replacing.filters:
                    yield self.extended(filter, action=REMOVED)
                for filter in leaf.filter.filters:
                    yield self.extended(filter, action=ADDED)

        else:
            if not leaf.filter.is_group:
                return

            for filter in leaf.filter.filters:
                yield self.extended(filter)

    def __repr__(self):
        leaf = self.leaf()
        return '<%s %r at 0x%x: %s %r>' % (
                    type(self).__name__,
                    self._branch_key(), id(self),
                    leaf.action, leaf.filter)


class Filter(object):

    """A filter. FontFilter is a type of filter."""

    key = default_key = None
    prio = PRIO_DEFAULT
    cost = COST_DEFAULT

    default_keys = []

    def _child_signature(self, child: 'Filter'): pass
    def _branch_signature(self, branch_change: BranchChange): pass
    def _descendant_signature(self, descendant: 'Filter',
                                    parent: 'Filter'): pass

    changed = Signal(doc='This filter was changed, and items need to be '
                         'rescanned')
    branch_changed = Signal(BranchChange, signature_func=_branch_signature,
                            doc='This change occurred within this filter or '
                                'a sub-branch')

    child_added = Signal('Filter', signature_func=_child_signature,
                         doc='A child of this filter was added')
    child_removed = Signal('Filter', signature_func=_child_signature,
                           doc='A child of this filter was removed')

    descendant_added = Signal('Filter', 'Filter',
                              signature_func=_descendant_signature,
                              doc='A child of the given filter was added')
    descendant_removed = Signal('Filter', 'Filter',
                                signature_func=_descendant_signature,
                                doc='A child of the given filter was removed')

    del _branch_signature, _child_signature, _descendant_signature

    unchanged_when_empty = True
    # make() returns None if the first argument is None
    remove_on_none = False
    # make() returns None if the first argument is empty
    remove_on_empty = False

    # this means that if no arguments are specified when creating
    # we won't create. It is not defined yet if the API interprets
    # this during make() or during FilterMapping().standard_filter()
    keep_none_when_unchanged = True

    value_attrname = 'value'
    key_attrname = None

    is_group = False

    @classproperty
    def is_switch(cls) -> bool:
        """True if the filter is a switch (accepts bool as an argument,
        possibly value_attrname is set to a bool, and filters a set of
        items in and out).

        By default, this checks the annotation of the first argument to
        __init__()."""
        if cls.is_group:
            return False
        return cls._construction_hints()['switch']

    @classproperty
    def is_invertible(cls) -> bool:
        """True if the filter is invertible using its second argument,
        defaulting to True. That bool is usually put in the value_attrname
        of the instance.

        By default, this checks the annotation of the second argument to
        __init__()."""
        if cls.is_group:
            return False
        return cls._construction_hints()['invertible']

    @classmethod
    def make(cls, *args,
                   empty_kwargs: bool=False, **kwargs) -> 'Optional[Filter]':
        """Create a new instance of this filter. This typically
        calls the main constructor, but can return None or objects
        of other classes.

        This returns None if the filter is to be removed, or not to
        be created, because the first argument is None, or """
        if not cls.would_make(*args, empty_kwargs=empty_kwargs, **kwargs):
            return None
        return cls(*args, **kwargs)

    @classmethod
    def would_make(cls, *args, empty_kwargs: bool=False,
                               no_create: bool=False, **kwargs) -> bool:
        """Return False if the filter would not be made, or would be removed,
        with the given arguments."""
        if no_create:
            return False
        if args:
            if args[0] is None and cls.remove_on_none:
                return False
            if cls.remove_on_empty and not args[0]:
                return False
        elif ((not kwargs or empty_kwargs) and
              (cls.keep_none_when_unchanged and cls.unchanged_when_empty)):
                return False
        return True

    def change(self, *args, empty_kwargs: bool=False,
                     **kwargs) -> 'Optional[Filter]':
        """Change the filter if we can and returned the changed instance,
        or a new instance if we can't change the current one."""
        if not args and (not kwargs or empty_kwargs) and self.unchanged_when_empty:
            return self
        return type(self).make(*args, **kwargs)

    def connect_branch_change(self, branch: Union[KeyTupleType, str],
                                    callback: Callable):
        """Connect a change to a given branch (specified by tuple of dotted
        string) to a callback."""
        if not isinstance(branch, tuple):
            branch = branch.split('.')

        @self.branch_changed.connect_wrapped(callback, pass_self=True)
        def wrapper(callback, self, branch_change):
            if branch == branch_change.key_tuple()[1:1 + len(branch)]:
                return callback(branch_change)

    def emit_change_signal(self, child_branch: BranchChange=None):
        """Emit change signal for this filter, optionally caused
        by a child filter. Removed filters don't themselves emit a
        signal, so this takes no other arguments."""
        self.branch_changed(BranchChange(self, child=child_branch))
        self.changed()

    def label(self, styled: bool=False) -> str:
        """Return a label for display to the user. If styled=True is
        passed, it is assumed that the filter will be styled according
        to style()"""
        annotation = self.annotation()
        if annotation is None:
            return repr(self)
        return annotation.get_name(translate=_)

    def search_text(self) -> str:
        """Return search text for the filter. By default, that
        returns the label."""
        return self.label(styled=True)

    def description(self, styled: bool=False) -> Optional[str]:
        """Return a description for the filter, like an extended label.
        It can also depend on whether it is styled."""
        return None

    def status_text(self, styled: bool=False) -> Optional[str]:
        """Return status text for the filter."""
        result = self.label(styled=styled)
        if len(result) > 1:
            if result[0].isupper() and result[1].islower():
                result = result[0].lower() + result[1:]
        return result

    def filter_count(self) -> int:
        """Return the count of the filters. This is 0 if we don't filter."""
        return 1 if not self.accepts_everything() else 0

    def style(self) -> SetOf[str]:
        """Return a set of style strings to style the label."""
        return frozenset()

    def icon(self) -> Optional[str]:
        """Return the name of an icon included with typeatlas to use."""
        annotation = self.annotation()
        if annotation is None:
            return None
        return annotation.icon

    def annotation(self) -> Optional[annotations.Annotation]:
        """Return an annotation that can be used by the default
        implementation of icon, etc."""
        return None

    def accept(self, item: object) -> bool:
        """Return True if the item is accepted by the filter."""
        return True

    def accepts_everything(self) -> Optional[bool]:
        """A hint that the filter would accept every item passed to
        it. This can be used to prune disabled filters, or as an
        optimization, or for display purposes. None means we do not
        know, but it should be treated the same as False."""
        return None

    def rejects_everything(self) -> Optional[bool]:
        """A hint that the filter would reject every item passed to
        it. This can be used as an optimization, or for display
        purposes. None means we do not know, but it should be
        treated the same as False."""
        return None

    def get_key(self) -> str:
        """Return a string key that can be used to represent the filter
        in a branch of filters, and identify the filter instance in a group.

        For key-value filters (e.g. language key 'en', required value True)
        this will usually match the key of the filter. For value-only filters
        (e.g. generic family 'serif'), this will match that value.

        This is not a requirement, the key-value pairs, used by
        self.value_mapping(), are distinct from these keys, used by
        self.filter_mapping(), but well-behaved filters should have them
        be equal.
        """
        result = self.key
        if result is None:
            self.key = result = self.generate_key()
        return result

    def generate_key(self) -> str:
        """Generate a random key for a filterless filter."""
        return '%s#%d' % (self.label() or 'filter', next(_filter_nums))

    def is_standard_filter(self) -> bool:
        """Return True if this is a standard filter."""
        key = self.key
        if key == self.default_key:
            return True

        if key in _default_keys and isinstance(self, _default_keys[key]):
            if not _default_kwargs.get(key):
                return True

            # FIXME: This can be slow, or if not slow, too much work?
            arguments = self.factory_arguments()
            if arguments is None:
                # We have no idea, serialization can't work. Assume yes?
                return True

            # Ensure the expected arguments for the default key are set,
            # and thus we are it.
            args, kwargs = arguments
            if kwargs:
                for key, value in _default_kwargs[key].items():
                    if key not in kwargs or kwargs[key] != value:
                        break
                else:
                    return True

        return False

    def _identity(self) -> object:
        """Return an identity that uniquely identifies the filter in a
        set of filters for removal."""
        return id(self)

    def todict(self) -> dict:
        """Convert to dictionary.

        If factory_arguments returns None, this method needs to be
        overriden, but the base should still be called for the type
        finding data to be filled."""

        result = {'key': self.key,
                  'type_key': self.default_key,
                  'type': "%s.%s" % (type(self).__module__,
                                     type(self).__name__)}

        arguments = self.factory_arguments()
        if arguments is None:
            if type(self).todict == Filter.todict:
                raise NotImplementedError
        else:
            result['factory_arguments'] = arguments

        return result

    @classmethod
    def fromdict(cls, data: Mapping) -> 'Filter':
        """Reconstruct from a dictionary.

        If factory_arguments returns None, this method needs to be
        overriden."""

        key = data['type_key']
        if key in _default_keys:
            factory = _default_keys[key]
        elif data['type'].endswith('.FilterConjunctiveGroup'):
            factory = FilterConjunctiveGroup
        if factory.fromdict.__func__ is Filter.fromdict.__func__:
            arguments = data.get('factory_arguments')
            if arguments is None:
                raise NotImplementedError
            args, kwargs = arguments
            return factory(*args, **kwargs)
        return factory.fromdict(data)

    @classmethod
    def fromstring(cls, value: str, *args, **kwargs) -> 'Filter':
        """Create from string."""

        # The default implementation calls the constructor using the
        # annotation of the first argument to construct.

        hints = cls._construction_hints()
        if hints['max_arguments'] < 1 or hints['min_arguments'] > 1:
            raise TypeError("Can't {!r} construct from string".format(cls))

        factory = hints['factory']

        if factory is not None:
            value = factory(value)

        return cls(value, *args, **kwargs)

    def factory_arguments(self) -> Optional[TupleOf[tuple, Mapping]]:
        """Return the arguments to reconstruct this object
        with its factory class. The first return value is the
        argument tuple, the second is the keyword argument dictionary.

        None if this object cannot be serialized that way.

        The default implementation handles the case when __init__
        takes a single argument, and value_attrname is set,
        for non-groups. Or when it takes two for classes with
        key_attrname set.
        """
        if self.is_group or not self.value_attrname:
            return None

        nargs = 2 if self.key_attrname else 1

        signature = inspect.signature(type(self).__init__)
        if len(signature.parameters) != nargs + 1:
            return None

        for param in list(signature.parameters.values())[1:]:
            if param.kind not in [inspect.Parameter.POSITIONAL_ONLY,
                                  inspect.Parameter.POSITIONAL_OR_KEYWORD]:
                return None

        if nargs == 1:
            return (getattr(self, self.value_attrname), ), {}
        elif nargs == 2:
            return (getattr(self, self.key_attrname),
                    getattr(self, self.value_attrname), ), {}
        else:
            raise RuntimeError("like the wooden gargoyles did to the live audience")

    @classmethod
    def _construction_hints(cls) -> Mapping:
        """Return construction hints as a dictionary with the following keys:
            factory: the factory to create from string, by default the annotation
                     of the first argument of __init__
            min_arguments: the minimum arguments required for construction
            max_arguments: the maximum arguments required for construction
            switch: True if this is a boolean switch (e.g. MonospaceFilter)
            invertible: True if this non-switch can be switched using its second
                        argument
        """

        clsvars = vars(cls)
        if '_construction_hints_cache' in clsvars:
            return clsvars['_construction_hints_cache']

        signature = inspect.signature(cls.__init__)

        argument_count = len(signature.parameters) - 1
        factory = None

        min_arguments = None
        is_invertible = False

        for i, param in enumerate(signature.parameters.values()):
            if min_arguments is None and param.default is param.empty:
                min_arguments = i

            if param.kind not in [param.POSITIONAL_ONLY,
                                  param.POSITIONAL_OR_KEYWORD]:
                argument_count = i
                break

            if i == 1:
                if param.annotation is not param.empty:
                    if callable(param.annotation):
                        factory = param.annotation
                    elif isinstance(param.annotation, str):
                        factory = namespace_resolve(globals(),
                                                    param.annotation)
            if i == 2 and param.annotation in ['bool', bool]:
                is_invertible = True

        if min_arguments is None:
            min_arguments = argument_count

        is_switch = factory is bool

        result = {'factory': factory,
                  'switch': is_switch,
                  'invertible': is_invertible,
                  'max_arguments': argument_count,
                  'min_arguments': min_arguments}

        cls._construction_hints_cache = result

        return result

    def __hash__(self):
        return hash(self._identity())

    def __eq__(self, other):
        if not isinstance(other, Filter):
            return NotImplemented
        return self._identity() == other._identity()

    def __ne__(self, other):
        if not isinstance(other, Filter):
            return NotImplemented
        return self._identity() != other._identity()

    def __repr__(self):
        return '<%s 0x%x %r %r>' % (type(self).__name__,
                                    id(self), self.key or '<untitled>',
                                    self._identity())


class FontFilter(Filter):

    """A filter for fonts."""

    def accept(self, item: fontlist.FontLike) -> bool:
        """Return True if the font item is accepted by the filter."""
        return super().accept(item)


class FilterGroup(Filter):

    """A group of filters.

    It acts as a single filter that, depending on the subclass,
    computes a conjuction or disjunction of the child filters.
    Either all filters need to accept the item for the filter
    group to accept it (FilterConjunctiveGroup), or one of
    the child filters needs to accept it (FilterDisjunctiveGroup).

    Unlike regular filters, the label, icon, etc. for a group
    can be explicily set. You can provide an iterable of child
    fitlers.

    An accept_when_empty attribute is provided, which signifies
    whether the group accepts items when it is empty. By default,
    it defaults on whether the group is disjunctive or conjuctive,
    but some groups may want to override that.

    The argument will  be rejected for groups that force it by
    making it a property.
    """

    keep_none_when_unchanged = False
    child_cls = None
    is_group = True

    # True if this is a disjunctive filter, where the filter with the
    # least cutoff dictates the result.
    inverted_cutoff = False

    @property
    def child_factory(self) -> Callable:
        """The factory for children. Can be a property returning
        a callable or a method."""
        return self.child_cls

    _filter_mapping = None
    _filter_sequence = None
    _value_mapping = None
    _value_set = None

    def __init__(self, label: str=None, icon: str=None,
                       filters: IterableOf[Filter]=[], *,
                       accept_when_empty: bool=_NOTHING):

        if accept_when_empty is not _NOTHING:
            try:
                self.accept_when_empty = accept_when_empty
            except AttributeError as exc:
                raise TypeError("accept_when_empty not supported by %r: %s: %s"
                                    % (self, type(exc).__name__, exc))

        self._label = label
        self._icon = icon
        self.prio = PRIO_DEFAULT
        self.filters = OrderedSet()
        self.filters_by_prio = []
        for f in filters:
            self.add(f)

    def filter_mapping(self) -> 'FilterMapping':
        """Return a dictionary-like view of the filters by their key.

        That allows you to view and edit them using a mapping
        interface. See get_key().
        """
        mapping = self._filter_mapping
        if mapping is None:
            self._filter_mapping = mapping = FilterMapping(self)
        return mapping

    def filter_sequence(self) -> 'FilterSequence':
        """Return a sequencee view of the filters by their key.

        The returned sequence has minimal NoisySequence-like interface,
        providing removed and inserted signals, but not value_changed.

        That allows you to view and edit them using a list-like
        interface. See get_key().
        """
        sequence = self._filter_sequence
        if sequence is None:
            self._filter_sequence = sequence = FilterSequence(self)
        return sequence

    def label(self, styled=False) -> str:
        """Return the label of the group, if one was set."""
        result = self._label
        if result:
            return _(result)
        if isinstance(self, FilterDisjunctiveGroup):
            return _('Any of')
        if isinstance(self, FilterConjunctiveGroup):
            return _('All of')
        return super().label(styled=styled)

    def icon(self) -> Optional[str]:
        return self._icon

    def update(self, filters: IterableOf[Filter]):
        """Add children filters to this group."""
        for filter in filters:
            self.add(filter, _suppress_changed=False)

    def get(self, key: str, recursive: bool=False) -> Filter:
        """Get a child filter by key. Not implemented yet."""
        raise NotImplementedError

    def add(self, filter: Filter, *, _suppress_changed: bool=False):
        """Add a child filter to this group."""
        if filter in self.filters:
            if not filter.is_standard_filter():
                return
            self.filters.remove(filter)
        self.filters.add(filter)
        self.child_added(filter)
        self.descendant_added(filter, self)
        filter.descendant_added.connect(self.descendant_added)
        filter.descendant_removed.connect(self.descendant_removed)
        filter.branch_changed.connect(self.update_info_and_emit_signals)
        if not _suppress_changed:
            self.update_info_and_emit_signals(
                        BranchChange(filter, action=ADDED))

    def remove(self, filter: Filter, *, _suppress_changed: bool=False):
        """Remove a child filter from this group."""
        filter.branch_changed.disconnect(self.update_info_and_emit_signals)
        filter.descendant_removed.disconnect(self.descendant_removed)
        filter.descendant_added.disconnect(self.descendant_added)
        self.descendant_removed(filter, self)
        self.child_removed(filter)
        self.filters.remove(filter)
        if not _suppress_changed:
            self.update_info_and_emit_signals(
                        BranchChange(filter, action=REMOVED))

    def replace(self, old_filter: Filter, new_filter: Filter):
        """Replace one child filter with another."""
        self.remove(old_filter, _suppress_changed=True)
        try:
            self.add(new_filter, _suppress_changed=True)
        finally:
            self.update_info_and_emit_signals(
                        BranchChange(new_filter, old_filter,
                                     action=REPLACED))

    def clear(self):
        """Remove all filters from this group."""
        # FIXME: Slow?
        for filter in sorted(self.filters,
                             key=lambda f: _restore_order.get(f.default_key, 0),
                             reverse=True):
            # FIXME: Some widgets are stupid enough to re-add an empty panose filter
            # class, so check if the filter is still not there for some reason.
            # How that makes our filter missing, it's not clear. There's a bug
            # elsewhere.
            if filter in self.filters:
                # FIXME: This is a workaround for an ordering bug
                # that is yet to be properly reproduced and diagnosed.
                # May be related to the re-adding of the empty PANOSE
                # filter.
                if filter.is_group:
                    filter.clear()
                self.remove(filter, _suppress_changed=False)

    def update_info_and_emit_signals(self, child_branch: BranchChange=None):
        """Update information and emit changed signals after child filters
        were added, removed or changed. If this is caused by a change in
        a child, the child's branch change needs to be provided.

        Does update_info() and emit_change_signal() in one step."""
        self.update_info()
        self.emit_change_signal(child_branch)

    def update_info(self):
        """Update information after child filters were added, removed
        or changed. This recalculates the filter priority, etc."""

        if self.filters:
            if self.inverted_cutoff:
                self.prio = max(f.prio for f in self.filters)
            else:
                self.prio = min(f.prio for f in self.filters)
            self.cost = max(f.cost for f in self.filters)
        else:
            self.prio = PRIO_DEFAULT
            self.cost = COST_DEFAULT

        if self.inverted_cutoff:
            self.filters_by_prio = sorted(self.filters,
                                          key=lambda f: f.cost-f.prio)
        else:
            self.filters_by_prio = sorted(self.filters,
                                          key=lambda f: f.cost+f.prio)

    @classproperty
    def supports_value_set(cls) -> bool:
        """True if the filter group can be represented as a set of values."""
        if cls.child_cls is None:
            return False
        return cls.child_cls.key_attrname is None

    @classproperty
    def supports_value_mapping(cls) -> bool:
        """True if the filter group can be represented as a mapping of values."""
        if cls.child_cls is None:
            return False
        return cls.child_cls.key_attrname is not None

    def value_set(self) -> 'FilterValueSet':
        """Return a set view of (scalar) values representing each subfilter,
        which can be used to view or manipulate the filter by just adding and
        removing values from the automatically managed set.

        This is provided by groups (similar to families) where each child filter
        is represented by e.g. a string family, which can be managed as
        a simple set.
        """
        if not self.supports_value_set:
            raise TypeError('value_set() not supported for %r' % (self, ))

        value_set = self._value_set
        if value_set is None:
            value_set = self._value_set = FilterValueSet(self)
        return value_set

    def value_mapping(self) -> 'FilterValueMapping':
        """Return a mapping view of (scalar) keys to (scalar) values representing
        each subfilter, which can be used to view or manipulate the filter by
        just adding, removing and setting key/valuye pairs in the automatically
        managed mapping..

        This is provided by groups (similar to languages) where each child filter
        is represented by e.g. a string language as a key, a value representing
        what to do with that languages.

        For a NoisyMapping view of the same type which can be linked to
        a particular filter key that is periodically deleted and recreated,
        look at NoisyGroupItemConnector.
        """

        if not self.supports_value_mapping:
            raise TypeError('value_mapping() not supported for %r' % (self, ))

        mapping = self._value_mapping
        if mapping is None:
            self._value_mapping = mapping = FilterValueMapping(self)
        return mapping

    def todict(self, keys: IterableOf[str]=None) -> dict:
        """Convert the filter group to a dictionary for serialization.

        You can do a partial serialization by providing a list of keys.
        """

        if keys is not None:
            mapping = self.filter_mapping()
            filters_data = []
            seen = set()
            for key in sorted(keys):
                skip_key = False
                parent = key
                while parent:
                    parent, sep, ignored = parent.rpartition('.')
                    if parent in seen:
                        skip_key = True
                        break
                if skip_key:
                    break
                filter = mapping.standard_filter(key)
                # This should not happen
                if filter is None:
                    continue
                filters_data.append((key, filter.todict()))
            return {'partial': True, 'filters': filters_data}

        result = super().todict()
        result['label'] = self._label
        result['icon'] = self._icon
        result['accept_when_empty'] = self.accept_when_empty
        if self.supports_value_mapping:
            result['values'] = list(self.value_mapping().items())
        elif self.supports_value_set:
            result['values'] = list(self.value_set())
        else:
            result['filters'] = {key: filter.todict()
                                 for key, filter
                                        in self.filter_mapping().items()}
        return result

    def restoredict(self, data: Mapping):

        if data.get('partial'):
            sortkey = lambda tpl: _restore_order.get(tpl[0].rpartition('.'), 0)
            for key, filter_data in sorted(data['filters'], key=sortkey):
                parent_key, key = key.rpartition('.')
                if parent_key:
                    parent = self.filter_mapping().standard_filter(parent_key)
                else:
                    parent = self

                filters = parent.filter_mapping()
                if key in filters and hasattr(filters[key], 'restoredict'):
                    filters[key].restoredict(filter_data)
                else:
                    filters[key] = Filter.fromdict(filter_data)
            return

        self._label = data['label']
        self._icon = data['icon']
        try:
            self.accept_when_empty = data['accept_when_empty']
        except AttributeError:
            pass

        if self.supports_value_mapping:
            mapping = self.value_mapping()
            mapping.clear()
            mapping.update(data['values'])

        elif self.supports_value_set:
            values = self.value_set()
            values.clear()
            values |= data['values']

        else:
            filters = self.filter_mapping()
            filters.clear()

            for key, filter_data in sorted(data['filters'].items(),
                                           key=lambda tpl:
                                                _restore_order.get(tpl[0], 0)):

                if key in filters and hasattr(filters[key], 'restoredict'):
                    filters[key].restoredict(filter_data)
                else:
                    filters[key] = Filter.fromdict(filter_data)

    @classmethod
    def fromdict(cls, data: Mapping) -> 'FilterGroup':
        self = cls()
        self.restoredict(data)
        return self

    def __repr__(self):
        return '<%s 0x%x %r: %r>' % (type(self).__name__,
                                    id(self), self.key or '<untitled>',
                                    list(self.filters))


class FilterConjunctiveGroup(FilterGroup):

    """A filter group that accepts items if all of its children
    filters accept the item."""

    @property
    def accept_when_empty(self) -> bool:
        return True

    def accept(self, item: object) -> bool:
        return all(f.accept(item) for f in self.filters_by_prio)

    def filter_count(self) -> int:
        return sum(filter.filter_count()
                   for filter in self.filters)

    def status_text(self, styled: bool=False) -> Optional[str]:
        if not self.filters:
            return None

        texts = (filter.status_text() for filter in self.filters)
        texts = [text for text in texts if text is not None]

        if len(texts) == 1:
            return texts[0]
        if not texts:
            return None

        return '; '.join(text for text in texts
                         if text is not None)

    def update_info(self):
        super().update_info()
        if SLOW_FILTERS:
            return

        # Pretty unnecessary optimizations go on here
        # If you face trouble, feel free to eradicate them
        self.filters_by_prio = [f for f in self.filters_by_prio
                                  if not f.accepts_everything()]

        try:
            del self.accept
        except AttributeError:
            pass

        if len(self.filters_by_prio) == 1:
            self.accept = self.filters_by_prio[0].accept

    def accepts_everything(self) -> bool:
        return all(f.accepts_everything() for f in self.filters)

    def rejects_everything(self) -> bool:
        return any(f.rejects_everything() for f in self.filters)


@register('names', accept_when_empty=True,
                   label=N_('Font names'), icon='font-item-unknown')
class FilterDisjunctiveGroup(FilterGroup):

    """A filter group that accepts items if any one of its children
    filters accepts the item."""

    accept_when_empty = False
    inverted_cutoff = True

    def accept(self, item: object) -> bool:
        if not self.filters:
            return self.accept_when_empty

        return any(f.accept(item) for f in self.filters_by_prio)

    def filter_count(self) -> int:
        if not self.filters and self.accept_when_empty:
            return 0
        return 1

    def status_text(self, styled: bool=False) -> Optional[str]:
        if not self.filters and self.accept_when_empty:
            return None
        texts = (filter.status_text() for filter in self.filters)
        texts = [text for text in texts if text is not None]

        if len(texts) == 1:
            return texts[0]
        if not texts:
            if self.filters:
                return None
            else:
                texts = ['-']

        return _('one of: %s') % (
                    ', '.join(text for text in texts
                              if text is not None), )

    def update_info(self):
        super().update_info()
        if SLOW_FILTERS:
            return

        # Pretty unnecessary optimizations go on here
        # If you face trouble, feel free to eradicate them
        self.filters_by_prio = [f for f in self.filters_by_prio
                                  if not f.rejects_everything()]

        try:
            del self.accept
        except AttributeError:
            pass

        if len(self.filters_by_prio) == 1:
            self.accept = self.filters_by_prio[0].accept

    def accepts_everything(self) -> bool:
        if not self.filters and self.accept_when_empty:
            return True
        return any(f.accepts_everything() for f in self.filters)

    def rejects_everything(self) -> bool:
        if not self.filters:
            return not self.accept_when_empty
        return all(f.rejects_everything() for f in self.filters)


class PropertyValueSetFilterGroupBase(FilterDisjunctiveGroup, FontFilter):

    """A disjunctive filter group that represents a set of values, and
    accepts a property of the item if the item matches one of the values.

    For performance reasons, the matching is performed by the group directly,
    unless the debugging SLOW_FILTERS is true.
    """

    property_name = None

    def __init__(self, *args, **kwargs):
        self.values = OrderedSet()
        super().__init__(*args, **kwargs)

    @property
    def get_item_value(self) -> Callable:
        """Get the value of an item. This can be either a property
        set to a callable or a method."""
        return attrgetter(self.property_name)

    def label(self, styled=False) -> str:
        return "%s in %r" % (self.property_name, set(self.values))

    def update(self, filters: IterableOf[Filter]):
        super().update(filters)
        self.values.clear()
        self.values.update(f.value for f in self.filters)

    def add(self, filter: Filter, **kw):
        value = getattr(filter, filter.value_attrname)
        self.values.add(value)
        super().add(filter, **kw)

    def remove(self, filter: Filter, **kw):
        # WARNING: The superclass emits signals, so change our set *first*
        value = getattr(filter, filter.value_attrname)
        self.values.remove(value)
        super().remove(filter, **kw)

    def clear(self):
        # WARNING: The superclass emits signals, so change our set *first*
        super().clear()
        self.values.clear()

    def accept(self, item: object) -> bool:
        if SLOW_FILTERS:
            return super().accept(item)

        values = self.values
        if not values and self.accept_when_empty:
            return True
        get_item_value = self.get_item_value
        return any(get_item_value(style) in values for style in item.styles)

    def _identity(self) -> object:
        return (self.property_name + 's', )


@register('outline')
@register_cmdline('--outline')
class OutlineFilter(FontFilter):

    """A filter selecting only outline fonts, or if the value is false,
    only non-outline fonts."""

    remove_on_none = True

    def __init__(self, value: bool=True):
        self.value = bool(value)

    @property
    def prio(self) -> int:
        return PRIO_MINOR_CUTOFF if self.value else PRIO_TOTAL_CUTOFF

    def label(self, styled: bool=False) -> str:
        return _('Outline') if self.value else _('Non-outline')

    def icon(self) -> str:
        if self.value:
            return 'outline'
        else:
            return 'bitmap'

    def annotation(self) -> annotations.Annotation:
        if self.value:
            return annotations.OUTLINE_FONT
        else:
            return annotations.BITMAP_FONT

    def accept(self, item: fontlist.FontLike) -> bool:
        value = self.value
        return any(bool(style.outline) == value for style in item.styles)

    def _identity(self) -> object:
        return ('outline', self.value)


@register('scalable')
@register_cmdline('--scalable')
class ScalableFilter(FontFilter):

    """A filter selecting only scalable fonts, or if the value is false,
    only non-scalable fonts."""

    remove_on_none = True

    def __init__(self, value: bool=True):
        self.value = bool(value)

    @property
    def prio(self) -> int:
        return PRIO_MINOR_CUTOFF if self.value else PRIO_TOTAL_CUTOFF

    def label(self, styled: bool=False) -> str:
        return _('Scalable') if self.value else _('Non-scalable')

    def icon(self) -> str:
        if self.value:
            return 'scalable'
        else:
            return 'bitmap'

    def annotation(self) -> annotations.Annotation:
        if self.value:
            return annotations.OUTLINE_FONT
        else:
            return annotations.BITMAP_FONT

    def accept(self, item: fontlist.FontLike) -> bool:
        value = self.value
        return any(bool(style.scalable) == value for style in item.styles)

    def _identity(self) -> object:
        return ('scalable', self.value)


@register('monospace')
@register_cmdline('--monospace')
class MonospaceFilter(FontFilter):

    """A filter selecting only monospace fonts, or if the value is false,
    only non-monospace fonts."""

    remove_on_none = True

    def __init__(self, value: bool=True):
        self.value = bool(value)

    @property
    def prio(self) -> int:
        return PRIO_TOTAL_CUTOFF if self.value else PRIO_MINOR_CUTOFF

    def label(self, styled: bool=False) -> str:
        return _('Monospace') if self.value else _('Proportional')

    def icon(self) -> Optional[str]:
        if self.value:
            return 'monospace'
        else:
            return None

    def accept(self, item: fontlist.FontLike) -> bool:
        value = self.value
        return any(bool(style.monospace) == value for style in item.styles)

    def _identity(self) -> object:
        return ('monospace', self.value)


@register('family', property_name='family')
@register('stylename', property_name='style')
@register('foundry', property_name='foundry')
@register('filepath', property_name='filepath', restore_order=1)
@register('filename', property_name='filename', restore_order=1)
@register('fullname', property_name='fullname', restore_order=1)
class NameFilter(FontFilter):

    """A filter selecting only fonts with a given name.

    By default, the name is looked up in the family property of the
    font, but you can specify other property, such as filepath, filename,
    fullname, foundry or style.

    It is looked up in the preferred language, but other languages
    can also be looked up.

    You can request an exact match with exact=True, regular expression match
    with regex=True, sequential workds with sequential=True.

    By default, wildcards are respected, and regex can be triggered with
    ~regex. This can be disabled with auto=False.

    By default, case insensitive matching is used, unless case_sensitive=True
    is passed.
    """

    remove_on_none = True
    remove_on_empty = True
    value_attrname = 'name'

    _ignore_styles_for = ['family']

    def __init__(self, name: str, property_name: str='family', *,
                       language: str=PREFERRED,
                       check_all_values: bool=False,
                       regex: bool=False, exact: bool=False,
                       sequential: bool=False,
                       case_sensitive: bool=False, auto: bool=True):

        if property_name in ['filepath', 'filename']:
            font_property = fontlist.property_by_name.get('file')
        else:
            font_property = fontlist.property_by_name.get(property_name)

        if not font_property or not font_property.multiple:
            check_all_values = False
        if not font_property or not font_property.localized:
            language = PREFERRED
        if property_name not in ['file', 'filename', 'filepath']:
            language = PREFERRED

        if not regex:
            name = name.strip()

        needle = None

        if auto and not exact and not regex:
            if name.startswith('~'):
                needle = name[1:]
                regex = True

            if re.search(r'[*?\[\]]', name):
                if sequential:
                    needle = fnmatch.translate(name)
                else:
                    needle = '|'.join(fnmatch.translate(word)
                                      for word in name.split())
                regex = True

        elif regex:
            needle = name

        if needle is None:
            needle = name if case_sensitive else name.casefold()

        self.name = name
        self.needle = needle

        if not sequential and not exact and not regex:
            self.needles = needles = needle.split()
            self.needle = ' '.join(sorted(needles))
        else:
            self.needles = needles = [needle]

        self.regex = regex
        self.exact = exact
        self.case_sensitive = case_sensitive

        self.language = language
        self.check_all_values = check_all_values
        self.property_name = property_name
        self.font_property = font_property

        if regex:
            self.mode = property_name + '-regex'
            name_matches = re.compile(needle,
                                      0 if case_sensitive else re.I).search
        elif exact:
            self.mode = property_name + '-equals'
            if case_sensitive:
                name_matches = lambda family: family == needle
            else:
                name_matches = lambda family: family.casefold() == needle
        elif len(needles) > 1:
            self.mode = property_name + '-contains-words'
            if case_sensitive:
                name_matches = lambda family: all(needle in family
                                                  for needle in needles)
            else:
                # FIXME: Multiple casefoldings, not fatal as all need to
                # match, but still
                name_matches = lambda family: all(needle in family.casefold()
                                                  for needle in needles)
        else:
            self.mode = property_name + '-contains'
            if case_sensitive:
                name_matches = lambda family: needle in family
            else:
                name_matches = lambda family: needle in family.casefold()

        ignore_styles = property_name in self._ignore_styles_for

        # The simple matchers
        if not check_all_values and language == PREFERRED:
            attribute = property_name
            if property_name in ['filepath', 'file']:
                attribute = 'file'
                item_matches = lambda item: name_matches(item.file)
            elif property_name == 'filename':
                item_matches = (lambda item:
                                    name_matches(os.path.basename(item.file)))
            elif ignore_styles:
                item_matches = (lambda item:
                                    name_matches(getattr(item, property_name)))
            else:
                item_matches = (lambda item:
                                    any(name_matches(getattr(item,
                                                             property_name))
                                        for style in item.styles))

        # The complex matchers
        else:
            assert check_all_values or language != PREFERRED
            assert font_property
            assert font_property.localized or font_property.multiple

            if ignore_styles:
                get_items = lambda item: [item]
            else:
                get_items = lambda item: item.styles

            if language == PREFERRED:
                assert check_all_values

                if property_name in ['filepath', 'file']:
                    attribute = 'file_alts'
                    get_names = lambda item: (
                                    font_file.file
                                    for font_file in item.file_alts)
                elif property_name == 'filename':
                    attribute = 'filepath_alts'
                    get_names = lambda item: (
                                    os.path.basename(font_file.file)
                                    for font_file in item.file_alts)
                else:
                    attribute = property_name + '_alts'
                    get_names = lambda item: getattr(item, attribute)

            elif language != ANY:
                assert property_name not in ['file', 'filename', 'filepath']
                if check_all_values:
                    attribute = property_name + '_alts_by_lang'
                    get_names = (lambda item:
                                    getattr(item, attribute).get(language, ()))
                else:
                    attribute = property_name + '_by_lang'

                    def get_names(item):
                        values = getattr(item, attribute)
                        value = values.get(language)
                        if value is not None:
                            yield value

            else:
                assert property_name not in ['file', 'filename', 'filepath']
                if check_all_values:
                    attribute = property_name + '_alts_by_lang'
                    get_names = lambda item: (
                                    value
                                    for lang, values
                                        in getattr(item, attribute).items()
                                    for value in values)
                else:
                    attribute = property_name + '_by_lang'
                    get_names = lambda item: (
                                    value
                                    for lang, value
                                        in getattr(item, attribute).items())

            item_matches = lambda item: any(
                                name_matches(name)
                                for subitem in get_items(item)
                                for name in get_names(subitem))


        self._name_matches = name_matches
        self.accept = self._item_matches = item_matches

        self._used_attribute = attribute

        if case_sensitive:
            self.mode += '-case'

    @classmethod
    def split_filter_text(cls, text: str,
                          case_sensitive: bool=False) -> TupleOf[str, Mapping]:
        """Split filter text into a font name filter, and a dict of other filters
        by their key."""
        text = text or ''

        if not case_sensitive:
            text = text.casefold()

        keys = {k: k for k in cls.default_keys}
        keys.update({'file': 'filename', 'path': 'filepath',
                     'chars': 'charset', 'charset': 'charset'})

        pattern = r'\s*\b({}):(\S+)*\s*'.format('|'.join(keys))

        extra_filters = {}

        def replacement(match):
            key = keys[match.group(1)]
            text = match.group(2)
            if key in extra_filters:
                extra_filters[key] += ' ' + text
            else:
                extra_filters[key] = text
            return ' '

        return re.sub(pattern, replacement, text).strip(), extra_filters

    @classmethod
    def unsplit_filter_text(cls, text: str,
                                 extra_filters: Mapping=None) -> str:
        """Create filter text from a font name filter, and a dict of other filters
        by their key."""
        if not extra_filters:
            return text

        parts = [text]

        for key in sorted(extra_filters):
            if key not in cls.default_keys and key != 'charset':
                raise KeyError(key)
            parts.extend((key + ':' + v) for v in extra_filters[key].split())

        return ' '.join(parts)

    def factory_arguments(self) -> TupleOf[tuple, Mapping]:
        return (self.name, self.property_name), dict(
                    language=self.language,
                    check_all_values=self.check_all_values,
                    regex=self.regex, exact=self.exact,
                    case_sensitive=self.case_sensitive)

    @property
    def prio(self) -> int:
        return PRIO_MAJOR_CUTOFF

    def label(self, styled: bool=False) -> str:

        if self.property_name in ['filepath', 'file']:
            propname = _('File path')
        elif self.property_name == 'filename':
            propname = _('File name')
        elif self.font_property:
            propname = _(self.font_property.label)
        else:
            propname = self.property_name.capitalize()

        if self.regex:
            return _('{property} matching {pattern}').format(
                        property=propname, pattern=self.name)
        elif self.exact:
            return _('{property} named {name}').format(
                        property=propname, name=self.name)
        else:
            return _('{property} containing {text}').format(
                        property=propname, text=self.name)

    def status_text(self, styled: bool=False) -> str:
        if self.regex:
            template = '~%s'
        elif self.exact:
            template = '=%s'
        else:
            template = '*%s*'
        return template % (self.needle, )

    def icon(self) -> str:
        return 'font-item-unknown'

    def accept(self, item: fontlist.FontLike) -> bool:
        return self._item_matches(item)

    def _identity(self) -> object:
        return (self.mode, self._used_attribute, self.needle, self.language)


split_filter_text = NameFilter.split_filter_text
unsplit_filter_text = NameFilter.unsplit_filter_text
name_filter_keys = NameFilter.default_keys | OrderedSet(['charset'])


CharListType = Union[str, SequenceOf[int]]


@register('charset')
class SupportsCharsFilter(FontFilter):

    """A filter accepting fonts that conatain a given list of characters.
    By default, all are required. You can pass contains_all=False to
    return fonts that contain any of them."""

    remove_on_none = True
    remove_on_empty = True
    value_attrname = 'chars'

    def __init__(self, chars: CharListType, contains_all: bool=True):
        original = chars

        chars = sorted(set(chars))
        if chars and isinstance(chars[0], int):
            self.chars = chars
            self.charstring = ''.join(map(chr, chars))
        else:
            self.chars = list(map(ord, chars))
            self.charstring = ''.join(chars)

        self.contains_all = contains_all

        if isinstance(original, str):
            self.original = original
        else:
            self.original = self.charstring

        self._prio = (PRIO_MINOR_CUTOFF
                        if self.charstring.isascii()
                        else PRIO_MAJOR_CUTOFF)
        self._require = all if contains_all else any

    @property
    def name(self):
        """For compatibility with NameFilter, return the charstring originally
        passed to us."""
        return self.original

    def factory_arguments(self) -> TupleOf[tuple, Mapping]:
        return (self.chars, self.contains_all), {}

    @property
    def prio(self) -> int:
        return self._prio

    def label(self, styled: bool=False) -> str:
        if self.contains_all:
            return _('Containing: {characters}').format(characters=self.charstring)
        else:
            return _('Contains one of: {characters}').format(characters=self.charstring)

    def icon(self) -> str:
        return 'character-letter'

    def accept(self, item: fontlist.FontLike) -> bool:
        charset = item.charset
        if charset is None:
            charset = item.get_charset()
        return self._require(c in charset for c in self.chars)

    def _identity(self) -> object:
        return ('contains', self.charstring)


@register('language')
@register_cmdline('--language', '--lang', '-L')
class FontLanguageFilter(FontFilter):

    """Language filter. The language is required if the value is True,
    or forbidden if the value is False."""

    remove_on_none = True
    remove_on_empty = True

    key_attrname = 'language'

    def __init__(self, language: str, value: bool=True):
        self.language = language
        self.value = bool(value)

    @property
    def prio(self) -> int:
        # TODO: Also other Latn languages from samples
        if self.language == 'en':
            return PRIO_MINOR_CUTOFF if self.value else PRIO_TOTAL_CUTOFF
        return PRIO_MAJOR_CUTOFF if self.value else PRIO_MINOR_CUTOFF

    def label(self, styled: bool=False) -> str:
        langdb = LanguageDatabase.get_instance()
        label = langdb.language_name(self.language)
        if not styled:
            return ('+' if self.value else '-') + label
        return label

    def style(self) -> Set:
        return set() if self.value else set([STRIKE])

    def icon(self) -> Optional[str]:
        if self.value:
            langdb = LanguageDatabase.get_instance()
            countryflag = langdb.guess_country_flag(self.language)
            if countryflag:
                return 'flags/' + countryflag
            return None
        return None

    def accept(self, item: fontlist.FontLike) -> bool:
        lang = self.language
        if self.value:
            return any(lang in style.lang for style in item.styles)
        else:
            return not all(lang in style.lang for style in item.styles)

    def _identity(self) -> object:
        return ('language', self.language, self.value)

    def generate_key(self) -> str:
        return self.language


@register('languages')
@register_cmdline('--languages', '--langs')
class FontLanguagesFilterGroup(FilterConjunctiveGroup, FontFilter):
    """Language filter group, accepting fonts with the given
    configuration of required and forbidden languages in the children
    filters.

    This filter supports value_mapping().
    """

    child_cls = FontLanguageFilter

    def label(self, styled: bool=False) -> str:
        return _("Languages")

    def icon(self) -> str:
        return 'select-language'


@register('fontformat')
@register_cmdline('--font-format', '--fontformat')
class FontFormatFilter(FontFilter):

    """Format filter. Only accept fonts of the given format."""

    remove_on_none = True
    remove_on_empty = True

    def __init__(self, value: str):
        self.value = value
        self.font_format_info = fontlist.font_formats.get(value)

    @property
    def prio(self) -> int:
        return PRIO_MAJOR_CUTOFF

    def label(self, styled: bool=False) -> str:
        if self.font_format_info is not None:
            return self.font_format_info.name
        return self.value

    def icon(self) -> Optional[str]:
        if self.font_format_info is not None:
            return self.font_format_info.category_icon
        return None

    def annotation(self) -> annotations.Annotation:
        if self.font_format_info is not None:
            return self.font_format_info.annotation
        return None

    def accept(self, item: fontlist.FontLike) -> bool:
        value = self.value
        return any(style.fontformat == value for style in item.styles)

    def _identity(self) -> object:
        return ('fontformat', self.value)


@register('fontformats')
@register_cmdline('--font-formats', '--fontformats')
class FontFormatsFilterGroup(PropertyValueSetFilterGroupBase):
    """Font format filter group, accepting fonts with one of the formats.

    This filter supports value_set().
    """

    property_name = 'fontformat'
    child_cls = FontFormatFilter

    def label(self, styled: bool=False) -> str:
        return _("Font format")

    def icon(self) -> Optional[str]:
        return None


class FontGroupFilterBase(FontFilter):

    """Categorization group filter (tag or category), accepting only fonts
    in the given category or tag.

    The group is required if the value is True, or forbidden if the
    value is False.

    Use the specific subclasses, FontCategoryFilter and FontTagFilter,
    which filter by category or tag.
    """

    remove_on_none = True
    remove_on_empty = True

    key_attrname = 'group'

    grouping_type = None
    grouping_factory = None

    def __init__(self, group: str, value: bool=True):
        # FIXME: Global variable in use here.
        self._categorization = datastore.Categorization.get_instance()
        self._container = self._categorization.container(self.grouping_type)
        self._info = self._container.info
        self._families = self._container.families

        self.group = group
        self.value = bool(value)

    @property
    def prio(self) -> int:
        return PRIO_MAJOR_CUTOFF if self.value else PRIO_MINOR_CUTOFF

    def label(self, styled: bool=False) -> str:
        if not styled:
            return ('+' if self.value else '-') + self.group
        return self.group

    def style(self) -> Set:
        return set() if self.value else set([STRIKE])

    def icon(self) -> Optional[str]:
        if self.value:
            info = self._info.get(self.group)
            if info:
                return info.icon
        return None

    def accept(self, item: fontlist.FontLike) -> bool:
        families = self._families.get(self.group, ())
        if self.value:
            return item.family in families
        else:
            return item.family not in families

    def _identity(self) -> object:
        return ('group', self.group, self.value)

    def generate_key(self) -> str:
        return self.group


class FontGroupsFilterGroupBase(FilterConjunctiveGroup, FontFilter):

    """Categorization group filter group, accepting fonts with the given
    configuration of required and forbidden tags/categories in the children
    filters.

    Use the specific subclasses, FontCategoriesFilterGroup and
    FontTagsFilterGroup which filter by category or tag.

    This filter supports value_mapping().
    """
    child_cls = FontGroupFilterBase

    grouping_type = None
    grouping_factory = None

    def label(self, styled: bool=False) -> str:
        return _(self.grouping_factory.type_label_plural).capitalize()

    def icon(self) -> Optional[str]:
        return 'select-' + self.grouping_factory.type_name

    @classmethod
    def make_cls_pair(cls, grouping_type) -> TupleOf[type, type]:
        """Return the two classes for the group (tag, categories)
        filter, and its filter group counterpart."""

        factory = datastore.FontGroup.get_type(grouping_type)
        grouping_type = factory.type_name

        @register(factory.type_name)
        class inner_subcls(cls.child_cls):

            grouping_type = factory.type_name
            grouping_factory = factory

        inner_subcls.__name__ = factory.__name__ + 'Filter'

        @register(factory.type_name_plural)
        class outer_subcls(cls):

            grouping_type = factory.type_name
            grouping_factory = factory
            child_cls = inner_subcls

        outer_subcls.__name__ = factory.__name__.replace(
                        factory.type_name.capitalize(),
                        factory.type_name_plural.capitalize()) + 'FilterGroup'

        return inner_subcls, outer_subcls


FontTagFilter, FontTagsFilterGroup = \
    FontGroupsFilterGroupBase.make_cls_pair(datastore.FontTag)
FontCategoryFilter, FontCategoriesFilterGroup = \
    FontGroupsFilterGroupBase.make_cls_pair(datastore.FontCategory)


@register('genericfamily')
@register_cmdline('--generic-family', '--genericfamily', '--genfam', '-G')
class GenericFamilyFilter(FontFilter):

    """Filter that accepts only fonts from a given generic family, like
    'serif'"""

    remove_on_none = True
    # '' is unclassified
    remove_on_empty = False

    def __init__(self, value: str):
        self.value = value

    @property
    def prio(self) -> int:
        return PRIO_MAJOR_CUTOFF

    def label(self, styled: bool=False) -> str:
        return _(self.value or N_('unclassified')).capitalize()

    def icon(self) -> Optional[str]:
        return self.value

    def accept(self, item: fontlist.FontLike) -> bool:
        value = self.value
        return any(style.genericfamily == value for style in item.styles)

    def _identity(self) -> object:
        return ('genericfamily', self.value)


@register('genericfamilies')
@register_cmdline('--generic-families', '--generic-families', '--genfams')
class GenericFamiliesFilterGroup(PropertyValueSetFilterGroupBase):
    """Generic family font filter group, accepting fonts with one of the
    generic families.

    This filter supports value_set().
    """

    property_name = 'genericfamily'
    child_cls = GenericFamilyFilter

    def label(self, styled: bool=False) -> str:
        return _("Generic families")

    def icon(self) -> Optional[str]:
        return None


@register('panosefamily')
@register_cmdline('--panose-family', '--panosefamily', '--panfam')
class PanoseFamilyFilter(FontFilter):
    """Filter that accepts only fonts from a given PANOSE family, like
    opentype.PANOSE_TEXT"""

    remove_on_none = True
    value_attrname = 'family'

    def __init__(self, family: int):
        self.family = family
        self.panose_property = opentype.get_panose_property(family, 0, family,
                                                            cache=False)

    @property
    def prio(self) -> int:
        return PRIO_MAJOR_CUTOFF

    def label(self, styled: bool=False) -> str:
        return self.panose_property.text(_)

    def icon(self) -> Optional[str]:
        return None

    def accept(self, item: fontlist.FontLike) -> bool:
        family = self.family

        return any(style.panoseclass.family.value == family
                   for style in item.styles)

    def _identity(self) -> object:
        return ('panoseclass.family.value', self.family)


@register('panosefamilies', restore_order=1)
@register_cmdline('--panose-families', '--panosefamilies', '--panfams')
class PanoseFamilyFilterGroup(PropertyValueSetFilterGroupBase):
    """PANOSE family font filter group, accepting fonts with one of the
    PANOSE families.

    This filter supports value_set().
    """

    property_name = 'panoseclass.family.value'
    child_cls = PanoseFamilyFilter

    def label(self, styled: bool=False) -> str:
        return _("PANOSE family")

    def icon(self) -> Optional[str]:
        return None


class _CallableFamilyMixin(object):

    """This mixin allows the family attribute of a class to be a custom
    callable, allowing one to connect the PANOSE family filter to the rest
    of the PANOSE filters with a callable, which always carries the correct
    PANOSE family."""

    @property
    def family(self) -> int:
        result = self._family
        if callable(result):
            result = result()
        return result

    def todict(self) -> dict:
        self.ensure_family_not_callable()
        return super().todict()

    def ensure_family_not_callable(self):
        if callable(self._family):
            # In this case, we will be restored from the parent, no need
            # to save those.
            raise TypeError("Callable family found, should be serialized "
                            "from parent instead")


LazyFamilyType = MaybeLazy[int]


@register('panose-property-value', restore_order=2)
class PanosePropertyValueFilter(FontFilter, _CallableFamilyMixin):
    """Filter that accepts only fonts which have a given value for a given
    PANOE property"""

    remove_on_none = True
    key_attrname = 'pos'

    def __init__(self, value,
                       pos: int=opentype.PANOSE_FAMILY,
                       family: LazyFamilyType=opentype.PANOSE_UNCLASSIFIED):
        if pos == opentype.PANOSE_FAMILY:
            family = value

        self.value = value
        self.pos = pos
        self._family = family

    def factory_arguments(self) -> TupleOf[tuple, Mapping]:
        return (self.value, ), dict(pos=self.pos, family=self.family)

    @property
    def panose_property(self):
        return opentype.get_panose_property(self.family, self.pos,
                                            self.value, cache=False)

    @property
    def prio(self) -> int:
        return PRIO_MAJOR_CUTOFF

    def label(self, styled: bool=False) -> str:
        return self.panose_property.text(_)

    def icon(self) -> Optional[str]:
        if self.pos == opentype.PANOSE_SUBFAMILY:
            icons = opentype.PANOSE_CLASS_ICONS.get(self.family)
            if icons is None:
                return None
            return icons.get(self.value)
        return None

    def accept(self, item: fontlist.FontLike) -> bool:
        value = self.value
        pos = self.pos

        return any(style.panoseclass[pos].value == value
                   for style in item.styles)

    def _identity(self) -> object:
        return ('panoseclass', self.pos, self.value)


@register('panose-properties', restore_order=2)
class PanosePropertiesFilter(FilterConjunctiveGroup, FontFilter,
                             _CallableFamilyMixin):
    """PANOSE property filter group, accepting fonts with the given
    configuration of PANOSE property values languages in the children
    filters."""

    child_cls = PanosePropertyValueFilter

    def __init__(self, *args,
                       family: LazyFamilyType=opentype.PANOSE_UNCLASSIFIED,
                       **kwargs):
        super().__init__(*args, **kwargs)
        self._family = family

    def child_factory(self, pos: int, value: int) -> PanosePropertyValueFilter:
        return PanosePropertyValueFilter(value, pos=pos,
                                         family=self._family)

    def label(self, styled: bool=False) -> str:
        return _("PANOSE properties")

    def icon(self) -> Optional[str]:
        return None


@register('panose-property-values', restore_order=2)
class PanosePropertyFilterGroup(PropertyValueSetFilterGroupBase,
                                _CallableFamilyMixin):

    """PANOSE property filter group for a fixed PANOSE property,
    accepting fonts with one of the values for that property.

    This filter supports value_set().
    """

    child_cls = PanosePropertyValueFilter
    supports_value_set = True
    supports_value_mapping = False

    def __init__(self, pos: int=opentype.PANOSE_FAMILY,
                       family: LazyFamilyType=opentype.PANOSE_UNCLASSIFIED,
                       *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.pos = pos
        self._family = family

    def child_factory(self, value: int) -> PanosePropertyValueFilter:
        return PanosePropertyValueFilter(value, pos=self.pos,
                                         family=self._family)

    @property
    def field(self) -> str:
        return opentype.get_panose_fields(self.family)[self.pos].fieldname

    @property
    def property_name(self) -> str:
        return 'panoseclass[%d]' % (self.pos, )

    def get_item_value(self, item: fontlist.FontLike) -> int:
        panoseclass = item.panoseclass
        if not panoseclass or panoseclass.family.value != self.family:
            return None

        return panoseclass[self.pos].value

    def label(self, styled: bool=False) -> str:
        return _(self.field)

    def icon(self) -> Optional[str]:
        return None


@register('panose-subfamilies', restore_order=2)
class PanoseSubfamilyFilterGroup(PanosePropertyFilterGroup):

    """PANOSE property filter group for the second PANOSE property,
    which provides different PANOSE 'subfamilies' - serif, tool, class, kind,
    etc. for each PANOSE  family.

    accepting fonts with one of the values for that property.

    This filter supports value_set().
    """

    def __init__(self, family: LazyFamilyType=opentype.PANOSE_UNCLASSIFIED,
                       *args, **kwargs):
        super().__init__(pos=opentype.PANOSE_SUBFAMILY,
                         family=family, *args, **kwargs)


@register('ibmclass')
@register_cmdline('--ibm-class', '--ibmclass', '--ibmcls')
class IbmClassFilter(FontFilter):

    """Filter that accepts only fonts from a given IBM class, like
    opentype.IBM_OLDSTYLE_SERIF"""

    remove_on_none = True

    def __init__(self, value: int):
        self.value = value

    @property
    def prio(self) -> int:
        return PRIO_MAJOR_CUTOFF

    def label(self, styled: bool=False) -> str:
        return _(opentype.IBM_CLASSES.get(self.value)) or \
               (_("IBM class") + ' ' + hex(self.value))

    def icon(self) -> Optional[str]:
        return None

    def annotation(self) -> annotations.Annotation:
        return None

    def accept(self, item: fontlist.FontLike) -> bool:
        value = self.value
        return any(style.ibmclass.class_id == value
                   for style in item.styles)

    def _identity(self) -> object:
        return ('ibmclass', self.value)


@register('ibmclasses')
@register_cmdline('--ibm-classes', '--ibmclasses')
class IbmClassesFilterGroup(PropertyValueSetFilterGroupBase):
    """IBM class family font filter group, accepting fonts with one of the
    IBM classes.

    This filter supports value_set().
    """
    property_name = 'ibmclass.class_id'
    child_cls = IbmClassFilter

    def label(self, styled: bool=False) -> str:
        return _("IBM class")

    def icon(self) -> Optional[str]:
        return None


@register('ibmsubclass', restore_order=1)
@register_cmdline('--ibm-subclass', '--ibmsubclass', '--ibmsub')
class IbmSubclassFilter(FontFilter):

    """Filter that accepts only fonts from a given IBM subclass, like
    opentype.IBM_OLDSTYLE_VENETIAN"""

    remove_on_none = True

    def __init__(self, value):
        self.value = value

    @property
    def prio(self) -> int:
        return PRIO_MAJOR_CUTOFF

    def label(self, styled: bool=False) -> str:
        return opentype.IBM_SUBCLASSES.get(self.value) or \
               (_("IBM subclass") + ' ' + hex(self.value))

    def icon(self) -> Optional[str]:
        return None

    def annotation(self) -> annotations.Annotation:
        return None

    def accept(self, item: fontlist.FontLike) -> bool:
        value = self.value
        return any(style.ibmclass.subclass_id == value
                   for style in item.styles)

    def _identity(self) -> object:
        return ('ibmsubclass', self.value)


@register('ibmsubclasses', restore_order=1)
@register_cmdline('--ibm-subclasses', '--ibmsubclasses')
class IbmSubclassesFilterGroup(PropertyValueSetFilterGroupBase):
    """IBM subclass family font filter group, accepting fonts with one of the
    IBM subclasses.

    This filter supports value_set().
    """

    property_name = 'ibmclass.subclass_id'
    child_cls = IbmSubclassFilter

    def label(self, styled: bool=False) -> str:
        return _("IBM subclass")

    def icon(self) -> Optional[str]:
        return None


#################
# Filter access #
#################


class FilterCollectionBase(Collection):

    """A base class for editable collection views of filter groups.

    Attributes are forwarded to the font group itself."""

    def __init__(self, filter_group: FilterGroup):
        self._filters = {}
        self.group = filter_group
        filter_group.child_removed.connect(self._filter_removed)
        filter_group.child_added.connect(self._filter_added)
        for filter in filter_group.filters:
            self._filter_added(filter)

    def __getattr__(self, attr):
        return getattr(self.group, attr)

    @abc.abstractmethod
    def filter_key(self, filter: Filter) -> str:
        """Get the key for a filter.

        This can use the canonical key of the filter for filter mappings
        or sequences, or the key-value key for value mappings, depending
        on the purpose of the view.
        """
        raise NotImplementedError

    def filter_conflict(self, old_filter: Filter, new_filter: Filter):
        """Called when a filter is added, but it already exists"""
        pass

    def _filter_removed(self, filter: Filter):
        key = self.filter_key(filter)
        if key in self._filters:
            del self._filters[key]

    def _filter_added(self, filter: Filter):
        key = self.filter_key(filter)
        if key in self._filters:
            self.filter_conflict(self._filters[key], filter)
        self._filters[key] = filter

    def __len__(self):
        return len(self._filters)

    def __iter__(self):
        return iter(self._filters)


class FilterMappingBase(FilterCollectionBase, Mapping):

    """A base class for editable mapping views of filter groups.

    Attributes are forwarded to the font group itself."""

    @abc.abstractmethod
    def filter_value(self, filter: Filter) -> object:
        """Get the value of a filter.

        This can be the filter itself for filter mappings or sequences,
        or the key-value value for value mappings, depending on the purpose
        of the view.
        """
        raise NotImplementedError

    def __contains__(self, key):
        return key in self._filters

    def __getitem__(self, key):
        return self.filter_value(self._filters[key])

    def __repr__(self):
        return '<%s 0x%x: %r>' % (type(self).__name__,
                                  id(self), self._filters)


class FilterSetBase(FilterCollectionBase, Set):

    """A base class for editable set views of filter groups.

    Attributes are forwarded to the font group itself."""

    def __contains__(self, key):
        return key in self._filters

    def __repr__(self):
        return '<%s 0x%x: %r>' % (type(self).__name__,
                                  id(self), set(self._filters))


class FilterMapping(FilterMappingBase, MutableMapping):

    """A mapping view of a filter group accessing filter instances
    by the default / canonical key. The view is editable, and manipulates
    the font group. Create one with font_group.filter_mapping().

    Attributes are forwarded to the font group itself."""

    def filter_key(self, filter: Filter) -> str:
        """The filter's get_key() result."""
        return filter.get_key()

    def filter_value(self, filter: Filter) -> Filter:
        """The filter itself."""
        return filter

    def standard_filter(self, key: str, *args, **kwargs) -> Optional[Filter]:
        """Get the standard filter of a given type, or None. It is
        added to the filters if need be, or changed, then it is
        returned.

        Works the same as make_standard_filter(), but can also use dotted
        syntax to create filters inside children of this filter.
        """

        would_make = None

        if '.' in key:
            path = key.split('.')
            groupmap = self
            for i, subkey in enumerate(path):
                # Do not create any nodes if we're not going to create the
                # final node.
                if subkey not in groupmap:
                    if would_make is None:
                        would_make = bool(would_make_standard_filter(
                                            path[-1], *args, **kwargs))
                    if not would_make:
                        return None

                if i == len(path) - 1:
                    return groupmap.standard_filter(subkey, *args, **kwargs)

                subfilter = groupmap.standard_filter(subkey)
                groupmap = subfilter.filter_mapping()

            return subfilter

        old_filter = self.get(key)
        if old_filter is None:
            new_filter = make_standard_filter(key, *args, **kwargs)
        else:
            # FIXME: This should be handled by change() azjaidyhd7b
            if _default_kwargs.get(key):
                kwargs = dict(_default_kwargs[key],
                              empty_kwargs=not kwargs,
                              **kwargs)
            new_filter = old_filter.change(*args, **kwargs)

        if new_filter is not old_filter:
            if new_filter is None:
                self.pop(key, None)
            else:
                self[key] = new_filter

        return new_filter

    @classmethod
    def standard_property(cls, key: str, *args,
                               filter_attr: str=None, **kwargs) -> property:
        """Return a property for reading or setting a standard filter.

        The key can contain dotted path to an inner descendant.
        """

        filter_cls = _default_keys[key.rpartition('.')[2]]
        if not filter_cls.is_group or filter_attr is not None:
            return cls.standard_scalar_property(key, *args, **kwargs)
        elif filter_cls.supports_value_mapping:
            return cls.standard_mapping_property(key, *args, **kwargs)
        elif filter_cls.supports_value_set:
            return cls.standard_set_property(key, *args, **kwargs)
        else:
            return cls.standard_scalar_property(key, *args, **kwargs)

    @classmethod
    def standard_scalar_property(cls, key: str, value_attr: str=None, *args,
                                      readonly: bool=False,
                                      filters_attr: str='filters',
                                      **kwargs) -> property:
        """Return a property for reading or setting a standard filter
        that matches a single scalar value, that is, not a group of
        filters"""

        @property
        def property_instance(self):
            filter = getattr(self, filters_attr).standard_filter(key)
            if filter is None:
                return None
            if value_attr is not None:
                return getattr(filter, value_attr)
            return getattr(filter, filter.value_attrname)

        if readonly:
            if args or kwargs:
                raise TypeError("No more attributes in readonly mode: %r, %r"
                                    % (args, kwargs))
        else:
            @property_instance.setter
            def property_instance(self, value):
                if value_attr is not None:
                    filter = getattr(self, filters_attr).standard_filter(key)
                    if getattr(filter, value_attr) != value:
                        setattr(filter, value_attr, value)
                        filter.emit_change_signal()
                    return
                getattr(self, filters_attr).standard_filter(key, value,
                                                            *args, **kwargs)

        return property_instance

    @classmethod
    def standard_mapping_property(cls, *args, **kwargs) -> property:
        """Return a property for reading or setting a standard filter
        that matches a single scalar value, that is, not a group of
        filters"""

        return cls._standard_values_property(*args, mapping_property=True,
                                              **kwargs)

    @classmethod
    def standard_set_property(cls, *args, **kwargs) -> property:
        """Return a property for reading or setting a standard filter
        that matches a single scalar value, that is, not a group of
        filters"""

        return cls._standard_values_property(*args, mapping_property=False,
                                              **kwargs)

    @classmethod
    def _standard_values_property(cls, key: str, *args,
                                       readonly: bool=False,
                                       filters_attr: str='filters',
                                       mapping_property: bool=True,
                                       method_kwargs: Mapping=None,
                                       keep_none_when_getting: bool=True,
                                       **kwargs) -> property:
        """The implementation of standard_mapping_property and
        standard_set_property"""

        if mapping_property:
            method = 'value_mapping'
        else:
            method = 'value_set'

        def make_filter(self, filter_mapping, setting=False):
            if (key not in filter_mapping and
                keep_none_when_getting and not setting):
                    return None

            kwnew = kwargs
            if method_kwargs:
                kwnew = dict(kwnew)
                kwnew.update((k, method(self))
                             for k, method in method_kwargs.items())

            return filter_mapping.standard_filter(key, *args, **kwnew)

        @property
        def property_instance(self):
            filter_mapping = getattr(self, filters_attr)

            filter = filter_mapping.get(key)
            if filter is None:
                filter = make_filter(self, filter_mapping)
                if filter is None:
                    return None
            return getattr(filter, method)()

        if readonly:
            if args or kwargs:
                raise TypeError("No more attributes in readonly mode: %r, %r"
                                    % (args, kwargs))
        else:
            @property_instance.setter
            def property_instance(self, new_values):

                filter_mapping = getattr(self, filters_attr)

                if new_values is None:
                    filter_mapping.pop(key, None)
                    return

                filter = filter_mapping.get(key)
                if filter is None:
                    filter = make_filter(self, filter_mapping, setting=True)
                    if filter is None:
                        raise AttributeError("Filter %r doesn't exist"
                                                    % (key, ))

                filter_values = getattr(filter, method)()
                if filter_values == new_values:
                    return
                if mapping_property:
                    for k in list(filter_values):
                        if k not in new_values:
                            del filter_values[k]

                    filter_values.update(new_values)

                else:
                    filter_values &= new_values
                    filter_values |= new_values

        return property_instance

    def __setitem__(self, key, value):
        value.key = key

        if key in self._filters:
            if value is self._filters[key]:
                return
            self.group.replace(self._filters[key], value)
        else:
            self.group.add(value)

    def __delitem__(self, key):
        self.group.remove(self._filters[key])
        # This is called by the signal, but ensure we clean up
        self._filters.pop(key, None)


standard_property = FilterMapping.standard_property

class FilterValueMapping(FilterMappingBase, MutableMapping):

    """A mapping view of a filter group accessing filter key-value
    pairs provided by the children filters. This is a simplified version of
    the filter group which only contains scalar keys-value pairs (which
    are distinct from the default/canonical key, although in most cases
    the two should match).

    It can also be constructed from custom key / value attributes of the
    filters in the group.

    The view is editable, and manipulates the font group.
    Create one with font_group.value_mapping().

    Attributes are forwarded to the font group itself."""

    def __init__(self, filter_group: FilterGroup,
                       factory: Callable=None,
                       key_attr: str=None, value_attr: str=None, *a, **kw):
        super().__init__(filter_group, *a, **kw)
        if factory is None:
            factory = filter_group.child_factory
        self.factory = factory
        self.key_attr = key_attr
        self.value_attr = value_attr

    def filter_key(self, filter: Filter) -> object:
        """The scalar key found in the key_attrname of the filter, or
        a custom attribute specified by the code requesting this mapping.
        This is distinct from filter.get_key(), but in most cases the two
        should be equal. See the documentation there on the distinction.
        """
        attr = self.key_attr
        if attr is None:
            attr = filter.key_attrname
        return getattr(filter, attr)

    def filter_value(self, filter: Filter) -> object:
        """The value  key found in the value_attrname of the filter, or
        a custom attribute specified by the code requesting this mapping."""
        attr = self.value_attr
        if attr is None:
            attr = filter.value_attrname
        return getattr(filter, attr)

    def __setitem__(self, key, value):
        if key in self._filters:
            if self.filter_value(self._filters[key]) == value:
                return
            filter = self.factory(key, value)
            self.group.replace(self._filters[key], filter)
        else:
            filter = self.factory(key, value)
            self.group.add(filter)

    def __delitem__(self, key):
        self.group.remove(self._filters[key])
        # This is called by the signal, but ensure we clean up
        self._filters.pop(key, None)


class FilterValueSet(FilterSetBase, MutableSet):

    """A mapping set of a filter group accessing filter values
    provided by the children filters. This is a simplified version of the
    filter group which only contains scalar values.

    It can also be constructed from a custom key attribute of the
    filters in the group.

    The view is editable, and manipulates the font group.
    Create one with font_group.value_set().

    Attributes are forwarded to the font group itself."""

    def __init__(self, filter_group: FilterGroup,
                       factory: Callable=None,
                       key_attr: str=None, *a, **kw):
        super().__init__(filter_group, *a, **kw)
        if factory is None:
            factory = filter_group.child_factory
        self.factory = factory
        self.key_attr = key_attr

    def filter_key(self, filter: Filter) -> object:
        """The value  key found in the value_attrname of the filter, or
        a custom attribute specified by the code requesting this mapping.

        This is because a set is constructed from the values, and we use
        the keys to populate the dictionary backing the set."""
        attr = self.key_attr
        if attr is None:
            attr = filter.value_attrname
        return getattr(filter, attr)

    def add(self, key):
        if key not in self._filters:
            filter = self.factory(key)
            self.group.add(filter)

    def discard(self, key):
        if key in self._filters:
            self.group.remove(self._filters[key])
        # This is called by the signal, but ensure we clean up
        self._filters.pop(key, None)

    @classmethod
    def _from_iterable(cls, it):
        return set(it)


class FilterSequence(Sequence):

    """A sequence view of a filter group. The view is NOT editable.
    Create one with font_group.filter_sequence().

    The group is partially noisy. It does not have value_changed signals, because
    the values are never changed.

    Attributes are forwarded to the font group itself."""

    def _insert_sig(self, index: int, value: object): pass

    remove_pending = Signal(int, object,
                            name='remove_pending', signature_func=_insert_sig,
                            doc="An index with a given value is about to be "
                                "removed")
    insert_pending = Signal(int, object,
                            name='insert_pending', signature_func=_insert_sig,
                            doc="At a given index a given value is about to be "
                                "inserted")

    removed = Signal(int, object,
                     name='removed', signature_func=_insert_sig,
                     doc="An index with a given value was removed")
    inserted = Signal(int, object,
                      name='inserted', signature_func=_insert_sig,
                      doc="At a given index a given value was inserted")

    del _insert_sig

    def __init__(self, filter_group, *, key=None, reverse=False):
        self.group = filter_group

        self._filters = []

        self._sortkey = key
        self._reverse = reverse

        self._filter_order = [] if key is not None else None

        filter_group.child_removed.connect(self._filter_removed)
        filter_group.child_added.connect(self._filter_added)
        for filter in filter_group.filters:
            self._filter_added(filter)

    def __repr__(self):
        return '<%s 0x%x: %r>' % (type(self).__name__,
                                  id(self), self._filters)

    def __getattr__(self, attr):
        return getattr(self.group, attr)

    def _filter_removed(self, filter: Filter):
        index = self._filters.index(filter)
        self.remove_pending(index, filter)
        del self._filters[index]
        if self._filter_order is not None:
            if self._reverse:
                del self._filter_order[len(self._filter_order) - index - 1]
            else:
                del self._filter_order[index]
        self.removed(index, filter)

    def _filter_added(self, filter: Filter):
        if self._filter_order is not None:
            key = self._sortkey(filter)
            if self._reverse:
                index = bisect.bisect_right(self._filter_order, key)
                self._filter_order.insert(index, filter)

                # FIXME FIXME FIXME: This was incorrectly in the else,
                # which is obviously wrong, but I wasn't feeling well when
                # I fixed it, so the logic needs review. The lack of
                # key= and reverse= for bisect is making everything
                # *VERY HARD*

                # Note that the length will be len() + 1 after the insertion,
                # so for indexes to be reversed. If you do the math above, you
                # wouldn't subtract 1
                index = len(self._filter_order) - index - 1

            else:
                index = bisect.bisect_left(self._filter_order, key)
                self._filter_order.insert(index, filter)

        else:
            index = len(self._filters)

        self.insert_pending(index, filter)
        self._filters.insert(index, filter)
        self.inserted(index, filter)

    def __len__(self):
        return len(self._filters)

    def __getitem__(self, item):
        return self._filters[item]

    def __iter__(self):
        return iter(self._filters)


##################
# Widget support #
##################


ITEM_TYPE_NONE = 1 << 0
ITEM_TYPE_BOOLEAN = 1 << 1
ITEM_FLAG_TRISTATE = 1 << 16

ITEM_TYPE_TRISTATE = ITEM_TYPE_BOOLEAN | ITEM_FLAG_TRISTATE


_item_factories = {}
_item_types = {}


def register_items(default_key: str,
                   type: int=ITEM_TYPE_BOOLEAN):

    """Return a decorator registering a given class of available items
    for a given filter group key. This for example provides you
    the available languages or tags for the languages and tags filter
    groups.

    They can be differentiated by type:
        - ITEM_TYPE_TRISTATE: Can be required (True), forbidden (False),
                              or not filtered by.
        - ITEM_TYPE_BOOLEAN: Presently unsed, but only has two states.
        - ITEM_TYPE_NONE: Cannot be searched by. Registered for other
                          purposes (simple display).
    """

    def decorator(cls):
        _item_factories[default_key] = cls
        _item_types[default_key] = type
        cls.default_key = default_key
        return cls

    return decorator


class Item(object):

    """A displayable item, e.g. representing an optional filter.

    This for example can be a tag, category, language. It can also be
    used by things one cannot filter by, such as search or interface arrangement.

    This class provides the necessary decorations over e.g. the set of
    available categories to display checkboxes in a list for their selection.

    Except for custom non-filtering uses, the items are registered for a given
    filter group type, and the NoisyGroupItemConnector provides the items
    and their values for a given filter group, allowing to have information
    and updates about both the current filter selection, and the list of available
    filters in that group that have not yet been added to it.
    """

    default_key = None

    def __init__(self, key: Hashable):
        self.key = key

    def label(self, styled: bool=False) -> str:
        """The label of the item. Styling is the same as for filters."""
        annotation = self.annotation
        if annotation is not None:
            return str(self.key)
        return annotation.get_name(translate=_)

    def search_text(self) -> str:
        """The search text of the item."""
        return self.label(styled=True)

    def annotation(self) -> annotations.Annotation:
        """The annotation of the item."""
        return None

    def description(self, styled: bool=False) -> Optional[str]:
        """The description of the item."""
        return None

    def status_text(self, styled: bool=False) -> Optional[str]:
        result = self.label(styled=styled)
        if len(result) > 1:
            if result[0].isupper() and result[1].islower():
                result = result[0].lower() + result[1:]

    def style(self) -> Set:
        """The style of the item."""
        return frozenset()

    def icon(self) -> Optional[str]:
        """The icon of the item."""
        annotation = self.annotation
        if annotation is None:
            return None
        return annotation.icon

    @classmethod
    def items(cls, feature_sets: fontlist.FeatureSets) -> 'IterableOf[Item]':
        """Return the items for the given feature sets."""
        if False:
            yield

    @classmethod
    def postupdate(cls, feature_sets: fontlist.FeatureSets,
                        item_values: 'ItemValues',
                        key: str, value: object=None,
                                  old_value: object=None):
        """This is called every time the item selection has changed, allowing
        the class to modify the list of available items accordingly."""
        pass

    def __repr__(self):
        return '%s(%r, <...>)' % (type(self).__name__, self.key)


@register_items('languages', ITEM_TYPE_TRISTATE)
class LanguageItem(Item):

    """A language item available for selection and filtering by."""

    def label(self, styled: bool=False) -> str:
        return LanguageDatabase.get_instance().language_name(self.key)

    def search_text(self) -> str:
        langdb = LanguageDatabase.get_instance()
        shown = langdb.language_name(self.key)
        native = langdb.language_name(self.key, NATIVE_NAME)
        english = langdb.language_name(self.key, ENGLISH_NAME)

        result = shown
        if native and native != shown:
            result += ' ' + native
        if native and english != shown and english != native:
            result += ' ' + english

        return result

    def icon(self) -> Optional[str]:
        langdb = LanguageDatabase.get_instance()
        countryflag = langdb.guess_country_flag(self.key)
        if countryflag:
            return 'flags/' + countryflag
        return None

    @classmethod
    def items(cls, feature_sets: fontlist.FeatureSets) -> 'IterableOf[LanguageItem]':
        langdb = LanguageDatabase.get_instance()
        for lang in langdb.sort_languages(feature_sets.languages):
            yield cls(lang)

    @classmethod
    def postupdate(cls, feature_sets: fontlist.FeatureSets,
                        item_values: 'ItemValues',
                        key: str, value: object=None,
                                  old_value: object=None):

        lang = key

        appears_with = feature_sets.lang_appears_with
        appears_without = feature_sets.lang_appears_without
        absent_together = feature_sets.lang_absent_together_with

        values = item_values.values
        fixed = item_values.fixed

        # Check if this is an allowed value, and discard it if it is not.
        if value is not None:
            # FIXME: Not sure that all those cases are correct if both are False
            acceptable = True

            if value:
                # If we have been selected, we must appear *WITHOUT* other deselected
                # languages
                if not all(appears_with(lang, selected_lang) if selected_val else
                           appears_without(lang, selected_lang)
                                for selected_lang, selected_val in values.items()
                                if selected_lang != lang):
                    acceptable = False

            else:
                # If we have been deselected, other selected languages must appears
                # *WITHOUT* us
                if not all(appears_without(selected_lang, lang) if selected_val else
                           absent_together(selected_lang, lang)
                                for selected_lang, selected_val in values.items()
                                if selected_lang != lang):
                    acceptable = False

            if not acceptable:

                remaining_vals = {True, False, None}
                remaining_vals.discard(value)
                remaining_vals.discard(old_value)

                values[lang] = remaining_vals.pop()
                return

        # If any other languages are fixed by our selection, fix them
        for item in item_values.items:
            other = item.key

            if other in values or other == lang:
                continue

            # FIXME: This bugs out with Bulgarian and Russian?
            if not all(appears_with(other, selected_lang) if selected_val else
                       appears_without(other, selected_lang)
                            for selected_lang, selected_val in values.items()):
                fixed[other] = False

            elif not all(appears_without(selected_lang, other) if selected_val else
                         absent_together(selected_lang, other)
                            for selected_lang, selected_val in values.items()):
                fixed[other] = True

            elif other in fixed:
                del fixed[other]


class GroupItems(NoisySequence):

    """A noisy sequence of group (category, tag) items that are
    automatically added and removed as user creates them. That allows
    views for selecting fonts by tags to automatically have the tags
    removed and added.

    Use TagItem.items() to create, or better yet the NoisyGroupItemConnector.

    This special class is necessary only because the list of available
    tags and categories can be edited, whereas the list of languages
    cannot, so TagItem.items() needs to return a NoisySequence for
    NoisyGroupItemConnector (for languages, it uses a static list).
    """

    def __init__(self, container: datastore.FontGroupsContainer,
                       item_factory: Callable):
        super().__init__()
        self.container = container
        self.item_factory = item_factory
        self._item_order = []

        info = container.info

        info.added.connect(self._added)
        info.deleted.connect(self._deleted)
        info.value_changed.connect(self._value_changed)

        container.added.connect(self._group_member_changed)
        container.removed.connect(self._group_member_changed)

        for key, value in sorted(info.items()):
            #self._added(key, value)
            self.append(self.item_factory(key, value, self.container))
            self._item_order.append(key)

    def _added(self, key, value):
        #self.append(self.item_factory(key, value, self.container))
        index = bisect.bisect_right(self._item_order, key)
        self.insert(index, self.item_factory(key, value, self.container))
        self._item_order.insert(index, key)

    def _deleted(self, key, value):
        index = bisect.bisect_left(self._item_order, key)
        if index < len(self) and self[index].key == key:
            del self[index]
            return

        warnmsgf("BUG: GroupItems was not properly sorted or populated? "
                 "Missing in its place: %r %r", key, value)
        for i, item in enumerate(self):
            if item.key == key:
                del self[i]
                return

    def _value_changed(self, key, value):
        index = bisect.bisect_left(self._item_order, key)
        if index < len(self) and self[index].key == key:
            self[index] = self.item_factory(key, value, self.container)
            return

        warnmsgf("BUG: GroupItems was not properly sorted or populated? "
                 "Missing in its place: %r %r", key, value)
        for i, item in enumerate(self):
            if item.key == key:
                self[i] = self.item_factory(key, value, self.container)
                return

    def _group_member_changed(self, family, group_name):
        index = bisect.bisect_left(self._item_order, group_name)
        if index < len(self) and self[index].key == group_name:
            self[index] = self[index]
            return

        warnmsgf("BUG: GroupItems was not properly sorted or populated? "
                 "Missing in its place: %r", group_name)
        for i, item in enumerate(self):
            if item.key == group_name:
                self[i] = self[i]
                return


class GroupItemBase(Item):
    """Base class for group items (tags, categories) that could be
    made available available for selection and filtering by.

    The grouping_type attribute is a string giving the type,
    and the grouping_factory is the datastore class used to represent
    this group.

    The signature of this class varies, do not create directly, use
    cls.items(), or better yet the NoisyGroupItemConnector.
    """

    grouping_type = None
    grouping_factory = None

    def __init__(self, key: str, group_info: datastore.FontGroup,
                       container: datastore.FontGroupsContainer=None,
                       *args, **kwargs):

        super().__init__(key, *args, **kwargs)
        self.group_info = group_info
        self.container = container

    def icon(self) -> Optional[str]:
        return self.group_info.icon

    def color(self) -> Optional[str]:
        return self.group_info.color

    @classmethod
    def items(cls, feature_sets: fontlist.FeatureSets) -> 'IterableOf[GroupItemBase]':
        # FIXME: Global variable in use here.
        categorization = datastore.Categorization.get_instance()
        container = categorization.container(cls.grouping_type)

        return GroupItems(container, cls)


@register_items('tags', ITEM_TYPE_TRISTATE)
class TagItem(GroupItemBase):
    """A tag item available for selection and filtering by."""

    grouping_type = 'tag'
    grouping_factory = datastore.FontTag

    def label(self, styled: bool=False) -> str:
        return '%s (%d)' % (self.key, len(self.group_info.families))


@register_items('categories', ITEM_TYPE_TRISTATE)
class CategoryItem(GroupItemBase):
    """A category item available for selection and filtering by."""

    grouping_type = 'category'
    grouping_factory = datastore.FontCategory

    def label(self, styled: bool=False) -> str:
        return '%s (%d)' % (self.key, len(self.group_info.families))


@register_items('searches', ITEM_TYPE_NONE)
class SearchItem(GroupItemBase):
    """A searches item available. You cannot search by search, but
    one may still want to display all saved searches in the GUI.
    The ITEM_TYPE_NONE signifies that no values (checkbox or otherwise)
    can be assigned to the searches."""

    grouping_type = 'search'
    grouping_factory = datastore.FontSearch


class ItemValues(object):

    """A pair of items and a mapping with their values, either of them
    noisy.

    This can be, for example, the available languages, and the currently
    selected languages (same as FontLanguagesFilterGroup.value_mapping()),
    except the latter view remains connected to the 'languages' filter
    even if it is deleted and recreated.

    The mapping key is in item.key.
    """

    factory = None

    def __init__(self, items: IterableOf[Item],
                       type: int=ITEM_TYPE_BOOLEAN,
                       values: Iterable=(),
                       fixed: Iterable=()):
        if not isnoisy(items):
            items = NoisySequence(items)
        if not isnoisy(values):
            values = NoisyMapping(values)
        if not isnoisy(fixed):
            fixed = NoisyMapping(fixed)

        self.items = items
        self.values = values
        self.fixed = fixed

        self.type = type


class NoisyGroupItemConnector(object):

    """A connector that listens for changes in a fitler tree, and
    allows you to connect to the items in a specific part of the subtree.

    You can connect to a font group within the filter tree, getting
    list of available filters (all languages), list of active filters
    and their values ('en': False), and display them in a dialog box
    that gets updated as they are updated.

    The connection remains even if the filter group is deleted and
    created again, since the connector listens for changes at the
    root of the tree."""

    def __init__(self, main_group: FilterGroup,
                       feature_sets: fontlist.FeatureSets):
        self.main_group = main_group
        self.feature_sets = feature_sets

        self._filter_mapping = main_group.filter_mapping()

        self._noisy_mapping = {}
        self._noisy_mapping_branches = defaultdict(list)

        self._item_values = {}

        main_group.branch_changed.connect(self._group_changed)

    def item_values(self, filterkey: str) -> ItemValues:
        """Get the connected ItemValues for a given filter key, which
        can contain a dotted syntax to a subfilter. You cannot connect to
        the root (self.main_group)."""

        if filterkey in self._item_values:
            return self._item_values[filterkey]

        factory = _item_factories[filterkey]

        result = ItemValues(factory.items(self.feature_sets),
                            _item_types[filterkey])
        if result.type != ITEM_TYPE_NONE:
            result.values = self.value_mapping(filterkey)
        result.factory = factory

        self._item_values[filterkey] = result

        return result

    def value_mapping(self, filterkey: str) -> NoisyMapping:
        """Return a value mapping for the given filter key that remains
        connected even if the filter group with the key is deleted."""

        tuple_key = tuple(filterkey.split('.'))

        if tuple_key not in self._noisy_mapping:
            filter = self._filter_mapping.standard_filter(filterkey, no_create=True)
            values = filter.value_mapping() if filter is not None else {}
            self._noisy_mapping[tuple_key] = noisymap = NoisyMapping(values)

            noisymap.__filterkey = filterkey
            noisymap.value_changed.connect(self._value_changed, pass_self=True)
            noisymap.added.connect(self._value_changed, pass_self=True)
            noisymap.deleted.connect(self._value_deleted, pass_self=True)

            for i in range(1, len(tuple_key) + 1):
                self._noisy_mapping_branches[tuple_key[:i]].append(noisymap)

        return self._noisy_mapping[tuple_key]

    def _value_changed(self, noisymap: NoisyMapping,
                             key: Hashable, value: object,
                             old_value: object=_NOTHING):
        """The returned value mapping was modified, update the filter group."""
        filterkey = noisymap.__filterkey

        filter = self._filter_mapping.standard_filter(filterkey)
        valuemap = filter.value_mapping()

        if key not in valuemap or valuemap[key] != value:
            valuemap[key] = value

        if value != old_value:
            item_values = self.item_values(filterkey)
            item_values.factory.postupdate(self.feature_sets, item_values,
                                          key, value, old_value)

    def _value_deleted(self, noisymap: NoisyMapping,
                             key: Hashable, value: object):
        """The returned value mapping was modified, update the filter group."""
        filterkey = noisymap.__filterkey

        filter = self._filter_mapping.standard_filter(filterkey)
        valuemap = filter.value_mapping()

        if key in valuemap:
            del valuemap[key]

        item_values = self.item_values(filterkey)
        item_values.factory.postupdate(self.feature_sets, item_values,
                                       key, old_value=value)

    def _group_changed(self, branch_change: BranchChange):
        """The filter group was modified, update the value mapping."""
        filterkey = branch_change.key_tuple()[1:]
        parentkey = filterkey[:-1]
        leaf = branch_change.leaf()

        if parentkey in self._noisy_mapping:
            filter = branch_change.leading_filter()
            key = getattr(filter, filter.key_attrname)
            if leaf.action == REMOVED:
                self._noisy_mapping[parentkey].pop(key, None)
            else:
                value = getattr(filter, filter.value_attrname)
                self._noisy_mapping[parentkey][key] = value

        if leaf.action in [REMOVED, REPLACED]:
            if filterkey in self._noisy_mapping_branches:
                for noisymap in self._noisy_mapping_branches[filterkey]:
                    noisymap.clear()

        if leaf.action in [ADDED, REPLACED]:
            if filterkey in self._noisy_mapping:
                filter = branch_change.leading_filter()
                self._noisy_mapping[filterkey].update(filter.value_mapping())
