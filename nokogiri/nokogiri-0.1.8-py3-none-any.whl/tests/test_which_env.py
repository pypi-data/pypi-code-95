#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import unittest
from nokogiri.which_env import which_env

class test_which_env(unittest.TestCase):
    def test_スクリプトとしてとして実行したときNOIPYTHONを返す(self):
        self.assertEqual(which_env.NOIPYTHON, which_env())

if __name__ == '__main__':
    unittest.main()
