# -*- coding: utf-8 -*-

from py4web import action #, request, abort, redirect, URL, HTTP
from mptools.frameworks.py4web.controller import LocalsOnly

from .... import settings
from ...common import webWrapper
from .callbacks import fetch as fetch_
from .callbacks import guess_street as guess_street_
from .callbacks import fetcharound as fetcharound_

# WARNING!
# Subsequent controller are available from localhost only

@action(f'{settings.PATHROOT}/fetch', method=['GET', 'POST'])
@action.uses(LocalsOnly())
def fetch():
    return webWrapper(fetch_, source_name='osm')()

@action(f'{settings.PATHROOT}/fetcharound', method=['GET', 'POST'])
@action.uses(LocalsOnly())
def fetcharound():
    return webWrapper(fetcharound_, source_name='osm')()

@action(f'{settings.PATHROOT}/guess_street/<sugg>', method=['GET'])
@action.uses(LocalsOnly())
def guess_street(sugg):
    return webWrapper(guess_street_, sugg=sugg, comune='Genova', source='osm')()
