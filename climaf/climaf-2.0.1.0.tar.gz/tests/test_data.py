#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test example to reproduce a bug
"""

from __future__ import unicode_literals, absolute_import, print_function, division

from climaf.api import *


# Clean the cache
craz(force=True)

# Define the datasets
test_dataset = ds(project="CMIP6", variable="tos", model="CNRM-CM6-1", experiment="piControl", period="1850-1859",
                  table="Omon", grid="gn")
ref_dataset = ds(project="ref_climatos", variable="tos", period="1850-1859", product="WOA13-v2")

# Compute and plot the annual means
test_dataset_ANM = clim_average(test_dataset, "ANM")
ref_dataset_ANM = clim_average(ref_dataset, "ANM")
ref_dataset_ANM_regrid = regrid(ref_dataset_ANM, test_dataset_ANM)
diff_datasets_ANM = minus(test_dataset_ANM, ref_dataset_ANM_regrid)
plot_diff_ANM = plot(diff_datasets_ANM)
cshow(plot_diff_ANM)

cshow(plot(diff_regrid(clim_average(test_dataset, "DJF"), clim_average(ref_dataset, "DJF"))))

craz()

# export CLIMAF_CACHE="/cnrm/est/USERS/rigoudyg/NO_SAVE/CESMEP_climaf_cache"
ref = ds(**{'project': 'ref_climatos',
            'product': 'WOA13-v2',
            'frequency': 'annual_cycle',
            'variable': 'tos',
            'table': 'Omon'
            })
test = ds(**{'grid': 'gn',
             'mesh_hgr': '/cnrm/est/COMMON/C-ESM-EP/grids/ORCA1_mesh_hgr.nc',
             'customname': 'piControl',
             'period': '1850-1859',
             'project': 'CMIP6',
             'experiment': 'piControl',
             'frequency': 'monthly',
             'realization': 'r1i1p1f2',
             'variable': 'tos',
             'table': 'Omon',
             'model': 'CNRM-CM6-1',
             'gridfile': '/cnrm/est/COMMON/C-ESM-EP/grids/ORCA1_mesh_zgr.nc'
             })
c = plot(minus(regridn(clim_average(test, "DJF"), cdogrid="r360x180", option="remapdis"),
               regridn(clim_average(ref, "DJF"), cdogrid="r360x180", option="remapdis")),
         color='temp_19lev',
         colors='-10 -8 -6 -5 -4 -3 -2 -1 -0.5 0 0.5 1 2 3 4 5 6 8 10',
         contours=1,
         focus='ocean',
         gsnCenterString='tos',
         gsnLeftString='1850-1859',
         gsnRightString='DJF',
         gsnStringFontHeightF=0.019,
         mpCenterLonF=200,
         offset=0,
         options='gsnAddCyclic=True',
         title='piControl (vs WOA13-v2)',
         units='degC')
cshow(c)
# NOK
ncview(regridn(clim_average(test, "DJF"), cdogrid="r360x180", option="remapdis"))
# NOK
ncview(clim_average(test, "DJF"))
# OK
ncview(test)

# Revider le cache et re-tester...


