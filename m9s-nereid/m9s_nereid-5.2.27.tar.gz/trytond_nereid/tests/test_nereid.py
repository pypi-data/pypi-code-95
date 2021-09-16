# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest

from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite

from .test_auth import TestAuth
from .test_address import TestAddress
from .test_i18n import TestI18N
from .test_static_file import TestStaticFile
from .test_currency import TestCurrency
from .test_routing import TestRouting
from .test_translation import TestTranslation
from .test_country import TestCountry
from .test_website import TestWebsite
from .test_user import TestUser


class NereidTestCase(ModuleTestCase):
    'Test Nereid module for Tryton'
    module = 'nereid'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            NereidTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestAuth))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestAddress))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestI18N))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestStaticFile))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestCurrency))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestRouting))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestTranslation))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestCountry))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestWebsite))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestUser))
    return suite
