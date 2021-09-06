# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 18:20:00 2020

@author: chris.kerklaan

Raster wrapper used for gis programming
This raster wrapper has as peculiarity that for every function the raster is 
copied/loaded into memory. Hence it always has to be written. I.e.,
it cannot be edited in place.

TODO:
    1. Buffer toevoegen aan een raster --> Misschien iets voor rastergroup ThreeDi
    4. Optimalizeren van blocks
    5. Testen voor dit hele script, testen moeten ook kijken naar geheugen issuses
    
Notes:
    Memory handling:
        1. Numpy calculations are done in tiles as much as possible - speed/memory efficiency
        2. This is also why rasters are edited in place and not returned as new rasters.
        
    Bottleneck:
        1. Rasters are loaded into memory if needed, before the use of functions 
        2. Due to the fact that the rasters are loaded into memory, performance depends on your system
        
    Functions:
        1. Each function handles the object in tiles.
        2. After each function the old file is released and the file is referenced.
        3. Functions outside of the class or either extremely complicated or
           also use multiple external functions
    
    Iterating:
        1. One can iterate over this raster using for tile in raster:
           Blocksizes are optimzed and arrays must be closed after using
           Recommeded code:
               output = raster.copy(shell=True)
               for tile in raster:
                   array = tile
                   # do something with array
                   output.array = array, *tile.location
                   

"""
# System import
import logging
import os
import pathlib

# Third-party imports
import numpy as np
from scipy import ndimage
from osgeo import ogr, gdal, gdal_array

# Local imports
from .vector import Vector
from .dataset import Dataset
from .geotransform import GeoTransform
from .layer import Layer
from .geometry import POLYGON
from .spatial_reference import SpatialReference
from threedi_raster_edits.utils.project import Progress


# GLOBALS
# Drivers
DRIVER_OGR_SHP = ogr.GetDriverByName("Esri Shapefile")
DRIVER_GDAL_GTIFF = gdal.GetDriverByName("GTiff")
DRIVER_GDAL_MEM = gdal.GetDriverByName("MEM")

# Options
WRITE_OPTIONS = ["COMPRESS=DEFLATE", "NUM_THREADS=4", "ZLEVEL=9", "TILED=YES"]

# Gdal/ogr band/field mapping
TYPE_MAPPING = {
    gdal.GDT_Byte: ogr.OFTInteger,
    gdal.GDT_UInt16: ogr.OFTInteger,
    gdal.GDT_Int16: ogr.OFTInteger,
    gdal.GDT_UInt32: ogr.OFTInteger,
    gdal.GDT_Int32: ogr.OFTInteger,
    gdal.GDT_Float32: ogr.OFTReal,
    gdal.GDT_Float64: ogr.OFTReal,
    gdal.GDT_CInt16: ogr.OFTInteger,
    gdal.GDT_CInt32: ogr.OFTInteger,
    gdal.GDT_CFloat32: ogr.OFTReal,
    gdal.GDT_CFloat64: ogr.OFTReal,
}
TYPE_MAPPING_INPUT = {
    float: gdal.GDT_Float32,
    int: gdal.GDT_Int32,
}
# memory counter
_loc_ras = 0

# logging
logger = logging.getLogger(__name__)


class Raster(object):
    def __init__(
        self,
        raster_input,
        name=None,
        blocksize=2048,
        optimize_blocksize=True,
        **kwargs,
    ):
        """Input can either be a path or ds
        Name is only extracted when a path is available, otherwise set name
        kwargs is used for geotransform, spatial_reference and nodata
        """

        if type(raster_input) in [str, pathlib.WindowsPath]:
            ds, name = self.from_path(raster_input, name)
        else:
            ds = raster_input

        if not name:
            name = "No name"

        self.ds = ds
        self.name = name
        self.optimize_blocksize = optimize_blocksize
        self.blocksize = blocksize
        self.return_raster = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_array(cls, array, name=None, **kwargs):
        """import from an array raster array"""
        cls.type = "array"
        if len(array.shape) != 2:
            raise ValueError("limited to 2d arrays, check array.shape")
        return cls(Dataset(array).dataset, name, **kwargs)

    @classmethod
    def from_scratch(
        cls,
        name,
        geotransform,
        columns,
        rows,
        nodata_value=-9999,
        data_type=gdal.GDT_Float32,
        epsg=28992,
    ):
        out, path = create_source(columns, rows, data_type)
        return cls(
            out,
            name=name,
            geotransform=geotransform,
            spatial_reference=epsg,
            nodata_value=nodata_value,
        )

    def from_path(self, path, name):
        if not os.path.exists(path):
            raise ValueError(f"Path does not exist: {path}")

        self.type = "path"
        if not name:
            name = pathlib.Path(path).stem
        return gdal.Open(str(path)), name

    def __iter__(self):
        generator = tile_generator(self.ds, self.optimize_blocksize, self.blocksize)
        for block, location in generator:
            raster = Raster(block, name=self.name)
            raster.location = location
            yield raster

    def __len__(self):
        return len(tile_list(self.ds, self.optimize_blocksize))

    def __setitem__(self, key, value):
        x, y = key
        return self.band.WriteArray(value, x, y)

    def __getitem__(self, key):
        x, y = key
        return self.band.ReadAsArray(x, y, self.w, self.h)

    def __str__(self):
        return self.name

    @property
    def array(self):
        return self.nan(self.band.ReadAsArray())

    @array.setter
    def array(self, value: (np.ndarray, 0, 0)):
        """Takes '(numpy array, x, y)' to set the array"""
        if type(value) != tuple:
            x = 0
            y = 0
            array = value
        else:
            array, x, y = value

        self.band.WriteArray(array, x, y)
        self.band.FlushCache()

    @property
    def geotransform(self):
        return GeoTransform(self.ds.GetGeoTransform())

    @geotransform.setter
    def geotransform(self, value):
        self.ds.SetGeoTransform(value)

    @property
    def nodata_value(self):
        return self.band.GetNoDataValue()

    @nodata_value.setter
    def nodata_value(self, value):
        self.band.SetNoDataValue(value)

    @property
    def spatial_reference(self):
        return SpatialReference(wkt=self.ds.GetProjection())

    @spatial_reference.setter
    def spatial_reference(self, sr_input):
        """input is either epsg or sr object"""
        if type(sr_input) == int:
            self.ds.SetProjection(SpatialReference.from_epsg(sr_input).wkt)
        else:
            self.ds.SetProjection(sr_input.wkt)

    @property
    def metadata(self):
        return self.ds.GetMetadata()

    @metadata.setter
    def metadata(self, metadata: dict):
        self.ds.SetMetadata(metadata)

    @property
    def band(self):
        return self.ds.GetRasterBand(1)

    @property
    def epsg(self):
        return self.spatial_reference.epsg

    @property
    def mask(self):
        return ~np.isnan(self.array)

    @property
    def data_type(self):
        return self.band.DataType

    @property
    def data_type_name(self):
        return gdal.GetDataTypeName(self.data_type)

    @property
    def np_data_type(self):
        return gdal_array.GDALTypeCodeToNumericTypeCode(self.data_type)

    @property
    def columns(self):
        return self.band.XSize

    @property
    def rows(self):
        return self.band.YSize

    @property
    def pixels(self):
        return self.columns * self.rows

    @property
    def resolution(self):
        return {"width": self.geotransform[1], "height": self.geotransform[5]}

    @property
    def extent(self):
        return self.get_extent()

    @property
    def extent_geometry(self):
        return ogr.CreateGeometryFromWkt(POLYGON.format(*self.get_extent()))

    @property
    def minx(self):
        return self.extent[0]

    @property
    def maxx(self):
        return self.extent[1]

    @property
    def miny(self):
        return self.extent[2]

    @property
    def maxy(self):
        return self.extent[3]

    @property
    def width(self):
        return self.maxx - self.minx

    @property
    def height(self):
        return self.maxy - self.miny

    @property
    def size(self):
        return self.rows * self.columns

    @property
    def block_size(self):
        return self.band.GetBlockSize()

    @property
    def settings(self):
        return {
            "spatial_reference": self.spatial_reference,
            "geotransform": self.geotransform,
            "nodata_value": self.nodata_value,
        }

    def load_to_memory(self):
        """loads this datasource to memory, usefull for boosting read array speed"""
        path = loc_dir(mem=True, add=False)
        self.change_source(DRIVER_GDAL_MEM.CreateCopy(path, self.ds), name=self.name)

    def close(self):
        self.ds.FlushCache()
        self.ds = None

    def change_source(self, in_ds, name=None):
        """closes old source and references this object to a new souce"""
        self.ds = None
        self.ds = in_ds
        if name == None:
            self.name = "No name"
        else:
            self.name = name

    def empty_copy(self, rows=None, columns=None, data_type=None, epsg=28992):
        """deprecated"""
        if not rows:
            rows = self.rows
        if not columns:
            columns = self.columns
        if not data_type:
            data_type = self.data_type

        out, path = create_source(columns, rows, data_type)
        empty_raster = Raster(out, name=self.name + " copy", **self.settings)

        return empty_raster

    def copy(self, shell=False, data_type=None):
        if not shell:
            return Raster(
                DRIVER_GDAL_MEM.CreateCopy(loc_dir(mem=True, add=True), self.ds)
            )
        if not data_type:
            data_type = self.data_type

        return Raster.from_scratch(
            self.name,
            self.geotransform,
            self.columns,
            self.rows,
            self.nodata_value,
            data_type,
            self.epsg,
        )

    def replace_nodata(self, nodata_value=-9999, quiet=False):
        """replaces the in-array nodata values in a tiled form"""
        target = self.copy(shell=True)
        pbar = Progress(self.__len__(), f"Replace nodata {self.nodata_value}")
        for tile in self:
            array = tile.array
            array[np.isnan(array)] = nodata_value
            target.array = array, *tile.location
            tile.close()
            pbar.update(quiet)

        target.nodata_value = nodata_value
        self.change_source(target.ds, name=self.name)

    def change_data_type(self, data_type=float):
        """changes the data type of raster using float, int or gdal dt"""
        if data_type in [float, int]:
            data_type = TYPE_MAPPING_INPUT[data_type]
        out, path = create_source(self.columns, self.rows, data_type)
        target = Raster(out, name=self.name, **self.settings)
        target.array = self.array
        self.change_source(target.ds, name=self.name)

    def nan(self, array):
        """returns an np array which the nodata values are set to np.nan"""
        if np.dtype(array.dtype).char in np.typecodes["AllInteger"]:
            array = array.astype(float)
        array[array == self.nodata_value] = np.nan
        return array

    def resize_band(self, width, height):
        self.band.WriteArray(np.full([height, width], np.nan))

    def get_extent(self):
        """returns the extent of the geotransform"""

        transform = self.geotransform
        maxx = transform[0] + self.columns * transform[1] + self.rows * transform[2]

        miny = transform[3] + self.columns * transform[4] + self.rows * transform[5]

        minx = transform[0]
        maxy = transform[3]
        return minx, maxx, miny, maxy

    def set_extent_geom(self):
        x1, x2, y1, y2 = self.get_extent()
        wkt = POLYGON.format(x1=x1, x2=x2, y1=y1, y2=y2)
        self.extent_geom = ogr.CreateGeometryFromWkt(wkt)

    @staticmethod
    def merge(raster_list):
        """takes a list of in memory rasters, returns a single raster
        Should not be in raster object, it is however very practical
        """
        if type(raster_list[0]) == Raster:
            raster_list = [r.ds for r in raster_list]

        path = loc_dir(mem=True).replace(".tif", ".vrt")
        vrt_options = gdal.BuildVRTOptions(resampleAlg="cubic")
        ds = gdal.BuildVRT(path, raster_list, options=vrt_options)
        return Raster(ds)

    def clip(self, vector, quiet=False):
        """clips the raster based on the vector extent,
        if vector is in memory, it used a different method
        """
        if hasattr(vector, "path"):
            return self.clip_path(vector, quiet)
        else:
            return self.clip_memory(vector)

    def clip_path(self, vector, quiet=False):
        """takes a vector_layer or geometry and clips the raster
        deprecated
        """
        logger.debug("Clip using the vector path")

        progress = gdal_progress
        progress.enable("Clip", quiet)

        options = {
            "cutlineDSName": vector.path,
            "cutlineLayer": vector.layer_name,
            "cropToCutline": True,
            "multithread": True,
            "creationOptions": WRITE_OPTIONS,
            "callback": progress.callback,
        }

        ds = gdal.Warp(loc_dir(mem=True), self.ds, **options)
        return Raster(ds, name=self.name)

    def clip_memory(self, vector):
        """different way of clipping, uses more memory, might be faster"""
        mask = Raster(
            vector.rasterize(
                rows=self.rows,
                columns=self.columns,
                geotransform=self.geotransform,
                return_ds=True,
            )
        )

        return self.align(mask, nodata_align=True)

    def reproject(self, epsg, quiet=True):
        progress = gdal_progress
        progress.enable("Reproject", quiet)

        options = {
            "dstSRS": f"EPSG:{epsg}",
            "creationOptions": WRITE_OPTIONS,
            "callback": progress.callback,
        }

        ds = gdal.Warp(loc_dir(mem=True), self.ds, **options)

        if self.return_raster:
            return Raster(ds)
        else:
            self.change_source(ds, name="reprojected")

    def resample(self, x_res, y_res, algorithm=gdal.GRA_NearestNeighbour, quiet=True):
        progress = gdal_progress
        progress.enable("Resample", quiet)

        options = {
            "xRes": x_res,
            "yRes": y_res,
            "resampleAlg": algorithm,
            "creationOptions": WRITE_OPTIONS,
            "callback": progress.callback,
        }

        ds = gdal.Translate(loc_dir(mem=True), self.ds, **options)

        if self.return_raster:
            return Raster(ds)
        else:
            self.change_source(ds, name="resampled")

    def smooth(
        self,
        method="gaussian",
        arguments={"sigma": 1, "mode": "nearest"},
        quiet=False,
    ):
        """
        Smooths a raster based on two methods, returns a raster object
        params:
            method: 'gaussian' or 'perona_malik'
            arguments:
                gaussian:
                    - sigma
                    - mode
                    see https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_filter.html
                perona_malik:
                    - iter
                    - K

        """
        target = self.copy(shell=True)
        if method == "gaussian":
            if not quiet:
                logger.debug(f"Applying gaussian filter with arguments: {arguments}")

            output_array = ndimage.gaussian_filter(
                self.array, output=self.np_data_type, **arguments
            )
        elif method == "perona_malik":
            output_array = perona_malik_filter(self.array, **arguments)

        target.array = output_array

        return target

    def push_vector(
        self,
        vector: Vector,
        value=None,
        field=None,
        set_to_nodata=False,
        quiet=False,
    ):
        """
        Pushes a vector this raster

        Params:
            Vector is a vector object
            Value (optional): pushes this value onto the raster
            Field (optional): pushes this field onto the raster
            set_to_nodata (optional): pushes nodata onto the raster

        """

        if self.epsg != vector.epsg:
            vector = vector.reproject(self.epsg)

        if value == self.nodata_value:
            set_to_nodata = True

        target = self.copy(shell=True)
        nodata = self.nodata_value

        # rasterize vector vector array
        rasterized_vector = Raster(
            vector.rasterize(
                rows=self.rows,
                columns=self.columns,
                geotransform=self.geotransform,
                nodata=nodata,
                field=field,
                return_ds=True,
            )
        )

        # make sure that it loops over the same blocks
        self.optimize_blocksize = False
        rasterized_vector.optimize_blocksize = False

        for raster_tile, vector_tile in zip(self, rasterized_vector):
            array = raster_tile.array
            vector_array = vector_tile.array

            # if no value and field are filled, it is set to nodata?
            if set_to_nodata:
                array[vector_array == 1] = nodata
                target.array = (array, *raster_tile.location)

            elif value:
                array[~np.isnan(vector_array)] = value
                target.array = (array, *raster_tile.location)

            elif field:
                mask = ~np.isnan(vector_array)
                array[mask] = vector_array[mask]
                target.array = (array, *raster_tile.location)

            del array
            del vector_array

        return target

    def push_raster(self, raster, value=None):
        """pushes raster data to object, you can also use a value, rasters should be aligned"""
        target = self.copy(shell=True)
        self.optimize_blocksize = False
        raster.optimize_blocksize = False

        logger.debug("raster - push_raster - start")
        for target_tile, raster_tile in zip(self, raster):
            target_array = target_tile.array
            raster_mask = raster_tile.mask

            if value:
                target_array[raster_mask] = value
            else:
                raster_array = raster_tile.array
                target_array[raster_mask] = raster_array[raster_mask]
            target.array = (target_array, *raster_tile.location)

        del target_array
        del raster_mask
        return target

    def polygonize(
        self,
        field_name="dn",
        layer_name="poly",
        mask_value=None,
        idx=0,
        no_mask=False,
        quiet=True,
    ):
        """polygonizes a raster
        params:
            field_name: field in vector
            layer_name: layer in vector
            mask_value: a value will be set to nodata
            no_mask: also polygonizes nodata
            quiet: if false it shows progress

        """
        polygonize_type = TYPE_MAPPING[self.band.DataType]
        path = loc_dir(ext="shp", mem=True)
        ds_vector = DRIVER_OGR_SHP.CreateDataSource(path)
        layer_vector = ds_vector.CreateLayer(layer_name, srs=self.spatial_reference)
        raster_field = ogr.FieldDefn(field_name, polygonize_type)
        layer_vector.CreateField(raster_field)

        if mask_value is not None:
            logger.debug("loading raster in memory due to mask value edits")
            self.load_to_memory()
            array = self.array
            array[array == mask_value] = self.nodata_value
            self.array = array
            no_mask = False

        band = self.band
        array = self.array

        if no_mask:
            no_data_band = None
        else:
            no_data_band = band.GetMaskBand()

        band.FlushCache()

        if not quiet:
            progress = gdal_progress
            progress.enable("Polygonize", quiet)
            callback = progress.callback
        else:
            callback = None

        if polygonize_type == ogr.OFTReal:
            gdal.FPolygonize(
                band,
                no_data_band,
                layer_vector,
                idx,
                [],
                callback=callback,
            )
        else:
            gdal.Polygonize(
                band,
                no_data_band,
                layer_vector,
                idx,
                [],
                callback=callback,
            )

        return path

    def align(self, template=None, fill_value=None, idw=False, nodata_align=True):
        return align(self, template, fill_value, idw, nodata_align)

    def fill_nodata(
        self,
        search_distance=10,
        smooth_iterations=0,
        max_iterations=10,
        array=None,
        quiet=False,
    ):

        """
        Inverse distance weighting - Fills a raster until all nodata is filled.
        For each iterations one pixel if filled
        Params:
            Search Distance: Maximum distance (in pixels) to search out for values to interpolate
                             This is also the amount of nodata pixels it will fill
            Smooth iterations: Number of smoothing iterations to run after the interpolation
            Max Iterations: Limits the amounts of IDW loops


        return a Raster object
        """

        if not array:
            array = self.array  # nan
        else:
            array = self.nan(array)

        # back to  not np.nan values
        array[np.isnan(array)] = self.nodata_value

        kwargs = self.settings
        kwargs["spatial_reference"] = self.spatial_reference.wkt

        # combine both nans and nodata_values
        fill_mask = array == self.nodata_value
        nan_count = np.count_nonzero(array[fill_mask])

        target = self.copy(shell=True)
        idw_iterations = 0
        while nan_count > 0:
            idw_iterations += 1
            if not quiet:
                logger.debug(f"IDW iteration {idw_iterations}, nan count {nan_count}")

            with Dataset(array, **kwargs) as work:
                work_band = work.GetRasterBand(1)
                mask_band = work_band.GetMaskBand()

                gdal.FillNodata(
                    work_band,
                    mask_band,
                    search_distance,  # search distance
                    smooth_iterations,  # smoothing iterations
                )

            nan_count = np.nansum(array == self.nodata_value)

            if idw_iterations >= max_iterations:
                logger.debug(f"Reached max iterations {max_iterations}")
                break

        if idw_iterations < max_iterations:
            logger.debug("No more nodata left")

        target.array = array
        return target

    def read_point(self, point: ogr.Geometry, nodata_value=-9999):
        """
        Samples points, based on 'raster'.
        input is an ogr geometry
        return a dictionary with sampled values
        """
        # inverse
        p, a, b, q, c, d = self.geotransform
        D = 1 / (a * d - b * c)
        e, f, g, h = d * D, -b * D, -c * D, a * D

        x, y = point.GetX(), point.GetY()
        j = np.int64(e * (x - p) + f * (y - q))
        i = np.int64(g * (x - p) + h * (y - q))

        try:
            array = self.band.ReadAsArray(int(j), int(i), 1, 1).astype(np.float)
            return array[0][0]
        except:
            return nodata_value  # Point outside dem?

    def read_geometry(self, geometry: ogr.Geometry):
        """
        Return numpy array.

        :param inflate: inflate envelope to grid, to make sure that
            the entire geometry is contained in resulting indices.

        If the bounds fall outside the dataset, the result is padded
        with no data values.

        This ingenuity is from raster-tools
        """

        geotransfrom = self.geotransform
        spatial_reference = self.spatial_reference
        nodata_value = self.nodata_value

        x1, y1, x2, y2 = geotransfrom.get_indices(geometry, inflate=True)

        # overlapping bounds
        w, h = self.columns, self.rows
        p1 = min(w, max(0, x1))
        q1 = min(h, max(0, y1))
        p2 = min(w, max(0, x2))
        q2 = min(h, max(0, y2))

        # result array plus a view for what's actually inside datasets
        array = np.full((y2 - y1, x2 - x1), nodata_value, self.np_data_type)
        view = array[q1 - y1 : q2 - y1, p1 - x1 : p2 - x1]

        kwargs = {
            "xoff": p1,
            "yoff": q1,
            "win_xsize": p2 - p1,
            "win_ysize": q2 - q1,
        }
        data = self.band.ReadAsArray(**kwargs)
        index = data != nodata_value
        view[index] = data[index]

        if 0 in view.shape:
            return view

        # not using self.settings due to speed
        kwargs = {
            "spatial_reference": spatial_reference.wkt,
            "geotransform": geotransfrom.shifted(geometry, inflate=True),
            "nodata_value": nodata_value,
        }

        select_2d = np.zeros(view.shape, dtype="u1")
        with Layer(geometry) as layer:
            with Dataset(select_2d[np.newaxis], **kwargs) as dataset:
                gdal.RasterizeLayer(dataset, [1], layer, burn_values=[1])

        if array.shape != select_2d.shape:
            return np.array([0])
        else:
            array_1d = array[select_2d.astype("b1")]

        # determine data or no data
        if array_1d.dtype.kind == "f":
            select_1d = ~np.isclose(array_1d, nodata_value)
        else:
            select_1d = ~np.equal(array_1d, nodata_value)

        return array_1d[select_1d]

    def read(self, geometry: ogr.Geometry):

        """
        Return numpy array or a value
        Functions combines an read_geometry and read_point

        """
        # find indices
        if geometry.GetGeometryType() == ogr.wkbPoint:
            return self.read_point(geometry)
        else:
            return self.read_geometry(geometry)

    def classify(self, new_classes, quiet=True):
        """
        classifies the raster based on a dictionary.
        e.g.,
            new_classes = {raster_value: [new_value]}
        """
        logger.info("start classifying raster")

        target = self.copy(shell=True, data_type=gdal.GDT_Float32)
        pbar = Progress(self.__len__(), "Classifying")
        for tile in self:
            array = tile.array

            if np.isnan(array).all():
                target.array = array, *tile.location
                continue

            codes = np.unique(array[~np.isnan(array)])

            output_array = np.copy(array)
            for code in codes:
                output_array[array == code] = new_classes[code]

            target.array = output_array, *tile.location

            # # Delete array
            del array
            del output_array

            pbar.update(quiet)

        return target

    def write(self, filename, overwrite=True):
        if overwrite:
            if os.path.exists(filename):
                DRIVER_GDAL_GTIFF.Delete(filename)

        ds = DRIVER_GDAL_GTIFF.CreateCopy(filename, self.ds, options=WRITE_OPTIONS)
        ds.GetRasterBand(1).SetNoDataValue(self.nodata_value)
        ds.SetProjection(self.spatial_reference.wkt)
        ds.SetGeoTransform(self.geotransform)
        ds.SetMetadata(self.metadata)
        ds = None

        return


class gdal_progress:
    """tracks gdal fuctions with tqdm
    Usage:
        progress = gdal_progress
        progress.enable("Resample", quiet)

    in function:
        callback = progress.callback
    """

    @classmethod
    def callback(cls, complete, message, unkown):
        cls.pbar.update(round(complete * 100) - cls.pbar.i)

    @classmethod
    def enable(cls, message, quiet=False):
        cls.pbar = Progress(100, message)


def loc_dir(_dir=None, _type="ras", ext="tif", mem=False, add=True):
    """Creates a string to be used in a datasource"""
    global _loc_ras
    if add:
        _loc_ras = _loc_ras + 1

    if mem:
        _dir = "/vsimem"
    return _dir + f"/{_type}_{_loc_ras}.{ext}"


def create_source(columns, rows, data_type):
    """Takes columns, rows and a data_type to create an in memory gdal datasource"""
    path = loc_dir(mem=True, add=True)
    out = DRIVER_GDAL_MEM.Create(
        path,
        columns,
        rows,
        1,
        data_type,
        options=WRITE_OPTIONS,
    )
    return out, path


def moving_window_generator(
    array, row_min=1, row_max=1, column_min=1, column_max=1, quiet=True
):
    """generates a moving window on top of the class"""
    rows, columns = array.shape
    for row in range(rows):
        for column in range(columns):

            # level 2 create window
            bottom = row - row_min
            top = row + row_max
            left = column - column_min
            right = column + column_max

            # window check
            if bottom < 0:
                bottom = 0
            if top > rows:
                top = rows
            if left < 0:
                left = 0
            if right > columns:
                right = columns
            # extract views
            yield array[bottom : top + 1, left : right + 1], (
                bottom,
                top,
                left,
                right,
            ), (row, column)


def optimize_blocksize(dataset, target_pixels=1000000):
    """Takes a band and creates an optimzed blocksize
    1. Blocksizes are at least orginal band block sizes
    2. New blocksizes are a multitude of original sizes
    3. Block size cannot be larger than the raster size
    4. If target pixels are approximated.

    """

    band = dataset.GetRasterBand(1)
    x_blocksize, y_blocksize = band.GetBlockSize()
    total_block_pixels = x_blocksize * y_blocksize
    total_raster_pixels = dataset.RasterXSize * dataset.RasterYSize

    x_optimized = x_blocksize
    y_optimized = y_blocksize

    while total_block_pixels < target_pixels:
        pre_x_optimized = x_optimized
        pre_y_optimized = y_optimized

        # block gets larger with multitude of blocks
        if x_optimized < y_optimized:
            x_optimized += x_blocksize
        else:
            y_optimized += y_blocksize

        # block cannot be larger than total_raster
        total_block_pixels = x_optimized * y_optimized
        if total_block_pixels > total_raster_pixels:
            x_optimized = pre_x_optimized
            y_optimized = pre_y_optimized
            break

    return x_optimized, y_optimized


def tile_list(
    dataset: gdal.Dataset, band_number: int = 1, optimize=True, blocksize=2048
):
    """Takes a gdal ds  and returns a list of coords based on blocks"""
    # band = dataset.GetRasterBand(band_number)
    # x_blocksize, y_blocksize = band.GetBlockSize()
    if optimize:
        x_blocksize, y_blocksize = optimize_blocksize(dataset)
    else:
        x_blocksize = blocksize
        y_blocksize = blocksize

    x_size = dataset.RasterXSize
    y_size = dataset.RasterYSize

    tiles = []
    for x in range(0, x_size, x_blocksize):

        if x + x_blocksize < x_size:
            cols = x_blocksize
        else:
            cols = x_size - x

        for y in range(0, y_size, y_blocksize):

            if y + y_blocksize < y_size:
                rows = y_blocksize
            else:
                rows = y_size - y
            tiles.append((x, y, cols, rows))
    return tiles


def tile_generator(
    dataset: gdal.Dataset,
    optimize: bool = True,
    blocksize=2048,
    band_number: int = 1,
):
    """returns a list of tiles in memory"""
    band = dataset.GetRasterBand(1)
    transform = dataset.GetGeoTransform()
    nodata_value = band.GetNoDataValue()
    projection = dataset.GetProjection()

    for x, y, cols, rows in tile_list(dataset, band_number, optimize, blocksize):
        tile_array = band.ReadAsArray(x, y, cols, rows)
        minx = transform[0] + transform[1] * x
        maxy = transform[3] + transform[5] * y
        tile_gt = (minx, transform[1], 0, maxy, 0, transform[5])
        tile_ds, path = create_source(cols, rows, gdal.GDT_Float32)
        tile_ds.SetGeoTransform(tile_gt)
        tile_ds.SetProjection(projection)
        tile_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
        tile_ds.GetRasterBand(1).WriteArray(tile_array)
        tile_array = None
        yield tile_ds, (x, y)


def align(raster, template=None, fill_value=None, idw=False, nodata_align=True):
    """
    Takes a Raster object and returns a aligned raster.
    Assumes the current location of the rasters is correct
    and a similar pixel size
    params:
        template: raster to which the raster is aligned
        fill_value: if nodata needs to be filled, it will use this fill value
        idw: Uses idw to fill nodata needs
        nodata_align: If checked, nodata is aligned

    """

    # template info
    gtt = template.geotransform
    columns = template.columns
    rows = template.rows

    # coordinate difference
    gti = raster.geotransform
    gtt_x, gtt_y = (gtt[0], gtt[3])
    gti_x, gti_y = (gti[0], gti[3])
    x_dif = (gtt_x - gti_x) / gtt[1]
    y_dif = (gtt_y - gti_y) / abs(gtt[5])

    logger.debug("Padding and deleting raster pixels where needed")

    raster_array = raster.array
    raster_array[np.isnan(raster_array)] = raster.nodata_value

    if x_dif > 0:
        raster_array = raster_array[:, abs(int(x_dif)) :]
        # raster is to much to the left, delete values to the left
    elif x_dif < 0:
        # raster is too much to the right, add values on the left side
        raster_array = np.pad(
            raster_array,
            (
                (0, 0),  # pad upside  # pad downside
                (abs(int(x_dif)), 0),  # pad left side  # pad on the right side
            ),
            constant_values=raster.nodata_value,
        )

    col_dif = columns - raster_array.shape[1]
    if col_dif > 0:
        # add columns, width is too small
        raster_array = np.pad(
            raster_array,
            [
                (0, 0),  # pad upside  # pad downside
                (
                    0,
                    abs(int(col_dif)),
                ),  # pad left side  # pad on the right side
            ],
            constant_values=raster.nodata_value,
        )

    elif col_dif < 0:
        # delete columns
        raster_array = raster_array[:, 0 : raster_array.shape[1] - abs(int(col_dif))]

    # works
    if y_dif > 0:
        # raster is to low
        # add rows on the upside if raster is to low
        raster_array = np.pad(
            raster_array,
            [
                (abs(int(y_dif)), 0),  # pad upside  # pad downside
                (0, 0),  # pad left side  # pad on the right side
            ],
            constant_values=raster.nodata_value,
        )
    elif y_dif < 0:
        # raster is too high
        # delete rows from upside if raster is too hgh
        raster_array = raster_array[abs(int(y_dif)) :, :]

    row_dif = rows - raster_array.shape[0]
    if row_dif > 0:
        raster_array = np.pad(
            raster_array,
            [
                (0, abs(int(row_dif))),  # pad upside  # pad downside
                (0, 0),  # pad left side  # pad on the right side
            ],
            constant_values=raster.nodata_value,
        )

    elif row_dif < 0:
        # raster is too large in height
        raster_array = raster_array[0 : raster_array.shape[0] - abs(int(row_dif)) :, :]

    if nodata_align == True:
        logger.debug("Padding nodata values onto the to be aligned array")

        nodata_index = np.isnan(template.array)
        raster_array[nodata_index] = raster.nodata_value

        if np.sum(raster_array == raster.nodata_value) != np.sum(nodata_index):
            if idw == True:
                pass  # done later in the process

            elif not fill_value == None:
                (values, counts) = np.unique(raster_array, return_counts=True)
                fill_value = values[np.argmax(counts)]
                if fill_value == raster.nodata_value:
                    fill_value = values[np.argmax(counts) - 1]

                raster_array[
                    ~nodata_index & (raster_array == raster.nodata_value)
                ] = fill_value

                logger.debug(
                    f"Padding fill value {fill_value} onto the to be aligned array"
                )

    raster_array[raster_array == raster.nodata_value] = np.nan
    output = template.copy(shell=True)
    output.array = raster_array

    if idw == True:
        logger.debug("Using inverse distance weighting to fill up nodata")
        output.fill_nodata()

    output.name = raster.name

    return output


def perona_malik_filter(data, iter=5, K=5, delta=0.2, method=2, **kwargs):
    """returns a filtered array"""

    dxW = np.array([[0, 0, 0], [1, -1, 0], [0, 0, 0]])
    dxE = np.array([[0, 0, 0], [0, -1, 1], [0, 0, 0]])
    dyN = np.array([[0, 1, 0], [0, -1, 0], [0, 0, 0]])
    dyS = np.array([[0, 0, 0], [0, -1, 0], [0, 1, 0]])

    pm_lambda = np.ones(data.shape) * delta

    k1 = np.ones(data.shape) * (-1.0 / K)
    k2 = np.ones(data.shape) * K * K

    for i in range(iter):

        dI_W = ndimage.filters.convolve(data, dxW)
        dI_E = ndimage.filters.convolve(data, dxE)
        dI_N = ndimage.filters.convolve(data, dyN)
        dI_S = ndimage.filters.convolve(data, dyS)

        if method == 1:

            cW = np.exp(dI_W * dI_W * k1)
            cE = np.exp(dI_E * dI_E * k1)
            cN = np.exp(dI_N * dI_N * k1)
            cS = np.exp(dI_S * dI_S * k1)

        elif method == 2:

            cW = np.ones(data.shape) / (np.ones(data.shape) + (dI_W * dI_W / k2))
            cE = np.ones(data.shape) / (np.ones(data.shape) + (dI_E * dI_E / k2))
            cN = np.ones(data.shape) / (np.ones(data.shape) + (dI_N * dI_N / k2))
            cS = np.ones(data.shape) / (np.ones(data.shape) + (dI_S * dI_S / k2))

        data = data + (pm_lambda * (cN * dI_N + cS * dI_S + cE * dI_E + cW * dI_W))

    return data
