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
__date__ = "29/06/2021"

import numpy
import logging

from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import StackView, Plot1D, Plot2D
from .utils import ChooseDimensionDock
from silx.utils.enum import Enum as _Enum

import darfix
from darfix.core.mapping import fit_rocking_curve
from darfix.core.dataset import Operation
from .operationThread import OperationThread

_logger = logging.getLogger(__file__)


class Method(_Enum):
    """
    Different maps that can be showed after fitting the data
    """
    INTENSITY = "Integrated intensity"
    FWHM = "FWHM"
    PEAK = "Peak position"


class RockingCurvesWidget(qt.QMainWindow):
    """
    Widget to apply fit to a set of images and plot the integrated intensity, fwhm and peak position maps.
    """
    sigFitted = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        widget = qt.QWidget(parent=self)
        layout = qt.QGridLayout()

        self._sv = StackView(parent=self)
        self._sv.setColormap(Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME))
        self._plot = Plot1D(parent=self)
        self._plot.setGraphTitle("Rocking curves")
        self._plot.setGraphXLabel("Degrees")
        self._plotMaps = Plot2D(self)
        self._plotMaps.setDefaultColormap(Colormap(name='cividis', normalization='linear'))
        self._methodCB = qt.QComboBox(self)
        self._methodCB.addItems(Method.values())
        self._methodCB.currentTextChanged.connect(self._updatePlot)
        self._plotMaps.hide()
        self._methodCB.hide()
        self._chooseDimensionDock = ChooseDimensionDock(self)
        intLabel = qt.QLabel("Intensity threshold:")
        self._intThresh = "15"
        self._intThreshLE = qt.QLineEdit(self._intThresh)
        self._intThreshLE.setValidator(qt.QDoubleValidator())
        self._computeFit = qt.QPushButton("Fit data")
        self._computeFit.clicked.connect(self._grainPlot)
        self._abortFit = qt.QPushButton("Abort")
        self._abortFit.clicked.connect(self.__abort)
        spacer1 = qt.QWidget(parent=self)
        spacer1.setLayout(qt.QVBoxLayout())
        spacer1.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self._dimension = None
        self._centerDataCheckbox = qt.QCheckBox("Center angle values")
        self._centerDataCheckbox.stateChanged.connect(self._checkboxStateChanged)
        self._chooseDimensionDock.widget.layout().addWidget(spacer1)
        self._chooseDimensionDock.hide()
        self._chooseDimensionDock.widget.filterChanged.connect(self._filterStack)
        self._chooseDimensionDock.widget.stateDisabled.connect(self._wholeStack)

        layout.addWidget(self._sv, 0, 0, 1, 2)
        layout.addWidget(self._plot, 0, 2, 1, 2)
        layout.addWidget(self._centerDataCheckbox, 1, 3, 1, 1)
        layout.addWidget(intLabel, 2, 0, 1, 1)
        layout.addWidget(self._intThreshLE, 2, 1, 1, 1)
        layout.addWidget(self._computeFit, 2, 2, 1, 2)
        layout.addWidget(self._abortFit, 2, 2, 1, 2)
        layout.addWidget(self._methodCB, 3, 0, 1, 4)
        layout.addWidget(self._plotMaps, 4, 0, 1, 4)
        self._abortFit.hide()
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._chooseDimensionDock)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def setDataset(self, dataset, indices=None, bg_indices=None, bg_dataset=None):
        """
        Dataset setter.

        :param Dataset dataset: dataset
        """
        self.dataset = dataset
        self.indices = indices
        self._update_dataset = dataset
        self._thread = OperationThread(self, self.dataset.apply_fit)
        self.setStack()
        self._sv.getPlotWidget().sigPlotSignal.connect(self._mouseSignal)
        self._sv.sigFrameChanged.connect(self._addPoint)
        if len(self.dataset.data.shape) > 3:
            self._chooseDimensionDock.show()
            self._chooseDimensionDock.widget.setDimensions(self.dataset.dims)
        if not self._chooseDimensionDock.widget._checkbox.isChecked():
            self._wholeStack()

    def setStack(self, dataset=None):
        """
        Sets new data to the stack.
        Mantains the current frame showed in the view.

        :param Dataset dataset: if not None, data set to the stack will be from the given dataset.
        """
        if dataset is None:
            dataset = self.dataset
        nframe = self._sv.getFrameNumber()
        if self.indices is None:
            self._sv.setStack(dataset.get_data() if dataset is not None else None)
        else:
            self._sv.setStack(dataset.get_data(self.indices) if dataset is not None else None)
        self._sv.setFrameNumber(nframe)

    def getStackViewColormap(self):
        """
        Returns the colormap from the stackView

        :rtype: silx.gui.colors.Colormap
        """
        return self._sv.getColormap()

    def setStackViewColormap(self, colormap):
        """
        Sets the stackView colormap

        :param colormap: Colormap to set
        :type colormap: silx.gui.colors.Colormap
        """
        self._sv.setColormap(colormap)

    def _mouseSignal(self, info):
        """
        Method called when a signal from the stack is called
        """
        if info['event'] == 'mouseClicked':
            # In case the user has clicked on a pixel in the stack
            data = self.dataset.get_data(self.indices, self._dimension)
            px = info['x']
            py = info['y']
            # Show vertical and horizontal lines for clicked pixel
            self._sv.getPlotWidget().addCurve((px, px), (0, data.shape[1]), legend='x', color='r')
            self._sv.getPlotWidget().addCurve((0, data.shape[2]), (py, py), legend='y', color='r')
            self.plotRockingCurves(data, px, py)

    def _addPoint(self, i):
        """
        Slot to add curve for frame number in rocking curves plot.

        :param int i: frame number
        """
        try:
            self._plot.addCurve([self.x[i]], [self.y[i]], symbol='o', legend='dot_o', color='b')
            i_gauss = i * int((len(self.y_gauss) - 1) / (len(self.x) - 1))
            self._plot.addCurve([self.x_gauss[i_gauss]], [self.y_gauss[i_gauss]], symbol='o', legend='dot_fit', color='r')
        # TODO
        except ValueError:
            pass
        except TypeError:
            pass

    def plotRockingCurves(self, data, px, py):
        """
        Plot rocking curves of data and fitted data at pixel (px, py).

        :param Data data: stack of images to plot
        :param px: x pixel
        :param py: y pixel
        """
        # Get rocking curves from data
        if self.dataset.in_memory:
            y = data[:, int(py), int(px)]
        else:
            y = [image[int(py), int(px)] for image in data]
        if self._dimension is not None:
            axis = self.dataset.dims.ndim - self._dimension[0][0] - 1
            dim = self.dataset.dims.get(axis)
            x = numpy.array([data.metadata[i].get_value(kind=dim.kind, name=dim.name) for i in range(len(data))]).reshape(-1)
            if self._centerDataCheckbox.isChecked():
                middle = (float(x[-1]) - float(x[0])) / 2
                # x = numpy.linspace(-middle, middle, len(x))
                x -= float(x[0]) + middle
            item = [numpy.array(y), None]
        else:
            item = [numpy.array(y), None]
            if self._centerDataCheckbox.isChecked():
                middle = data.shape[0] / 2
                x = numpy.arange(-middle, middle)
            else:
                x = numpy.arange(data.shape[0])
        # Show rocking curves and fitted curve into plot
        self._plot.clear()
        self._plot.addCurve(x, y, legend="data", color='b')
        i = self._sv.getFrameNumber()
        try:
            y_gauss = fit_rocking_curve(item, values=x, num_points=1000)
        except TypeError:
            y_gauss = y
            _logger.warning("Cannot fit")

        # Add curves (points) for stackview frame number
        self.x_gauss = numpy.linspace(x[0], x[-1], len(y_gauss))
        self._plot.addCurve(self.x_gauss, y_gauss, legend="fit", color='r')
        self._plot.addCurve([x[i]], [y[i]], symbol='o', legend='dot_o', color='b')
        i_gauss = i * int((len(y_gauss) - 1) / (len(x) - 1))
        self._plot.addCurve([self.x_gauss[i_gauss]], [y_gauss[i_gauss]], symbol='o', legend='dot_fit', color='r')
        self.x, self.y, self.y_gauss = x, y, y_gauss

    def _grainPlot(self):
        """
        Method called when button for computing fit is clicked
        """
        self._computeFit.hide()
        self._intThresh = self._intThreshLE.text()
        self.sigFitted.emit()
        self._thread.setArgs(self.indices, self._dimension, float(self._intThresh))
        self._thread.finished.connect(self._updateData)
        self._thread.start()
        self._abortFit.show()

    def _updatePlot(self, method):
        """
        Updates the plots with the chosen method
        """
        method = Method(method)
        data = self._update_dataset.get_data(self.indices)
        if method == Method.INTENSITY:
            self._plotMaps.addImage(data.sum(axis=0))
        elif method == Method.FWHM:
            std = numpy.std(data, axis=0)
            std[numpy.isnan(std)] = 0
            self._plotMaps.addImage(darfix.config.FWHM_VAL * std)
        elif method == Method.PEAK:
            if self._dimension is not None:
                axis = self.dataset.dims.ndim - self._dimension[0][0] - 1
                dim_vals = numpy.copy(self.dataset.dims.get(axis).unique_values)
                x = numpy.argmax(data, axis=0)
                if self._centerDataCheckbox.isChecked():
                    middle = float(dim_vals[0]) + (float(dim_vals[-1]) - float(dim_vals[0])) / 2
                    dim_vals -= middle
                image = x * numpy.ptp(dim_vals) / len(data) + min(dim_vals)
                self._plotMaps.addImage(image)
            else:
                x = numpy.argmax(data, axis=0)
                if self._centerDataCheckbox.isChecked():
                    middle = len(data) / 2
                    vals = numpy.linspace(-middle, middle, len(data))
                    x = x * numpy.ptp(vals) / len(data) + numpy.min(vals)
                self._plotMaps.addImage(x)

    def __abort(self):
        self._abortFit.setEnabled(False)
        self.dataset.stop_operation(Operation.FIT)

    def _updateData(self):
        """
        Method called when fit computation has finished
        """
        self._thread.finished.disconnect(self._updateData)
        self._abortFit.hide()
        self._computeFit.show()
        if self._thread.data:
            self._update_dataset = self._thread.data
            assert self._update_dataset is not None
            self._updatePlot(self._methodCB.currentText())
            self._plotMaps.show()
            self._methodCB.show()
        else:
            print("\nCorrection aborted")

    def _filterStack(self, dim=0, val=0):
        if type(dim) is int:
            self._dimension = [[dim], [val]]
        else:
            self._dimension = [dim, val]
        data = self.dataset.get_data(self.indices, self._dimension)
        if data.shape[0]:
            self._sv.setStack(data)
        else:
            self._sv.setStack(None)
        xc = self._sv.getPlotWidget().getCurve('x')
        if xc:
            px = xc.getXData()[0]
            py = self._sv.getPlotWidget().getCurve('y').getYData()[0]
            self.plotRockingCurves(data, px, py)

    def _wholeStack(self):
        self._dimension = None
        self.setStack(self.dataset)
        xc = self._sv.getPlotWidget().getCurve('x')
        if xc:
            px = xc.getXData()[0]
            py = self._sv.getPlotWidget().getCurve('y').getYData()[0]
            self.plotRockingCurves(self.dataset.get_data(self.indices), px, py)

    def _checkboxStateChanged(self):
        """
        Update widgets linked to the checkbox state
        """
        data = self.dataset.get_data(self.indices, self._dimension)
        xc = self._sv.getPlotWidget().getCurve('x')
        if xc:
            px = xc.getXData()[0]
            py = self._sv.getPlotWidget().getCurve('y').getYData()[0]
            self.plotRockingCurves(data, px, py)
        if Method(self._methodCB.currentText()) == Method.PEAK:
            self._updatePlot(Method.PEAK)

    @property
    def intThresh(self):
        return self._intThresh

    @intThresh.setter
    def intThresh(self, intThresh):
        self._intThresh = intThresh
        self._intThreshLE.setText(intThresh)

    @property
    def dimension(self):
        return self._dimension
