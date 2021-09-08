# -*- coding: utf-8 -*-

# geoarray, A fast Python interface for image geodata - either on disk or in memory.
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import warnings
from pkgutil import find_loader
from collections import OrderedDict
from copy import copy, deepcopy
from typing import Union, Optional  # noqa F401

import numpy as np
from osgeo import gdal, gdal_array, gdalnumeric
from shapely.geometry import Polygon
from shapely.wkt import loads as shply_loads
# dill -> imported when dumping GeoArray

from py_tools_ds.convenience.object_oriented import alias_property
from py_tools_ds.geo.coord_calc import get_corner_coordinates
from py_tools_ds.geo.coord_grid import snap_bounds_to_pixGrid
from py_tools_ds.geo.coord_trafo import mapXY2imXY, imXY2mapXY, transform_any_prj, reproject_shapelyGeometry
from py_tools_ds.geo.projection import prj_equal, WKT2EPSG, EPSG2WKT, isLocal, CRS
from py_tools_ds.geo.raster.conversion import raster2polygon
from py_tools_ds.geo.vector.topology \
    import get_footprint_polygon, polyVertices_outside_poly, fill_holes_within_poly
from py_tools_ds.geo.vector.geometry import boxObj
from py_tools_ds.io.raster.gdal import get_GDAL_ds_inmem
from py_tools_ds.numeric.numbers import is_number
from py_tools_ds.numeric.array import get_array_tilebounds

#  internal imports
from .subsetting import get_array_at_mapPos
from .metadata import GDAL_Metadata

__author__ = 'Daniel Scheffler'


class GeoArray(object):
    """A class providing a fast Python interface for geodata - either on disk or in memory.

    GeoArray can be instanced with a file path or with a numpy array and the corresponding geoinformation. Instances
    can always be indexed and sliced like normal numpy arrays, no matter if it has been instanced from file or from an
    in-memory array. GeoArray provides a wide range of geo-related attributes belonging to the dataset as well as
    some functions for quickly visualizing the data as a map, a simple image or an interactive image.
    """

    def __init__(self, path_or_array, geotransform=None, projection=None, bandnames=None, nodata=None, basename='',
                 progress=True, q=False):
        # type: (Union[str, np.ndarray, GeoArray], tuple, str, list, float, str, bool, bool) -> None
        """Get an instance of GeoArray.

        :param path_or_array:   a numpy.ndarray or a valid file path
        :param geotransform:    GDAL geotransform of the given array or file on disk
        :param projection:      projection of the given array or file on disk as WKT string
                                (only needed if GeoArray is instanced with an array)
        :param bandnames:       names of the bands within the input array, e.g. ['mask_1bit', 'mask_clouds'],
                                (default: ['B1', 'B2', 'B3', ...])
        :param nodata:          nodata value
        :param basename:        a short base name of the dataset (e.g., used in some status messages)
        :param progress:        show progress bars (default: True)
        :param q:               quiet mode (default: False)
        """
        if not (isinstance(path_or_array, (str, np.ndarray, GeoArray)) or
           issubclass(getattr(path_or_array, '__class__'), GeoArray)):
            raise ValueError("%s parameter 'arg' takes only string, np.ndarray or GeoArray(and subclass) instances. "
                             "Got %s." % (self.__class__.__name__, type(path_or_array)))

        if path_or_array is None:
            raise ValueError("The %s parameter 'path_or_array' must not be None!" % self.__class__.__name__)

        if isinstance(path_or_array, str):
            assert ' ' not in path_or_array, "The given path contains whitespaces. This is not supported by GDAL."

            if not os.path.exists(path_or_array) and not path_or_array.startswith('/vsi'):
                raise FileNotFoundError(path_or_array)

        if isinstance(path_or_array, GeoArray) or issubclass(getattr(path_or_array, '__class__'), GeoArray):
            self.__dict__ = path_or_array.__dict__.copy()
            self._initParams = dict([x for x in locals().items() if x[0] != "self"])
            self.geotransform = geotransform or self.geotransform
            self.projection = projection or self.projection
            self.bandnames = bandnames or list(self.bandnames.keys())
            self.basename = basename or self.basename
            self._nodata = nodata if nodata is not None else self._nodata
            self.progress = False if progress is False else self.progress
            self.q = q or self.q

        else:
            self._initParams = dict([x for x in locals().items() if x[0] != "self"])
            self.arg = path_or_array
            self._arr = path_or_array if isinstance(path_or_array, np.ndarray) else None
            self.filePath = path_or_array if isinstance(path_or_array, str) and path_or_array else None
            basename_default = os.path.splitext(os.path.basename(self.filePath))[0] if not self.is_inmem else 'IN_MEM'
            self.basename = basename or basename_default
            self.progress = progress
            self.q = q
            self._arr_cache = None  # dict containing key 'pos' and 'arr_cached'
            self._geotransform = None
            self._projection = None
            self._shape = None
            self._dtype = None
            self._nodata = nodata
            self._mask_nodata = None
            self._mask_baddata = None
            self._footprint_poly = None
            self._gdalDataset_meta_already_set = False
            self._metadata = None
            self._bandnames = None

            if bandnames:
                self.bandnames = bandnames  # use property in order to validate given value
            if geotransform:
                self.geotransform = geotransform  # use property in order to validate given value
            if projection:
                self.projection = projection  # use property in order to validate given value

            if self.filePath:
                self.set_gdalDataset_meta()

            if 'nodata' in self._initParams and self._initParams['nodata'] is not None:
                self._validate_nodataVal()

    def _validate_nodataVal(self):
        """Check if a given nodata value is within the valid value range of the data type."""
        _nodata = self._initParams['nodata']

        if np.issubdtype(self.dtype, np.integer):
            dt_min, dt_max = np.iinfo(self.dtype).min, np.iinfo(self.dtype).max
        elif np.issubdtype(self.dtype, np.floating):
            dt_min, dt_max = np.finfo(self.dtype).min, np.finfo(self.dtype).max
        else:
            return

        if not dt_min <= _nodata <= dt_max:
            raise ValueError("The given no-data value (%s) is out range for data type %s."
                             % (self._initParams['nodata'], str(np.dtype(self.dtype))))

    @property
    def arr(self):
        return self._arr

    @arr.setter
    def arr(self, ndarray):
        assert isinstance(ndarray, np.ndarray), "'arr' can only be set to a numpy array! Got %s." % type(ndarray)
        # assert ndarray.shape == self.shape, "'arr' can only be set to a numpy array with shape %s. Received %s. " \
        #                                    "If you need to change the dimensions, create a new instance of %s." \
        #                                    %(self.shape, ndarray.shape, self.__class__.__name__)
        #  THIS would avoid warping like this: geoArr.arr, geoArr.gt, geoArr.prj = warp(...)

        if ndarray.shape != self.shape:
            self.flush_cache()  # the cached array is not useful anymore

        self._arr = ndarray
        self._dtype = ndarray.dtype
        self._shape = ndarray.shape

    @property
    def bandnames(self):
        if self._bandnames and len(self._bandnames) == self.bands:
            return self._bandnames
        else:
            del self.bandnames  # runs deleter which sets it to default values
            return self._bandnames

    @bandnames.setter
    def bandnames(self, list_bandnames):
        # type: (list) -> None

        if list_bandnames:
            if not isinstance(list_bandnames, list):
                raise TypeError("A list must be given when setting the 'bandnames' attribute. "
                                "Received %s." % type(list_bandnames))
            if len(list_bandnames) != self.bands:
                raise ValueError('Number of given bandnames does not match number of bands in array.')
            if len(list(set([type(b) for b in list_bandnames]))) != 1 or not isinstance(list_bandnames[0], str):
                raise ValueError("'bandnames must be a set of strings. Got other datatypes in there.'")

            bN_dict = OrderedDict((band, i) for i, band in enumerate(list_bandnames))

            if len(bN_dict) != self.bands:
                raise ValueError('Bands must have unique names. Received band list: %s' % list_bandnames)

            self._bandnames = bN_dict

            try:
                self.metadata.band_meta['band_names'] = list_bandnames
            except AttributeError:
                # in case self._metadata is None
                pass
        else:
            del self.bandnames

    @bandnames.deleter
    def bandnames(self):
        self._bandnames = OrderedDict(('B%s' % band, i) for i, band in enumerate(range(1, self.bands + 1)))
        if self._metadata is not None:
            self.metadata.band_meta['band_names'] = list(self._bandnames.keys())

    @property
    def is_inmem(self):
        """Check if associated image array is completely loaded into memory."""
        return isinstance(self.arr, np.ndarray)

    @property
    def shape(self):
        """Get the array shape of the associated image array."""
        if self.is_inmem:
            return self.arr.shape
        else:
            if self._shape:
                return self._shape
            else:
                self.set_gdalDataset_meta()
                return self._shape

    @property
    def ndim(self):
        """Get the number dimensions of the associated image array."""
        return len(self.shape)

    @property
    def rows(self):
        """Get the number of rows of the associated image array."""
        return self.shape[0]

    @property
    def columns(self):
        """Get the number of columns of the associated image array."""
        return self.shape[1]

    cols = alias_property('columns')

    @property
    def bands(self):
        """Get the number of bands of the associated image array."""
        return self.shape[2] if len(self.shape) > 2 else 1

    @property
    def dtype(self):
        """Get the numpy data type of the associated image array."""
        if self.is_inmem:
            return self.arr.dtype
        else:
            if self._dtype:
                return self._dtype
            else:
                self.set_gdalDataset_meta()
                return self._dtype

    @property
    def geotransform(self):
        """Get the GDAL GeoTransform of the associated image, e.g., (283500.0, 5.0, 0.0, 4464500.0, 0.0, -5.0)."""
        if self._geotransform:
            return self._geotransform
        elif not self.is_inmem:
            self.set_gdalDataset_meta()
            return self._geotransform
        else:
            return [0, 1, 0, 0, 0, -1]

    @geotransform.setter
    def geotransform(self, gt):
        # type: (Union[list, tuple]) -> None
        assert isinstance(gt, (list, tuple)) and len(gt) == 6,\
            'geotransform must be a list with 6 numbers. Got %s.' % str(gt)

        for i in gt:
            assert is_number(i), "geotransform must contain only numbers. Got '%s' (type: %s)." % (i, type(i))

        self._geotransform = gt

    gt = alias_property('geotransform')

    @property
    def xgsd(self):
        """Get the X resolution in units of the given or detected projection."""
        return self.geotransform[1]

    @property
    def ygsd(self):
        """Get the Y resolution in units of the given or detected projection."""
        return abs(self.geotransform[5])

    @property
    def xygrid_specs(self):
        """Get the specifications for the X/Y coordinate grid.

        This returns for example [[15,30], [0,30]] for a coordinate
        with its origin at X/Y[15,0] and a GSD of X/Y[15,30].
        """
        def get_grid(gt, xgsd, ygsd): return [[gt[0], gt[0] + xgsd], [gt[3], gt[3] - ygsd]]
        return get_grid(self.geotransform, self.xgsd, self.ygsd)

    @property
    def projection(self):
        """Get the projection of the associated image.

        Setting the projection is only allowed if GeoArray has been instanced from memory or the associated file on
        disk has no projection.
        """
        if self._projection:
            return self._projection
        elif not self.is_inmem:
            self.set_gdalDataset_meta()
            return self._projection  # or "LOCAL_CS[\"MAP\"]"
        else:
            return ''  # '"LOCAL_CS[\"MAP\"]"

    @projection.setter
    def projection(self, prj):
        # type: (str) -> None
        self._projection = prj

    prj = alias_property('projection')

    @property
    def epsg(self):
        # type: () -> int
        """Get the EPSG code of the projection of the GeoArray."""
        return WKT2EPSG(self.projection)

    @epsg.setter
    def epsg(self, epsg_code):
        # type: (int) -> None
        self.projection = EPSG2WKT(epsg_code)

    @property
    def box(self):
        mapPoly = get_footprint_polygon(get_corner_coordinates(gt=self.geotransform, cols=self.columns, rows=self.rows))
        return boxObj(gt=self.geotransform, prj=self.projection, mapPoly=mapPoly)

    @property
    def is_map_geo(self):
        # type: () -> bool
        """Return 'True' if the image has a valid geoinformation with map instead of image coordinates."""
        return all([self.gt, list(self.gt) != [0, 1, 0, 0, 0, -1], self.prj])

    @property
    def nodata(self):
        """Get the nodata value of the GeoArray instance.

        If GeoArray has been instanced with a file path the metadata of the file on disk is checked for an existing
        nodata value. Otherwise (if no value is exlicitly given during object instanciation) an automatic detection
        based on 3x3 windows at each image corner is run that analyzes the mean and standard deviation of these windows.
        """
        if self._nodata is not None:
            return self._nodata
        else:
            # try to get nodata value from file
            if not self.is_inmem:
                self.set_gdalDataset_meta()
            if self._nodata is None:
                self.find_noDataVal()
                if self._nodata == 'ambiguous':
                    warnings.warn('Nodata value could not be clearly identified. It has been set to None.')
                    self._nodata = None
                else:
                    if self._nodata is not None and not self.q:
                        print("Automatically detected nodata value for %s '%s': %s"
                              % (self.__class__.__name__, self.basename, self._nodata))
            return self._nodata

    @nodata.setter
    def nodata(self, value):
        # type: (Optional[bool, int, float]) -> None
        if isinstance(value, np.bool_):
            value = bool(value)
        elif isinstance(value, np.integer):
            value = int(value)
        elif isinstance(value, np.floating):
            value = float(value)

        self._nodata = value

        if self._metadata and value is not None:
            self.metadata.global_meta.update({'data_ignore_value': str(value)})

    @property
    def mask_nodata(self):
        """Get the nodata mask of the associated image array. It is generated based on all image bands."""
        if self._mask_nodata is not None:
            return self._mask_nodata
        else:
            self.calc_mask_nodata()  # sets self._mask_nodata
            return self._mask_nodata

    @mask_nodata.setter
    def mask_nodata(self, mask):
        """Set the bad data mask.

        :param mask:    Can be a file path, a numpy array or an instance o GeoArray.
        """
        if mask is not None:
            from .masks import NoDataMask
            geoArr_mask = NoDataMask(mask, progress=self.progress, q=self.q)
            geoArr_mask.gt = geoArr_mask.gt if geoArr_mask.gt not in [None, [0, 1, 0, 0, 0, -1]] else self.gt
            geoArr_mask.prj = geoArr_mask.prj if geoArr_mask.prj else self.prj
            imName = "the %s '%s'" % (self.__class__.__name__, self.basename)

            assert geoArr_mask.bands == 1, \
                'Expected one single band as nodata mask for %s. Got %s bands.' % (self.basename, geoArr_mask.bands)
            assert geoArr_mask.shape[:2] == self.shape[:2], 'The provided nodata mask must have the same number of ' \
                                                            'rows and columns as the %s itself.' % imName
            assert geoArr_mask.gt == self.gt, \
                'The geotransform of the given nodata mask for %s must match the geotransform of the %s itself. ' \
                'Got %s.' % (imName, self.__class__.__name__, geoArr_mask.gt)
            assert not geoArr_mask.prj or prj_equal(geoArr_mask.prj, self.prj), \
                'The projection of the given nodata mask for the %s must match the projection of the %s itself.' \
                % (imName, self.__class__.__name__)

            self._mask_nodata = geoArr_mask
        else:
            del self.mask_nodata

    @mask_nodata.deleter
    def mask_nodata(self):
        self._mask_nodata = None

    @property
    def mask_baddata(self):
        """Return the bad data mask.

        Note: The mask must be explicitly set to a file path or a numpy array before.
        """
        return self._mask_baddata

    @mask_baddata.setter
    def mask_baddata(self, mask):
        """Set bad data mask.

        :param mask:    Can be a file path, a numpy array or an instance o GeoArray.
        """
        if mask is not None:
            from .masks import BadDataMask
            geoArr_mask = BadDataMask(mask, progress=self.progress, q=self.q)
            geoArr_mask.gt = geoArr_mask.gt if geoArr_mask.gt not in [None, [0, 1, 0, 0, 0, -1]] else self.gt
            geoArr_mask.prj = geoArr_mask.prj if geoArr_mask.prj else self.prj
            imName = "the %s '%s'" % (self.__class__.__name__, self.basename)

            assert geoArr_mask.bands == 1, \
                'Expected one single band as bad data mask for %s. Got %s bands.' % (self.basename, geoArr_mask.bands)
            assert geoArr_mask.shape[:2] == self.shape[:2], 'The provided bad data mask must have the same number of ' \
                                                            'rows and columns as the %s itself.' % imName
            assert geoArr_mask.gt == self.gt, \
                'The geotransform of the given bad data mask for %s must match the geotransform of the %s itself. ' \
                'Got %s.' % (imName, self.__class__.__name__, geoArr_mask.gt)
            assert prj_equal(geoArr_mask.prj, self.prj), \
                'The projection of the given bad data mask for the %s must match the projection of the %s itself.' \
                % (imName, self.__class__.__name__)

            self._mask_baddata = geoArr_mask
        else:
            del self.mask_baddata

    @mask_baddata.deleter
    def mask_baddata(self):
        self._mask_baddata = None

    @property
    def footprint_poly(self):
        """Get the footprint polygon of the associated image array (shapely.geometry.Polygon)."""
        # FIXME should return polygon in image coordinates if no projection is available
        if self._footprint_poly is None:
            assert self.mask_nodata is not None, 'A nodata mask is needed for calculating the footprint polygon. '
            if False not in self.mask_nodata[:]:
                # do not run raster2polygon if whole image is filled with data
                self._footprint_poly = self.box.mapPoly
            else:
                try:
                    multipolygon = raster2polygon(self.mask_nodata.astype(np.uint8), self.gt, self.prj, exact=False,
                                                  progress=self.progress, q=self.q, maxfeatCount=10, timeout=15)
                    self._footprint_poly = fill_holes_within_poly(multipolygon)
                except (RuntimeError, TimeoutError):
                    if not self.q:
                        warnings.warn("\nCalculation of footprint polygon failed for %s '%s'. Using outer bounds. One "
                                      "reason could be that the nodata value appears within the actual image (not only "
                                      "as fill value). To avoid this use another nodata value. Current nodata value is "
                                      "%s." % (self.__class__.__name__, self.basename, self.nodata))
                    self._footprint_poly = self.box.mapPoly

            # validation
            assert not polyVertices_outside_poly(self._footprint_poly, self.box.mapPoly, tolerance=1e-5), \
                "Computing footprint polygon for %s '%s' failed. The resulting polygon is partly or completely " \
                "outside of the image bounds." % (self.__class__.__name__, self.basename)
            # assert self._footprint_poly
            # for XY in self.corner_coord:
            #    assert self.GeoArray.box.mapPoly.contains(Point(XY)) or self.GeoArray.box.mapPoly.touches(Point(XY)), \
            #        "The corner position '%s' is outside of the %s." % (XY, self.imName)

        return self._footprint_poly

    @footprint_poly.setter
    def footprint_poly(self, poly):
        if isinstance(poly, Polygon):
            self._footprint_poly = poly
        elif isinstance(poly, str):
            self._footprint_poly = shply_loads(poly)
        else:
            raise ValueError("'footprint_poly' can only be set from a shapely polygon or a WKT string.")

    @property
    def metadata(self):
        # type: () -> GDAL_Metadata
        """Return a DataFrame containing all available metadata (read from file if available).

        Use 'metadata[band_index].to_dict()' to get a metadata dictionary for a specific band.
        Use 'metadata.loc[row_name].to_dict()' to get all metadata values of the same key for all bands as dictionary.
        Use 'metadata.loc[row_name, band_index] = value' to set a new value.

        :return:    instance of GDAL_Metadata
        """
        if self._metadata is not None:
            return self._metadata
        else:
            default = GDAL_Metadata(nbands=self.bands, nodata_allbands=self._nodata)

            self._metadata = default
            if not self.is_inmem:
                self.set_gdalDataset_meta()
                return self._metadata
            else:
                return self._metadata

    @metadata.setter
    def metadata(self, meta):
        if not isinstance(meta, GDAL_Metadata) or meta.bands != self.bands:
            raise ValueError("%s.metadata can only be set with an instance of geoarray.metadata.GDAL_Metadata of "
                             "which the band number corresponds to the band number of %s."
                             % (self.__class__.__name__, self.__class__.__name__))
        self._metadata = meta

    meta = alias_property('metadata')  # type: GDAL_Metadata

    def __getitem__(self, given):
        if isinstance(given, (int, float, slice, np.integer, np.floating)) and self.ndim == 3:
            # handle 'given' as index for 3rd (bands) dimension
            if self.is_inmem:
                return self.arr[:, :, given]
            else:
                return self.from_path(self.arg, [given])

        elif isinstance(given, str):
            # behave like a dictionary and return the corresponding band
            if self.bandnames:
                if given not in self.bandnames:
                    raise ValueError("'%s' is not a known band. Known bands are: %s"
                                     % (given, ', '.join(list(self.bandnames.keys()))))
                if self.is_inmem:
                    return self.arr if self.ndim == 2 else self.arr[:, :, self.bandnames[given]]
                else:
                    return self.from_path(self.arg, [self.bandnames[given]])
            else:
                raise ValueError('String indices are only supported if %s has been instanced with bandnames given.'
                                 % self.__class__.__name__)

        elif isinstance(given, (tuple, list)):
            # handle requests like geoArr[[1,2],[3,4]  -> not implemented in from_path if array is not in mem
            types = [type(i) for i in given]

            if list in types or tuple in types:

                # avoid that the whole cube is read if only data from a single band is requested
                if not self.is_inmem \
                   and len(given) == 3 \
                   and isinstance(given[2], (int, float, np.integer, np.floating)):
                    band_subset = GeoArray(self.filePath)[:, :, given[2]]
                    return band_subset[given[:2]]

                self.to_mem()

            if len(given) == 3:

                # handle strings in the 3rd dim of 'given' -> convert them to a band index
                if isinstance(given[2], str):
                    if self.bandnames:
                        if given[2] not in self.bandnames:
                            raise ValueError("'%s' is not a known band. Known bands are: %s"
                                             % (given[2], ', '.join(list(self.bandnames.keys()))))

                        band_idx = self.bandnames[given[2]]
                        # NOTE: the string in the 3rd is ignored if ndim==2 and band_idx==0
                        if self.is_inmem:
                            return self.arr if (self.ndim == 2 and band_idx == 0) else self.arr[:, :, band_idx]
                        else:
                            getitem_params = \
                                given[:2] if (self.ndim == 2 and band_idx == 0) else given[:2] + (band_idx,)
                            return self.from_path(self.arg, getitem_params)
                    else:
                        raise ValueError(
                            'String indices are only supported if %s has been instanced with bandnames given.'
                            % self.__class__.__name__)

                # in case a third dim is requested from 2D-array -> ignore 3rd dim if 3rd dim is 0
                elif self.ndim == 2 and given[2] == 0:
                    if self.is_inmem:
                        return self.arr[given[:2]]
                    else:
                        return self.from_path(self.arg, given[:2])

        # if nothing has been returned until here -> behave like a numpy array
        if self.is_inmem:
            return self.arr[given]
        else:
            getitem_params = [given] if isinstance(given, slice) else given
            return self.from_path(self.arg, getitem_params)

    def __setitem__(self, idx, array2set):
        """Overwrite the pixel values of GeoArray.arr with the given array.

        :param idx:         <int, list, slice> the index position to overwrite
        :param array2set:   <np.ndarray> array to be set. Must be compatible to the given index position.
        """
        if self.is_inmem:
            self.arr[idx] = array2set
        else:
            raise NotImplementedError('Item assignment for %s instances that are not in memory is not yet supported.'
                                      % self.__class__.__name__)

    def __getattr__(self, attr):
        # check if the requested attribute can not be present because GeoArray has been instanced with an array
        attrsNot2Link2np = ['__deepcopy__']   # attributes we don't want to inherit from numpy.ndarray

        if attr not in self.__dir__() and not self.is_inmem and attr in ['shape', 'dtype', 'geotransform',
                                                                         'projection']:
            self.set_gdalDataset_meta()

        if attr in self.__dir__():  # __dir__() includes also methods and properties
            return self.__getattribute__(attr)  # __getattribute__ avoids infinite loop
        elif attr not in attrsNot2Link2np and hasattr(np.array([]), attr):
            return self[:].__getattribute__(attr)
        else:
            raise AttributeError("%s object has no attribute '%s'." % (self.__class__.__name__, attr))

    def __getstate__(self):
        """Define how the attributes of the GeoArray instance are pickled (e.g., by multiprocessing.Pool)."""
        # clean array cache in order to avoid cache pickling
        self.flush_cache()

        return self.__dict__

    def __setstate__(self, state):
        """Define how the attributes of the GeoArray instance are unpickled (e.g., by multiprocessing.Pool).

        NOTE: This method has been implemented because otherwise pickled and unpickled instances show recursion errors
        within __getattr__ when requesting any attribute.
        """
        self.__dict__ = state

    def calc_mask_nodata(self, fromBand=None, overwrite=False, flag='all'):
        # type: (int, bool, str) -> np.ndarray
        """Calculate a no data mask with values False (=nodata) and True (=data).

        :param fromBand:   index of the band to be used (if None, all bands are used)
        :param overwrite:  whether to overwrite existing nodata mask that has already been calculated
        :param flag:       algorithm how to flag pixels (default: 'all')
                           'all': flag those pixels as nodata that contain the nodata value in ALL bands
                           'any': flag those pixels as nodata that contain the nodata value in ANY band
        :return:
        """
        if self._mask_nodata is None or overwrite:
            if flag not in ['all', 'any']:
                raise ValueError(flag)

            assert self.ndim in [2, 3], "Only 2D or 3D arrays are supported. Got a %sD array." % self.ndim
            arr = self[:, :, fromBand] if self.ndim == 3 and fromBand is not None else self[:]

            if self.nodata is None:
                mask = np.ones((self.rows, self.cols), bool)

            elif np.isnan(self.nodata):
                nanmask = np.isnan(arr)
                nanbands = np.all(np.all(nanmask, axis=0), axis=0)

                if np.all(nanbands):
                    mask = np.full(arr.shape[:2], False)
                elif arr.ndim == 2:
                    mask = ~np.isnan(arr)
                else:
                    arr_1st_databand = arr[:, :, np.argwhere(~nanbands)[0][0]]
                    arr_remain = arr[:, :, ~nanbands][:, :, 1:]

                    mask = ~np.isnan(arr_1st_databand)  # True where 1st data band has data

                    if flag == 'all':
                        # ALL bands need to contain np.nan to flag the mask as nodata
                        # overwrite the mask at nodata positions (False) with True in case there is data in ANY band
                        mask[~mask] = np.any(~np.isnan(arr_remain[~mask]), axis=1)
                    else:
                        # ANY band needs to contain np.nan to flag the mask as nodata
                        # overwrite the mask at data positions (True) with False in case there is np.nan in ANY band
                        mask[mask] = ~np.any(np.isnan(arr_remain[mask]), axis=1)

            else:
                bandmeans = np.mean(np.mean(arr, axis=0), axis=0)
                nodatabands = bandmeans == self.nodata

                if np.nanmean(bandmeans) == self.nodata:
                    mask = np.full(arr.shape[:2], False)
                elif arr.ndim == 2:
                    mask = arr != self.nodata
                else:
                    arr_1st_databand = arr[:, :, np.argwhere(~nodatabands)[0][0]]
                    arr_remain = arr[:, :, ~nodatabands][:, :, 1:]

                    mask = np.array(arr_1st_databand != self.nodata)  # True where 1st data band has data

                    if flag == 'all':
                        # ALL bands need to contain nodata to flag the mask as such
                        # overwrite the mask at nodata positions (False) with True in case there is data in ANY band
                        mask[~mask] = np.any(arr_remain[~mask] != self.nodata, axis=1)
                    else:
                        # ANY band needs to contain nodata to flag the mask as such
                        # overwrite the mask at data positions (True) with False in case there is nodata in ANY band
                        mask[mask] = ~np.any(arr_remain[mask] == self.nodata, axis=1)

            self.mask_nodata = mask

            return mask

    def find_noDataVal(self, bandIdx=0, sz=3):
        """Try to derive no data value from homogenious corner pixels within 3x3 windows (by default).

        :param bandIdx:
        :param sz: window size in which corner pixels are analysed
        """
        wins = [self[0:sz, 0:sz, bandIdx], self[0:sz, -sz:, bandIdx],
                self[-sz:, -sz:, bandIdx], self[-sz:, 0:sz, bandIdx]]  # UL, UR, LR, LL

        means, stds = [np.mean(win) for win in wins], [np.std(win) for win in wins]
        possVals = [mean for mean, std in zip(means, stds) if std == 0 or np.isnan(std)]
        # possVals==[]: all corners are filled with data; np.std(possVals)==0: noDataVal clearly identified

        if possVals:
            if np.std(possVals) != 0:
                if np.isnan(np.std(possVals)):
                    # at least one of the possible values is np.nan
                    nodata = np.nan
                else:
                    # different possible nodata values have been found in the image corner
                    nodata = 'ambiguous'
            else:
                if len(possVals) <= 2:
                    # each window in each corner
                    warnings.warn("\nAutomatic nodata value detection returned the value %s for GeoArray '%s' but this "
                                  "seems to be unreliable (occurs in only %s). To avoid automatic detection, just pass "
                                  "the correct nodata value."
                                  % (possVals[0], self.basename, ('2 image corners' if len(possVals) == 2 else
                                                                  '1 image corner')))
                nodata = possVals[0]
        else:
            nodata = None

        self.nodata = nodata
        return nodata

    def set_gdalDataset_meta(self):
        """Retrieve GDAL metadata from file.

        This is only executed once to avoid overwriting of user defined attributes,
        that are defined after object instanciation.
        """
        if not self._gdalDataset_meta_already_set:
            assert self.filePath
            ds = gdal.Open(self.filePath)
            if not ds:
                raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())

            # set private class variables (in order to avoid recursion error)
            self._shape = tuple([ds.RasterYSize, ds.RasterXSize] + ([ds.RasterCount] if ds.RasterCount > 1 else []))
            self._dtype = gdal_array.GDALTypeCodeToNumericTypeCode(ds.GetRasterBand(1).DataType)
            self._geotransform = list(ds.GetGeoTransform())

            # for some reason GDAL reads arbitrary geotransforms as (0, 1, 0, 0, 0, 1) instead of (0, 1, 0, 0, 0, -1)
            self._geotransform[5] = -abs(self._geotransform[5])  # => force ygsd to be negative

            # consequently use WKT1 strings here as GDAL always exports transformation results as WKT1
            wkt = ds.GetProjection()
            self._projection = CRS(wkt).to_wkt(version="WKT1_GDAL") if not isLocal(wkt) else ''

            if 'nodata' not in self._initParams or self._initParams['nodata'] is None:
                band = ds.GetRasterBand(1)
                # FIXME this does not support different nodata values within the same file
                self.nodata = band.GetNoDataValue()

            # set metadata attribute
            if self.is_inmem or not self.filePath:
                # metadata cannot be read from disk -> set it to the default
                self._metadata = GDAL_Metadata(nbands=self.bands, nodata_allbands=self._nodata)

            else:
                self._metadata = GDAL_Metadata(filePath=self.filePath)

            # copy over the band names
            if 'band_names' in self.metadata.band_meta and self.metadata.band_meta['band_names']:
                self.bandnames = self.metadata.band_meta['band_names']

            # noinspection PyUnusedLocal
            ds = None

        self._gdalDataset_meta_already_set = True

    def from_path(self, path, getitem_params=None):
        # type: (str, list) -> np.ndarray
        """Read a GDAL compatible raster image from disk, with respect to the given image position.

        NOTE: If the requested array position is already in cache, it is returned from there.

        :param path:            <str> the file path of the image to read
        :param getitem_params:  <list> a list of slices in the form [row_slice, col_slice, band_slice]
        :return out_arr:        <np.ndarray> the output array
        """
        ds = gdal.Open(path)
        if not ds:
            raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())

        R, C, B = ds.RasterYSize, ds.RasterXSize, ds.RasterCount
        del ds

        # convert getitem_params to subset area to be read #
        rS, rE, cS, cE, bS, bE, bL = [None] * 7

        # populate rS, rE, cS, cE, bS, bE, bL
        if getitem_params:
            # populate rS, rE, cS, cE
            if len(getitem_params) >= 2:
                givenR, givenC = getitem_params[:2]
                if isinstance(givenR, slice):
                    rS = givenR.start
                    rE = givenR.stop - 1 if givenR.stop is not None else None
                elif isinstance(givenR, (int, np.integer)):
                    rS = givenR
                    rE = givenR
                if isinstance(givenC, slice):
                    cS = givenC.start
                    cE = givenC.stop - 1 if givenC.stop is not None else None
                elif isinstance(givenC, (int, np.integer)):
                    cS = givenC
                    cE = givenC

            # populate bS, bE, bL
            if len(getitem_params) in [1, 3]:
                givenB = getitem_params[2] if len(getitem_params) == 3 else getitem_params[0]
                if isinstance(givenB, slice):
                    bS = givenB.start
                    bE = givenB.stop - 1 if givenB.stop is not None else None
                elif isinstance(givenB, (int, np.integer)):
                    bS = givenB
                    bE = givenB
                elif isinstance(givenB, (tuple, list)):
                    typesInGivenB = [type(i) for i in givenB]
                    assert len(list(set(typesInGivenB))) == 1, \
                        'Mixed data types within the list of bands are not supported.'
                    if isinstance(givenB[0], (int, np.integer)):
                        bL = list(givenB)
                    elif isinstance(givenB[0], str):
                        bL = [self.bandnames[i] for i in givenB]
                elif type(givenB) in [str]:
                    bL = [self.bandnames[givenB]]

        # set defaults for not given values
        rS = rS if rS is not None else 0
        rE = rE if rE is not None else R - 1
        cS = cS if cS is not None else 0
        cE = cE if cE is not None else C - 1
        bS = bS if bS is not None else 0
        bE = bE if bE is not None else B - 1
        bL = list(range(bS, bE + 1)) if not bL else bL

        # convert negative to positive ones
        rS = rS if rS >= 0 else self.rows + rS
        rE = rE if rE >= 0 else self.rows + rE
        cS = cS if cS >= 0 else self.columns + cS
        cE = cE if cE >= 0 else self.columns + cE
        bS = bS if bS >= 0 else self.bands + bS
        bE = bE if bE >= 0 else self.bands + bE
        bL = [b if b >= 0 else (self.bands + b) for b in bL]

        # validate subset area bounds to be read
        def msg(v, idx, sz):
            # FIXME numpy raises that error ONLY for the 2nd axis
            return '%s is out of bounds for axis %s with size %s' % (v, idx, sz)

        for val, axIdx, axSize in zip([rS, rE, cS, cE, bS, bE], [0, 0, 1, 1, 2, 2], [R, R, C, C, B, B]):
            if not 0 <= val <= axSize - 1:
                raise ValueError(msg(val, axIdx, axSize))

        # summarize requested array position in arr_pos
        # NOTE: # bandlist must be string because truth value of an array with more than one element is ambiguous
        arr_pos = dict(rS=rS, rE=rE, cS=cS, cE=cE, bS=bS, bE=bE, bL=bL)

        def _ensure_np_shape_consistency_3D_2D(arr):
            """Ensure numpy output shape consistency according to the given indexing parameters.

            This may require 3D to 2D conversion in case out_arr can be represented by a 2D array AND index has been
            provided as integer (avoids shapes like (1,2,2). It also may require 2D to 3D conversion in case only one
            band has been requested and the 3rd dimension has been provided as a slice.

            NOTE: -> numpy also returns a 2D array in that case
            NOTE: if array is indexed with a slice -> keep it a 3D array
            """
            # a single value -> return as float/int
            if arr.ndim == 2 and arr.size == 1:
                arr = arr[0, 0]

            # 2D -> 3D
            if arr.ndim == 2 and isinstance(getitem_params, (tuple, list)) and len(getitem_params) == 3 and \
                    isinstance(getitem_params[2], slice):
                arr = arr[:, :, np.newaxis]

            # 3D -> 2D
            if 1 in arr.shape and len(getitem_params) != 1:
                outshape = []
                for i, sh in enumerate(arr.shape):
                    if sh == 1 and isinstance(getitem_params[i], (int, np.integer, float, np.floating)):
                        pass
                    else:
                        outshape.append(sh)

                arr = arr.reshape(*outshape)

            return arr

        # check if the requested array position is already in cache -> if yes, return it from there
        if self._arr_cache is not None and self._arr_cache['pos'] == arr_pos:
            out_arr = self._arr_cache['arr_cached']
            out_arr = _ensure_np_shape_consistency_3D_2D(out_arr)

        else:
            # TODO insert a multiprocessing.Lock here in order to prevent IO bottlenecks?
            # read subset area from disk
            if bL == list(range(0, B)):
                tempArr = gdalnumeric.LoadFile(path, cS, rS, cE - cS + 1, rE - rS + 1)
                out_arr = np.swapaxes(np.swapaxes(tempArr, 0, 2), 0, 1) if B > 1 else tempArr
                if out_arr is None:
                    raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())
            else:
                ds = gdal.Open(path)
                if len(bL) == 1:
                    band = ds.GetRasterBand(bL[0] + 1)
                    out_arr = band.ReadAsArray(cS, rS, cE - cS + 1, rE - rS + 1)
                    if out_arr is None:
                        raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())
                    del band
                else:
                    out_arr = np.empty((rE - rS + 1, cE - cS + 1, len(bL)))
                    for i, bIdx in enumerate(bL):
                        band = ds.GetRasterBand(bIdx + 1)
                        out_arr[:, :, i] = band.ReadAsArray(cS, rS, cE - cS + 1, rE - rS + 1)
                        if out_arr is None:
                            raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())
                        del band

                del ds

            out_arr = _ensure_np_shape_consistency_3D_2D(out_arr)

            # only set self.arr if the whole cube has been read (in order to avoid sudden shape changes)
            if out_arr.shape == self.shape:
                self.arr = out_arr

            # write _arr_cache
            self._arr_cache = dict(pos=arr_pos, arr_cached=out_arr)

        return out_arr  # TODO implement check of returned datatype (e.g. NoDataMask should always return bool
        # TODO -> would be np.int8 if an int8 file is read from disk

    def save(self, out_path, fmt='ENVI', creationOptions=None):
        # type: (str, str, list) -> None
        """Write the raster data to disk.

        :param out_path:        <str> output path
        :param fmt:             <str> the output format / GDAL driver code to be used for output creation, e.g. 'ENVI'
                                Refer to https://gdal.org/drivers/raster/index.html to get a full list of supported
                                formats.
        :param creationOptions: <list> GDAL creation options,
                                e.g., ["QUALITY=80", "REVERSIBLE=YES", "WRITE_METADATA=YES"]
        """
        if not self.q:
            print('Writing GeoArray of size %s to %s.' % (self.shape, out_path))
        assert self.ndim in [2, 3], 'Only 2D- or 3D arrays are supported.'

        driver = gdal.GetDriverByName(fmt)
        if driver is None:
            raise Exception("'%s' is not a supported GDAL driver. Refer to https://gdal.org/drivers/raster/index.html "
                            "for full list of GDAL driver codes." % fmt)

        if not os.path.isdir(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        envi_metadict = self.metadata.to_ENVI_metadict()

        ###########################
        # get source GDAL dataset #
        ###########################

        ds_src: gdal.Dataset
        ds_out: gdal.Dataset

        if self.is_inmem:
            ds_src = get_GDAL_ds_inmem(self.arr,  # expects rows,columns,bands
                                       self.geotransform, self.projection,
                                       self._nodata)  # avoid to compute the nodata value here, so use private attrib.

        else:
            ds_src = gdal.Open(self.filePath)
            # metadomains = {dom: src_ds.GetMetadata(dom) for dom in src_ds.GetMetadataDomainList()}

        if not ds_src:
            raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())

        #########################################
        # write output dataset and set metadata #
        #########################################

        try:
            # ENVI #
            ########
            if fmt == 'ENVI':
                # NOTE:  The dataset has to be written BEFORE metadata are added. Otherwise, metadata are not written.

                # write ds_src to disk and re-open it to add the metadata
                gdal.Translate(out_path, ds_src, format=fmt, creationOptions=creationOptions)
                del ds_src
                ds_out = gdal.Open(out_path, gdal.GA_Update)

                for bidx in range(self.bands):
                    band = ds_out.GetRasterBand(bidx + 1)

                    if 'band_names' in envi_metadict:
                        bandname = self.metadata.band_meta['band_names'][bidx].strip()
                        band.SetDescription(bandname)
                        assert band.GetDescription() == bandname

                    del band

                # avoid that band names are written to global meta
                if 'band_names' in envi_metadict:
                    del envi_metadict['band_names']

                # the expected key name is 'data_ignore_value', see below
                if 'nodata' in envi_metadict:
                    del envi_metadict['nodata']

                # set data_ignore_value in case self.metadata.band_meta contains a unique nodata value
                if 'nodata' in self.metadata.band_meta:
                    if len(set(self.metadata.band_meta['nodata'])) == 1:
                        envi_metadict['data_ignore_value'] = str(self.metadata.band_meta['nodata'][0])
                    else:
                        warnings.warn("Band-specific nodata values are not supported by the ENVI header format.")

                ds_out.SetMetadata(envi_metadict, 'ENVI')

                if 'description' in envi_metadict:
                    ds_out.SetDescription(envi_metadict['description'])

                ds_out.FlushCache()

                # NOTE: In case of ENVI format and GDAL_PAM_ENABLED=NO, the metadata is not written
                gdal.Unlink(out_path + '.aux.xml')

            else:
                # disable to write separate metadata XML files
                os.environ['GDAL_PAM_ENABLED'] = 'NO'

                ds_out = ds_src

                # set metadata
                if self.metadata.all_meta:

                    # set global domain metadata
                    if self.metadata.global_meta:
                        ds_out.SetMetadata(dict((k, repr(v)) for k, v in self.metadata.global_meta.items()))

                    if 'description' in envi_metadict:
                        ds_out.SetDescription(envi_metadict['description'])

                    # set band domain metadata
                    bandmeta_dict = self.metadata.to_DataFrame().astype(str).to_dict()

                    for bidx in range(self.bands):
                        band = ds_out.GetRasterBand(bidx + 1)
                        bandmeta = bandmeta_dict[bidx].copy()

                        # filter global metadata out
                        bandmeta = {k: v for k, v in bandmeta.items() if k not in self.metadata.global_meta}
                        # meta2write = dict((k, repr(v)) for k, v in self.metadata.band_meta.items() if v is not np.nan)

                        if 'band_names' in bandmeta:
                            band.SetDescription(self.metadata.band_meta['band_names'][bidx].strip())
                            del bandmeta['band_names']

                        if 'nodata' in bandmeta:
                            band.SetNoDataValue(self.metadata.band_meta['nodata'][bidx])
                            del bandmeta['nodata']

                        if bandmeta:
                            band.SetMetadata(bandmeta)

                        band.FlushCache()
                        del band

                    ds_out.FlushCache()

                # write ds_out to disk,
                # -> writes the in-memory array or transforms the linked dataset into the target format
                gdal.Translate(out_path, ds_out, format=fmt, creationOptions=creationOptions)
                del ds_src

        finally:
            if 'GDAL_PAM_ENABLED' in os.environ:
                del os.environ['GDAL_PAM_ENABLED']

            if not os.path.exists(out_path):
                raise Exception(gdal.GetLastErrorMsg())

            del ds_out

    def dump(self, out_path):
        # type: (str) -> None
        """Serialize the whole object instance to disk using dill."""
        import dill
        with open(out_path, 'wb') as outF:
            dill.dump(self, outF)

    def _get_plottable_image(self, xlim=None, ylim=None, band=None, boundsMap=None, boundsMapPrj=None, res_factor=None,
                             nodataVal=None, out_prj=None, ignore_rotation=False):
        # handle limits
        if boundsMap:
            boundsMapPrj = boundsMapPrj if boundsMapPrj else self.prj
            image2plot, gt, prj = self.get_mapPos(boundsMap, boundsMapPrj, band2get=band,
                                                  fillVal=nodataVal if nodataVal is not None else self.nodata)
        else:
            cS, cE = xlim if isinstance(xlim, (tuple, list)) else (0, self.columns)
            rS, rE = ylim if isinstance(ylim, (tuple, list)) else (0, self.rows)

            image2plot = self[rS:rE, cS:cE, band] if band is not None else self[rS:rE, cS:cE]
            gt, prj = self.geotransform, self.projection

        transOpt = ['SRC_METHOD=NO_GEOTRANSFORM'] if tuple(gt) == (0, 1, 0, 0, 0, -1) else None
        xdim, ydim = None, None
        in_nodata = nodataVal if nodataVal is not None else self.nodata
        out_nodata = in_nodata if in_nodata is not None else -9999
        if not np.can_cast(out_nodata, image2plot.dtype):
            image2plot = image2plot.astype(np.int32)
        if image2plot.dtype == bool:
            image2plot = image2plot.astype(int)

        # rotated images always have to be resampled for plotting
        if not ignore_rotation and (gt[2] or gt[4]):
            out_prj = out_prj or self.projection

        if res_factor != 1. and image2plot.shape[0] * image2plot.shape[1] > 1e6:  # shape > 1000*1000
            # sample image down / normalize
            xdim, ydim = \
                (self.columns * res_factor, self.rows * res_factor) if res_factor else \
                tuple(np.array([self.columns, self.rows]) / (max([self.columns, self.rows]) / 1000))
            xdim, ydim = int(xdim), int(ydim)

        if xdim or ydim or out_prj:
            from py_tools_ds.geo.raster.reproject import warp_ndarray
            image2plot, gt, prj = warp_ndarray(image2plot, self.geotransform, self.projection,
                                               out_XYdims=(xdim, ydim),
                                               in_nodata=in_nodata,
                                               out_nodata=out_nodata,
                                               transformerOptions=transOpt,
                                               out_prj=out_prj,
                                               q=True)
            if transOpt and 'NO_GEOTRANSFORM' in ','.join(transOpt):
                image2plot = np.flipud(image2plot)
                gt = list(gt)
                gt[3] = 0

            if xdim or ydim:
                print('Note: array has been downsampled to %s x %s for faster visualization.' % (xdim, ydim))

        return image2plot, gt, prj

    @staticmethod
    def _get_cmap_vmin_vmax(cmap, vmin, vmax, pmin, pmax, image2plot, nodataVal):
        from matplotlib import pyplot as plt

        # set color palette
        palette = \
            plt.get_cmap(cmap) if cmap and isinstance(cmap, str) else \
            cmap if cmap else \
            plt.get_cmap('gray')
        palette = copy(palette)  # allows to modify the colormap as in-place modifications are not allowed anymore

        if nodataVal is not None and \
           np.std(image2plot.astype(float)) != 0:  # do not show nodata; float is needed to avoid overflow error

            image2plot = np.ma.masked_equal(image2plot, nodataVal)
            vmin_auto = np.nanpercentile(image2plot.compressed(), pmin)
            vmax_auto = np.nanpercentile(image2plot.compressed(), pmax)
            palette.set_bad('aqua', 0)

        else:
            vmin_auto = np.nanpercentile(image2plot, pmin)
            vmax_auto = np.nanpercentile(image2plot, pmax)

        vmin = vmin if vmin is not None else vmin_auto
        vmax = vmax if vmax is not None else vmax_auto

        palette.set_over('1')
        palette.set_under('0')

        return palette, vmin, vmax

    def show(self, xlim=None, ylim=None, band=None, boundsMap=None, boundsMapPrj=None, figsize=None,
             interpolation='none', vmin=None, vmax=None, pmin=2, pmax=98, cmap=None, nodataVal=None,
             res_factor=None, interactive=False, ax=None, ignore_rotation=False):
        """Plot the desired array position into a figure.

        :param xlim:            [start_column, end_column]
        :param ylim:            [start_row, end_row]
        :param band:            the band index of the band to be plotted (if None and interactive==True all bands are
                                shown, otherwise the first band is chosen)
        :param boundsMap:       xmin, ymin, xmax, ymax
        :param boundsMapPrj:
        :param figsize:
        :param interpolation:
        :param vmin:            darkest pixel value to be included in stretching
        :param vmax:            brightest pixel value to be included in stretching
        :param pmin:            percentage to be used for excluding the darkest pixels from stretching (default: 2)
        :param pmax:            percentage to be used for excluding the brightest pixels from stretching (default: 98)
        :param cmap:
        :param nodataVal:
        :param res_factor:      <float> resolution factor for downsampling of the image to be plotted in order to save
                                plotting time and memory (default=None -> downsampling is performed to 1000x1000)
        :param interactive:     <bool> activates interactive plotting based on 'holoviews' library.
                                NOTE: this deactivates the magic '% matplotlib inline' in Jupyter Notebook
        :param ax:              <matplotlib.axis>   only usable in non-interactive mode
        :param ignore_rotation: whether to ignore an image rotation angle included in the GDAL GeoTransform tuple for
                                plotting (default: False)
        :return:
        """
        from matplotlib import pyplot as plt

        band = (band if band is not None else 0) if not interactive else band

        # get image to plot
        nodataVal = nodataVal if nodataVal is not None else self.nodata if self.nodata is not None else -9999
        image2plot, gt, prj = \
            self._get_plottable_image(xlim, ylim, band,
                                      boundsMap=boundsMap,
                                      boundsMapPrj=boundsMapPrj,
                                      res_factor=res_factor,
                                      nodataVal=nodataVal,
                                      ignore_rotation=ignore_rotation)

        palette, vmin, vmax = self._get_cmap_vmin_vmax(cmap, vmin, vmax, pmin, pmax, image2plot, nodataVal)
        if nodataVal is not None and np.std(image2plot.astype(float)) != 0:
            image2plot = np.ma.masked_equal(image2plot, nodataVal)

        # check availability of holoviews
        if interactive and not find_loader('holoviews'):
            warnings.warn("Interactive mode requires holoviews. Install it by running, e.g., "
                          "'conda install -c conda-forge holoviews'. Using non-interactive mode.")
            interactive = False

        if interactive and image2plot.ndim == 3:
            import holoviews as hv
            from skimage.exposure import rescale_intensity
            hv.notebook_extension('matplotlib')

            cS, cE = xlim if isinstance(xlim, (tuple, list)) else (0, self.columns - 1)
            rS, rE = ylim if isinstance(ylim, (tuple, list)) else (0, self.rows - 1)

            # noinspection PyTypeChecker
            image2plot = rescale_intensity(image2plot, in_range=(vmin, vmax))  # type: np.ndarray

            def get_hv_image(b):
                # FIXME ylabels have the wrong order
                hv_image = hv.Image(image2plot[:, :, b] if b is not None else image2plot,
                                    bounds=(cS, rS, cE, rE))
                return hv_image.opts(style={'cmap': 'gray'},
                                     plot={'fig_inches': 4 if figsize is None else figsize,
                                           'show_grid': True})

            # hvIm = hv.Image(image2plot)(style={'cmap': 'gray'}, figure_inches=figsize)
            hmap = hv.HoloMap([(band, get_hv_image(band))
                               for band in range(image2plot.shape[2])],
                              kdims=['band'])

            return hmap

        else:
            if interactive:
                warnings.warn('Currently there is no interactive mode for single-band arrays. '
                              'Switching to standard matplotlib figure..')  # TODO implement zoomable fig

            # show image
            if not ax:
                plt.figure(figsize=figsize)
                ax = plt.gca()

            rows, cols = image2plot.shape[:2]
            im = ax.imshow(image2plot,
                           palette,
                           interpolation=interpolation,
                           extent=(0, cols, rows, 0),
                           vmin=vmin,
                           vmax=vmax
                           )  # compressed excludes nodata values
            plt.show()

            return im

    def show_map(self, xlim=None, ylim=None, band=0, boundsMap=None, boundsMapPrj=None, out_epsg=None, figsize=None,
                 interpolation='none', vmin=None, vmax=None, pmin=2, pmax=98, cmap=None, nodataVal=None,
                 res_factor=None, return_map=False):
        """Show a cartopy map of the associated image data (requires geocoding and projection information).

        :param xlim:
        :param ylim:
        :param band:            band index (starting with 0)
        :param boundsMap:       xmin, ymin, xmax, ymax
        :param boundsMapPrj:
        :param out_epsg:        EPSG code of the output projection
        :param figsize:
        :param interpolation:
        :param vmin:            darkest pixel value to be included in stretching
        :param vmax:            brightest pixel value to be included in stretching
        :param pmin:            percentage to be used for excluding the darkest pixels from stretching (default: 2)
        :param pmax:            percentage to be used for excluding the brightest pixels from stretching (default: 98)
        :param cmap:
        :param nodataVal:
        :param res_factor:      <float> resolution factor for downsampling of the image to be plotted in order to save
                                plotting time and memory (default=None -> downsampling is performed to 1000x1000)
        :param return_map:
        :return:
        """
        from matplotlib import pyplot as plt
        from cartopy.crs import epsg as ccrs_from_epsg, PlateCarree

        assert self.geotransform and tuple(self.geotransform) != (0, 1, 0, 0, 0, -1), \
            'A valid geotransform is needed for a map visualization. Got %s.' % list(self.geotransform)
        assert self.projection, "A projection is needed for a map visualization. Got '%s'." % self.projection

        # get image to plot
        # (reproject to LonLat as workaround in case self.epsg is None because cartopy relies on an existing EPSG code)
        nodataVal = nodataVal if nodataVal is not None else self.nodata
        gA2plot = GeoArray(*self._get_plottable_image(xlim, ylim, band, boundsMap=boundsMap,
                                                      boundsMapPrj=boundsMapPrj, res_factor=res_factor,
                                                      nodataVal=nodataVal,
                                                      out_prj=None if self.epsg is not None else 4326),
                           nodata=nodataVal)
        image2plot = gA2plot[:]

        # create map
        def get_cartopy_crs_from_epsg(epsg_code):
            try:
                return ccrs_from_epsg(epsg_code)
            except ValueError:
                if epsg_code == 4326:
                    return PlateCarree()
                else:
                    raise NotImplementedError('The show_map() method currently does not support the given projection.')

        crs_in = get_cartopy_crs_from_epsg(gA2plot.epsg)
        crs_out = get_cartopy_crs_from_epsg(out_epsg if out_epsg is not None else gA2plot.epsg)

        fig = plt.figure(figsize=figsize)
        ax = plt.axes(projection=crs_out)

        ax.set_extent(gA2plot.box.boundsMap, crs=crs_in)

        palette, vmin, vmax = gA2plot._get_cmap_vmin_vmax(cmap, vmin, vmax, pmin, pmax, image2plot, nodataVal)
        if nodataVal is not None and np.std(image2plot) != 0:  # do not show nodata
            image2plot = np.ma.masked_equal(image2plot, nodataVal)
        ax.imshow(image2plot, cmap=palette, interpolation=interpolation, vmin=vmin, vmax=vmax,
                  origin='upper', transform=crs_in,
                  extent=list(gA2plot.box.boundsMap)
                  )

        # show grid lines
        try:
            # cartopy>=0.18.0 only
            # NOTE: The current version of cartopy (0.18.0) can only label PlateCarree grid lines -
            #       (crs=crs_out) is not yet supported and the labels are just missing in that case.
            ax.gridlines(draw_labels=True, linewidth=2, color='gray', alpha=0.5, linestyle='--')
        except TypeError as e:
            if 'Cannot label gridlines on a _EPSGProjection plot.' in str(e):
                warnings.warn('The grid line labels cannot be drawn with cartopy<0.18.0.')
                ax.gridlines(draw_labels=False, linewidth=2, color='gray', alpha=0.5, linestyle='--')
            else:
                raise

        if return_map:
            return fig, ax
        else:
            plt.show()

    def show_footprint(self):
        """Show a web map containing the computed footprint of the GeoArray instance in a Jupyter notebook."""
        if not find_loader('folium') or not find_loader('geojson'):
            raise ImportError(
                "This method requires the libraries 'folium' and 'geojson'. They can be installed with "
                "the shell command 'pip install folium geojson'.")

        import folium
        import geojson

        lonlatPoly = reproject_shapelyGeometry(self.footprint_poly, self.prj, 4326)

        m = folium.Map(location=tuple(np.array(lonlatPoly.centroid.coords.xy).flatten())[::-1])
        gjs = geojson.Feature(geometry=lonlatPoly, properties={})
        folium.GeoJson(gjs).add_to(m)
        return m

    def show_histogram(self, band=1, bins=200, normed=False, exclude_nodata=True, vmin=None, vmax=None, figsize=None):
        # type: (int, int, bool, bool, float, float, tuple) -> None
        """Show a histogram of a given band.

        :param band:            the band to be used to plot the histogram
        :param bins:            number of bins to plot (default: 200)
        :param normed:          whether to normalize the y-axis or not (default: False)
        :param exclude_nodata:  whether tp exclude nodata value from the histogram
        :param vmin:            minimum value for the x-axis of the histogram
        :param vmax:            maximum value for the x-axis of the histogram
        :param figsize:         figure size (tuple)
        """
        from matplotlib import pyplot as plt

        if self.nodata is not None and exclude_nodata:
            data = np.ma.masked_equal(self[band] if not self.bands == 1 else self[:], self.nodata)
            data = data.compressed()
        else:
            data = self[band] if not self.bands == 1 else self[:]

        vmin = vmin if vmin is not None else np.nanpercentile(data, 1)
        vmax = vmax if vmax is not None else np.nanpercentile(data, 99)
        image2plot = data

        plt.figure(figsize=figsize)
        plt.hist(list(image2plot.flat), density=normed, bins=bins, color='gray', range=[vmin, vmax])
        plt.xlabel('Pixel value')
        plt.ylabel('Probabilty' if normed else 'Count')
        plt.show()

        if not self.q:
            print('STD:', np.std(data))
            print('MEAN:', np.mean(data))
            print('2 % percentile:', np.nanpercentile(data, 2))
            print('98 % percentile:', np.nanpercentile(data, 98))

    def _show_profile(self, x, y, xlabel, ylabel, title, xlim, ylim, figsize, show_nodata, return_fig):
        from matplotlib import pyplot as plt

        nd = None

        if self._nodata is not None and self._nodata in y:
            if show_nodata:
                nd = np.ma.masked_not_equal(y, self._nodata)
                title += ' (no-data is indicated in red)'
            else:
                title += ' (no-data is not shown)'

            y = np.ma.masked_equal(y, self._nodata)

        fig = plt.figure(figsize=figsize)
        plt.plot(x, y, 'k')
        if show_nodata and nd is not None:
            plt.plot(x, nd, 'r')

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xlim(*xlim or (min(x), max(x)))
        if ylim:
            plt.ylim(*ylim)
        plt.grid()
        plt.title(title)

        if return_fig:
            return fig
        else:
            plt.show()

    def show_xprofile(self, row, band, xlim=None, ylim=None, title=None, figsize=(10, 5), show_nodata=True,
                      return_fig=False):
        """Show an x-profile at the given row/band image position.

        :param row:             image row number (counts from 0)
        :param band:            image band number (counts from 0)
        :param xlim:            x-axis limits to be used in the plot
        :param ylim:            y-axis limits to be used in the plot
        :param title:           a custom plot title
        :param figsize:         figure size (tuple)
        :param show_nodata:     whether to show no-data values in the plot
        :param return_fig:      whether to return the figure instead of showing it directly
        :return:  plt.figure
        """
        x = range(self.columns)
        y = self[row, :, band]
        title = title or f'X-Profile at row {range(self.rows)[row]}, band {range(self.bands)[band]}'

        return self._show_profile(x, y, 'column', 'value', title, xlim, ylim, figsize, show_nodata, return_fig)

    def show_yprofile(self, column, band, xlim=None, ylim=None, title=None, figsize=(10, 5), show_nodata=True,
                      return_fig=False):
        """Show a y-profile at the given column/band image position.

        :param column:          image column number (counts from 0)
        :param band:            image band number (counts from 0)
        :param xlim:            x-axis limits to be used in the plot
        :param ylim:            y-axis limits to be used in the plot
        :param title:           a custom plot title
        :param figsize:         figure size (tuple)
        :param show_nodata:     whether to show no-data values in the plot
        :param return_fig:      whether to return the figure instead of showing it directly
        :return:  plt.figure
        """
        x = range(self.rows)
        y = self[:, column, band]
        title = title or f'Y-Profile at column {range(self.columns)[column]}, band {range(self.bands)[band]}'

        return self._show_profile(x, y, 'row', 'value', title, xlim, ylim, figsize, show_nodata, return_fig)

    def show_zprofile(self, row, column, xlim=None, ylim=None, title=None, figsize=(10, 5), show_nodata=True,
                      return_fig=False):
        """Show a z-profile at the given row/column image position.

        :param row:             image row number (counts from 0)
        :param column:          image column number (counts from 0)
        :param xlim:            x-axis limits to be used in the plot
        :param ylim:            y-axis limits to be used in the plot
        :param title:           a custom plot title
        :param figsize:         figure size (tuple)
        :param show_nodata:     whether to show no-data values in the plot
        :param return_fig:      whether to return the figure instead of showing it directly
        :return:  plt.figure
        """
        if self.ndim <= 2:
            raise RuntimeError(f'Plotting a z-profile is not possible for a {self.ndim}D array.')

        if 'wavelength' in self.meta.band_meta:
            x = self.meta.band_meta['wavelength']
            x_label = 'wavelength'

        else:
            x = range(self.bands)
            x_label = 'band'

        y = self[row, column, :]
        title = title or f'Z-Profile at row {range(self.rows)[row]}, column {range(self.columns)[column]}'

        return self._show_profile(x, y, x_label, 'value', title, xlim, ylim, figsize, show_nodata, return_fig)

    def clip_to_footprint(self):
        """Clip the GeoArray instance to the outer bounds of the actual footprint."""
        self.clip_to_poly(self.footprint_poly)

    def clip_to_poly(self, poly):
        # type: (Polygon) -> None
        """Clip the GeoArray instance to the outer bounds of a given shapely polygon.

        :param poly: instance of shapely.geometry.Polygon
        """
        self.arr, self.gt, self.projection = self.get_mapPos(mapBounds=poly.bounds, mapBounds_prj=self.prj)
        self.mask_nodata.arr, self.mask_nodata.gt, self.mask_nodata.projection = \
            self.mask_nodata.get_mapPos(mapBounds=poly.bounds, mapBounds_prj=self.prj)
        assert self.shape == self.mask_nodata.shape

        if self._mask_baddata is not None:
            self.mask_baddata.arr, self.mask_baddata.gt, self.mask_baddata.projection = \
                self.mask_baddata.get_mapPos(mapBounds=poly.bounds, mapBounds_prj=self.prj)
            assert self.shape == self.mask_baddata.shape

        # update footprint polygon
        if self._footprint_poly:
            if not (self.footprint_poly.within(self.box.mapPoly) or self.footprint_poly.equals(self.box.mapPoly)):
                self.footprint_poly = self.footprint_poly.intersection(self.box.mapPoly)

    def tiles(self, tilesize=(100, 100)):
        # type: (tuple) -> 'GeneratorLen'
        """Get tiles of the full dataset in the given tile size.

        :param tilesize:    target size of the tiles (rows, columns)
                            NOTE: If rows or columns are None, all rows/columns are returned
        :return:            Generator with elements like: (((rowStart, rowEnd), (colStart, colEnd)), tiledata)
        """
        bounds_alltiles = get_array_tilebounds(self.shape, tilesize)

        class GeneratorLen(object):
            """Generator class adding __len__."""

            def __init__(self, gen, length):
                self.gen = gen
                self.length = length

            def __len__(self):
                return self.length

            def __iter__(self):
                return self.gen

        if self.ndim == 3:
            out_gen = ((((rS, rE), (cS, cE)), self[rS: rE + 1, cS: cE + 1, :])
                       for (rS, rE), (cS, cE) in bounds_alltiles)
        else:
            out_gen = ((((rS, rE), (cS, cE)), self[rS: rE + 1, cS: cE + 1])
                       for (rS, rE), (cS, cE) in bounds_alltiles)

        return GeneratorLen(out_gen, length=len(bounds_alltiles))

    def get_mapPos(self, mapBounds, mapBounds_prj, band2get=None, out_prj=None, arr_gt=None, arr_prj=None, fillVal=None,
                   rspAlg='near', progress=None, v=False):  # TODO implement slice for indexing bands
        # type: (tuple, str, int, str, tuple, str, int, str, bool, bool) -> (np.ndarray, tuple, str)
        """Return the array data of GeoArray at a given geographic position.

        NOTE: The given mapBounds are snapped to the pixel grid of GeoArray. If the given mapBounds include areas
        outside of the extent of GeoArray, these areas are filled with the fill value of GeoArray.

        :param mapBounds:       xmin, ymin, xmax, ymax
        :param mapBounds_prj:   WKT projection string corresponding to mapBounds
        :param band2get:        band index of the band to be returned (full array if not given)
        :param out_prj:         output projection as WKT string. If not given, the self.projection is used.
        :param arr_gt:          GDAL GeoTransform (taken from self if not given)
        :param arr_prj:         WKT projection string (taken from self if not given)
        :param fillVal:         nodata value
        :param rspAlg:          <str> Resampling method to use. Available methods are:
                                near, bilinear, cubic, cubicspline, lanczos, average, mode, max, min, med, q1, q2
        :param progress:        whether to show progress bars or not
        :param v:               verbose mode (not related to GeoArray.v; must be explicitly set)
        :return:
        """
        arr_gt = arr_gt or self.geotransform
        arr_prj = arr_prj or self.projection
        out_prj = out_prj or arr_prj
        fillVal = fillVal if fillVal is not None else self.nodata
        progress = progress if progress is not None else self.progress

        if self.is_inmem and (not arr_gt or not arr_prj):
            raise ValueError('In case of in-mem arrays the respective geotransform and projection of the array '
                             'has to be passed.')

        if v:
            print('%s.get_mapPos() input parameters:')
            print('\tmapBounds', mapBounds, '<==>', self.box.boundsMap)
            print('\tEPSG', WKT2EPSG(mapBounds_prj), self.epsg)
            print('\tarr_gt', arr_gt, self.gt)
            print('\tarr_prj', WKT2EPSG(arr_prj), self.epsg)
            print('\tfillVal', fillVal, self.nodata, '\n')

        sub_arr, sub_gt, sub_prj = get_array_at_mapPos(self, arr_gt, arr_prj,
                                                       out_prj=out_prj,
                                                       mapBounds=mapBounds,
                                                       mapBounds_prj=mapBounds_prj,
                                                       fillVal=fillVal,
                                                       rspAlg=rspAlg,
                                                       out_gsd=(self.xgsd, self.ygsd),
                                                       band2get=band2get,
                                                       progress=progress)
        return sub_arr, sub_gt, sub_prj

    def get_subset(self, xslice=None, yslice=None, zslice=None, return_GeoArray=True,
                   reset_bandnames=False):
        # type: (slice, slice, Union[slice, list], bool, bool) -> GeoArray
        """Return a new GeoArray instance representing a subset of the initial one wit respect to given array position.

        :param xslice:          a slice providing the X-position for the subset in the form slice(xstart, xend, xstep)
        :param yslice:          a slice providing the Y-position for the subset in the form slice(ystart, yend, ystep)
        :param zslice:          a slice providing the Z-position for the subset in the form slice(zstart, zend, zstep)
                                or a list containing the indices of the bands to extract
        :param return_GeoArray: whether to return an instance of GeoArray (default) or a tuple(np.ndarray, gt, prj)
        :param reset_bandnames: whether band names of subset should be copied from source GeoArray or reset to
                                'B1', 'B2', 'B3', ...
        :return:
        """
        xslice, yslice, zslice = xslice or slice(None), yslice or slice(None), zslice or slice(None)
        xslicing = xslice.start is not None or xslice.stop is not None or xslice.step is not None  # type: bool
        yslicing = yslice.start is not None or yslice.stop is not None or yslice.step is not None  # type: bool
        zslicing = isinstance(zslice, list) or \
            zslice.start is not None or zslice.stop is not None or zslice.step is not None  # type: bool

        # get array subset #
        ####################

        # get sub_arr
        if zslicing:
            # validation
            if self.ndim == 2:
                raise ValueError('Invalid zslice. A 2D GeoArray is not slicable in z-direction.')

            sub_arr = self[yslice, xslice, zslice]  # row, col, band
        else:
            sub_arr = self[yslice, xslice]  # row, col

        if sub_arr is None:
            raise ValueError('Unable to return an array for the given slice parameters.')

        # copy GeoArray instance #
        ##########################

        # get deepcopy of self (but without slowly copying the full-size self.arr)
        # -> cache self.arr, overwrite with subset, quickly create sub_gA and recreate self.arr
        # -> do the same with attributes 'mask_nodata' and 'mask_baddata'
        from .masks import NoDataMask, BadDataMask
        full_arr = self.arr
        full_mask_nodata = self._mask_nodata
        full_mask_baddata = self._mask_baddata

        self.arr = sub_arr
        if isinstance(self._mask_nodata, NoDataMask):  # avoid computing it here by using private
            self._mask_nodata = self._mask_nodata.get_subset(xslice=xslice, yslice=yslice)
        if isinstance(self._mask_baddata, BadDataMask):  # avoid computing it here by using private
            self._mask_baddata = self._mask_baddata.get_subset(xslice=xslice, yslice=yslice)

        sub_gA = deepcopy(self)  # do not copy any references, otherwise numpy arrays would be copied as views

        self._arr = full_arr
        if isinstance(self._mask_nodata, NoDataMask):
            self._mask_nodata = full_mask_nodata
        if isinstance(self._mask_baddata, BadDataMask):
            self._mask_baddata = full_mask_baddata

        # numpy array references need to be cleared separately (also called by self._mask_nodata.get_subset() above)
        sub_gA.deepcopy_array()

        # handle metadata #
        ###################

        # adapt geotransform
        sub_ulXY = imXY2mapXY((xslice.start or 0, yslice.start or 0), self.gt)
        sub_gt = (sub_ulXY[0], self.gt[1], self.gt[2], sub_ulXY[1], self.gt[4], self.gt[5])

        # apply zslice to bandnames and metadata
        if zslicing:
            bNs_out = list(np.array(list(self._bandnames))[zslice]) if self._bandnames else None
            _meta_out = self.metadata.get_subset(bands2extract=zslice)
        else:
            bNs_out = list(self._bandnames) if self._bandnames else None
            _meta_out = self.meta

        sub_gA.gt = sub_gt
        sub_gA.metadata = _meta_out
        sub_gA.bandnames = bNs_out
        sub_gA.filePath = self.filePath
        if xslicing or yslicing:
            sub_gA._footprint_poly = None  # reset footprint_poly -> has to be updated

        if reset_bandnames:
            del sub_gA.bandnames  # also updates bandnames within self.meta

        return sub_gA if return_GeoArray else (sub_arr, sub_gt, self.prj)

    def reproject_to_new_grid(self, prototype=None, tgt_prj=None, tgt_xygrid=None, rspAlg='cubic', CPUs=None):
        """Reproject all array-like attributes to a given target grid.

        :param prototype:   <GeoArray> an instance of GeoArray to be used as pixel grid reference
        :param tgt_prj:     <str> WKT string of the projection
        :param tgt_xygrid:  <list> target XY grid, e.g. [[xmin,xmax], [ymax, ymin]] for the UL corner
        :param rspAlg:      <str, int> GDAL compatible resampling algorithm code
        :param CPUs:        <int> number of CPUs to use (default: None -> use all available CPUs)
        :return:
        """
        assert (tgt_prj and tgt_xygrid) or prototype, "Provide either 'prototype' or 'tgt_prj' and 'tgt_xygrid'!"
        tgt_prj = tgt_prj or prototype.prj
        tgt_xygrid = tgt_xygrid or prototype.xygrid_specs
        assert tgt_xygrid[1][0] > tgt_xygrid[1][1]

        # set target GSD
        tgt_xgsd, tgt_ygsd = abs(tgt_xygrid[0][0] - tgt_xygrid[0][1]), abs(tgt_xygrid[1][0] - tgt_xygrid[1][1])

        # set target bounds
        tgt_bounds = reproject_shapelyGeometry(self.box.mapPoly, self.prj, tgt_prj).bounds

        gt = (tgt_xygrid[0][0], tgt_xgsd, 0, max(tgt_xygrid[1]), 0, -tgt_ygsd)
        xmin, ymin, xmax, ymax = snap_bounds_to_pixGrid(tgt_bounds, gt, roundAlg='on')

        from py_tools_ds.geo.raster.reproject import warp_ndarray
        self.arr, self.gt, self.prj = \
            warp_ndarray(self[:], self.gt, self.prj, tgt_prj,
                         out_gsd=(tgt_xgsd, tgt_ygsd),
                         out_bounds=(xmin, ymin, xmax, ymax),
                         out_bounds_prj=tgt_prj,
                         rspAlg=rspAlg,
                         in_nodata=self.nodata,
                         CPUs=CPUs,
                         progress=self.progress,
                         q=self.q)

        if hasattr(self, '_mask_nodata') and self._mask_nodata is not None:
            self.mask_nodata.reproject_to_new_grid(prototype=prototype,
                                                   tgt_prj=tgt_prj,
                                                   tgt_xygrid=tgt_xygrid,
                                                   rspAlg='near',
                                                   CPUs=CPUs)

        if hasattr(self, '_mask_baddata') and self._mask_baddata is not None:
            self.mask_baddata.reproject_to_new_grid(prototype=prototype,
                                                    tgt_prj=tgt_prj,
                                                    tgt_xygrid=tgt_xygrid,
                                                    rspAlg='near',
                                                    CPUs=CPUs)

        # update footprint polygon
        if self._footprint_poly:
            if not (self.footprint_poly.within(self.box.mapPoly) or self.footprint_poly.equals(self.box.mapPoly)):
                self.footprint_poly = self.footprint_poly.intersection(self.box.mapPoly)

    def read_pointData(self, mapXY_points, mapXY_points_prj=None, band=None, offside_val=np.nan):
        """Return the array values for the given set of X/Y coordinates.

        NOTE: If GeoArray has been instanced with a file path, the function will read the dataset into memory.

        :param mapXY_points:        <np.ndarray, tuple> X/Y coordinates of the points of interest. If a numpy array is
                                    given, it must have the shape [Nx2]
        :param mapXY_points_prj:    <str, int> WKT string or EPSG code of the projection corresponding to the given
                                    coordinates.
        :param band:                <int> the band index of the band of interest. If None, the values of all bands are
                                    returned.
        :param offside_val:         fill value in case input coordinates are geographically outside of the GeoArray
                                    instance
        :return:                    - int in case only a singe coordinate is passed
                                    - np.ndarray with shape [Nx1] in case only one band is requested
                                    - np.ndarray with shape [Nx1xbands] in case all bands are requested
        """
        mapXY = mapXY_points if isinstance(mapXY_points, np.ndarray) else np.array(mapXY_points).reshape(1, 2)
        prj = mapXY_points_prj if mapXY_points_prj else self.prj

        assert prj, 'A projection is needed for returning image DNs at specific map X/Y coordinates!'
        if not prj_equal(prj1=prj, prj2=self.prj):
            mapX, mapY = transform_any_prj(prj, self.prj, mapXY[:, 0], mapXY[:, 1])
            mapXY = np.hstack([mapX.reshape(-1, 1),
                               mapY.reshape(-1, 1)])

        imXY = mapXY2imXY(mapXY, self.geotransform)

        # get a mask of all map positions geographically outside of the GeoArray instance
        mask_off = (np.any(imXY < 0, axis=1)) |\
                   (imXY[:, 0] >= self.columns) |\
                   (imXY[:, 1] >= self.rows)

        imYX = np.fliplr(np.array(imXY)).astype(np.int16)

        if imYX.size == 2:  # only one coordinate pair
            Y, X = imYX[0].tolist()

            if X < 0 or X >= self.columns or Y < 0 or Y >= self.rows:
                pointdata = offside_val
            else:
                pointdata = self[Y, X, band]

        else:  # multiple coordinate pairs
            if True in mask_off:
                shape_exp = (imXY.shape[0], 1, self.bands) if band is None else (imXY.shape[0], 1)
                pointdata = np.full(shape_exp, offside_val)
                imYX = imYX[~mask_off, :]

                if band is None:
                    pointdata[~mask_off, 0, :] = \
                        self[tuple(imYX.T.tolist() + [band])] \
                        .reshape(imYX.shape[0], self.bands)
                else:
                    pointdata[~mask_off, 0] = \
                        self[tuple(imYX.T.tolist() + [band])]
            else:
                pointdata = self[tuple(imYX.T.tolist() + [band])]

        return pointdata

    def to_mem(self):
        """Read the whole dataset into memory and sets self.arr to the read data."""
        self.arr = self[:]
        return self

    def to_disk(self):
        """Set self.arr back to None for in-memory instances, to release memory.

        Note: This requires that the GeoArray was instanced with a file path.
        """
        if self.filePath and os.path.isfile(self.filePath):
            self._arr = None
        else:
            warnings.warn('GeoArray object cannot be turned into disk mode because this asserts that GeoArray.filePath '
                          'contains a valid file path. Got %s.' % self.filePath)
        return self

    def deepcopy_array(self):
        if self.is_inmem:
            temp = np.empty_like(self.arr)
            temp[:] = self.arr
            self.arr = temp  # deep copy: converts view to its own array in order to avoid wrong output

    def cache_array_subset(self, arr_pos):
        # type: (list) -> None
        """Set the array cache of the GeoArray instance to the given array to speed up calculations afterwards.

        :param arr_pos: a list of array indices as passed to __getitem__
        """
        if not self.is_inmem:
            # noinspection PyStatementEffect
            self[arr_pos]  # runs __getitem__ and sets self._arr_cache
        else:
            pass  # no array cache needed because array is in memory anyways

    def flush_cache(self):
        """Clear the array cache of the GeoArray instance."""
        self._arr_cache = None


def get_GeoArray_from_GDAL_ds(ds):
    # TODO implement as class method of GeoArray
    arr = gdalnumeric.DatasetReadAsArray(ds)
    if len(arr.shape) == 3:
        arr = np.swapaxes(np.swapaxes(arr, 0, 2), 0, 1)
    return GeoArray(arr, ds.GetGeoTransform(), ds.GetProjection())


class MultiGeoArray(object):  # pragma: no cover
    def __init__(self, GeoArray_list):
        """Get an instance of MultiGeoArray.

        :param GeoArray_list:   a list of GeoArray instances having a geographic overlap
        """
        self._arrs = None

        self.arrs = GeoArray_list

        raise NotImplementedError('This class is not yet working.')  # FIXME

    @property
    def arrs(self):
        return self._arrs

    @arrs.setter
    def arrs(self, GeoArray_list):
        for geoArr in GeoArray_list:
            assert isinstance(geoArr, GeoArray), "'arrs' can only be set to a list of GeoArray instances."

        self._arrs = GeoArray_list
