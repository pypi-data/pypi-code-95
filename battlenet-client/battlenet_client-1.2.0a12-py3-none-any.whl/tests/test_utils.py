try:
    import unittest2 as unittest
except ImportError:
    import unittest as unittest

from battlenet_client.util import *


class UtilityTests(unittest.TestCase):

    def setUp(self):
        super().setUp()

    def test_localize(self):
        lang, country = localize('EnuS')
        self.assertIsInstance(lang, str)
        self.assertIsInstance(country, str)
        self.assertEqual(lang, 'en')
        self.assertEqual(country, 'US')

    def test_localize_wrong_type(self):
        self.assertRaises(TypeError, lambda: localize(1))
        self.assertRaises(TypeError, lambda: localize(['EnuS', 'EngB']))
        self.assertRaises(TypeError, lambda: localize(('EnuS', 'EngB')))
        self.assertRaises(TypeError, lambda: localize({'lang': 'en', 'country': 'US'}))

    def test_localize_wrong_lang_country(self):
        self.assertRaises(ValueError, lambda: localize('zzus'))
        self.assertRaises(ValueError, lambda: localize('enZZ'))

    def test_slugify(self):
        name = slugify('Zul\'jin')
        self.assertEqual(name, 'zuljin')

    def test_slugify_case(self):
        name = slugify('Zul\'jin')
        self.assertTrue(name.islower())

    def test_slugify_type_error(self):
        self.assertRaises(TypeError, lambda: slugify(1))
        self.assertRaises(TypeError, lambda: slugify(['EnuS', 'EngB']))
        self.assertRaises(TypeError, lambda: slugify(('EnuS', 'EngB')))
        self.assertRaises(TypeError, lambda: slugify({'lang': 'en', 'country': 'US'}))

    def test_slugify_no_apostrophe(self):
        name = slugify('Zul\'jin')
        self.assertEqual(name.find('\''), -1)

    def test_slugify_no_space(self):
        name = slugify('Moon Guard')
        self.assertEqual(name.find(' '), -1)

    def test_currency_convertor_positive(self):
        money = currency_convertor(394567)
        self.assertIsInstance(money, (list, tuple))
        self.assertEqual(len(money), 3)
        self.assertEqual(money, (39, 45, 67))

    def test_currency_convertor_zero(self):
        money = currency_convertor('0')
        self.assertIsInstance(money, (list, tuple))
        self.assertEqual(len(money), 3)
        self.assertEqual(money, (0, 0, 0))

    def test_currency_convertor_negative(self):
        self.assertRaises(ValueError, lambda: currency_convertor(-1))

    def test_currency_convertor_wrong_types(self):
        self.assertRaises(TypeError, lambda: currency_convertor([1, 3, 4]))
        self.assertRaises(TypeError, lambda: currency_convertor((1, 3, 4)))
        self.assertRaises(TypeError, lambda: currency_convertor({'g': 1, 's': 3, 'c': 4}))
