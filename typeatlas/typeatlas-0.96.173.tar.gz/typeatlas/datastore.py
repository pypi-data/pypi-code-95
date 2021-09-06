# -*- coding: utf-8 -*-
#
#    TypeAtlas Data Store
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

"""Store of state and cache data for TypeAtlas."""

import typeatlas
from typeatlas.util import OrderedSet, Overwriter, warnmsgf, errmsgf, U_, N_
from typeatlas.util import generic_type
from typeatlas import proginfo, opentype, rangemath, event
from collections import namedtuple, Mapping, Callable
import time
import json
import os
import io
import sys
import errno
import traceback

Union = generic_type('Union')
Optional = generic_type('Optional')
IterableOf = generic_type('Iterable')

CACHE_FILL_MAXIMUM = 2.2
CACHE_FILL_GOAL = 1.8

# Two years
CACHE_EXPIRATION = 3600 * 24 * 366 * 2


_UNCHANGED = object()


class DataStore(object):

    """The base for JSON-based data stores.

    The following attributes are common:
        instance - the primary (singleton) instance
        location - the directory to save in (proginfo.DATA_DIR or proginfo.CACHE_DIR)
        basename - the name of the file to save in
        variables - supported variables that will be automatically serialized
                    (subclasses prefer to override the serialization)
        defaults - the variable defaults when reloading automatically
                    (subclasses prefer to override the deserialization)
        current_load_initiated - True if the current config was loaded, or didn't
                                 exist or failed to load. Save will be disabled if
                                 this did not occur.
        protect_previous - if True, the previous configuration is protected if it
                           was not loaded

    """

    instance = None
    variables = []
    defaults = {}
    location = proginfo.DATA_DIR
    basename = None

    current_load_initiated = False
    protect_previous = True

    def __init__(self, *args, protect_previous: bool=True, **kwargs):
        self.protect_previous = protect_previous
        super().__init__(*args, **kwargs)

    def get_default(self, variable: str):
        """Get the default for a variable when deserializing and it
        isn't found."""
        return self.defaults.get(variable)

    def loaddict(self, d: Mapping):
        """Restore the data store from a dictionary, loading its data into
        the instance.

        Currently, it is assumed that you will not use the dictionary for
        anything, as some subclasses may (accidentally) modify it."""
        for var in self.variables:
            try:
                value = d[var]
            except KeyError:
                value = self.get_default(var)
            setattr(self, var, value)

    def todict(self) -> dict:
        """Convert the data store to a dictionary and return it.

        Currently, it is expected that you will not modify it, as some
        subclasses may (accidentally) reuse their inner data."""
        result = {}
        for variable in self.variables:
            result[variable] = getattr(self, variable)
        return result

    @classmethod
    def get_instance(cls, *args, **kwargs) -> 'DataStore':
        """Return the singleton instance of the given datastore, or
        create one if not created yet."""
        if cls.instance is None:
            cls.instance = cls(*args, **kwargs)
        return cls.instance

    getInstance = get_instance

    def get_filename(self, create: bool=False) -> Optional[str]:
        """Get the filename of the datastore.

        If create is True, directories leading up to it will be created,
        and even if the data store does not exist, the name is returned.

        If create is False, and the data store does not exist,
        return None.
        """

        if create:
            if not os.path.exists(self.location):
                os.makedirs(self.location)
        filename = os.path.join(self.location, self.basename)
        if not os.path.exists(filename) and not create:
            filename = None
        return filename

    def save(self, file: io.TextIOBase=None, strict: bool=None) -> bool:
        """Save the data store, optionally to the provided file object.
        By default, inability to save is ignored, but if strict=True
        is passed, exceptions are thrown. If an explicit file is passed,
        strict=True is the default.

        The current data file is protected if it was not loaded."""
        if strict is None:
            strict = file is not None

        if file is None:
            if self.protect_previous and not self.current_load_initiated:

                filename = self.get_filename()
                if filename is not None:
                    warnmsgf("Will not overwrite data file %r from %r: "
                             "was not loaded", filename, self)
                    if strict:
                        raise FileExistsError(errno.EEXIST,
                                              os.strerror(errno.EEXIST),
                                              filename)
                    return False

            with Overwriter(self.get_filename(create=True), 'w',
                            encoding='utf8') as file:
                retval = self.save(file)
            return retval

        if not strict:
            try:
                return self.save(file, strict=True)

            except BaseException as exc:
                errmsgf("Data file failed to be saved: %r from %r: %s: %s",
                        file, self, type(exc).__name__, exc)
                traceback.print_exc()
                return False

        json.dump(self.todict(), file, indent=4, ensure_ascii=False)
        return True

    def load(self, file: io.TextIOBase=None, strict: bool=None) -> bool:
        """Load the data store, optionally from the provided file object.
        By default, broken data files are ignored, but if strict=True
        is passed, we throw exceptions on failure. If an explicit file is
        passed, strict=True is the default."""
        if strict is None:
            strict = file is not None

        if file is None:
            self.current_load_initiated = True

            filename = self.get_filename()
            if filename is None:
                return False
            with open(filename, 'r', encoding='utf8') as file:
                retval = self.load(file, strict=strict)
            return retval

        if not strict:
            try:
                return self.load(file, strict=True)

            except BaseException as exc:
                errmsgf("Data file failed to load: %r for %r: %s: %s",
                        file, self, type(exc).__name__, exc)
                traceback.print_exc()
                return False

        self.loaddict(json.load(file))
        return True


class FontGroup(object):

    """A group of fonts (a category, tag or search) that can be saved in a
    data store. All groups have a name, icon, and color."""

    data_attributes = {}
    types = {}

    type_name = 'group'

    def __init__(self, name: str, icon: str=None, color: str=None, **kwargs):
        super().__init__()
        self.name = name
        self.icon = icon
        self.color = color

    @classmethod
    def register(cls, name: str, plural: str=None,
                      label: str=None, label_plural: str=None) -> Callable:
        """Return a decorator register a new type of group.

        You should provide a name of the group (e.g. 'tag'), but you can
        also provide plural (e.g. 'tags'), a label (e.g. N_('tag')) and
        a label_plural.

        If no labels are provided, the names are used."""

        def decorator(subcls: type) -> type:
            subcls.type_name = name
            subcls.type_name_plural = plural or name
            subcls.type_label = label or name
            subcls.type_label_plural = label_plural or label or plural or name
            cls.types[name] = subcls

            return subcls

        return decorator

    @classmethod
    def get_type(cls, name: 'FontGroupTypeKey'):
        """Get a given FontGroup type, usually by name. Passing the class
        as a constant returns the class itself."""
        if isinstance(name, type):
            return name
        return cls.types[name]

    def modify(self, icon: Optional[str]=_UNCHANGED,
                     color: Optional[str]=_UNCHANGED):
        """Modify the icon and/or color of a given group."""
        if icon is not _UNCHANGED:
            self.icon = icon
        if color is not _UNCHANGED:
            self.color = color

    @classmethod
    def fromdict(cls, d: Mapping) -> 'FontGroup':
        """Reconstruct from dictionary."""
        return cls(**d)

    def todict(self, info_only: bool=False) -> dict:
        """Convert to dictionary.

        If info_only=True is passed, only the information such as label,
        icon and color (without the data) is saved. This is useful for
        mass-serialization of groups, that includes the group elements
        with the font family instead of the font group.
        """
        result = dict(vars(self))
        for key, simplify in self.data_attributes.items():
            if info_only and key in result:
                del result[key]
            elif simplify is not None:
                result[key] = simplify(result[key])
        return result

    def __repr__(self):
        return '<%s(%r)>' % (type(self).__name__, self.name)


FontGroupTypeKey = Union[type, str]


@FontGroup.register(N_('category'), N_('categories'))
class FontCategory(FontGroup):

    """A font category containing a list of font families that can be
    stored in a data store."""

    data_attributes = {'families': list}

    def __init__(self, *args, families: IterableOf[str]=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.families = OrderedSet(families or ())


@FontGroup.register(N_('tag'), N_('tags'))
class FontTag(FontGroup):

    """A font tag containing a list of font families that can be
    stored in a data store."""

    data_attributes = {'families': list}

    def __init__(self, *args, families: IterableOf[str]=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.families = OrderedSet(families or ())


@FontGroup.register(N_('search'), N_('searches'))
class FontSearch(FontGroup):

    """A font search containing a list of filters."""

    data_attributes = {'filters': None}

    def __init__(self, *args,
                 filters: 'Union[typeatlas.filtering.Filter, Mapping]'=None,
                 **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(filters, 'todict'):
            filters = filters.todict()
        self.filters = dict(filters or ())

    def modify(self, *args,
               filters: 'Union[typeatlas.filtering.Filter, Mapping]'=_UNCHANGED,
               **kwargs):
        """Modify the search, potentially replacing the filters in addition
        to the icon, name and/or color."""

        super().modify(*args, **kwargs)

        if filters is not _UNCHANGED:
            if hasattr(filters, 'todict'):
                filters = filters.todict()
            self.filters = dict(filters or ())

    def apply_filter(self, filter_root: 'typeatlas.filtering.FilterGroup'):
        """Apply the saved search to a given filter group."""
        filter_root.restoredict(self.filters)


class FontGroupsContainer(object):

    """A container of font groups, such as tags, categories, or searches.

    The info attribute contains the groups.
    The families dict maps group to sets of families, if applicable.
    The by_family dict maps families to sets of group names, if applicable.

    References to these can be kept, they are *NOT* replaced
    with other dictionaries. The info and by_family dictionaries
    are noisy.

    Each container is created for a given group type, specified by name
    or class.
    """

    save = event.Signal(name='save',
                        doc="Call this signal to save the categorization")

    def __init__(self, grouping_type: FontGroupTypeKey):
        self.factory = FontGroup.get_type(grouping_type)
        self.grouping_type = self.factory.type_name

        self.info = event.OrderedNoisyMapping()
        self.families = {}
        self.by_family = event.OrderedNoisyMapping()

    def clear(self):
        """Clear all fonts from the group."""

        removed_by_family = dict(self.by_family)

        self.families.clear()
        self.by_family.clear()
        for family in removed_by_family:
            for group_name in removed_by_family[family]:
                self.removed(family, group_name)
        self.info.clear()

    def rename(self, group_name: str, new_name: str, overwrite: bool=False):
        """Rename a group. If overwrite=True is passed, allow overwriting
        an existing group."""
        if group_name == new_name:
            return

        if not overwrite and new_name in self.info:
            raise KeyError(new_name)
        if group_name not in self.info:
            raise KeyError(group_name)
        
        if group_name in self.families:
            self.families[new_name] = self.families.pop(group_name)
            for family, groups in self.families[new_name].items():
                if group_name in groups:
                    groups.remove(group_name)
                    groups.add(new_name)
                else:
                    warnmsgf("BUG: family %r both in %s %r and not in it",
                             family, self.grouping_type, group_name)

        if group_name in self.info:
            self.info[new_name] = self.info.pop(group_name)

    def define(self, group_name: str, *args, **kwargs) -> FontGroup:
        """Create or update a tag, category, search or other type of font group,
        optionally specifying icon and color, and return it.

        The first argument is the actual tag, category or search name.

        If the group exists, it is modified.
        """

        if group_name not in self.info:
            group = self.factory(group_name, *args, **kwargs)
            self.info[group_name] = group
            if hasattr(group, 'families'):
                self.families[group_name] = group.families
            else:
                self.families[group_name] = OrderedSet()

        elif args or kwargs:
            group = self.info[group_name]
            group.modify(*args, **kwargs)

        return group

    def undefine(self, group_name: str, *,
                       skip_nonempty: bool=False,
                       protect_nonempty: bool=False) -> Optional[FontGroup]:
        """Clear a grouping created by define(), and return the removed group.

        If skip_nonempty is True,  non-empty categories/tags won't be
        deleted. If protect_nonempty is True, an error will be thrown.
        """

        group = self.info.get(group_name)
        if group is not None:
            families = self.families
            if families:
                if protect_nonempty:
                    raise ValueError('{!r} not empty'.format(group))
                if skip_nonempty:
                    return
                for family in families:
                    self.discard(group_name, family)
            del self.info[group_name]
            del self.families[group_name]

        return group

    def add(self, family: str, group_name: str):
        """Add a tag, category or other group to a font family.

        The arguments are the family name and the group name.
        """

        if group_name not in self.info:
            self.define(group_name)

        self.families[group_name].add(family)
        if family not in self.by_family:
            self.by_family[family] = OrderedSet()
        self.by_family[family].add(group_name)
        self.added(family, group_name)

    def remove(self, family: str, group_name: str):
        """Remove a tag, category or other group from a font family.

        The arguments are the family name and the group name.
        """
        if group_name not in self.info:
            return

        self.families[group_name].remove(family)

        if family in self.by_family:
            self.by_family[family].remove(group_name)
            if not self.by_family[family]:
                del self.by_family[family]

        self.removed(family, group_name)

    added = event.Signal(str, str, name='added', signature_func=add,
                         doc="A tag, category or was added for a "
                             "font family")
    removed = event.Signal(str, str, name='added', signature_func=remove,
                           doc="A tag, category or was removed from a "
                               "font family")

    def discard(self, family: str, group_name: str):
        """Discard a tag, category or other group from a font family,
        without raising an exception if it is already removed.

        The arguments are the family name and the group name.
        """
        if group_name not in self.info:
            return

        was_present = False

        group_families = self.families.get(group_name)
        if group_families is not None:
            if family in group_families:
                was_present = True
            group_families.discard(family)

        family_groups = self.by_family.get(family)
        if family_groups is not None:
            if group_name in family_groups:
                was_present = True
            family_groups.discard(group_name)
            if not family_groups:
                del self.by_family[family]

        self.removed(family, group_name)

    def todict(self) -> dict:
        return dict(grouping_type=self.grouping_type,
                    info={name: group.todict(info_only=bool(self.by_family))
                          for name, group in self.info.items()},
                    #families=self.families,
                    by_family={family: list(group_names)
                               for family, group_names
                                    in self.by_family.items()})

    @classmethod
    def fromdict(cls, data: Mapping) -> 'FontGroupsContainer':
        self = cls(data['grouping_type'])
        self.loaddict(data)
        return self

    def loaddict(self, d: Mapping):

        if d['grouping_type'] != self.grouping_type:
            raise ValueError('{!r} container cannot load {!r} dict'.format(
                                    self.grouping_type, d['grouping_type']))

        self.clear()
        self.info.update({name: self.factory.fromdict(category)
                          for name, category in d['info'].items()})

        for group_name, group in self.info.items():
            if hasattr(group, 'families'):
                self.families[group_name] = group.families

        for family, group_names in d['by_family'].items():
            current_groups = OrderedSet()
            for group_name in group_names:
                if group_name not in self.info:
                    self.define(group_name)
                group_families = self.families.get(group_name)
                if group_families is None:
                    group_families = self.families[group_name] = OrderedSet()
                group_families.add(family)
            self.by_family[family] = OrderedSet(group_names)
            for group_name in group_names:
                self.added(family, group_name)

    def __repr__(self):
        return '<%s(%r) at 0x%x>' % (type(self).__name__,
                                     self.grouping_type, id(self))


class History(event.NoisySequence):

    """A noisy sequence used to store a history of things.

    This is usually a history of strings entered in a search box,
    but other classes presently use it."""

    __slots__ = ()

    def push(self, value, replacing=None):
        """Push a value into the front of the history, potentially
        replacing an existing value. If the value is already in the
        history, it is moved to the front.

        The replacement of an existing value is used when the history was
        used to store text that the user was typing, and a partial string
        had been saved, and needs to be replaced.
        """

        self.push_pending(value)
        if value in self:
            self.remove(value)
        if replacing is not None and replacing in self:
            self.remove(replacing)
        self.insert(0, value)
        self.pushed(value)

    push_pending = event.Signal(object, name='push_pending',
                                doc="A value is about to be pushed")
    pushed = event.Signal(object, name='pushed',
                          doc="A value was pushed")


class Histories(DataStore):

    """A data store that saves histories. Usually, a history is a list
    of strings that were previously entered in a text or search box.
    Each history (for a given text / search box) is stored by name.

    One uses the .push() method of each history, which triggers
    auto-save. Each history is limited to the global limit,
    specified in the constructor. Older entries are
    discarded."""

    location = proginfo.DATA_DIR
    basename = proginfo.HISTORY_FILE

    def __init__(self, *args, limit: int=30, **kwargs):
        super().__init__(*args, **kwargs)
        self.histories = {}
        self.limit = limit
        self._ignore_updates = False

    def get_history(self, name: str) -> History:
        """Get a given named history, e.g. for a given text / search box"""
        if name not in self.histories:
            self.histories[name] = self._connect(History())
        return self.histories[name]

    def todict(self) -> dict:
        return {name: list(values) for name, values in self.histories.items()}

    def loaddict(self, d: Mapping):
        if self.histories:
            for history in self.histories.values():
                self._disconnect(history)
            self.histories = {}
        self.histories = {name: self._connect(History(values))
                          for name, values in d.items()}

    def _connect(self, history: History):
        """Connect the auto-save and auto-cleanup signals for a given
        History instance."""
        history.pushed.connect(self._history_changed, pass_self=True)
        return history

    def _disconnect(self, history: History):
        """Disonnect the auto-save and auto-cleanup signals from the given
        History instance."""
        history.pushed.disconnect(self._history_changed, pass_self=True)
        return history

    def _history_changed(self, history: History, value):
        """Called when the history changed."""
        if len(history) > self.limit >= 0:
            del history[self.limit:]

        self.save()


class InterfaceArrangements(DataStore):

    """A data store that interface arrangements / configurations.

    The arrangements are placed in two groups, name 'recent' and 'saved'.

    One uses .push() of the arragement group to save a new-arrangement.
    For 'recent', they are saved on program close, for 'saved' they are
    saved immediately.

    The 'recent' entries are limited to the limit specified in
    the constructor, older are discarded. The 'saved' entries
    require manual removal (which needs to saved with explicit .save()
    call).

    You can specify the interface type, which decides which
    file to save the interfaces in. Currently, only 'gui' is
    supported.
    """

    location = proginfo.DATA_DIR

    filenames = {
        'gui': proginfo.GUI_ARRANGEMENT_FILE,
    }

    temporary = set(['recent'])

    def __init__(self, interface_type: str='gui', *args,
                       limit: str=5, **kwargs):

        self.basename = self.filenames[interface_type]

        super().__init__(*args, **kwargs)
        self.arrangements = {}
        self.limit = limit
        self.changed = False

    def get_arrangements(self, name: str) -> History:
        """Get the group of arrangements, either 'saved' or 'recent'"""
        if name not in self.arrangements:
            self.arrangements[name] = self._connect(name, History())
        return self.arrangements[name]

    def todict(self) -> dict:
        return {name: list(values) for name, values in self.arrangements.items()}

    def loaddict(self, d: Mapping):
        if self.arrangements:
            for arrangement in self.arrangements.values():
                self._disconnect(arrangement)
            self.arrangements = {}
        self.arrangements = {name: self._connect(name, History(values))
                             for name, values in d.items()}
        self.changed = False

    def _connect(self, name: str, arrangements: History):
        """Connect the auto-save or auto-clean signals for the
        group of arrangements."""
        if name in self.temporary:
            method = self._recent_changed
        else:
            method = self._saved_changed
        arrangements.pushed.connect(method, pass_self=True)
        return arrangements

    def _disconnect(self, name: str, arrangements: History):
        """Disconnect the auto-save or auto-clean signals from the
        group of arrangements."""
        if name in self.temporary:
            method = self._recent_changed
        else:
            method = self._saved_changed
        arrangements.pushed.disconnect(method, pass_self=True)
        return arrangements

    def _saved_changed(self, arrangements: History, value):
        """Trigger auto-save. This is a slot for a signal, because
        event.Signal() currently does not support passing less arguments than
        needed."""
        self.save()

    def _recent_changed(self, arrangements: History, value):
        """Trigger auto-clean of recent. This is a slot for a signal, because
        event.Signal() currently does not support passing less arguments than
        needed."""
        self.changed = True
        if len(arrangements) > self.limit >= 0:
            del arrangements[self.limit:]

    def autosave(self):
        """Save if recent changed."""
        if self.changed:
            self.save()
            self.changed = False


class Categorization(DataStore):

    """A data store that saves font groups, like searches, categories and
    tags.

    For each group, the values are stored in a FontGroupsContainer, requested
    with self.container(grouping_type).
    """

    location = proginfo.DATA_DIR
    #location = proginfo.CONFIG_DIR
    basename = proginfo.CATEGORIES_FILE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._containers = {}
        for grouping_type, factory in FontGroup.types.items():
            container = FontGroupsContainer(grouping_type)

            self._containers[grouping_type] = container
            self._containers[factory.type_name_plural] = container
            setattr(self, factory.type_name_plural, container)

            container.save.connect(self.save)

    def container(self, grouping_type: FontGroupTypeKey) -> FontGroupsContainer:
        """Get the container for the given type of group. This value can be
        kept as it will always return the same instance."""
        if isinstance(grouping_type, type):
            grouping_type = grouping_type.type_name
        return self._containers[grouping_type]

    def todict(self) -> dict:
        result = {}
        for grouping_type, factory in FontGroup.types.items():
            group_container = getattr(self, factory.type_name_plural)
            result[grouping_type] = group_container.todict()

        return result

    def loaddict(self, d: Mapping):
        for grouping_type, factory in FontGroup.types.items():
            group_container = getattr(self, factory.type_name_plural)
            if grouping_type not in d:
                group_container.clear()
            else:
                group_container.loaddict(d[grouping_type])


class MetadataCache(DataStore):

    """A cache store that caches font metadata that is more expensive to discover,
    such as parsing PANOSE and IBM classes from inside each font (fontTools is
    slow Python-based OTF parser), charset on Windows/macOS where getting the list
    of supported characters is extremely expensive, etc."""

    location = proginfo.CACHE_DIR
    basename = proginfo.METADATA_CACHE
    variables = ['metadata', 'version']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata = {}
        self.changed = False
        self.seen = set()
        self.version = time.time()

    def load(self, *a, **kw):
        retval = super().load(*a, **kw)
        self.version = time.time()
        return retval

    def cache_classes(self, font: 'typeatlas.fontlist.Font'):
        """Cache the IBM classes and PANOSE classes for this font"""
        self.set_panoseclass(font)
        self.set_ibmclass(font)
        self.set_embedding(font)

    def fill_classes(self, font: 'typeatlas.fontlist.Font') -> bool:
        """Read the IBM classes and PANOSE classes for this font
        from cache. Return True if they were found."""
        panoseclass = self.get_panoseclass(font)
        ibmclass = self.get_ibmclass(font)
        embedding = self.get_embedding(font)

        if (panoseclass is not opentype.NO_PANOSE_DATA and
            ibmclass is not opentype.NO_IBM_CLASS_DATA and
            embedding is not opentype.NO_EMBEDDING_INFO):
                font.panoseclass = panoseclass
                font.ibmclass = ibmclass
                font.embedding = embedding
                return True

        return False

    def fill_charset(self, font: 'typeatlas.fontlist.Font') -> bool:
        """Fill any cached charset for the font, and return True if we
        had any success or the charset was already filled."""
        if font.charset is not None:
            return True

        charset = self.get_field(font, 'charset')
        if charset is None:
            return False

        try:
            charset = rangemath.OrdinalRange.from_fontconfig(charset)
        except (TypeError, ValueError) as exc:
            self.field_corrupt(font, 'charset', exc)
            return False

        else:
            font.charset = charset
            return True

    def cache_charset(self, font: 'typeatlas.fontlist.Font'):
        """Cache the character set supported by the font."""
        if font.charset is None:
            return
        self.set_field(font, 'charset', font.charset.to_fontconfig())

    def get_ibmclass(self, font: 'typeatlas.fontlist.Font',
                           default=opentype.NO_IBM_CLASS_DATA,
                           ) -> opentype.IBMFontClass:
        """Get the IBM class cached for a given font."""

        family_class = self.get_field(font, 'ibmclass', int)
        if family_class is None:
            return default
        return opentype.get_ibm_class(family_class)

    def set_ibmclass(self, font: 'typeatlas.fontlist.Font'):
        """Set the IBM class cached for a given font, taking it from
        the font."""
        ibmclass = getattr(font, 'ibmclass', None)
        if ibmclass is None or ibmclass is opentype.NO_IBM_CLASS_DATA:
            return

        self.set_field(font, 'ibmclass', opentype.ibm_class_to_int(ibmclass))

    def get_panoseclass(self, font: 'typeatlas.fontlist.Font',
                              default=opentype.NO_PANOSE_DATA
                              ) -> opentype.PanoseFontClass2:
        """Get the PANOSE class cached for a given font."""

        panoseclass = self.get_field(font, 'panoseclass',
                                     opentype.PanoseFontClass2.fromints,
                                     convert=True)
        if panoseclass is None:
            return default
        return panoseclass

    def set_panoseclass(self, font: 'typeatlas.fontlist.Font'):
        """Set the PANOSE class cached for a given font, taking it from
        the font."""
        panoseclass = getattr(font, 'panoseclass', None)
        if panoseclass is None or panoseclass is opentype.NO_PANOSE_DATA:
            return

        self.set_field(font, 'panoseclass', panoseclass.toints())

    def get_embedding(self, font: 'typeatlas.fontlist.Font',
                            default=opentype.NO_EMBEDDING_INFO,
                            ) -> opentype.EmbeddingInfo:
        """Get the embedding info cached for a given font."""

        fstype = self.get_field(font, 'embedding', int)
        if fstype is None:
            return default
        return opentype.EmbeddingInfo(fstype)

    def set_embedding(self, font: 'typeatlas.fontlist.Font'):
        """Set the embedding info cached for a given font, taking it from
        the font."""

        embedding = getattr(font, 'embedding', None)
        if embedding is None or embedding is opentype.NO_EMBEDDING_INFO:
            return

        self.set_field(font, 'embedding', embedding.flags)

    def has_field(self, font: 'typeatlas.fontlist.Font', field: str):
        """Get the cache of a specific field for a font."""
        return self.get_field(font, field) is not None

    def get_field(self, font: 'typeatlas.fontlist.Font', field: str,
                        type: Union[type, Callable]=None,
                        convert: bool=False):
        """Get the cache of a specific field for a font.

        You can pass type to verify the type of the result (not recommended)
        or pass type and convert=True to convert it - then it can be any callable.
        """
        if not isinstance(font, str):
            key = font.cachekey()
        else:
            key = font

        self.seen.add(key)

        values = self.metadata.get(key)
        if values is None:
            return None

        values['seen'] = self.version

        result = values.get(field)
        if result is None:
            return None

        if type is not None:
            if convert:
                try:
                    return type(result)
                except (TypeError, ValueError) as exc:
                    self.field_corrupt(font, field, exc)
                return None

            elif not isinstance(result, type):
                self.field_corrupt(font, field,
                                   TypeError("{!r} expected".format(type)))
                return None

        return result

    def set_field(self, font: 'typeatlas.fontlist.Font', field: str, value):
        """Set the cache of a specific field for a font."""
        if not isinstance(font, str):
            key = font.cachekey()
        else:
            key = font

        self.seen.add(key)

        values = self.metadata.setdefault(key, {})
        values['seen'] = self.version

        # If the value literally came from the cache, we're not setting anything
        if field in values and values[field] is value:
            return

        values[field] = value
        values['updated'] = self.version

        self.changed = True

    def unset_field(self, font: 'typeatlas.fontlist.Font', field: str):
        """Unset the specified field."""
        if not isinstance(font, str):
            key = font.cachekey()
        else:
            key = font

        self.seen.add(key)

        values = self.metadata.get(key)
        if values is None:
            return

        values['seen'] = self.version

        if field in values:
            del values[field]
            values['updated'] = self.version

    def field_corrupt(self, font: 'typeatlas.fontlist.Font', field: str,
                            exc_value: BaseException=None):
        """Inform us that the specified field is corrupt."""
        if exc_value is None:
            exc_value = sys.exc_info()[2]
        if exc_value is not None:
            error_text = "%s: %s" % (type(exc_value).__name__, exc_value)
        else:
            error_text = U_('Unknown error')

        warnmsgf(U_("Deleting corrupted cache for %r field of font %r: %s"),
                 field, font, error_text)

        self.unset_field(font, field)

    def clean_obsolete(self):
        """Clean any values not seen recently. This uses CACHE_FILL_MAXIMUM,
        CACHE_FILL_GOAL, CACHE_EXPIRATION constants to decide what to do.
        """

        if not self.seen or not self.metadata:
            return

        if len(self.metadata) < CACHE_FILL_MAXIMUM * len(self.seen):
            return

        goal = int(CACHE_FILL_GOAL * len(self.seen))
        delete = len(self.metadata) - goal

        expiration = self.version - CACHE_EXPIRATION

        for key, values in sorted(self.metadata.items(),
                                  key=lambda tpl: tpl[1]['seen']):

            if delete >= 0:
                assert key not in self.seen, "%r was found in seen" % (key, )
                del self.metadata[key]
                delete -= 1

            elif values['seen'] < expiration:
                del self.metadata[key]

            else:
                break

        self.changed = True

    def autosave(self):
        """Auto-save the cache if it changed."""
        if self.changed:
            self.clean_obsolete()
            self.save()
            self.changed = False
