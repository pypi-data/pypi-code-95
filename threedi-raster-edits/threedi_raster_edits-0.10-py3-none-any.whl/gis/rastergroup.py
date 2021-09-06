# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 17:02:45 2021

@author: chris.kerklaan

#TODO:
    1. Write checks

Bug:
    Maximum extentn cannot be written
"""
# First-party imports
import logging

# Third-party imports
import numpy as np
from osgeo import gdal

# local imports
from .raster import Raster

from threedi_raster_edits.utils.project import Progress

# GLOBALS
logger = logging.getLogger(__name__)


class RasterGroup(object):
    """input is list of Raster objects,
    Params:
        align_extent: if set to True, all will be alligned to the first raster

    Message:
        check if data is aligned, is it is not request to run data aligning
        align_data: if set to True, data/nodata will also be aligned

    Note:
        input has to be aligned to be able to do calculations

    """

    def __init__(
        self,
        rasters: list,
        epsg=28992,
        nodata=-9999,
        data_type=gdal.GDT_Float32,
        np_data_type="f4",
    ):
        self.rasters = rasters
        self.names = [raster.name for raster in self.rasters]
        self.nodata = nodata
        self.epsg = epsg
        self.data_type = data_type
        self.np_data_type = np_data_type

        for name, raster in zip(self.names, self.rasters):
            setattr(self, name, raster)

    def __iter__(self):
        for raster in self.rasters:
            yield raster

    def __getitem__(self, name):
        return self.rasters[self.names.index(name)]

    def __setitem__(self, name, value):
        """without alignemnt"""
        if name in self.names:
            self.rasters[self.names.index(name)] = value
        else:
            self.rasters.append(value)
            self.names.append(name)

        setattr(self, name, value)

    @property
    def count(self):
        return len(self.rasters)

    def check_alignment(self, count_nodata=True):
        logger.info("checking the alignment of the rasters")
        return check_alignment(self.rasters, count_nodata)

    def get_maximum_extent(self):
        if not hasattr(self, "maximum_extent"):
            self.maximum_extent = max_template(self.rasters)

    def align(self, index=0, use_maximum_extent=False, count_nodata=True):
        """aligns all rasters based on index"""
        logger.info("Aligning all rasters")

        if use_maximum_extent:
            self.get_maximum_extent()

            align_raster = self.maximum_extent
            rasters = self.rasters
        else:
            align_raster = self.rasters[index]
            rasters = [r for i, r in enumerate(self.rasters) if i != index]

        aligned_rasters = [r.align(align_raster, nodata_align=False) for r in rasters]

        if not use_maximum_extent:
            aligned_rasters.insert(index, align_raster)

        self.rasters = aligned_rasters

    def merge(self):
        """merges the rasters based on the maximum extent
        loops over every tile and adds data on top of the nodata of the other
        """
        logger.info("start merging")

        # they all must be align, have the same extent an the same nodata value
        self.get_maximum_extent()
        self.align(use_maximum_extent=True)
        for raster in self.rasters:
            raster.optimize_blocksize = False

        pbar = Progress(raster.__len__(), "Merging")

        target = self.rasters[0].copy()
        for tiles in zip(*tuple(self.rasters)):
            tile_array = tiles[0].array

            for tile in tiles[1:]:
                mask = np.isnan(tile_array)
                tile_array[mask] = tile.array[mask]

            pbar.update()
            target.array = tile_array, *tile.location

        return target

    def insert(self, raster: Raster):
        logger.info(f"Inserting a {raster.name} into the group")
        align_raster = self.rasters[0]
        raster.align(align_raster, nodata_align=False)
        self.rasters.append(raster)

    def clip(self, vector):
        """clips all available rasters to the vector file"""
        for raster in self:
            logger.debug(f"Clipping {raster.name}")
            clipped = raster.clip(vector)
            self[raster.name] = clipped


def check_alignment(raster_list, count_nodata=True):
    """checks data/nodata alignemnt and extent alignment"""
    dem = raster_list[0]

    output = {
        "extent": {},
        "counts": {},
        "location": {},
        "errors": [],
        "to_be_aligned": [],
    }
    for raster in raster_list:
        # extent
        if (raster.columns, raster.rows) != (dem.columns, dem.rows):
            msg = f"{raster.name} has unqual columns and rows "
            logger.debug(msg)
            output["errors"].append(("extent", msg))
            if not raster.name in output["to_be_aligned"]:
                output["to_be_aligned"].append(raster.name)

        output["extent"][raster.name] = {
            "rows": raster.rows,
            "columns": raster.columns,
        }
        if count_nodata:
            # data/nodata
            output["counts"][raster.name] = count_data_nodata(raster)

        # location
        if raster.geotransform != dem.geotransform:
            msg = f"{raster.name} has not a similar geotransform as the first raster"
            logger.debug(msg)
            output["errors"].append(("location", msg))
            if not raster.name in output["to_be_aligned"]:
                output["to_be_aligned"].append(raster.name)

        output["location"][raster.name] = raster.geotransform

    for key, values in output["counts"].items():
        if values != output["counts"][dem.name]:
            msg = f"{key} pixel data/nodata count not equal"
            logger.debug(msg)
            output["errors"].append(("counts", msg))
            if not key in output["to_be_aligned"]:
                output["to_be_aligned"].append(key)

    if len(output["errors"]) == 0:
        logger.debug("RasterGroup - Check alignment found no problems")

    return output


def count_data_nodata(raster):
    """input array has np.nan as nodata"""
    count_data = 0
    count_nodata = 0
    raster.optimize_blocksize = False
    for data in raster:
        arr = data.array
        total_size = arr.size
        add_cnt_nodata = np.count_nonzero(np.isnan(arr))
        add_cnt_data = total_size - add_cnt_nodata
        count_nodata += add_cnt_nodata
        count_data += add_cnt_data
        del arr
    return count_data, count_nodata


def max_template(rasters=[Raster, Raster], resolution=None):
    """Takes a list of Raster objects and returns the largest template
    Note that the resolution of the first raster is taken, if not overwritten
    by the resolution param.
    """

    x_min = 1e31
    x_max = -1e31
    y_min = 1e31
    y_max = -1e31

    if resolution == None:
        resolution = rasters[0].resolution["width"]

    for raster in rasters:

        gtt = raster.geotransform
        # xmin
        if gtt[0] < x_min:
            x_min = gtt[0]

        # xmax
        if gtt[0] + (raster.rows * gtt[1]) > x_max:
            x_max = gtt[0] + (raster.rows * gtt[1])

        # ymax
        if gtt[3] > y_max:
            y_max = gtt[3]

        # ymin
        if gtt[3] + (raster.columns * gtt[5]) < y_min:
            y_min = gtt[3] + (raster.columns * gtt[5])

    rows = (y_max - y_min) / resolution
    columns = (x_max - x_min) / resolution
    template = Raster.from_array(np.zeros((int(columns), int(rows))))
    template.geotransform = (x_min, resolution, 0.0, y_max, 0.0, -resolution)
    template.nodata_value = -9999
    template.spatial_reference = raster.epsg

    return template
