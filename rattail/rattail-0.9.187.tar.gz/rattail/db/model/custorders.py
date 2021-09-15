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
Data Models for Customer Orders
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import Base, uuid_column
from rattail.db.model import Store, Customer, Person, Product, User
from rattail.db.types import GPCType


class CustomerOrderBase(object):
    """
    Base class for customer orders; defines common fields.
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__customer_order_table_args__()

    @classmethod
    def __customer_order_table_args__(cls):
        table_name = cls.__tablename__
        return (
            sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'],
                                    name='{}_fk_store'.format(table_name)),
            sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'],
                                    name='{}_fk_customer'.format(table_name)),
            sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'],
                                    name='{}_fk_person'.format(table_name)),
        )

    store_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def store(cls):
        return orm.relationship(
            Store,
            doc="""
            Reference to the store to which the order applies.
            """)

    customer_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def customer(cls):
        return orm.relationship(
            Customer,
            doc="""
            Reference to the customer account for which the order exists.
            """)

    person_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def person(cls):
        return orm.relationship(
            Person,
            doc="""
            Reference to the person to whom the order applies.
            """)

    phone_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    Customer contact phone number for sake of this order.
    """)

    email_address = sa.Column(sa.String(length=255), nullable=True, doc="""
    Customer contact email address for sake of this order.
    """)

    total_price = sa.Column(sa.Numeric(precision=10, scale=3), nullable=True, doc="""
    Full price (not including tax etc.) for all items on the order.
    """)


@six.python_2_unicode_compatible
class CustomerOrder(CustomerOrderBase, Base):
    """
    Represents an order placed by the customer.
    """
    __tablename__ = 'custorder'

    @declared_attr
    def __table_args__(cls):
        return cls.__customer_order_table_args__() + (
            sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'],
                                    name='custorder_fk_created_by'),
        )

    uuid = uuid_column()

    id = sa.Column(sa.Integer(), doc="""
    Numeric, auto-increment ID for the order.
    """)

    created = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the order/batch was first created.
    """)

    created_by_uuid = sa.Column(sa.String(length=32), nullable=True)
    created_by = orm.relationship(
        User,
        doc="""
        Reference to the user who initially created the order/batch.
        """)

    status_code = sa.Column(sa.Integer(), nullable=False)

    items = orm.relationship('CustomerOrderItem', back_populates='order',
                             collection_class=ordering_list('sequence', count_from=1), doc="""
    Sequence of :class:`CustomerOrderItem` instances which belong to the order.
    """)

    def __str__(self):
        if self.id:
            return "#{}".format(self.id)
        return "(pending)"


@six.python_2_unicode_compatible
class CustomerOrderItemBase(object):
    """
    Base class for customer order line items.
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__customer_order_item_table_args__()

    @classmethod
    def __customer_order_item_table_args__(cls):
        table_name = cls.__tablename__
        return (
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'],
                                    name='{}_fk_product'.format(table_name)),
        )

    product_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def product(cls):
        return orm.relationship(
            Product,
            doc="""
            Reference to the master product record for the line item.
            """)

    product_upc = sa.Column(GPCType(), nullable=True, doc="""
    UPC for the product associated with the row.
    """)

    product_brand = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name for the product being ordered.  This should be a cache of the
    relevant :attr:`Brand.name`.
    """)

    product_description = sa.Column(sa.String(length=60), nullable=True, doc="""
    Primary description for the product being ordered.  This should be a cache
    of :attr:`Product.description`.
    """)

    product_size = sa.Column(sa.String(length=30), nullable=True, doc="""
    Size of the product being ordered.  This should be a cache of
    :attr:`Product.size`.
    """)

    product_weighed = sa.Column(sa.String(length=4), nullable=True, doc="""
    Flag indicating whether the product is sold by weight.  This should be a
    cache of :attr:`Product.weighed`.
    """)

    # TODO: probably should get rid of this, i can't think of why it's needed.
    # for now we just make sure it is nullable, since that wasn't the case.
    product_unit_of_measure = sa.Column(sa.String(length=4), nullable=True, doc="""
    Code indicating the unit of measure for the product.  This should be a
    cache of :attr:`Product.unit_of_measure`.
    """)

    department_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of the department to which the product belongs.
    """)

    department_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name of the department to which the product belongs.
    """)

    case_quantity = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Case pack count for the product being ordered.  This should be a cache of
    :attr:`Product.case_size`.
    """)

    # TODO: i now think that cases_ordered and units_ordered should go away.
    # but will wait until that idea has proven itself before removing.  am
    # pretty sure they are obviated by order_quantity and order_uom.

    cases_ordered = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were initially ordered.
    """)

    units_ordered = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were initially ordered.
    """)

    order_quantity = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Quantity being ordered by the customer.
    """)

    order_uom = sa.Column(sa.String(length=4), nullable=True, doc="""
    Code indicating the unit of measure for the order itself.  Does not
    directly reflect the :attr:`~rattail.db.model.Product.unit_of_measure`.
    """)

    product_unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Unit cost of the product being ordered.  This should be a cache of the
    relevant :attr:`rattail.db.model.ProductCost.unit_cost`.
    """)

    unit_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Unit price for the product being ordered.  This is the price which is
    quoted to the customer and/or charged to the customer, but for a unit only
    and *before* any discounts are applied.  It generally will be a cache of
    the relevant :attr:`ProductPrice.price`.
    """)

    discount_percent = sa.Column(sa.Numeric(precision=5, scale=3), nullable=False, default=0, doc="""
    Discount percentage which will be applied to the product's price as part of
    calculating the :attr:`total_price` for the item.
    """)

    total_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Full price (not including tax etc.) which the customer is asked to pay for the item.
    """)

    paid_amount = sa.Column(sa.Numeric(precision=8, scale=3), nullable=False, default=0, doc="""
    Amount which the customer has paid toward the :attr:`total_price` of theitem.
    """)

    payment_transaction_number = sa.Column(sa.String(length=8), nullable=True, doc="""
    Transaction number in which payment for the order was taken, if applicable.
    """)

    def __str__(self):
        return str(self.product or "(no product)")


class CustomerOrderItem(CustomerOrderItemBase, Base):
    """
    Represents a particular line item (product) within a customer order.
    """
    __tablename__ = 'custorder_item'

    @declared_attr
    def __table_args__(cls):
        return cls.__customer_order_item_table_args__() + (
            sa.ForeignKeyConstraint(['order_uuid'], ['custorder.uuid'],
                                    name='custorder_item_fk_order'),
        )

    uuid = uuid_column()

    order_uuid = sa.Column(sa.String(length=32), nullable=False)
    order = orm.relationship(CustomerOrder, back_populates='items', doc="""
    Reference to the :class:`CustomerOrder` instance to which the item belongs.
    """)

    sequence = sa.Column(sa.Integer(), nullable=False, doc="""
    Numeric sequence for the item, i.e. its "line number".  These values should
    obviously increment in sequence and be unique within the context of a
    single order.
    """)

    status_code = sa.Column(sa.Integer(), nullable=False)


class CustomerOrderItemEvent(Base):
    """
    An event in the life of a customer order item
    """
    __tablename__ = 'custorder_item_event'
    __table_args__ = (
        sa.ForeignKeyConstraint(['item_uuid'], ['custorder_item.uuid'], name='custorder_item_event_fk_item'),
        sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'], name='custorder_item_event_fk_user'),
    )

    uuid = uuid_column()

    item_uuid = sa.Column(sa.String(length=32), nullable=False)

    item = orm.relationship(
        CustomerOrderItem,
        doc="""
        Reference to the :class:`CustomerOrder` instance to which the item belongs.
        """,
        backref=orm.backref(
            'events',
            order_by='CustomerOrderItemEvent.occurred'))

    type_code = sa.Column(sa.Integer, nullable=False)

    occurred = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the event occurred.
    """)

    user_uuid = sa.Column(sa.String(length=32), nullable=False)

    user = orm.relationship(
        User,
        doc="""
        User who was the "actor" for the event.
        """)

    note = sa.Column(sa.Text(), nullable=True, doc="""
    Optional note recorded for the event.
    """)
