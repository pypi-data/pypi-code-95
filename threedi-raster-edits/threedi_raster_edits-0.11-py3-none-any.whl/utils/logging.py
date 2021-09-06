# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:39:17 2019

@author: chris.kerklaan
"""


def show_console_logging():
    import logging
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
