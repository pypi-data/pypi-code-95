# -*- coding: utf-8 -*-

from os import path
import inspect

def setup():
    here = path.dirname(path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
    with open(path.join(here, 'sql/mercantile.sql')) as pgmercantile:
        sql = pgmercantile.read()
    from ..common import db
    db.executesql(sql)
    db.commit()
