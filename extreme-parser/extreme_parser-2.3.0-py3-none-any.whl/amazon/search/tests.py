from unittest import TestCase

from extreme_parser.amazon.search.parse import parse_products
from extreme_parser.util import read_file


class ParseTest(TestCase):
    def test_parse_products(self):
        html = read_file("./testdata/1.html")
        products = parse_products(html)
        self.assertEqual(len(products), 69)
