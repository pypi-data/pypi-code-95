#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Goddy <goddy@mykg.ai> 2021/9/16
# Desc:

import sys
import random


def main():
    with open('./{}.txt'.format(random.randint(0, 100)), 'w') as f:
        f.write(str(sys.argv))
    print(str(sys.argv))
