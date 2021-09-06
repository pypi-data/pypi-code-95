# -*- coding: utf-8 -*-

from ..common import db
from .tools import Syncher, get_uri

from py4web import Field
import datetime
import mercantile as mc

now = lambda : datetime.datetime.utcnow()

db.define_table("tracked_tile",
    Field('xtile', 'integer', required=True, notnull=True),
    Field('ytile', 'integer', required=True, notnull=True),
    Field('zoom', 'integer', required=True, notnull=True, default=18),
    Field('uri', required=False, unique=True, notnull=True,
        compute = lambda row: get_uri(row['xtile'], row['ytile'], row['zoom'])
    ),
    # Field('filled', 'boolean', default=False),
    Field('created_on', 'datetime',
        # required = True,
        notnull = True,
        default = now,
        writable = False, readable = True
    ),
    Field('modified_on', 'datetime',
        # required = True, # notnull=True,
        update = now,
        default = now,
        # compute = lambda _=None: now(),
        writable = False, readable = True
    ),
    Field("is_active", "boolean", default=False, readable=False, writable=False),
    # Field('task_id', "reference scheduler_task", notnull=True, requires=None),
    Field.Virtual('feature', lambda row: mc.feature(
        mc.quadkey_to_tile(mc.quadkey(row.tracked_tile.xtile, row.tracked_tile.ytile, row.tracked_tile.zoom)),
        fid = row.tracked_tile.uri,
        props = {'created': row.tracked_tile.created_on, 'updated': row.tracked_tile.modified_on}
    )),
    # Field.Virtual('last_update', lambda row: get_last_update(row.tile.uri))
)


class OsmGetter(object):
    """docstring for OsmGetter."""

    def __init__(self):
        super(OsmGetter, self).__init__()
        self.rec = db.tracked_tile(is_active=False)

    def __enter__(self):
        self.rec.update_record(is_active=True)
        run = Syncher(self.rec.xtile, self.rec.ytile, self.rec.zoom, self.rec.uri)
        run(pgcopy=False)

    def __exit__(self, exc_type, exc_value, traceback):
        if not traceback is None:
            self.rec.update_record(is_active=False)

class OsmUpdater(object):
    """ TODO """
