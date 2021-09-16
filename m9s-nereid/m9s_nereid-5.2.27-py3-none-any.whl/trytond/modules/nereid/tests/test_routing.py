# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import USER, with_transaction
from trytond.transaction import Transaction

from nereid.testing import NereidTestCase

from wtforms import ValidationError

from .test_common import setup_objects


class TestRouting(NereidTestCase):
    'Test URL Routing'

    def setUp(self):
        trytond.tests.test_tryton.activate_module('nereid_test')
        setup_objects(self)
        self.templates = {
            'home.jinja': '{{ Transaction().language }}',
            }

    def setup_defaults(self):
        """
        Setup the defaults
        """
        self.usd, self.eur = self.currency_obj.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
            }, {
            'name': 'Euro',
            'code': 'EUR',
            'symbol': 'E',
            'rates': [('create', [{'rate': Decimal('2')}])],
            }])
        self.party, = self.party_obj.create([{
            'name': 'MBSolutions',
            }])
        self.company, = self.company_obj.create([{
            'party': self.party,
            'currency': self.usd,
            }])
        party, = self.party_obj.create([{
            'name': 'Registered User',
            }])
        self.registered_user, = self.nereid_user_obj.create([{
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }])

        self.en, = self.language_obj.search([('code', '=', 'en')])
        self.es, = self.language_obj.search([('code', '=', 'es')])
        self.locale_en, self.locale_es = self.nereid_website_locale_obj.create(
            [{
            'code': 'en',
            'language': self.en,
            'currency': self.usd,
            }, {
            'code': 'es',
            'language': self.es,
            'currency': self.eur,
            }])

        self.nereid_website, = self.nereid_website_obj.create([{
            'name': 'localhost',
            'company': self.company,
            'application_user': USER,
            'default_locale': self.locale_en,
            'locales': [('add', [self.locale_en.id, self.locale_es.id])],
            }])

    def get_template_source(self, name):
        """
        Return templates
        """
        return self.templates.get(name)

    def get_app(self):
        """
        Inject transaction into the template context for the home template
        """
        app = super(TestRouting, self).get_app()
        app.jinja_env.globals['Transaction'] = Transaction
        return app

    @with_transaction()
    def test_0010_home_with_locales(self):
        """
        When accessing / for website with locales defined, there should be a
        redirect to the /locale
        """
        self.setup_defaults()
        app = self.get_app()

        with app.test_client() as c:
            response = c.get('/')
            self.assertEqual(response.status_code, 308)
            self.assertEqual(response.location,
                'http://localhost/%s' % self.locale_en.code)

        # Change the default locale to es and then check
        self.nereid_website.default_locale = self.locale_es
        self.nereid_website.save()
        self.nereid_website.clear_url_adapter_cache()

        app = self.get_app()

        with app.test_client() as c:
            response = c.get('/')
            self.assertEqual(response.status_code, 308)
            self.assertEqual(response.location,
                'http://localhost/%s' % self.locale_es.code)

    @with_transaction()
    def test_0020_home_without_locales(self):
        """
        When accessed without locales the site should return 200 on /
        """
        self.setup_defaults()

        # unset the locales
        self.nereid_website.locales = []
        self.nereid_website.save()

        app = self.get_app()

        with app.test_client() as c:
            response = c.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode('utf-8'), 'en')

    @with_transaction()
    def test_0030_lang_context_with_locale(self):
        """
        Test that the language available in the context is the right one
        """
        self.setup_defaults()
        app = self.get_app()

        with app.test_client() as c:
            response = c.get('/en/')
            self.assertEqual(response.data.decode('utf-8'), 'en')

        with app.test_client() as c:
            response = c.get('/es/')
            self.assertEqual(response.data.decode('utf-8'), 'es')

    @with_transaction()
    def test_0040_lang_context_without_locale(self):
        """
        Test that the language available in the context is the right one
        """
        self.setup_defaults()
        self.nereid_website.locales = []
        self.nereid_website.save()
        app = self.get_app()

        with app.test_client() as c:
            response = c.get('/')
            self.assertEqual(response.data.decode('utf-8'), 'en')

        # Change the default locale to es and then check
        self.nereid_website.default_locale = self.locale_es
        self.nereid_website.save()

        with app.test_client() as c:
            response = c.get('/')
            self.assertEqual(response.data.decode('utf-8'), 'es')

    @with_transaction()
    def test_0050_website_routing(self):
        """
        Test should not check for match on single website.
        """
        self.setup_defaults()
        self.nereid_website.locales = []
        self.nereid_website.save()
        app = self.get_app()

        with app.test_client() as c:
            response = c.get('http://localhost/')
            self.assertEqual(response.data.decode('utf-8'), 'en')

            response = c.get('http://any_single_website_should_generally_work/')
            self.assertEqual(response.data.decode('utf-8'), 'en')

            self.nereid_website_obj.create([{
                'name': 'another_website',
                'company': self.company,
                'application_user': USER,
                'default_locale': self.locale_en,
            }])

            # Should break, as there are more than 1 website.
            response = c.get('http://this_should_break/')
            self.assertEqual(response.status_code, 404)
            self.assertIn(
                'The requested website was not found on the server',
                response.data.decode('utf-8'))

    @with_transaction()
    def test_0060_invalid_active_id_url(self):
        """
        Test that the url in 404 if record for active_id doesn't exist
        """
        self.setup_defaults()
        self.nereid_website.locales = []
        self.nereid_website.save()
        app = self.get_app()
        country, = self.country_obj.create([{
            'name': 'India',
            'code': 'IN'
            }])

        with app.test_client() as c:
            response = c.get('/countries/%d/subdivisions' % country.id)
            self.assertEqual(response.status_code, 200)

            response = c.get('/countries/6/subdivisions')  # Invalid record
            self.assertEqual(response.status_code, 404)

    @with_transaction()
    def test_0070_csrf(self):
        """
        Test that the csrf for POST request works
        """
        self.setup_defaults()
        self.nereid_website.locales = []
        self.nereid_website.save()
        app = self.get_app()
        # Enable CSRF
        app.config['WTF_CSRF_ENABLED'] = True

        with app.test_client() as c:
            # NO csrf-token
            response = c.post('/test-csrf',
                data={
                    'name': 'dummy name'
                })
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'The CSRF token is missing.',
                response.data.decode('utf-8'))

            # csrf token with invalid form
            csrf_token = c.get('/gen-csrf').data.decode('utf-8')
            response = c.post('/test-csrf',
                data={
                    'csrf_token': csrf_token,
                })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode('utf-8'), 'Failure')

            # csrf token with valid form
            csrf_token = c.get('/gen-csrf').data.decode('utf-8')
            response = c.post('/test-csrf',
                data={
                    'name': 'dummy name',
                    'csrf_token': csrf_token,
                })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode('utf-8'), 'Success')

    @with_transaction()
    def test_0070_csrf_exempt(self):
        """
        Test that the csrf exempt for POST request works
        """
        self.setup_defaults()
        self.nereid_website.locales = []
        self.nereid_website.save()
        app = self.get_app()
        # Enable CSRF
        app.config['WTF_CSRF_ENABLED'] = True

        with app.test_client() as c:
            # invalid form
            response = c.post('/test-csrf-exempt',
                data={
                    'name': '',
                })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode('utf-8'), 'Failure')

            # valid form
            response = c.post('/test-csrf-exempt',
                data={
                    'name': 'dummy name',
                })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode('utf-8'), 'Success')


def suite():
    "Nereid Routing test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestRouting))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
