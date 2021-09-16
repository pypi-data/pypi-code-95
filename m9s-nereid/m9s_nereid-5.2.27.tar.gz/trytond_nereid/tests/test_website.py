# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import json

import trytond.tests.test_tryton
from trytond.tests.test_tryton import USER, with_transaction
from nereid.testing import NereidTestCase

from .test_common import setup_objects


class TestWebsite(NereidTestCase):
    'Test Website'

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
            }])
        self.party, = self.party_obj.create([{
            'name': 'MBSolutions',
            }])
        self.company, = self.company_obj.create([{
            'party': self.party,
            'currency': usd,
            }])

        en, = self.language_obj.search([('code', '=', 'en')])
        currency, = self.currency_obj.search([('code', '=', 'USD')])
        locale, = self.nereid_website_locale_obj.create([{
            'code': 'en',
            'language': en,
            'currency': currency,
            }])
        self.nereid_website_obj.create([{
            'name': 'localhost',
            'company': self.company,
            'application_user': USER,
            'default_locale': locale,
            }])

    @with_transaction()
    def test_0010_user_status(self):
        """
        Test that user status returns jsonified object on POST
        request.
        """
        self.setup_defaults()
        app = self.get_app()

        with app.test_client() as c:
            rv = c.get('/user_status')
            self.assertEqual(rv.status_code, 200)

            rv = c.post('/user_status')
            data = json.loads(rv.data)

            self.assertEqual(data['status']['logged_id'], False)
            self.assertEqual(data['status']['messages'], [])


def suite():
    "Nereid Website test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestWebsite))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
