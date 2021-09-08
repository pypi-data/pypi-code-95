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

import numpy as np

# internal imports
from .baseclasses import GeoArray

__author__ = 'Daniel Scheffler'


class _Mask(GeoArray):
    _CLASSNAME = 'Mask baseclass'

    def _validate_array_values(self, array):
        if not array.dtype == bool:
            if np.issubdtype(array.dtype, np.integer):
                if array.min() < 0 or array.max() > 1:
                    pixelvals = sorted(list(np.unique(array)))
                    assert len(pixelvals) <= 2, 'The %s must have only two pixel values (boolean) - 0 and 1 or ' \
                                                'False and True! The given mask for %s contains the values %s.' \
                                                % (self._CLASSNAME, self.basename, pixelvals)
                    assert pixelvals in [[0, 1], [0], [1], [False, True], [False], [True]], \
                        'Found unsupported pixel values in the given %s for %s: %s. ' \
                        'Only the values True, False, 0 and 1 are supported. ' \
                        % (self._CLASSNAME, self.basename, pixelvals)
            else:
                raise TypeError('Boolean or integer array expected.')


class BadDataMask(_Mask):
    _CLASSNAME = 'bad data mask'

    def __init__(self, path_or_array, geotransform=None, projection=None, bandnames=None, nodata=False, progress=True,
                 q=False):
        super(BadDataMask, self).__init__(path_or_array, geotransform=geotransform, projection=projection,
                                          bandnames=bandnames, nodata=nodata, progress=progress, q=q)

        if self.is_inmem:
            # validate input data - before converting to bool
            self._validate_array_values(self.arr)
            self.arr = self.arr.astype(bool)

            # del self._mask_baddata, self.mask_baddata # TODO delete property (requires deleter)

    @property
    def arr(self):
        return self._arr

    @arr.setter
    def arr(self, ndarray):
        assert isinstance(ndarray, np.ndarray), "'arr' can only be set to a numpy array!"
        self._validate_array_values(ndarray)
        self._arr = ndarray.astype(bool)


class NoDataMask(_Mask):
    _CLASSNAME = 'no data mask'

    def __init__(self, path_or_array, geotransform=None, projection=None, bandnames=None, nodata=False, progress=True,
                 q=False):
        super(NoDataMask, self).__init__(path_or_array, geotransform=geotransform, projection=projection,
                                         bandnames=bandnames, nodata=nodata, progress=progress, q=q)

        if self.is_inmem:
            # validate input data - before converting to bool
            self._validate_array_values(self.arr)
            self.arr = self.arr.astype(bool)

            # del self._mask_nodata, self.mask_nodata # TODO delete property (requires deleter)
            # TODO disk-mode: init must check the numbers of bands, and ideally also the pixel values in mask

    @property
    def arr(self):
        return self._arr

    @arr.setter
    def arr(self, ndarray):
        assert isinstance(ndarray, np.ndarray), "'arr' can only be set to a numpy array!"
        self._validate_array_values(ndarray)
        self._arr = ndarray.astype(bool)


class CloudMask(_Mask):
    _CLASSNAME = 'cloud mask'

    def __init__(self, path_or_array, geotransform=None, projection=None, bandnames=None, nodata=None, progress=True,
                 q=False):
        # TODO implement class definitions and specific metadata

        super(CloudMask, self).__init__(path_or_array, geotransform=geotransform, projection=projection,
                                        bandnames=bandnames, nodata=nodata, progress=progress, q=q)

        # del self._mask_nodata, self.mask_nodata # TODO delete property (requires deleter)
        # TODO check that: "Automatically detected nodata value for CloudMask 'IN_MEM': 1.0"

    def to_ENVI_classification(self):  # pragma: no cover
        raise NotImplementedError  # TODO
