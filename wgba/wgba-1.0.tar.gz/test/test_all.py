import unittest
import wgba

class TestAll(unittest.TestCase):
    def test_example_bw(self):
        assert 'hg19' in wgba.check_bigwig(path = "test/test.bw")

    def test_example_bed(self):
        assert 'grch38' in wgba.check_bed(path = "test/grch38.bed")
