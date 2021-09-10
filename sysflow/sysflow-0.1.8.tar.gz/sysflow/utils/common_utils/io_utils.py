#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : io_utils.py
# Author            : Jiahao Yao
# Email             : jiahaoyao.math@gmail.com
# Date              : 03.16.2021
# Last Modified Date: 03.16.2020
# Last Modified By  : Jiahao Yao
#
# This file is part of the sysflow codebase
# Distributed under MIT license
#
# python basic io utilities
import pyperclip

def cprint(a):
    print(a)
    # safe 
    try: 
        pyperclip.copy(a)
    except: 
        pass