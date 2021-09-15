# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Problem Reports for Rattail Systems
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.db import Session, model
from rattail.problems import ProblemReport


class RattailProblemReport(ProblemReport):
    """
    Base class for problem reports pertaining to a Rattail systems.
    """
    system_key = 'rattail'


class ProductWithoutPrice(RattailProblemReport):
    """
    Looks for products which have null (or $0) regular price.
    """
    problem_key = 'product_without_price'
    problem_title = "Products with no price"

    def find_problems(self, **kwargs):
        problems = []
        session = Session()
        products = session.query(model.Product)\
                          .options(orm.joinedload(model.Product.regular_price))

        def inspect(product, i):
            price = product.regular_price
            if not price or not price.price:
                problems.append(product)

        self.progress_loop(inspect, products,
                           message="Looking for products with no price")
        session.close()
        return problems


class UpgradePending(RattailProblemReport):
    """
    Looks for any system upgrades which have yet to be executed.
    """
    problem_key = 'upgrade_pending'
    problem_title = "Pending upgrade"

    def find_problems(self, **kwargs):
        session = Session()
        upgrades = session.query(model.Upgrade)\
                          .filter(model.Upgrade.status_code == self.enum.UPGRADE_STATUS_PENDING)\
                          .options(orm.joinedload(model.Upgrade.created_by)\
                                   .joinedload(model.User.person))\
                          .all()
        session.close()
        return upgrades
