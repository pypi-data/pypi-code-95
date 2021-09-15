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


__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "22/12/2020"

import numpy

from silx.gui import qt
from silx.gui.plot import Plot1D

from .operationThread import OperationThread


class PCAWidget(qt.QMainWindow):
    """
    Widget to apply PCA to a set of images and plot the eigenvalues found.
    """
    sigComputed = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        self._plot = Plot1D()
        self._plot.setDataMargins(0.05, 0.05, 0.05, 0.05)
        self._plot.setGraphTitle("Components representation of the dataset")
        self._plot.setGraphXLabel("Components")
        self._plot.setGraphYLabel("Singular values")
        self.setCentralWidget(self._plot)

    def _computePCA(self):
        try:
            self._thread = OperationThread(self, self.dataset.pca)
            self._thread.setArgs(return_vals=True)
            self._thread.finished.connect(self._updateData)
            self._thread.start()
        except Exception as e:
            raise e

    def setDataset(self, dataset, indices=None, bg_indices=None, bg_dataset=None):
        """
        Dataset setter.

        :param Dataset dataset: dataset
        """
        self.dataset = dataset
        self.indices = indices
        self.bg_indices = bg_indices
        self.bg_dataset = bg_dataset
        self._computePCA()

    def _updateData(self):
        """
        Plots the eigenvalues.
        """
        self._thread.finished.disconnect(self._updateData)
        vals = self._thread.data
        self._plot.show()
        self._plot.addCurve(numpy.arange(len(vals)), vals, symbol='.', linestyle=' ')
        self.sigComputed.emit()
