# -*- coding: utf-8 -*-

from mptools.dbutils.wiz import Wiz

from .. import settings

def initdb():
    dbwiz = Wiz(path = settings.DB_FOLDER, cache = None)
    dbwiz.collect(settings.DB_URI, 'postgis', 'fuzzystrmatch', 'pgh3')
    dbwiz.setup()
    return dbwiz
