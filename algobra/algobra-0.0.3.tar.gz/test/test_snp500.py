from datetime import datetime
import unittest
import pytest
from algobra.snp500 import ObtainWikiSNP500Symbols


class TestAlgobra(unittest.TestCase):
    def test_snp500_http_request(self):
        symbols = ObtainWikiSNP500Symbols()
        assert isinstance(symbols[0][0], str)
        assert isinstance(symbols[0][-1], datetime)
