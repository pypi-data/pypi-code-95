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

__metaclass__ = type

__all__ = ['ObjectCreatedEvent',
           'ObjectDeletedEvent',
           'ObjectModifiedEvent',
           ]

from zope.interface import implementer
import zope.security.management as management
from lazr.lifecycle.interfaces import (
    IObjectCreatedEvent, IObjectModifiedEvent, IObjectDeletedEvent)


class LifecyleEventBase:
    """Base class for all LAZR lifecycle event.

    It fills the user attribute based on the current interaction.
    """

    def __init__(self, object, user=None):
        self.object = object
        if user is None:
            user = self._getDefaultUser()
        self.user = user

    def _getDefaultUser(self):
        """Return the principal registered in the interaction.

        This raises a ValueError in case there is more than one principal in
        the interaction.
        """
        interaction = management.queryInteraction()
        if interaction is None:
            return None

        principals = [
            participation.principal
            for participation in list(interaction.participations)
            if participation.principal is not None
            ]
        if len(principals) == 1:
            return principals[0]
        elif len(principals) > 1:
            raise ValueError('Too many principals')
        else:
            return None


@implementer(IObjectCreatedEvent)
class ObjectCreatedEvent(LifecyleEventBase):
    """See `IObjectCreatedEvent`."""


@implementer(IObjectDeletedEvent)
class ObjectDeletedEvent(LifecyleEventBase):
    """See `IObjectDeletedEvent`."""


@implementer(IObjectModifiedEvent)
class ObjectModifiedEvent(LifecyleEventBase):
    """See `ISQLObjectModifiedEvent`."""

    def __init__(self, object, object_before_modification, edited_fields,
                 user=None):
        super(ObjectModifiedEvent, self).__init__(object, user=user)
        self.object_before_modification = object_before_modification
        self.edited_fields = edited_fields

    # Compatibility with zope.lifecycleevent.  (Note that the returned
    # modification descriptions only implement `IModificationDescription` if
    # suitable objects were passed when constructing this event.)
    @property
    def descriptions(self):
        return self.edited_fields
