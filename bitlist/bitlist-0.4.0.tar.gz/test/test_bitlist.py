"""Functional unit tests for class and methods.

Test suite containing functional unit tests (based
on bit vector implementations of common arithmetic
operations) for the class and some of its methods.
"""
from unittest import TestCase

from bitlist.bitlist import bitlist

def add(x, y):
    """Bitwise addition algorithm."""
    r = bitlist(0)

    # Upper bound is not inclusive.
    # Use negative indices for big-endian interface.
    carry = 0
    for i in range(1, max(len(x), len(y)) + 1):
        r[-i] = (x[-i] ^ y[-i]) ^ carry
        carry = (x[-i] & y[-i]) | (x[-i] & carry) | (y[-i] & carry)
    r[-(max(len(x), len(y)) + 1)] = carry

    return r

def mul(x, y):
    """Bitwise multiplication algorithm."""
    r = bitlist(0)

    # Upper bound is not inclusive.
    # Use negative indices for big-endian interface.
    for i in range(1, len(x) + 1):
        if x[-i] == 1:
            r = add(r, y)
        y = y << 1

    return r

def exp(x, y):
    """Bitwise exponentiation algorithm."""
    r = bitlist(1)

    # Upper bound is not inclusive.
    # Use negative indices for big-endian interface.
    for i in range(1, len(y) + 1):
        if y[-i] == 1:
            r = mul(r, x)
        x = mul(x, x)

    return r

def div(x, y):
    """Bitwise division algorithm."""
    if y > x:
        return bitlist(0)

    for _ in range(0, len(x)):
        y = y << 1

    t = bitlist(0)
    q = bitlist(0)
    p = bitlist(2**len(x))
    for _ in range(0, len(x)+1):
        if add(t, y) <= x:
            t = add(t, y)
            q = add(q, p)
        y = y >> 1
        p = p >> 1

    return q

class Test_bitlist(TestCase):
    def test_from_integer(self):
        self.assertEqual(bitlist(123), bitlist('1111011'))

    def test_add(self):
        op = lambda a, b: int(add(bitlist(a), bitlist(b)))
        for (x, y) in [(a+b, op(a, b)) for a in range(0, 100) for b in range(0, 100)]:
            self.assertEqual(x, y)

    def test_mul(self):
        op = lambda a, b: int(mul(bitlist(a), bitlist(b)))
        for (x, y) in [(a*b, op(a, b)) for a in range(0, 30) for b in range(0, 30)]:
            self.assertEqual(x, y)

    def test_exp(self):
        op = lambda a, b: int(exp(bitlist(a), bitlist(b)))
        for (x, y) in [(a**b, op(a, b)) for a in range(0, 12) for b in range(0, 4)]:
            self.assertEqual(x, y)

    def test_div(self):
        op = lambda a, b: int(div(bitlist(a), bitlist(b)))
        for (x, y) in [(a//b, op(a, b)) for a in range(0, 12) for b in range(1, 12)]:
            self.assertEqual(x, y)
