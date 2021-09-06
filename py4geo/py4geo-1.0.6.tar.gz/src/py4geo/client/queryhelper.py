# -*- coding: utf-8 -*-

from py4geo.client.controllers.tools import _get_buffered_bounds, geomdbset

from ..setup.pgviews import Sqler
from ..common import db

class BaselTileViewsModel(Sqler):
    """ """

    GEOM_VIEW = 'gview'

    def __init__(self, minlon, minlat, maxlon, maxlat, zoom=18, classic=True,
        source_name='__GENERIC__', tags=[], geofield=db.points.geom):
        super(BaselTileViewsModel, self).__init__()
        self.GFIELD = geofield
        self.GTAB = geofield.table
        self.QUERIES = {}

        left, bottom, right, top, resolution = _get_buffered_bounds(
            minlon, minlat, maxlon, maxlat,
            zoom = zoom, classic = classic
        )

        if classic:
            tile_ = f"T_tile({self.GFIELD}, {resolution})"
            tilename_ = f"T_tilename({tile_})"
            # polygon_ = f"T_bounds({tile_})"
            self.get_poly_method = f"T_bounds({self.GEOM_VIEW}.tile)"

            # tilename_ = f"tilename(points.geom, {resolution})"
            # polygon_ = f"bounds_for_tile_indices(ST_Y(tile_indices_for_lonlat(points.geom, {resolution})), ST_X(tile_indices_for_lonlat(points.geom, {resolution})), {resolution})"
        else:
            tile_ = f"h3_geo_to_h3index({self.GFIELD}, {resolution})"
            tilename_ = tile_
            # polygon_ = f"h3_h3index_to_geoboundary(h3_geo_to_h3index(points.geom, {resolution}))"
            self.get_poly_method = f"h3_h3index_to_geoboundary({self.GEOM_VIEW}.tile)"

        self.tile = f"{tile_} as tile"
        self.tilename = f"{tilename_} as tilename"
        self.baseset = geomdbset(
            self.GTAB, left, bottom, right, top,
            source_name=source_name, tags=tags
        )

        self._queries_setup()

    def _queries_setup(self):
        """ """
        raise NotImplementedError()

    def _views_setup(self):
        for name, query in self.QUERIES.items():
            self.init_view(name, query)

    def __enter__(self):

        # Redefine this method

        # First running views setup method
        # self._views_setup()

        # And then setting up your views models
        # e.g. something like:
        # db.define_table(self.GEOM_VIEW,
        #     Field('geom', 'geometry()'),
        #     ...
        #     migrate = False,
        #     redefine = True
        # )

        raise NotImplementedError()

        # Last but not least returning self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.rollback()
