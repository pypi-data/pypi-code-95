# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.lifecycle
#
# lazr.lifecycle is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.lifecycle is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.lifecycle.  If not, see <http://www.gnu.org/licenses/>.

"""Provides object snapshotting functionality.

This is particularly useful in calculating deltas.
"""

__metaclass__ = type

__all__ = [
    'doNotSnapshot',
    'SnapshotCreationError',
    'Snapshot',
    ]

from zope.component import queryAdapter
from zope.interface.interfaces import IInterface
from zope.interface import alsoProvides, directlyProvides
from zope.schema.interfaces import IField
from zope.schema import Field
from zope.security.proxy import removeSecurityProxy

from lazr.lifecycle.interfaces import (
    IDoNotSnapshot, ISnapshotValueFactory)


_marker = object()


def doNotSnapshot(field):
    """Simple wrapper method to provide `IDoNotSnapshot`."""
    alsoProvides(field, IDoNotSnapshot)
    return field


class SnapshotCreationError(Exception):
    """Something went wrong while creating a snapshot."""


class Snapshot:
    """Provides a simple snapshot of the given object.

    The snapshot will have the attributes listed in names. It
    will also provide the interfaces listed in providing. If no names
    are supplied but an interface is provided, all Fields of that
    interface will be included in the snapshot.

    The attributes are copied by passing them through a ISnapshotValueFactory.
    The default implementation of that adapter just returns the value itself.
    """
    def __init__(self, ob, names=None, providing=None):
        ob = removeSecurityProxy(ob)

        if names is None and providing is None:
            raise SnapshotCreationError(
                "You have to specify either 'names' or 'providing'.")

        if IInterface.providedBy(providing):
            providing = [providing]

        if names is None:
            names = set()
            for iface in providing:
                for name in iface.names(all=True):
                    field = iface[name]
                    if (IField.providedBy(field) and
                        not IDoNotSnapshot.providedBy(field)):
                        names.add(name)

        for name in names:
            value = getattr(ob, name, _marker)
            if value is _marker:
                raise AssertionError("Attribute %s not in object %r"
                                     % (name, ob))
            snapshot_value = queryAdapter(
                value, ISnapshotValueFactory, default=_marker)
            if snapshot_value is _marker:
                snapshot_value = value
            setattr(self, name, snapshot_value)

        if providing is not None:
            directlyProvides(self, providing)
