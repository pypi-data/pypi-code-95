# -*- coding: utf-8 -*-
import random
from dkmath.number import base, debase
from dkmath.primes import digitslice


def encrypt(key, value):
    key = eval(key)
    r = random.randrange(debase('1111', 18), debase('hhhh', 18))
    # take a slice of the 109163 digit prime p, starting at r, ending at r+32
    pslice = digitslice(109163, key, r, r+32)
    res = base(r, 18)   # index into prime
    res += base(pslice ^ value, 36)
    return res


def decrypt(key, encrypted_value):
    key = eval(key)
    r = debase(encrypted_value[:4], 18)
    pslice = digitslice(109163, key, r, r+32)
    return pslice ^ debase(encrypted_value[4:], 36)
