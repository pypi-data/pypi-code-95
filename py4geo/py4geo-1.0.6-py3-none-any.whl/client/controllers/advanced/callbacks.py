# -*- coding: utf-8 -*-

from ..tools import geomdbset

from ....setup.pgviews import Sqler

# WIP

def fetchtiled_(minlon, minlat, maxlon, maxlat, zoom=18, classic=False,
    source_name='__GENERIC__', tags=[]):
    """
    minlon, minlat, maxlon, maxlat @float : Bbox limits;
    zoon @integer : Square tile zoom level or hexagonal tile resolution;
    classic @boolean : Whether to use classic square tiles or Uber H3 hexagonal ones;
    source_name @string : Source name filter;
    tags @dict[] : Tags to be used as filter.

    Returns: Rows
    """

    tab = db.polys
    tiled_geom = 'centroid'

    if classic:
        tile_ = f"T_tile({tab}.{tiled_geom}, {zoom})"
        tilename_ = f"T_tilename({tile_})"
        get_poly_method = "T_bounds(buzz.tile)"
    else:
        tile_ = f"h3_geo_to_h3index({tab}.{tiled_geom}, {zoom})"
        tilename_ = tile_
        get_poly_method = "h3_h3index_to_geoboundary(buzz.tile)"

    dbset = geomdbset(tab, minlon=minlon, minlat=minlat, maxlon=maxlon, maxlat=maxlat,
        source_name=source_name, tags=tags, zoom_level=zoom, classic_tile=classic
    )

    tile = f"{tile_} as tile"
    tilename = f"{tilename_} as tilename"
    count = f"COUNT(0) as count"

    query = dbset._select(
        db.polys.id.min().with_alias('id'),
        tile,
        tilename,
        count,
        orderby = "tilename",
        groupby = "tilename, tile"
    )

    _view_name = 'buzz'

    with Sqler() as sqler:
        sqler.init_view(_view_name,
            f"SELECT {get_poly_method} as geom, * FROM ({query[:-1]}) as {_view_name}",
            materialized = False
        )

        db.define_table(_view_name,
            Field('geom', 'geometry()'),
            Field('tilename'),
            Field('count', 'integer'),
            Field('mrate', 'double'),
            Field.Virtual('feat_geometry', lambda row: wkt.loads(row[_view_name].geom)),
            migrate = False,
            redefine = True
        )

        result = db(db[_view_name]).select()
        sqler.break_io()

    return result
