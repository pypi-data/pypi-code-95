# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

"""
Module for defining processes to be used by the library `pypushflow`. Each of
the processes defined here can be used (its corresponding widgets) within an
Orange workflow and later be converted to a script without the GUI part needed.
"""

__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "16/07/2021"


import numpy
from collections import namedtuple

from silx.gui import qt
from darfix.core import utils
from darfix.gui.blindSourceSeparationWidget import Method
from darfix.gui.grainPlotWidget import GrainPlotWidget
from darfix.gui.zSumWidget import ZSumWidget
from darfix.gui.rsmWidget import PixelSize

_input_desc = namedtuple("_input_desc", ["name", "type", "handler", "doc"])

_output_desc = namedtuple("_output_desc", ["name", "type", "doc"])


class IgnoreProcess:
    """Simple util class to ignore a processing when using pypushflow"""

    def process(self, scan):
        return scan

    def set_properties(self, properties):
        pass

    __call__ = process


class _NoiseRemoval:
    inputs = [_input_desc(name='dataset', type=tuple, handler='process',
                          doc='dataset to process'), ]

    outputs = [
        _output_desc(name='dataset', type=tuple, doc='dataset to process'), ]

    def __init__(self):
        self._properties = {}

    def process(self, dataset):
        dataset, indices, li_indices, bg_dataset = dataset
        method = self._properties['method'] if 'method' in self._properties else ''
        background_type = self._properties['background_type'] if 'background_type' in self._properties else ''
        step = int(self._properties['step']) if 'step' in self._properties and self._properties['step'] else None
        chunks = self._properties['chunks'] if 'chunks' in self._properties and self._properties['chunks'] else None
        bg = None
        if background_type == "Dark data":
            bg = bg_dataset
        elif background_type == "Low intensity data":
            bg = li_indices
        size = self._properties['kernel_size'] if 'kernel_size' in self._properties else ''
        if method != '':
            dataset = dataset.apply_background_subtraction(indices=indices, method=method, background=bg, step=step, chunk_shape=chunks)
        if size != '':
            dataset = dataset.apply_hot_pixel_removal(indices=indices, kernel=int(size))
        return dataset, indices, li_indices, bg_dataset

    def set_properties(self, properties):
        self._properties = properties


class _ROI:
    inputs = [_input_desc(name='dataset', type=tuple, handler='process',
                          doc='dataset to process'), ]

    outputs = [
        _output_desc(name='dataset', type=tuple, doc='dataset to process'), ]

    def __init__(self):
        self._properties = {}

    def process(self, dataset):
        dataset, indices, li_indices, bg_dataset = dataset
        if 'roi_origin' in self._properties and 'roi_size' in self._properties and self._properties['roi_origin'] != '' and self._properties['roi_size'] != '':
            roi_origin = self._properties['roi_origin']
            roi_size = self._properties['roi_size']
            dataset = dataset.apply_roi(origin=numpy.flip(roi_origin), size=numpy.flip(roi_size))
            if bg_dataset is not None:
                bg_dataset = bg_dataset.apply_roi(origin=numpy.flip(roi_origin), size=numpy.flip(roi_size))
        else:
            print(ValueError('Roi origin and/or size not defined'))
        return dataset, indices, li_indices, bg_dataset

    def set_properties(self, properties):
        self._properties = properties


class _DataPartition:
    inputs = [_input_desc(name='dataset', type=tuple, handler='process',
                          doc='dataset to process'), ]

    outputs = [
        _output_desc(name='dataset', type=tuple, doc='dataset to process'), ]

    def __init__(self):
        self._properties = {}

    def process(self, dataset):
        dataset, indices, li_indices, bg_dataset = dataset
        bins = self.properties['bins'] if 'bins' in self.properties else None
        nbins = self.properties['n_bins'] if 'n_bins' in self.properties else 1
        indices, li_indices = dataset.partition_by_intensity(bins, nbins)
        return dataset, indices, li_indices, bg_dataset

    def set_properties(self, properties):
        self._properties = properties


class _DimensionDefinition:
    inputs = [_input_desc(name='dataset', type=tuple, handler='process',
                          doc='dataset to process'), ]

    outputs = [
        _output_desc(name='dataset', type=tuple, doc='dataset to process'), ]

    def __init__(self):
        self._properties = {}

    def process(self, dataset):
        dataset, indices, li_indices, bg_dataset = dataset
        if '_dims' in self._properties:
            dims = utils.convertDictToDim(self._properties['_dims'])
            assert type(dims) is dict
            for axis, dim in dims.items():
                assert type(axis) is int
                if dataset is not None and len(dataset.data.metadata) > 0:
                    if not dim.unique_values:
                        values = numpy.unique(
                            [data.get_value(kind=dim.kind, name=dim.name)[0]
                             for data in dataset.data.metadata])
                        dim.set_unique_values(values)
                dataset.add_dim(axis=axis, dim=dim)
            dataset = dataset.reshape_data()
        else:
            print(ValueError("Dimensions not defined"))
        return dataset, indices, li_indices, bg_dataset

    def set_properties(self, properties):
        self._properties = properties


class _ShiftCorrection:
    inputs = [_input_desc(name='dataset', type=tuple, handler='process',
                          doc='dataset to process'), ]

    outputs = [
        _output_desc(name='dataset', type=tuple, doc='dataset to process'), ]

    def __init__(self):
        self._properties = {}

    def process(self, dataset):
        dataset, indices, li_indices, bg_dataset = dataset
        if 'shift' in self._properties and len(self._properties['shift']) > 0:
            frames = numpy.arange(dataset.get_data(indices=indices).shape[0])
            dataset.apply_shift(numpy.outer(self._properties['shift'], frames), indices=indices)
        else:
            print(ValueError("Shift not defined"))
        return dataset, indices, li_indices, bg_dataset

    def set_properties(self, properties):
        self._properties = properties


class _BlindSourceSeparation:
    inputs = [_input_desc(name='dataset', type=tuple, handler='process',
                          doc='dataset to process'), ]

    outputs = [
        _output_desc(name='dataset', type=tuple, doc='dataset to process'), ]

    def __init__(self):
        self._properties = {}

    def process(self, dataset):
        dataset, indices, li_indices, bg_dataset = dataset
        if 'method' in self._properties and self._properties['method'] != '':
            method = Method(self._properties['method'])
            n_comp = self._properties['n_comp'] if 'n_comp' in self._properties else None
            if method == Method.PCA:
                comp, W = dataset.pca(n_comp, indices=indices)
            elif method == Method.NNICA:
                comp, W = dataset.nica(n_comp, indices=indices)
            elif method == Method.NMF:
                comp, W = dataset.nmf(n_comp, indices=indices)
            elif method == Method.NNICA_NMF:
                comp, W = dataset.nica_nmf(n_comp, indices=indices)
            else:
                raise ValueError('BSS method not managed')
            # TODO: finish
        else:
            print(ValueError("BSS method not defined"))

    def set_properties(self, properties):
        self._properties = properties


class _RockingCurves:
    inputs = [_input_desc(name='dataset', type=tuple, handler='process',
                          doc='dataset to process'), ]

    outputs = [
        _output_desc(name='dataset', type=tuple, doc='dataset to process'), ]

    def __init__(self):
        self._properties = {}

    def process(self, dataset):
        dataset, indices, li_indices, bg_dataset = dataset
        int_thresh = self._properties['int_thresh'] if 'int_thresh' in self._properties else None
        dimension = self._properties['dimension'] if 'dimension' in self._properties else None
        dataset = dataset.apply_fit(indices=indices, dimension=dimension, int_thresh=int_thresh)
        return dataset, indices, li_indices, bg_dataset

    def set_properties(self, properties):
        self._properties = properties


class _GrainPlot:
    inputs = [_input_desc(name='dataset', type=tuple, handler='process',
                          doc='dataset to process'), ]

    outputs = [
        _output_desc(name='dataset', type=tuple, doc='dataset to process'), ]

    def process(self, dataset):
        app = qt.QApplication([])
        widget = GrainPlotWidget()
        if dataset:
            widget.setDataset(*dataset)
        widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        widget.show()
        app.exec_()
        return dataset


class _Transformation:
    inputs = [_input_desc(name='dataset', type=tuple, handler='process',
                          doc='dataset to process'), ]

    outputs = [
        _output_desc(name='dataset', type=tuple, doc='dataset to process'), ]

    def __init__(self):
        self._properties = {}

    def process(self, dataset):
        dataset, indices, li_indices, bg_dataset = dataset
        magnification = self._properties['magnification'] if 'magnification' in self._properties else None
        pixelSize = self._properties['pixelSize'] if 'pixelSize' in self._properties else None
        kind = self._properties['kind'] if 'kind' in self._properties else True
        rotate = self._properties['rotate'] if 'rotate' in self._properties else None
        if dataset and dataset.dims.ndim:
            if dataset.dims.ndim == 1 and kind:
                dataset.compute_transformation(PixelSize[pixelSize].value,
                                               kind="rsm",
                                               rotate=rotate)
            else:
                dataset.compute_transformation(magnification)
        return dataset, indices, li_indices, bg_dataset

    def set_properties(self, properties):
        self._properties = properties


class _ZSum:
    inputs = [_input_desc(name='dataset', type=tuple, handler='process',
                          doc='dataset to process'), ]

    outputs = [
        _output_desc(name='dataset', type=tuple, doc='dataset to process'), ]

    def process(self, dataset):
        app = qt.QApplication([])
        widget = ZSumWidget()
        if dataset:
            widget.setDataset(*dataset)
        widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        widget.show()
        app.exec_()
        return dataset
