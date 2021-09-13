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

"""Lifecycle-related interfaces."""

__metaclass__ = type
__all__ = [
    'IDoNotSnapshot',
    'IObjectCreatedEvent',
    'IObjectDeletedEvent',
    'IObjectModifiedEvent',
    'ISnapshotValueFactory',
    ]

import zope.lifecycleevent.interfaces as z3lifecycle
from zope.interface.interfaces import IObjectEvent
from zope.interface import Interface, Attribute


class IObjectCreatedEvent(z3lifecycle.IObjectCreatedEvent):
    """An object has been created."""
    user = Attribute("The user who created the object.")


class IObjectDeletedEvent(IObjectEvent):
    """An object is being deleted."""
    user = Attribute("The user who is making this change.")


class IObjectModifiedEvent(z3lifecycle.IObjectModifiedEvent):
    """An object has been modified."""

    object_before_modification = Attribute("The object before modification.")
    edited_fields = Attribute(
        "The list of fields that were edited. A field name may appear in "
        "this list if it were shown on an edit form, but not actually "
        "changed.")
    user = Attribute("The user who modified the object.")


class ISnapshotValueFactory(Interface):
    """This is a marker interface used to obtain snapshot of values.

    The interface isn't meant to be provided, but is only used as a factory
    lookup. The snapshot value is what should be returned from the adapter
    lookup.
    """


class IDoNotSnapshot(Interface):
    """Marker interface for attributes to exclude from the snapshot.

    Some attributes such as collections should not be included as part of the
    snapshot as they may be huge and not intrinsic to the object.
    """
