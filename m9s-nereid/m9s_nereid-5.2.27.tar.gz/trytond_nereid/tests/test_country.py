# -*- coding: utf-8 -*-
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import json
import unittest
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import USER, with_transaction
from nereid.testing import NereidTestCase

from .test_common import setup_objects


class TestCountry(NereidTestCase):
    """
    Test Country
    """

    def setUp(self):
        trytond.tests.test_tryton.activate_module('nereid')
        setup_objects(self)

    def setup_defaults(self):
        """
        Setup the defaults
        """
        usd, = self.currency_obj.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
            'rates': [('create', [{'rate': Decimal('1')}])],
            }])
        eur, = self.currency_obj.create([{
            'name': 'Euro',
            'code': 'EUR',
            'symbol': 'E',
            'rates': [('create', [{'rate': Decimal('2')}])],
            }])
        self.party, = self.party_obj.create([{
            'name': 'MBSolutions',
            }])
        self.company, = self.company_obj.create([{
            'currency': usd,
            'party': self.party,
            }])
        c1, = self.currency_obj.create([{
            'code': 'C1',
            'symbol': 'C1',
            'name': 'Currency 1',
            'rates': [('create', [{'rate': Decimal('10')}])],
            }])
        c2, = self.currency_obj.create([{
            'code': 'C2',
            'symbol': 'C2',
            'name': 'Currency 2',
            'rates': [('create', [{'rate': Decimal('20')}])],
            }])
        self.lang_currency, = self.currency_obj.create([{
            'code': 'C3',
            'symbol': 'C3',
            'name': 'Currency 3',
            'rates': [('create', [{'rate': Decimal('30')}])],
            }])
        self.currency_obj.create([{
            'code': 'C4',
            'symbol': 'C4',
            'name': 'Currency 4',
            'rates': [('create', [{'rate': Decimal('40')}])],
            }])
        self.website_currencies = [c1, c2]
        self.en, = self.language_obj.search([('code', '=', 'en')])
        self.es, = self.language_obj.search([('code', '=', 'es')])
        self.usd, = self.currency_obj.search([('code', '=', 'USD')])
        self.eur, = self.currency_obj.search([('code', '=', 'EUR')])
        locale_en, locale_es = self.nereid_website_locale_obj.create([{
            'code': 'en',
            'language': self.en,
            'currency': self.usd,
            }, {
            'code': 'es',
            'language': self.es,
            'currency': self.eur,
            }])
        self.nereid_website_obj.create([{
            'name': 'localhost',
            'company': self.company,
            'application_user': USER,
            'default_locale': locale_en.id,
            'currencies': [('add', self.website_currencies)],
            }])
        self.templates = {
            'home.jinja': '{{ "hell" }}',
            }

    @with_transaction()
    def test_0010_all_countries(self):
        """
        Check list of json serialized countries
        """
        self.setup_defaults()
        app = self.get_app()

        self.country_obj.create([{
            'name': 'India',
            'code': 'IN'
            }, {
            'name': 'Australia',
            'code': 'AU',
            }])

        with app.test_client() as c:
            rv = c.get('/all-countries')
            self.assertEqual(rv.status_code, 200)
            data = json.loads(rv.data)
            self.assertEqual(len(data['countries']), 2)

    @with_transaction()
    def test_0010_subdivisions(self):
        """
        Check subdivisons for given country
        """
        self.setup_defaults()
        app = self.get_app()

        country1, country2, = self.country_obj.create([{
            'name': 'India',
            'code': 'IN'
            }, {
            'name': 'Australia',
            'code': 'AU',
            }])

        # Create subdivision only for country1
        self.subdivision_obj.create([{
            'country': country1.id,
            'code': 'IN-OR',
            'name': 'Orissa',
            'type': 'state',
            }])

        with app.test_client() as c:
            rv = c.get('/countries/%d/subdivisions' % country1.id)
            self.assertEqual(rv.status_code, 200)
            data = json.loads(rv.data)
            self.assertEqual(len(data['result']), 1)
            self.assertTrue(data['result'][0]['name'] == 'Orissa')
            self.assertTrue(data['result'][0]['code'] == 'IN-OR')

            rv = c.get('/countries/%d/subdivisions' % country2.id)
            self.assertEqual(rv.status_code, 200)
            data = json.loads(rv.data)
            self.assertEqual(len(data['result']), 0)


def suite():
    "Nereid Country test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestCountry))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
