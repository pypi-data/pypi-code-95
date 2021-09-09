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
Customer Order Views
"""

from __future__ import unicode_literals, absolute_import

import decimal

import six
from sqlalchemy import orm

from rattail import pod
from rattail.db import model
from rattail.util import pretty_quantity
from rattail.batch import get_batch_handler

from webhelpers2.html import tags

from tailbone.db import Session
from tailbone.views import MasterView


class CustomerOrderView(MasterView):
    """
    Master view for customer orders
    """
    model_class = model.CustomerOrder
    route_prefix = 'custorders'
    editable = False
    deletable = False

    grid_columns = [
        'id',
        'customer',
        'person',
        'created',
        'status_code',
    ]

    form_fields = [
        'id',
        'customer',
        'person',
        'phone_number',
        'email_address',
        'created',
        'status_code',
    ]

    def query(self, session):
        return session.query(model.CustomerOrder)\
                      .options(orm.joinedload(model.CustomerOrder.customer))

    def configure_grid(self, g):
        super(CustomerOrderView, self).configure_grid(g)

        g.set_joiner('customer', lambda q: q.outerjoin(model.Customer))
        g.set_joiner('person', lambda q: q.outerjoin(model.Person))

        g.filters['customer'] = g.make_filter('customer', model.Customer.name,
                                              label="Customer Name",
                                              default_active=True,
                                              default_verb='contains')
        g.filters['person'] = g.make_filter('person', model.Person.display_name,
                                            label="Person Name",
                                            default_active=True,
                                            default_verb='contains')

        g.set_sorter('customer', model.Customer.name)
        g.set_sorter('person', model.Person.display_name)

        g.set_enum('status_code', self.enum.CUSTORDER_STATUS)

        g.set_sort_defaults('created', 'desc')

        # TODO: enum choices renderer
        g.set_label('status_code', "Status")
        g.set_label('id', "ID")

    def configure_form(self, f):
        super(CustomerOrderView, self).configure_form(f)

        # id
        f.set_readonly('id')
        f.set_label('id', "ID")

        # person
        f.set_renderer('person', self.render_person)

        # created
        f.set_readonly('created')

        # label overrides
        f.set_label('status_code', "Status")

    def render_person(self, order, field):
        person = order.person
        if not person:
            return ""
        text = six.text_type(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def create(self, form=None, template='create'):
        """
        View for creating a new customer order.  Note that it does so by way of
        maintaining a "new customer order" batch, until the user finally
        submits the order, at which point the batch is converted to a proper
        order.
        """
        self.handler = get_batch_handler(
            self.rattail_config, 'custorder',
            default='rattail.batch.custorder:CustomerOrderBatchHandler')

        batch = self.get_current_batch()

        if self.request.method == 'POST':

            # first we check for traditional form post
            action = self.request.POST.get('action')
            post_actions = [
                'start_over_entirely',
                'delete_batch',
            ]
            if action in post_actions:
                return getattr(self, action)(batch)

            # okay then, we'll assume newer JSON-style post params
            data = dict(self.request.json_body)
            action = data.get('action')
            json_actions = [
                'get_customer_info',
                'set_customer_data',
                'find_product_by_upc',
                'get_product_info',
                'add_item',
                'update_item',
                'delete_item',
                'submit_new_order',
            ]
            if action in json_actions:
                result = getattr(self, action)(batch, data)
                return self.json_response(result)

        items = [self.normalize_row(row)
                 for row in batch.active_rows()]
        context = {'batch': batch,
                   'normalized_batch': self.normalize_batch(batch),
                   'order_items': items}
        return self.render_to_response(template, context)

    def get_current_batch(self):
        user = self.request.user
        if not user:
            raise RuntimeError("this feature requires a user to be logged in")

        try:
            # there should be at most *one* new batch per user
            batch = self.Session.query(model.CustomerOrderBatch)\
                                .filter(model.CustomerOrderBatch.mode == self.enum.CUSTORDER_BATCH_MODE_CREATING)\
                                .filter(model.CustomerOrderBatch.created_by == user)\
                                .filter(model.CustomerOrderBatch.executed == None)\
                                .one()

        except orm.exc.NoResultFound:
            # no batch yet for this user, so make one

            batch = self.handler.make_batch(
                self.Session(), created_by=user,
                mode=self.enum.CUSTORDER_BATCH_MODE_CREATING)
            self.Session.add(batch)
            self.Session.flush()

        return batch

    def start_over_entirely(self, batch):
        # just delete current batch outright
        # TODO: should use self.handler.do_delete() instead?
        self.Session.delete(batch)
        self.Session.flush()

        # send user back to normal "create" page; a new batch will be generated
        # for them automatically
        route_prefix = self.get_route_prefix()
        url = self.request.route_url('{}.create'.format(route_prefix))
        return self.redirect(url)

    def delete_batch(self, batch):
        # just delete current batch outright
        # TODO: should use self.handler.do_delete() instead?
        self.Session.delete(batch)
        self.Session.flush()

        # set flash msg just to be more obvious
        self.request.session.flash("New customer order has been deleted.")

        # send user back to customer orders page, w/ no new batch generated
        route_prefix = self.get_route_prefix()
        url = self.request.route_url(route_prefix)
        return self.redirect(url)

    def get_customer_info(self, batch, data):
        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a customer UUID"}

        customer = self.Session.query(model.Customer).get(uuid)
        if not customer:
            return {'error': "Customer not found"}

        return self.info_for_customer(batch, data, customer)

    def info_for_customer(self, batch, data, customer):
        phone = customer.first_phone()
        email = customer.first_email()
        return {
            'uuid': customer.uuid,
            'phone_number': phone.number if phone else None,
            'email_address': email.address if email else None,
        }

    def set_customer_data(self, batch, data):
        if 'customer_uuid' in data:
            batch.customer_uuid = data['customer_uuid']
            if 'person_uuid' in data:
                batch.person_uuid = data['person_uuid']
            elif batch.customer_uuid:
                self.Session.flush()
                batch.person = batch.customer.first_person()
            else: # no customer set
                batch.person_uuid = None
        if 'phone_number' in data:
            batch.phone_number = data['phone_number']
        if 'email_address' in data:
            batch.email_address = data['email_address']
        self.Session.flush()
        return {'success': True}

    def find_product_by_upc(self, batch, data):
        upc = data.get('upc')
        if not upc:
            return {'error': "Must specify a product UPC"}

        product = self.handler.locate_product_for_entry(
            self.Session(), upc, product_key='upc')
        if not product:
            return {'error': "Product not found"}

        return self.info_for_product(batch, data, product)

    def get_product_info(self, batch, data):
        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a product UUID"}

        product = self.Session.query(model.Product).get(uuid)
        if not product:
            return {'error': "Product not found"}

        return self.info_for_product(batch, data, product)

    def uom_choices_for_product(self, product):
        choices = []

        # Each
        if not product or not product.weighed:
            unit_name = self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_EACH]
            choices.append({'key': self.enum.UNIT_OF_MEASURE_EACH,
                            'value': unit_name})

        # Pound
        if not product or product.weighed:
            unit_name = self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_POUND]
            choices.append({
                'key': self.enum.UNIT_OF_MEASURE_POUND,
                'value': unit_name,
            })

        # Case
        case_text = None
        case_size = self.handler.get_case_size_for_product(product)
        if case_size is None:
            case_text = "{} (&times; ?? {})".format(
                self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_CASE],
                unit_name)
        elif case_size > 1:
            case_text = "{} (&times; {} {})".format(
                self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_CASE],
                pretty_quantity(case_size),
                unit_name)
        if case_text:
            choices.append({'key': self.enum.UNIT_OF_MEASURE_CASE,
                            'value': case_text})

        return choices

    def info_for_product(self, batch, data, product):
        return {
            'uuid': product.uuid,
            'upc': six.text_type(product.upc),
            'upc_pretty': product.upc.pretty(),
            'full_description': product.full_description,
            'image_url': pod.get_image_url(self.rattail_config, product.upc),
            'uom_choices': self.uom_choices_for_product(product),
        }

    def normalize_batch(self, batch):
        return {
            'uuid': batch.uuid,
            'total_price': six.text_type(batch.total_price or 0),
            'total_price_display': "${:0.2f}".format(batch.total_price or 0),
            'status_code': batch.status_code,
            'status_text': batch.status_text,
        }

    def normalize_row(self, row):
        product = row.product
        department = product.department if product else None
        cost = product.cost if product else None
        data = {
            'uuid': row.uuid,
            'sequence': row.sequence,
            'item_entry': row.item_entry,
            'product_uuid': row.product_uuid,
            'product_upc': six.text_type(row.product_upc or ''),
            'product_upc_pretty': row.product_upc.pretty() if row.product_upc else None,
            'product_brand': row.product_brand,
            'product_description': row.product_description,
            'product_size': row.product_size,
            'product_full_description': product.full_description if product else row.product_description,
            'product_weighed': row.product_weighed,

            'case_quantity': pretty_quantity(row.case_quantity),
            'cases_ordered': pretty_quantity(row.cases_ordered),
            'units_ordered': pretty_quantity(row.units_ordered),
            'order_quantity': pretty_quantity(row.order_quantity),
            'order_uom': row.order_uom,
            'order_uom_choices': self.uom_choices_for_product(product),

            'department_display': department.name if department else None,
            'vendor_display': cost.vendor.name if cost else None,

            'unit_price': six.text_type(row.unit_price) if row.unit_price is not None else None,
            'unit_price_display': "${:0.2f}".format(row.unit_price) if row.unit_price is not None else None,
            'total_price': six.text_type(row.total_price) if row.total_price is not None else None,
            'total_price_display': "${:0.2f}".format(row.total_price) if row.total_price is not None else None,

            'status_code': row.status_code,
            'status_text': row.status_text,
        }

        unit_uom = self.enum.UNIT_OF_MEASURE_POUND if data['product_weighed'] else self.enum.UNIT_OF_MEASURE_EACH
        if row.order_uom == self.enum.UNIT_OF_MEASURE_CASE:
            if row.case_quantity is None:
                case_qty = unit_qty = '??'
            else:
                case_qty = data['case_quantity']
                unit_qty = pretty_quantity(row.order_quantity * row.case_quantity)
            data.update({
                'order_quantity_display': "{} {} (&times; {} {} = {} {})".format(
                    data['order_quantity'],
                    self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_CASE],
                    case_qty,
                    self.enum.UNIT_OF_MEASURE[unit_uom],
                    unit_qty,
                    self.enum.UNIT_OF_MEASURE[unit_uom]),
            })
        else:
            data.update({
                'order_quantity_display': "{} {}".format(
                    pretty_quantity(row.order_quantity),
                    self.enum.UNIT_OF_MEASURE[unit_uom]),
            })

        return data

    def add_item(self, batch, data):
        if data.get('product_is_known'):

            uuid = data.get('product_uuid')
            if not uuid:
                return {'error': "Must specify a product UUID"}

            product = self.Session.query(model.Product).get(uuid)
            if not product:
                return {'error': "Product not found"}

            row = self.handler.make_row()
            row.item_entry = product.uuid
            row.product = product
            row.order_quantity = decimal.Decimal(data.get('order_quantity') or '0')
            row.order_uom = data.get('order_uom')
            self.handler.add_row(batch, row)
            self.Session.flush()
            self.Session.refresh(row)

        else: # product is not known
            raise NotImplementedError # TODO

        return {'batch': self.normalize_batch(batch),
                'row': self.normalize_row(row)}

    def update_item(self, batch, data):
        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a row UUID"}

        row = self.Session.query(model.CustomerOrderBatchRow).get(uuid)
        if not row:
            return {'error': "Row not found"}

        if row not in batch.active_rows():
            return {'error': "Row is not active for the batch"}

        if data.get('product_is_known'):

            uuid = data.get('product_uuid')
            if not uuid:
                return {'error': "Must specify a product UUID"}

            product = self.Session.query(model.Product).get(uuid)
            if not product:
                return {'error': "Product not found"}

            row.item_entry = product.uuid
            row.product = product
            row.order_quantity = decimal.Decimal(data.get('order_quantity') or '0')
            row.order_uom = data.get('order_uom')
            self.handler.refresh_row(row)
            self.Session.flush()
            self.Session.refresh(row)

        else: # product is not known
            raise NotImplementedError # TODO

        return {'batch': self.normalize_batch(batch),
                'row': self.normalize_row(row)}

    def delete_item(self, batch, data):

        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a row UUID"}

        row = self.Session.query(model.CustomerOrderBatchRow).get(uuid)
        if not row:
            return {'error': "Row not found"}

        if row not in batch.active_rows():
            return {'error': "Row is not active for this batch"}

        self.handler.do_remove_row(row)
        return {'ok': True,
                'batch': self.normalize_batch(batch)}

    def submit_new_order(self, batch, data):
        result = self.execute_new_order_batch(batch, data)
        if not result:
            return {'error': "Batch failed to execute"}

        next_url = None
        if isinstance(result, model.CustomerOrder):
            next_url = self.get_action_url('view', result)

        return {'ok': True, 'next_url': next_url}

    def execute_new_order_batch(self, batch, data):
        return self.handler.do_execute(batch, self.request.user)

# TODO: deprecate / remove this
CustomerOrdersView = CustomerOrderView


def includeme(config):
    CustomerOrderView.defaults(config)
