# -*- coding: utf-8 -*-
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import USER, with_transaction
from trytond.exceptions import UserError
from nereid.testing import NereidTestCase

from .test_common import setup_objects


class TestUser(NereidTestCase):
    """
    Test User
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
    def test_0010_user(self):
        """
        Test for former deprecated display_name field
        """
        self.setup_defaults()

        user, = self.nereid_user_obj.create([{
            "name": "MBSolutions",
            "party": self.party.id,
            "company": self.company.id,
            }])
        assert user.name == "MBSolutions"

        search_result, = self.nereid_user_obj.search([
            ('name', '=', 'MBSolutions'),
            ])
        assert search_result == user

    @with_transaction()
    def test_0020_user_email_case_sensitive(self):
        """Backend user should not be allowed to create user with case
        sensitive emails
        """
        self.setup_defaults()

        user, = self.nereid_user_obj.create([{
            "name": "MBSolutions",
            "email": "pp@m9s.biz",
            "party": self.party.id,
            "company": self.company.id,
            }])

        # Try create a new user with same email but in upper case
        with self.assertRaises(UserError):
            user, = self.nereid_user_obj.create([{
                "name": "MBSolutions",
                "email": "PP@M9S.BIZ",
                "party": self.party.id,
                "company": self.company.id,
                }])


def suite():
    "Nereid User test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestUser))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
