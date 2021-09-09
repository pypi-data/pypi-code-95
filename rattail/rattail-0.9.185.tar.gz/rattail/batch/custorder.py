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
Handler for "customer order" batches
"""

from __future__ import unicode_literals, absolute_import, division

import six
from sqlalchemy import orm

from rattail.db import model
from rattail.batch import BatchHandler


class CustomerOrderBatchHandler(BatchHandler):
    """
    Handler for all "customer order" batches, regardless of "mode".  The
    handler must inspect the
    :attr:`~rattail.db.model.batch.custorder.CustomerOrderBatch.mode` attribute
    of each batch it deals with, in order to determine which logic to apply.
    """
    batch_model_class = model.CustomerOrderBatch

    def get_case_size_for_product(self, product):
        return product.case_size

    def refresh_row(self, row):
        if not row.product:
            if row.item_entry:
                session = orm.object_session(row)
                # TODO: should do more than just query for uuid here
                product = session.query(model.Product).get(row.item_entry)
                if product:
                    row.product = product
            if not row.product:
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return

        product = row.product
        row.product_upc = product.upc
        row.product_brand = six.text_type(product.brand or "")
        row.product_description = product.description
        row.product_size = product.size
        row.product_weighed = product.weighed
        row.case_quantity = self.get_case_size_for_product(product)

        department = product.department
        row.department_number = department.number if department else None
        row.department_name = department.name if department else None

        cost = product.cost
        row.product_unit_cost = cost.unit_cost if cost else None

        regprice = product.regular_price
        row.unit_price = regprice.price if regprice else None

        # we need to know if total price is updated
        old_total = row.total_price

        # maybe update total price
        if row.unit_price is None:
            row.total_price = None
        elif not row.unit_price:
            row.total_price = 0
        else:
            row.total_price = row.unit_price * row.order_quantity
            if row.order_uom == self.enum.UNIT_OF_MEASURE_CASE:
                row.total_price *= (row.case_quantity or 1)

        # update total price for batch too, if it changed
        if row.total_price != old_total:
            batch = row.batch
            batch.total_price = ((batch.total_price or 0)
                                 + (row.total_price or 0)
                                 - (old_total or 0))

        row.status_code = row.STATUS_OK

    def remove_row(self, row):
        batch = row.batch

        if not row.removed:
            row.removed = True

            if row.total_price:
                batch.total_price = (batch.total_price or 0) - row.total_price

        self.refresh_batch_status(batch)

    def execute(self, batch, user=None, progress=None, **kwargs):
        """
        Default behavior here will simply create a new (proper) Customer Order
        based on the batch contents.  Override as needed.
        """
        batch_fields = [
            'store',
            'id',
            'customer',
            'person',
            'phone_number',
            'email_address',
            'total_price',
        ]

        order = model.CustomerOrder()
        order.created_by = user
        order.status_code = self.enum.CUSTORDER_STATUS_ORDERED
        for field in batch_fields:
            setattr(order, field, getattr(batch, field))

        row_fields = [
            'product',
            'product_upc',
            'product_brand',
            'product_description',
            'product_size',
            'product_weighed',
            'department_number',
            'department_name',
            'case_quantity',
            'order_quantity',
            'order_uom',
            'product_unit_cost',
            'unit_price',
            'discount_percent',
            'total_price',
            'paid_amount',
            'payment_transaction_number',
        ]

        def convert(row, i):
            item = model.CustomerOrderItem()
            item.sequence = i + 1
            item.status_code = self.enum.CUSTORDER_ITEM_STATUS_ORDERED
            for field in row_fields:
                setattr(item, field, getattr(row, field))
            order.items.append(item)

        self.progress_loop(convert, batch.active_rows(), progress,
                           message="Converting batch rows to order items")

        session = orm.object_session(batch)
        session.add(order)
        session.flush()

        return order
