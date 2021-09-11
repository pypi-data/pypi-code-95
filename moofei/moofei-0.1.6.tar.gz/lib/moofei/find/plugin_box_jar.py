#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

import sys
import re
import warnings
from moofei._find import _py

import time
import zipfile 

try:
    from .plugin_box_zip import Plugin_Box_Zip as Plugin_Box_Jar
except ModuleNotFoundError:
    from moofei.find.plugin_box_zip import Plugin_Box_Zip as Plugin_Box_Jar


       
       