#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import unittest
from nokogiri.cell import cell

class test_cell(unittest.TestCase):
    def test_スクリプトとしてとして実行したときはラムダ式を返す(self):
        self.assertEqual("<lambda>", cell(globals()).__name__)

if __name__ == '__main__':
    unittest.main()
