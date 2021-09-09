# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Clientele Handler
"""

from __future__ import unicode_literals, absolute_import

from rattail.util import load_object
from rattail.app import GenericHandler


class ClienteleHandler(GenericHandler):
    """
    Base class and default implementation for clientele handlers.
    """

    def ensure_customer(self, person):
        """
        Returns the customer record associated with the given person, creating
        it first if necessary.
        """
        customer = self.get_customer(person)
        if customer:
            return customer

        session = self.get_session(person)
        customer = self.make_customer(person)
        session.add(customer)
        session.flush()
        session.refresh(person)
        return customer

    def get_customer(self, person):
        """
        Returns the customer associated with the given person, if there is one.
        """
        return person.only_customer(require=False)

    def get_person(self, customer):
        """
        Returns the person associated with the given customer, if there is one.
        """
        return customer.only_person(require=False)

    def make_customer(self, person, **kwargs):
        """
        Create and return a new customer record.
        """
        customer = self.model.Customer()
        customer.name = person.display_name
        customer.people.append(person)
        return customer


def get_clientele_handler(config, **kwargs):
    """
    Create and return the configured :class:`ClienteleHandler` instance.
    """
    spec = config.get('rattail', 'clientele.handler')
    if spec:
        factory = load_object(spec)
    else:
        factory = ClienteleHandler
    return factory(config, **kwargs)
