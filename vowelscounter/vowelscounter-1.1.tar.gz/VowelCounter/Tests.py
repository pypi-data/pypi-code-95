import unittest
import Counter


class Tests(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(Counter.check_valid("Oscar"), True)
        self.assertEqual(Counter.check_valid(""), False)

    def test_counter(self):
        self.assertEqual(Counter.count_vowels("Hola"), {"a": 1, "o": 1})
        self.assertEqual(Counter.count_vowels(""), "String not Valid")
        self.assertEqual(Counter.count_vowels("W"), {})
