# -*- coding: utf-8 -*-


def pretty_title(s, simbol='*', width=100):
    space = " " * int((width - len(s)) / 2)
    line = simbol * width
    print(f"{line}\n{space}{s}{space}\n{line}")
