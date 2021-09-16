# -*- coding: utf-8 -*-

from .pgfunctions import setup as pgfunctions_setup
from .pgviews import setup as pgviews_setup

def modelsetup():
    pgfunctions_setup()
    pgviews_setup()
