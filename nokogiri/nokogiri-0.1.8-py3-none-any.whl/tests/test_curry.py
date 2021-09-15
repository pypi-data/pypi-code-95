#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import unittest
from nokogiri.curry import curry


def func(a="a", b="b", c="c", d="d", e="e"):
    return f"/{a}/{b}/{c}/{d}/{e}"
F = curry(func)


class test_curry(unittest.TestCase):
    def test_元の関数として実行出来る(self):
        self.assertEqual("/A/b/c/d/e", F("A"))
    def test_文字列の部分適用をgetattrでできる(self):
        self.assertEqual("/A/hoge/fuga/piyo/e", F.hoge.fuga.piyo("A"))
    def test_任意の型の部分適用をgetitemでできる(self):
        self.assertEqual("/A/0/False/None/e", F[0][False][None]("A"))
    def test_名前付き引数への部分適用を_でできる(self):
        self.assertEqual("/A/b/c/d/E", F._(e="E")("A"))

if __name__ == '__main__':
    unittest.main()
