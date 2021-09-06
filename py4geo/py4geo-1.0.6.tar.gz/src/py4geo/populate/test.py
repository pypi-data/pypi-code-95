# -*- coding: utf-8 -*-

"""
Still experimental but useful
"""

from .tools import Syncher
from ..tools.tile import Bbox
from .optutils.base import Turbo
import json, geojson
import osm2geojson
from supermercado.burntiles import burn
import mercantile
from tqdm import tqdm

import overpy
# https://overpass-api.de/api/interpreter
# https://overpass.osm.ch/api/interpreter
overpy.Overpass.default_url = "https://overpass.kumi.systems/api/interpreter"

# minlon, minlat, maxlon, maxlat = 6.43798828125, 36.50963615733049, 18.6328125, 47.18971246448421,

edu_query = [
    [{"k": 'amenity', "v": 'college'}],
    [{"k": 'amenity', "v": 'driving_school'}],
    [{"k": 'amenity', "v": 'kindergarten'}],
    [{"k": 'amenity', "v": 'language_school'}],
    [{"k": 'amenity', "v": 'library'}],
    [{"k": 'amenity', "v": 'toy_library'}],
    [{"k": 'amenity', "v": 'music_school'}],
    [{"k": 'amenity', "v": 'school'}],
    [{"k": 'amenity', "v": 'university'}],
]

transp_query = [
    [{"k": "highway", "v": "bus_stop"}],
    [{"k": "public_transport", "v": "platform"}],
    [{"k": "amenity", "v": "parking"}],
    [{"k": "amenity", "v": "parking_space"}],
    [{"k": "amenity", "v": "fuel"}],
    [{"k": "amenity", "v": "bus_station"}]
]

def get_polys(featureCollection):
    for feature in featureCollection['features']:
        if feature['geometry']['type'] == 'MultiPolygon':
            for poly in feature['geometry']['coordinates']:
                xfeature = { "type": "Feature", "properties": {}, "geometry": { "type": "Polygon" } }
                xfeature['geometry']['coordinates'] = poly
                yield xfeature
        elif feature['geometry']['type'] == 'Polygon':
            yield feature

def tile2poly(xyz):
    x, y, z = xyz
    bounds = mercantile.bounds(x, y, z)
    bbox = Bbox(bounds.west, bounds.south, bounds.east, bounds.north)
    poly = bbox.as_gj_polygon
    return poly


def smart_osm_fetch(nome, zoom=14, admin_level=8):

    def flt():
        yield {
            # "bbox": Bbox(minlon, minlat, maxlon, maxlat).osm,
            "query": [[
                {"k": "boundary", "v": "administrative"},
                {"k": "admin_level", "v": f"{admin_level:d}"},
                {"k":"name", "v": f"{nome}"},
                {"k": "wikipedia", "regv": "it:"}
            ]],
            "gtypes": ['relation']
        }

    query = Turbo.build_query(flt)
    turbo = Turbo()
    data_, _ = turbo.__raw_call__(query.encode())
    data = json.loads(data_)
    fc = osm2geojson.json2geojson(data)

    polys = list(get_polys(fc))

    assert len(polys)>0

    tiles = burn(polys, zoom)

    coll = geojson.FeatureCollection(list(map(
        lambda gg: geojson.Feature(geometry=gg),
        map(tile2poly, tiles)
    )))

    for tile in tqdm(tiles):

        download = Syncher(*tile, query=edu_query+transp_query)
        download()
