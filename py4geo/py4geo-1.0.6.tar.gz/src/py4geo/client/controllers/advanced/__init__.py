# -*- coding: utf-8 -*-

from mptools.frameworks.py4web.controller import LocalsOnly

from .... import settings
from .common import pbfWebWrapper
from .callbacks import vtile_

@action(f'{settings.PATHROOT}/vtile/<xtile:int>/<ytile:int>/<zoom:int>', method=['GET'])
@action.uses(LocalsOnly())
@action.uses(pbfWebWrapper)
def vtile_xyz(xtile, ytile, zoom):
    return pbfWebWrapper(vtile_, x=xtile, y=ytile, z=zoom, source_name='osm')()

@action(f'{settings.PATHROOT}/vtile/<xtile:int>/<ytile:int>', method=['GET','POST'])
@action.uses(LocalsOnly())
@action.uses(pbfWebWrapper)
def vtile_xy(xtile, ytile):
    return pbfWebWrapper(vtile_, x=xtile, y=ytile, source_name='osm')()

@action(f'{settings.PATHROOT}/vtile', method=['GET','POST'])
@action.uses(LocalsOnly())
@action.uses(pbfWebWrapper)
def vtile():
    return pbfWebWrapper(vtile_, source_name='osm')()
