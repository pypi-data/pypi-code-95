#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import unittest
from nokogiri.tqdm_load import tqdm_load

class test_tqdm_load(unittest.TestCase):
    def test_loadしたpickleが保存したものと一致する(self):
        import pickle
        data = "data"
        fname = "/tmp/a"
        with open(fname, "wb") as f:
            pickle.dump(data, f)
        loaded = tqdm_load(fname)
        self.assertEqual(data, loaded)
            

if __name__ == '__main__':
    unittest.main()
