# -*- coding: utf-8 -*-
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import USER, with_transaction
from trytond.transaction import Transaction
from trytond.config import config
from trytond.pool import PoolMeta, Pool

from nereid import render_template, route
from nereid.testing import NereidTestCase
from nereid.testing import POOL as pool
from nereid.contrib.locale import make_lazy_gettext, make_lazy_ngettext

from .test_common import setup_objects

config.set('email', 'from', 'from@xyz.com')
config.set('database', 'path', '/tmp/temp_tryton_data/')


class StaticFileServingHomePage(metaclass=PoolMeta):
    __name__ = 'nereid.website'

    @classmethod
    @route('/static-file-test')
    def static_file_test(cls):
        static_file_obj = Pool().get('nereid.static.file')

        static_file, = static_file_obj.search([])
        return render_template(
            'home.jinja',
            static_file_obj=static_file_obj,
            static_file_id=static_file.id
        )


class TestStaticFile(NereidTestCase):

    @classmethod
    def setUpClass(cls):
        pool.register(StaticFileServingHomePage, module='nereid', type_='model')
        pool.init(update=['nereid'])

    @classmethod
    def tearDownClass(cls):
        mpool = pool.classes['model'].setdefault('nereid', [])
        del(mpool[StaticFileServingHomePage])
        pool.init(update=['nereid'])

    def setUp(self):
        trytond.tests.test_tryton.activate_module('nereid')
        setup_objects(self)

        self.templates = {
            'home.jinja':
            '''
            {% set static_file = static_file_obj(static_file_id) %}
            {{ static_file.url }}
            ''',
            }

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
            'locales': [('add', [locale.id])],
            }])

    def create_static_file(self, file_memoryview):
        """
        Creates the static file for testing
        """
        folder_id, = self.static_folder_obj.create([{
            'name': 'test',
            'description': 'Test Folder'
            }])

        return self.static_file_obj.create([{
            'name': 'test.png',
            'folder': folder_id,
            'file_binary': file_memoryview,
            }])[0]

    @with_transaction()
    def test_0010_static_file(self):
        """
        Create a static folder, and a static file
        and check if it can be fetched
        """
        self.setup_defaults()

        file_memoryview = memoryview(b'test-content')
        static_file = self.create_static_file(file_memoryview)

        app = self.get_app()

        with app.test_client() as c:
            rv = c.get('/en/static-file/test/test.png')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'test-content')
            self.assertEqual(rv.headers['Content-Type'], 'image/png')

    @with_transaction()
    def test_0020_static_file_url(self):
        self.setup_defaults()

        file_memoryview = memoryview(b'test-content')
        file = self.create_static_file(file_memoryview)
        self.assertFalse(file.url)

        app = self.get_app()
        with app.test_client() as c:
            rv = c.get('/en/static-file-test')
            self.assertEqual(rv.status_code, 200)
            self.assertTrue('/en/static-file/test/test.png' in
                rv.data.decode('utf-8'))


def suite():
    "Nereid Static File test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestStaticFile))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
