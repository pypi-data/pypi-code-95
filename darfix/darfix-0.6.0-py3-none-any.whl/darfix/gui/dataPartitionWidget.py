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
__date__ = "11/05/2020"

import logging

import numpy

from silx.gui import qt
from silx.gui.plot import Plot1D

from .operationThread import OperationThread
from darfix.core.dataset import Operation

_logger = logging.getLogger(__file__)


class DataPartitionWidget(qt.QMainWindow):

    sigComputed = qt.Signal()

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)

        self._plot = Plot1D()

        binsLabel = qt.QLabel("Bins:")
        binsNumberLabel = qt.QLabel("Number of bins:")
        self.bins = qt.QLineEdit("")
        self.bins.setToolTip("Defines the number of equal-width bins in the given range for \
            the histogram")
        self.bins.setValidator(qt.QIntValidator())
        self.binsNumber = qt.QLineEdit("1")
        self.binsNumber.setToolTip("Number of bins of the histogram of intensities that \
            will be considered as low intensity data")
        self.binsNumber.setValidator(qt.QIntValidator())
        self.computeHistogram = qt.QPushButton("Compute histogram")
        self.computePartition = qt.QPushButton("Compute partition")
        self.abortB = qt.QPushButton("Abort")
        self.abortB.hide()
        self.computeHistogram.pressed.connect(self._computeHistogram)
        self.computePartition.pressed.connect(self._computePartition)
        self.abortB.pressed.connect(self.abort)
        widget = qt.QWidget(parent=self)
        layout = qt.QGridLayout()
        layout.addWidget(binsLabel, 0, 0, 1, 1)
        layout.addWidget(self.bins, 0, 1, 1, 1)
        layout.addWidget(binsNumberLabel, 1, 0, 1, 1)
        layout.addWidget(self.binsNumber, 1, 1, 1, 1)
        layout.addWidget(self.computeHistogram, 0, 2, 1, 1)
        layout.addWidget(self.computePartition, 1, 2, 1, 1)
        layout.addWidget(self.abortB, 2, 2, 1, 1)
        layout.addWidget(self._plot, 3, 0, 1, 3)
        widget.setLayout(layout)
        widget.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.setCentralWidget(widget)
        self._plot.hide()

    def _computeHistogram(self):
        self.computeHistogram.setEnabled(False)
        self.computePartition.setEnabled(False)
        self.abortB.show()
        try:
            self._thread = OperationThread(self, self._dataset.compute_frames_intensity)
            self._thread.finished.connect(self._showHistogram)
            self._thread.start()
        except Exception as e:
            self.computeHistogram.setEnabled(True)
            raise e

    def _computePartition(self):
        self.computeHistogram.setEnabled(False)
        self.computePartition.setEnabled(False)
        self.abortB.show()
        try:
            self._thread = OperationThread(self, self._dataset.partition_by_intensity)
            self._thread.setArgs(bins=int(self.bins.text()), num_bins=int(self.binsNumber.text()))
            self._thread.finished.connect(self._filterData)
            self._thread.start()
        except Exception as e:
            self.computePartition.setEnabled(True)
            raise e

    def abort(self):
        self.abortB.setEnabled(False)
        self._dataset.stop_operation(Operation.PARTITION)

    def setDataset(self, dataset, indices=None, bg_indices=None, bg_dataset=None):
        """
        Dataset setter.

        :param Dataset dataset: dataset
        """
        self._dataset = dataset
        self.indices = indices
        self.bg_indices = bg_indices
        self.bg_dataset = bg_dataset
        self.bins.setText(str(self._dataset.nframes))

    def _showHistogram(self):
        """
        Plots the eigenvalues.
        """
        self._thread.finished.disconnect(self._showHistogram)
        self.abortB.hide()
        self.abortB.setEnabled(True)
        self.computePartition.setEnabled(True)
        self.computeHistogram.setEnabled(True)
        if self._thread.data is not None:
            frames_intensity = self._thread.data
            self._plot.remove()
            self._plot.show()
            values, bins = numpy.histogram(frames_intensity, int(self.bins.text()))
            self._plot.addHistogram(values, bins, fill=True)
        else:
            print("\nComputation aborted")

    def _filterData(self):
        """
        Plots the eigenvalues.
        """
        self._thread.finished.disconnect(self._filterData)
        self.abortB.hide()
        self.abortB.setEnabled(True)
        self.computeHistogram.setEnabled(True)
        self.computePartition.setEnabled(True)
        if self._thread.data is not None:
            self.indices, self.bg_indices = self._thread.data
            self.sigComputed.emit()
        else:
            print("\nComputation aborted")

    def getDataset(self):
        return self._dataset, self.indices, self.bg_indices, self. bg_dataset
