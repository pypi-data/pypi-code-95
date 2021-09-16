# -*- coding: utf-8 -*-
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import with_transaction
from nereid.contrib.pagination import Pagination, BasePagination, \
    QueryPagination
from nereid.testing import POOL as pool
from sql import Table


class TestPagination(unittest.TestCase):

    def setUp(self):
        trytond.tests.test_tryton.activate_module('nereid')

        self.nereid_user_obj = pool.get('nereid.user')
        self.company_obj = pool.get('company.company')
        self.party_obj = pool.get('party.party')
        self.currency_obj = pool.get('currency.currency')
        self.address_obj = pool.get('party.address')

    def setup_defaults(self):
        """
        Setup the defaults
        """
        usd, = self.currency_obj.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
            }])
        self.party, = self.party_obj.create([{
            'name': 'MBSolutions',
            }])
        self.company, = self.company_obj.create([{
            'party': self.party,
            'currency': usd,
            }])
        self.guest_party, = self.party_obj.create([{
            'name': 'Guest User',
            }])

    def test_0010_base_pagination(self):
        """
        Test basic pagination
        """
        pagination = BasePagination(1, 3, [])
        self.assertEqual(pagination.count, 0)
        self.assertEqual(pagination.pages, 0)
        self.assertEqual(pagination.begin_count, 0)
        self.assertEqual(pagination.end_count, 0)

        pagination = BasePagination(1, 3, list(range(1, 10)))
        self.assertEqual(pagination.count, 9)
        self.assertEqual(pagination.pages, 3)
        self.assertEqual(pagination.begin_count, 1)
        self.assertEqual(pagination.end_count, 3)
        self.assertEqual(pagination.all_items(), [1, 2, 3, 4, 5, 6, 7, 8, 9])

    @with_transaction()
    def test_0020_model_pagination(self):
        """
        Test pagination for models
        """
        self.setup_defaults()

        # Create a 100 nereid users
        for id in range(0, 100):
            self.nereid_user_obj.create([{
                'party': self.guest_party,
                'name': 'User %s' % id,
                'email': 'user-%s@openlabs.co.in' % id,
                'password': 'password',
                'company': self.company.id,
                }])

        pagination = Pagination(self.nereid_user_obj, [], 1, 10)
        self.assertEqual(pagination.count, 100)
        self.assertEqual(pagination.pages, 10)
        self.assertEqual(pagination.begin_count, 1)
        self.assertEqual(pagination.end_count, 10)

    @with_transaction()
    def test_0030_model_pagination_serialization(self):
        """
        Test serialization of pagination for models
        """
        self.setup_defaults()

        # Create a 100 nereid users
        for id in range(0, 100):
            self.nereid_user_obj.create([{
                'party': self.guest_party,
                'name': 'User %s' % id,
                'email': 'user-%s@openlabs.co.in' % id,
                'password': 'password',
                'company': self.company.id,
                }])

        pagination = Pagination(self.nereid_user_obj, [], 1, 10)
        serialized = pagination.serialize()

        self.assertEqual(serialized['count'], 100)
        self.assertEqual(serialized['pages'], 10)
        self.assertEqual(serialized['page'], 1)
        self.assertEqual(len(serialized['items']), 10)

        self.assertTrue('name' in serialized['items'][0])

    @with_transaction()
    def test_0040_model_pagination_serialization(self):
        """
        Test serialization of pagination for model which does not have
        serialize method
        """
        self.setup_defaults()

        # Create a 100 addresses
        for id in range(0, 100):
            self.address_obj.create([{
                'party': self.guest_party,
                'name': 'User %s' % id,
                }])

        pagination = Pagination(self.address_obj, [], 1, 10)
        serialized = pagination.serialize()

        self.assertTrue('id' in serialized['items'][0])
        self.assertTrue('rec_name' in serialized['items'][0])

    @with_transaction()
    def test_0050_query_pagination(self):
        """
        Test pagination via `nereid.contrib.QueryPagination.`
        """
        self.setup_defaults()

        # Create a 100 addresses
        for id in range(0, 100):
            self.address_obj.create([{
                'party': self.guest_party,
                'name': 'User %s' % id,
                }])

        table = Table('party_address')
        select_query = table.select()

        pagination = QueryPagination(self.address_obj, select_query, table,
            page=1, per_page=10)

        self.assertEqual(pagination.count, 100)
        self.assertEqual(pagination.pages, 10)
        self.assertEqual(pagination.begin_count, 1)
        self.assertEqual(pagination.end_count, 10)

    # TODO: Test the order handling of serialization


if __name__ == '__main__':
    unittest.main()
