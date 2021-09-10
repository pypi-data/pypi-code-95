#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

This module defines several projects that can be used to

"""
import os

from env.environment import *
from env.site_settings import atCNRM
from climaf.classes import cproject, cdef
from climaf.dataloc import dataloc


if atCNRM:
    # Define the root directory and the main tree of data
    root = "/cnrm/amacs/DATA/OBS/netcdf/"
    tree_root = "${root}/${frequency}/${product}/"

    # Define the projects complete tree
    for project in ["AMIP-II", ]:
        cproject("AMIP-II")

    # Define the project
    cproject("ref_obs_cnrm", )

    # Define some default values
    cdef()

    # Define the organisation of the date
    patterns = list()
    dataloc()
