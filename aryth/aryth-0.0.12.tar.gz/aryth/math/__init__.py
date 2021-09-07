from math import floor, log10


def int_exp(x): return floor(log10(abs(x)))


def is_positive(x): return x == abs(x)


def near(x, y, epsilon): return abs(x - y) < epsilon


def round_d1(x): return round(x * 10) / 10


def round_d2(x): return round(x * 100) / 100


def round_d3(x): return round(x * 1000) / 1000


def round_d4(x): return round(x * 10000) / 10000
