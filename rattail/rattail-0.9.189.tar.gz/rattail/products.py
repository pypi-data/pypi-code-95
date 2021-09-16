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
Products Handler
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm

from rattail import pod
from rattail.util import load_object
from rattail.app import GenericHandler


class ProductsHandler(GenericHandler):
    """
    Base class and default implementation for product handlers.

    A products handler of course should get the final say in how products are
    handled.  This means everything from pricing, to whether or not a
    particular product can be deleted, etc.
    """

    def get_image_url(self, upc=None, product=None, **kwargs):
        """
        Return the preferred image URL for the given UPC or product.
        """
        if product and product.upc:
            upc = product.upc
        if upc:
            return self.get_pod_image_url(upc)

    def get_pod_image_url(self, upc, **kwargs):
        """
        Return the POD image URL for the given UPC.
        """
        if upc:
            return pod.get_image_url(self.config, upc)

    def get_uom_sil_codes(self, session, uppercase=False, **kwargs):
        """
        This should return a dict, keys of which are UOM abbreviation strings,
        and values of which are corresponding SIL code strings.

        :param session: Reference to current Rattail DB session.
        :param uppercase: Set to ``True`` to cause all UOM abbreviations to be
           upper-cased when adding to the map.
        :returns: Dictionary containing all known UOM / SIL code mappings.
        """
        model = self.model

        def normalize(uom):
            if uom.sil_code:
                return uom.sil_code

        def make_key(uom, normal):
            key = uom.abbreviation
            if uppercase:
                key = key.upper()
            return key

        return self.cache_model(session, model.UnitOfMeasure,
                                normalizer=normalize,
                                key=make_key)

    def get_uom_sil_code(self, session, uom, uppercase=False, **kwargs):
        """
        This should return a SIL code which corresponds to the given UOM
        abbreviation string.  Useful when you just need one out of the blue,
        but if you need multiple codes looked up then you're probably better
        off using :meth:`get_uom_sil_codes()` for efficiency.

        :param session: Reference to current Rattail DB session.
        :param uppercase: Set to ``True`` to cause the UOM abbreviation to be
           upper-cased before performing the lookup.  This effectively makes
           the search case-insensitive.
        :param uom:  Unit of measure as abbreviated string, e.g. ``'LB'``.
        :returns: SIL code for the UOM, as string (e.g. ``'49'``), or ``None``
           if no matching code was found.
        """
        model = self.model
        query = session.query(model.UnitOfMeasure)
        if uppercase:
            query = query.filter(sa.func.upper(model.UnitOfMeasure.abbreviation) == uom.upper())
        else:
            query = query.filter(model.UnitOfMeasure.abbreviation == uom)
        try:
            match = query.one()
        except orm.exc.NoResultFound:
            pass
        else:
            return match.sil_code

    def collect_wild_uoms(self, **kwargs):
        """
        Collect all UOM abbreviations "from the wild" and ensure each is
        represented within the Rattail Units of Measure table.

        Note that you should not need to override this method.  Please override
        :meth:`find_wild_uoms()` instead.
        """
        session = self.make_session()
        model = self.model

        wild_uoms = self.find_wild_uoms(session, **kwargs)

        known_uoms = self.cache_model(session, model.UnitOfMeasure,
                                      key='abbreviation')

        for wild_uom in wild_uoms:
            if wild_uom not in known_uoms:
                uom = model.UnitOfMeasure()
                uom.abbreviation = wild_uom
                session.add(uom)

        session.commit()
        session.close()

    def find_wild_uoms(self, session, **kwargs):
        """
        Query some database(s) in order to discover all UOM abbreviations which
        exist "in the wild".

        You are encouraged to override this method as needed.  Note that
        certain POS integration packages may provide some common logic which
        may be used for this.

        :param session: Reference to current Rattail DB session.

        :returns: A list of strings, e.g. ``['OZ', 'LB', ...]``.
        """
        return []


def get_products_handler(config, **kwargs):
    """
    Create and return the configured :class:`ProductsHandler` instance.
    """
    spec = config.get('rattail', 'products.handler')
    if spec:
        factory = load_object(spec)
    else:
        factory = ProductsHandler
    return factory(config, **kwargs)
