# -*- coding: utf-8 -*-

from ..tools import geomdbset, housenumber_components
from ...models import db
from ....tools.tile import tilebbox

import mercantile as mt

def fetch_(minlon=None, minlat=None, maxlon=None, maxlat=None,
    source_name='__GENERIC__', tags=[], zoom_level=None, classic_tile=True,
    filter_geometries = None
):
    """ Returns a multi geometry type FeatureCollection accordingly to given tags
    and bounding box limits.
    minlon               @float :
    minlat               @float :
    maxlon               @float :
    maxlat               @float :
    source_name         @string :
    tags                @dict[] :
    zoom_level         @integer :
    classic_tile       @boolean :
    filter_geometries @callable : filter function for geometries.
    """

    def feats():
        for tab in filter(filter_geometries, (db.points, db.ways, db.polys,)):
            yield geomdbset(
                tab, minlon, minlat, maxlon, maxlat, source_name,
                tags=tags, zoom_level=zoom_level, classic_tile=classic_tile
            ).select()

    return map(lambda row: row.feature, chain(*feats()))

def fetch(minlon=None, minlat=None, maxlon=None, maxlat=None,
    source_name='__GENERIC__', tags=[], zoom_level=None, classic_tile=True,
    filter_geometries = None
):
    return {
        "type": "FeatureCollection",
        "features": list(fetch_(**vars()))
    }

def fetcharound(lon, lat, dist=200, bdim=None, buffer=0, source_name='__GENERIC__',
    tags=[], filter_geometries = None
):
    """ Returns a multi geometry type FeatureCollection accordingly to given tags
    around a center point.
    """
    _extra = {}
    if not bdim is None: _extra['bdim'] = bdim
    bbox = tilebbox(dist=dist, lon=lon, lat=lat, buffer=buffer, **_extra)
    # logger.debug(bbox)
    return fetch(
        minlon = bbox.minx,
        minlat = bbox.miny,
        maxlon = bbox.maxx,
        maxlat = bbox.maxy,
        source_name = source_name,
        tags = tags,
        filter_geometries = filter_geometries
    )

def vtile(x, y, z=18, source_name='__GENERIC__', tags=[], filter_geometries = None):
    """ """
    bounds = mt.bounds(x, y, z)
    feats_ = fetch_(
        minlon = bounds.west,
        minlat = bounds.south,
        maxlon = bounds.east,
        maxlat = bounds.north,
        source_name = source_name,
        tags = tags,
        filter_geometries = filter_geometries
    )
    return dict(features=feats_)

def guess_street(sugg, comune, source=None, limit=10):
    """ """

    if source=='disabled': return dict()

    words = filter(lambda e: e, re.split(";|,|\.|\n| |'", sugg))
    query = (db.housenumbers.housenumber!='') & \
        db.housenumbers.street.contains(list(words), all=True) & \
        db.housenumbers.city.contains(comune)

    if not source is None:
        query &= (db.housenumbers.source_name==source)

    housenumbers = "array_agg(housenumbers.housenumber)"

    res = db(query).select(
        housenumbers,
        db.housenumbers.street,
        db.housenumbers.city,
        db.housenumbers.street.lower(),
        groupby = db.housenumbers.street|db.housenumbers.city,
        orderby = db.housenumbers.street,
        limitby = (0,min((int(limit), 50,)),)
    ).group_by_value(db.housenumbers.street)

    return OrderedDict(
        sorted((k, OrderedDict(map(
            lambda tt: (tt[-1], {k: tt[i] for i,k in enumerate(['number', 'letter', 'color']) if tt[i]}),
            sorted(map(housenumber_components, [r[housenumbers] for r in v][0]))
        )),) \
        # sorted((k, map(housenumber_components, [r[housenumbers] for r in v][0]),) \
            for k,v in res.items()
        )
    )
