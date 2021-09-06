# -*- coding: utf-8 -*-

import h3
import mercantile as mt

from shapely.geometry import Point
from shapely.ops import transform
from shapely.affinity import translate

from pyproj import Transformer, Proj

to3857 = Proj('epsg:3857')
to4326 = lambda x, y: to3857(x, y, inverse=True)

transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

def housenumber_components(hn):
    def loopOlettrs(ll):
        for l in ll:
            if l.isdigit():
                yield l
            else:
                break
    # components = {}
    number = ''.join(loopOlettrs(hn))
    letter, color = '', '',
    if hn.endswith('r'):
        color = 'r'
        letters = hn[len(number):-1].strip()
    elif hn.lower().endswith('rosso'):
        color = 'r'
        letters = hn[len(number):-len('rosso')].strip()
    else:
        letters = hn[len(number):]
    if letters:
        letter = letters
    return number and int(number), letter, color, hn,

def _get_buffered_bounds(minlon, minlat, maxlon, maxlat, zoom=18, classic=True):
    """
    minlon, minlat, maxlon, maxlat @float : Bbox limits;
    zoon @integer : Square tile zoom level or hexagonal tile resolution;
    classic @boolean : Whether to use classic square tiles or Uber H3 hexagonal ones.

    Returns the bbox limits that fits to the tiles touched by the bbox area introduced.
    In this way you are sure to fetch all the inolved points.
    """

    resolution = zoom
    if classic:
        # resolution = zoom
        ultile = mt.tile(minlon, maxlat, zoom)
        left, top = mt.ul(*ultile)
        rbtile = mt.tile(maxlon, minlat, zoom)
        brtile = lambda x, y, z: (x+1, y+1, z)
        right, bottom = mt.ul(*brtile(*rbtile))
        # get_tile = lambda lon, lat: mt.tile(lon, lat, zoom)
    else:
        # ultile = h3.geo_to_h3(maxlat, minlon, zoom)
        # resolution = min(12, zoom)

        ultile = h3.geo_to_h3(maxlat, minlon, resolution)
        ulboundary = h3.h3_to_geo_boundary(ultile)

        P1 = Point(ulboundary[0][::-1])
        P3 = Point(ulboundary[3][::-1])

        P1_3857 = transform(transformer.transform, P1)
        P3_3857 = transform(transformer.transform, P3)

        buffer = P1_3857.distance(P3_3857)

        ul_3857_ = transform(transformer.transform, Point((minlon, maxlat,)))

        ul_3857 = translate(ul_3857_, -buffer, buffer)

        br_3857_ = transform(transformer.transform, Point((maxlon, minlat,)))

        br_3857 = translate(br_3857_, buffer, -buffer)

        left, top = to3857(*ul_3857.coords[0], inverse=True)
        right, bottom = to3857(*br_3857.coords[0], inverse=True)

    return left, bottom, right, top, resolution,

def geomdbset(tab, minlon=None, minlat=None, maxlon=None, maxlat=None,
    source_name='__GENERIC__', tags=[], zoom_level=None, classic_tile=True, geom='geom'):
    """
    tab @pydal.table : DB table to query.
    minlon @float : Bounding box left limit longitude coordinate.
    minlat @float : Bounding box bottom limit latitude coordinate.
    maxlon @float : Bounding box right limit longitude coordinate.
    maxlat @float : Bounding box top limit latitude coordinate.
    source_name @text : Source name (ex.: osm).
    tags @list : List of dictionaries of tags to query for (ex.: [{'amenity': 'bar'}, ...]);
        Geometries resulting from query will must have at least all tags from any dictionary in the list.
    otags : Tags to query for.
        Geometries resulting from query will must be tagged as one of the passed tag.

    """
    basequery = (tab.source_name==source_name)

    if not any(map(lambda cc: cc is None, [minlon, minlat, maxlon, maxlat])):
        if not zoom_level is None:
            minlon, minlat, maxlon, maxlat, _ = _get_buffered_bounds(minlon, minlat, maxlon, maxlat, zoom=zoom_level, classic=classic_tile)
        basequery &= f"ST_Intersects({tab}.{geom}, ST_MakeEnvelope({minlon}, {minlat}, {maxlon}, {maxlat}, 4326))"

    if tags:
        basequery &= "("+" OR ".join([
            " AND ".join([
                f"({tab}.tags->>'{key}' = '{value}')" # .format(key=key, value=value, tab=tab) \
                    for key,value in tt.items()
                ]) for tt in tags
            ])+")"

    # logger.debug(db(basequery)._select())
    return tab._db(basequery)
