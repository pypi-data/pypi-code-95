# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)


from idebug import *




def print_title(title):
    width = int(len(title) * 2)
    line = '#' * width
    space = ' ' * int((width - len(title)) / 2)
    print(line)
    print(f"{space}{title}{space}")
    print(line)
