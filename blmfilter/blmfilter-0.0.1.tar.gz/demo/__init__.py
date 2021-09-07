# coding: utf-8
from blmfilter import BloomFilter

demo = [i for i in "abcdefghigklmnopqrstuvwxyz"]
demo_upper = [i for i in "abcdefghigklmnopqrstuvwxyz".upper()]

bf = BloomFilter(1024 * 1024)

for key in demo:
    bf.add(key)

for key in demo:
    assert bf.check(key) == True

for key in demo_upper:
    assert bf.check(key) == False
