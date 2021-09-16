# -*- coding: utf-8 -*-

from ..common import logger
from .optutils.base import Turbo
from . import io
import json
import osm2geojson
from ..tools.tile import Bbox
# from .tile import boxtiles

from tqdm import tqdm
from sys import stdout, getsizeof #, _getframe
from mptools.dataformat import smartbytes
import geojson
from supermercado.burntiles import burn
import mercantile

T = lambda s: s

get_uri = lambda xtile, ytile, zoom: "{xtile:d}/{ytile:d}/{zoom:d}".format(xtile=xtile, ytile=ytile, zoom=zoom)

class barFormat(object):
    """docstring for barFormat."""

    base_fmt = 'desc', 'n', 'rate', 'rate_inv', 'elapsed', 'remaining', 'unit',
    augm_fmt = 'percentage', 'total',

    @staticmethod
    def cast(value):
        """ """
        try:
            return json.loads(value)
        except ValueError:
            return value

    @classmethod
    def template(cls, augm=False):
        fmt = lambda args: 'progress '+'{{{}}}'.format('};{'.join(args))
        return fmt(cls.headers(augm=augm))

    @classmethod
    def headers(cls, augm=True):
        if augm:
            return cls.base_fmt+cls.augm_fmt
        else:
            return cls.base_fmt

    @classmethod
    def parse(cls, *rows):
        """ """
        return filter(lambda shit: shit, map(
            lambda row: dict(zip(cls.headers(), map(cls.cast, filter(lambda v: v.strip(), row.split(';'))))),
            rows
        ))

class MyTqdm(dict):
    """docstring for MyTqdm."""

    def __init__(self, desc, **kwargs):
        super(MyTqdm, self).__init__(**kwargs)
        tot = sum(map(len, kwargs.values()))
        self.tqdm = tqdm(
            desc = desc,
            total = tot,
            # bar_format = barFormat.template(not not tot),
            # file = stdout
        )

    def set_description(self, *args, **kwargs):
        return self.tqdm.set_description(*args, **kwargs)

    def __getattr__(self, key):
        def __main():
            for v in self[key]:
                self.tqdm.update(1)
                yield v
        return [x for x in __main()]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.tqdm.close()

def fetch_and_log_from_osm(query, pgcopy=False):
    """
    query @string : The OSM filter query; Overpass QL or XML.
    """

    # out_task_id = web2py_uuid()
    # plugins.planet.logger.info("### {} >>>".format(out_task_id))
    # plugins.planet.logger.info(query)

    turbo = Turbo()
    data = turbo(query.encode())

    nodes = list(tqdm(
        data.nodes,
        desc = str(T('Downloading nodes from osm')),
        # bar_format = barFormat.template(True if data.nodes else False),
        # file = stdout
    ))

    ways = list(tqdm(
        data.ways,
        desc = str(T('Downloading ways from osm')),
        # bar_format = barFormat.template(True if data.ways else False),
        # file = stdout
    ))

    relations = list(tqdm(
        data.relations,
        desc = str(T('Downloading relations from osm')),
        # bar_format = barFormat.template(True if data.relations else False),
        # file = stdout
    ))

    # dcounter = MyTqdm(
    #     str(T('Saving data to DB')),
    #     nodes = nodes,
    #     ways = ways,
    #     relations = relations
    # )

    # io.osm(dcounter.nodes, dcounter.ways, dcounter.relations, copy=pgcopy)
    io.osm(*map(tqdm, (nodes, ways, relations,)), copy=pgcopy)
    io.db.commit()
    # if request.is_scheduler:
    #     timeLoggerDecorator(plugins.planet.logger)(Put.commit())

    logger.info("Response size: {}".format(smartbytes(getsizeof(data))))
    # plugins.planet.logger.info("<<< {} ###".format(out_task_id[:8]))
    # return out_task_id

class Syncher(object):
    """docstring for Syncher."""
    def __init__(self, xtile, ytile, zoom, uri=None, query=None, gtypes=['node', 'way', 'relation']):
        super(Syncher, self).__init__()
        self.uri = uri or get_uri(xtile, ytile, zoom)
        self.tile = {'x': xtile, 'y': ytile, 'z': zoom}
        tile_bounds = mercantile.bounds(mercantile.quadkey_to_tile(mercantile.quadkey(xtile, ytile, zoom)))
        keys = ('w', 's', 'e', 'n',)
        self.bbox = dict(zip(keys, map(str, (
            tile_bounds.west,
            tile_bounds.south,
            tile_bounds.east,
            tile_bounds.north,
        )))) # minx, miny, maxx, maxy

        if query is None:
            query = [[{"k": "qwertyuiop", "modv": "not", "regv": "."}]]

        self.base_query = {
            'query': query,
            'bbox': self.bbox,
            'gtypes': ['node', 'way', 'relation'],
        }

    def __call__(self, newer_than=None, pgcopy=False):
        """
        newer_than @datetime : Last update timestamp
        """
        if newer_than is None:
            _query = dict(self.base_query)
        else:
            _query = dict(self.base_query,
                newer_than = newer_than.strftime("%Y-%m-%dT%H:%M:%SZ")
            )

        fetch_and_log_from_osm(
            Turbo.build_query(lambda: [_query]),
            pgcopy = pgcopy
        )

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

class OsmShell(object):
    """ Downloads custom data from OSM inside administrative boundary geometry """

    @staticmethod
    def __boundary_filter(*args, **kw):
        def main():
            query = [
                {"k": k, "v": "{}".format(v)} \
            for k,v in kw.items()]+list(args)

            yield {
                # "bbox": Bbox(minlon, minlat, maxlon, maxlat).osm,
                "query": [query],
                "gtypes": ['relation']
            }
        return main

    def __init__(self, name, admin_level=8, zoom=14):
        """
        name         @string : Boiundary name (e.g. Genova, Milano, etc.)
        admin_level @integer : Please refer to https://wiki.openstreetmap.org/wiki/Key:admin_level
            (e.g. 8 Comune or 6 Provincia)
        zoom        @integer : Dimension of tiles used for pixelating the boundary
        """
        super(OsmShell, self).__init__()
        query = Turbo.build_query(self.__boundary_filter(
            {"k": "wikipedia", "regv": "it:"},
            boundary = "administrative",
            admin_level = admin_level,
            name = name
        ))

        turbo = Turbo()
        data_, _ = turbo.__raw_call__(query.encode())
        data = json.loads(data_)
        fc = osm2geojson.json2geojson(data)

        polys = list(get_polys(fc))

        assert len(polys)>0

        self.tiles = burn(polys, zoom)

    @property
    def tileCollection(self):
        """ """
        return geojson.FeatureCollection(list(map(
            lambda gg: geojson.Feature(geometry=gg),
            map(tile2poly, self.tiles)
        )))

    def __call__(self, query=None):
        if query is None:
            # Generic query for downloading everything
            query = [[{"k": "qwertyuiop", "modv": "not", "regv": "."},],]

        for tile in tqdm(self.tiles):
            dbsyncher = Syncher(*tile, query=query)
            dbsyncher()
