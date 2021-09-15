"""Tests for trading.datasets.utils.id_utils."""
# pylint: disable=missing-class-docstring,missing-function-docstring,line-too-long

from trading.datasets.utils import id_utils


class TestIDUtils:

    def test_reproducable_ids(self):
        assert id_utils.generate_uuid('b') == '8b58a5a75d3658ee8fa41bd2be8f0998'
        assert id_utils.generate_uuid('t') == '46e96b1a23285336903aef0c89812afc'
        assert id_utils.generate_uuid('t') == '46e96b1a23285336903aef0c89812afc'
        assert id_utils.generate_uuid('b') == '8b58a5a75d3658ee8fa41bd2be8f0998'
