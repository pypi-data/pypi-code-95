# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017-2019 European Synchrotron Radiation Facility
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
__date__ = "26/04/2021"

import numpy

from silx.gui import qt
from silx.gui import icons
from silx.gui.colors import Colormap
from silx.gui.plot import ScatterView, StackView, Plot1D
from silx.gui.widgets.FrameBrowser import HorizontalSliderWithBrowser
import silx.resources

import darfix
from darfix.io.utils import write_components


class DisplayComponentsWidget(qt.QMainWindow):
    """
    Widget to apply blind source separation.
    """

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)

        # Widget with the type of bss and the number of components to compute
        widget = qt.QWidget(self)
        self._sv_components = StackView(parent=self)
        self._sv_components.setColormap(Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME,
                                        normalization=darfix.config.DEFAULT_COLORMAP_NORM))
        self._sv_components.setGraphTitle("Components")
        self._sv_components.sigFrameChanged.connect(self._setCurve)

        self._plot_rocking_curves = PlotRockingCurves()
        self._plot_rocking_curves.sigFrameChanged.connect(self._updateFrameNumber)
        self._plot_rocking_curves.sigMotorChanged.connect(self._updateMotorAxis)
        self._plot_rocking_curves.sigActiveCurveChanged.connect(self._activeCurveChanged)

        self._scatter_rocking_curves = ScatterView()
        self._scatter_rocking_curves.hide()

        self._toolbar = qt.QToolBar(parent=self)
        self._toolbar.setIconSize(self._toolbar.iconSize() * 1.2)
        if "darfix" not in silx.resources._RESOURCE_DIRECTORIES:
            silx.resources.register_resource_directory("darfix", "darfix.resources")
        curves_icon = icons.getQIcon('darfix:gui/icons/curves')
        scatter_icon = icons.getQIcon('darfix:gui/icons/scatter')
        self.curves_action = qt.QAction(curves_icon, "Curves", self)
        self.curves_action.setCheckable(True)
        self.curves_action.setChecked(True)
        self.colormap_action = qt.QAction(scatter_icon, "Scatter", self)
        self.colormap_action.setCheckable(True)
        self.curves_action.toggled.connect(self._activateCurvesPlot)
        self.colormap_action.triggered.connect(self.curves_action.toggle)
        self._toolbar.addAction(self.curves_action)
        self._toolbar.addAction(self.colormap_action)
        self._toolbar.setOrientation(qt.Qt.Vertical)
        self._toolbar.hide()

        self.bottom_widget = qt.QWidget(self)
        layout = qt.QGridLayout()
        componentsLabel = qt.QLabel("Components")
        rockingCurvesLabel = qt.QLabel("Rocking curves")
        font = qt.QFont()
        font.setBold(True)
        componentsLabel.setFont(font)
        rockingCurvesLabel.setFont(font)
        layout.addWidget(componentsLabel, 1, 0, 1, 2, qt.Qt.AlignCenter)
        layout.addWidget(rockingCurvesLabel, 1, 3, 1, 2, qt.Qt.AlignCenter)
        layout.addWidget(self._sv_components, 2, 0, 2, 2)
        layout.addWidget(self._plot_rocking_curves, 2, 3, 2, 2)
        layout.addWidget(self._scatter_rocking_curves, 2, 3, 2, 2)
        layout.addWidget(self._toolbar, 2, 5, 2, 1)
        self.saveB = qt.QPushButton("Save components")
        self.saveB.pressed.connect(self._saveComp)
        layout.addWidget(self.saveB, 4, 4, 1, -1)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def hideButton(self):
        self._computeB.hide()

    def showButton(self):
        self._computeB.show()

    def setComponents(self, components, W, dimensions, shape):
        """
        Components setter. Updates the plots with the components and their
        corresponding rocking curves.

        :param array_like components: stack of images with the components
        :param array_like W: array with the rocking curves intensity
        :param dict dimensions: dictionary with the values of the dimensions
        """
        self.components = components
        self.W = W
        self.dimensions = dimensions
        self.dimensions_shape = shape
        self._activateCurvesPlot(True)
        self._sv_components.setStack(self.components)
        self._plot_rocking_curves.getPlot().clear()
        for i in range(len(self.W.T)):
            self._plot_rocking_curves.getPlot().addCurve(numpy.arange(len(self.W.T[i])),
                                                         self.W.T[i], legend=str(i))
        if self.dimensions:
            colormap = Colormap(name='jet', normalization='linear')
            keys = list(self.dimensions.keys())
            self._scatter_rocking_curves.getPlotWidget().setGraphXLabel(keys[0])
            self._scatter_rocking_curves.getPlotWidget().setGraphYLabel(keys[1])
            self._scatter_rocking_curves.setData(
                self.dimensions[keys[0]].astype(numpy.float),
                self.dimensions[keys[1]].astype(numpy.float), self.W.T[0])
            self._scatter_rocking_curves.setColormap(colormap)
            self._scatter_rocking_curves.resetZoom()

            self._plot_rocking_curves.showMotors(True)
            self._toolbar.show()
            self._plot_rocking_curves.resetDimensions()
            # Motor dimension and index
            self.dimension = 0
            self.index = 0
            for dimension in self.dimensions:
                self._plot_rocking_curves.addDimension(dimension)
        else:
            self._plot_rocking_curves.showMotors(False)
            self._toolbar.hide()

        self._plot_rocking_curves.getPlot().setActiveCurve("0")

    def _activateCurvesPlot(self, checked=False):
        if checked:
            self.colormap_action.setChecked(False)
            self._scatter_rocking_curves.hide()
            self._plot_rocking_curves.show()
        else:
            self._plot_rocking_curves.hide()
            self._scatter_rocking_curves.show()

    def _saveComp(self):
        """
        Loads the file from a FileDialog.
        """
        fileDialog = qt.QFileDialog()

        fileDialog.setFileMode(fileDialog.AnyFile)
        fileDialog.setAcceptMode(fileDialog.AcceptSave)
        fileDialog.setOption(fileDialog.DontUseNativeDialog)
        fileDialog.setDefaultSuffix(".h5")
        if fileDialog.exec_():
            write_components(fileDialog.selectedFiles()[0], 'entry',
                             self.dimensions, self.W, self.components, 1)

    def _activeCurveChanged(self, prev_legend=None, legend=None):
        if legend:
            self._setComponent(int(legend))

    def _setComponent(self, index=None):
        if index is not None:
            status = self._sv_components.blockSignals(True)
            self._sv_components.setFrameNumber(index)
            self._sv_components.blockSignals(status)
            values = numpy.array(list(self.dimensions.values())).astype(numpy.float)
            if self.dimensions:
                self._scatter_rocking_curves.setData(values[0], values[1], self.W.T[index])

    def _setCurve(self, index=-1):
        if index >= 0:
            status = self._plot_rocking_curves.blockSignals(True)
            self._plot_rocking_curves.getPlot().setActiveCurve(str(index))
            self._plot_rocking_curves.blockSignals(status)
            values = numpy.array(list(self.dimensions.values())).astype(numpy.float)
            if self.dimensions:
                self._scatter_rocking_curves.setData(values[0], values[1], self.W.T[index])

    def _updateMotorAxis(self, axis=-1):
        """
        Updates the motor to show the rocking curve from.

        :param int axis: 0 if no motor is chosen, else axis of the motor.
        """
        if axis == 0:
            # Whole rocking curves are showed
            self._plot_rocking_curves.clear()
            for i in range(len(self.W.T)):
                self._plot_rocking_curves.addCurve(numpy.arange(len(self.W.T[i])), self.W.T[i], legend=str(i))
            self._plot_rocking_curves.getBrowser().setEnabled(False)
            self._plot_rocking_curves.getPlot().setGraphXLabel("Image id")
        elif axis != -1 and axis is not None:
            self.dimension = len(self.dimensions) - axis
            self._plot_rocking_curves.clear()
            self._plot_rocking_curves.getBrowser().setEnabled(True)
            self._plot_rocking_curves.getBrowser().setRange(0, self.dimensions_shape[self.dimension] - 1)
            self._plot_rocking_curves.getBrowser().setValue(0)
            text = list(self.dimensions.keys())[self.dimension]
            self._plot_rocking_curves.getPlot().setGraphXLabel(text)
            dim_values = list(self.dimensions.values())[self.dimension]
            dim_values = numpy.take(dim_values.reshape(self.dimensions_shape), self.index, self.dimension)
            for i in range(len(self.W.T)):
                W = numpy.take(self.W.T[i].reshape(self.dimensions_shape), self.index, self.dimension)
                self._plot_rocking_curves.addCurve(dim_values, W, legend=str(i))
        else:
            raise ValueError('Axis %s is not managed' % axis)

    def _updateFrameNumber(self, index):
        """Update the current plot.

        :param index: index of the frame to be displayed
        """
        self.index = index
        self._plot_rocking_curves.clear()
        dim_values = list(self.dimensions.values())[self.dimension]
        dim_values = numpy.take(dim_values.reshape(self.dimensions_shape), self.index, self.dimension)
        for i in range(len(self.W.T)):
            W = numpy.take(self.W.T[i].reshape(self.dimensions_shape), self.index, self.dimension)
            self._plot_rocking_curves.addCurve(dim_values, W, legend=str(i))

    def setStackViewColormap(self, colormap):
        """
        Sets the stackView colormap

        :param colormap: Colormap to set
        :type colormap: silx.gui.colors.Colormap
        """
        self._sv_components.setColormap(colormap)

    def getStackViewColormap(self):
        """
        Returns the colormap from the stackView

        :rtype: silx.gui.colors.Colormap
        """
        return self._sv_components.getColormap()


class PlotRockingCurves(qt.QMainWindow):
    """
    Widget to plot the rocking curves of the components. It can be filtered
    to show only the rocking curves of a certain moving dimension.
    """

    sigFrameChanged = qt.Signal(int)
    sigMotorChanged = qt.Signal(int)
    sigActiveCurveChanged = qt.Signal(object, object)

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)

        self._plot = Plot1D()
        self._plot.setGraphTitle("Rocking curves")
        self._plot.setGraphXLabel("Image id")
        self._plot.sigActiveCurveChanged.connect(self.sigActiveCurveChanged)

        self._motors = qt.QWidget()
        self._motors.setLayout(self._motorsLayout())
        self._motors.hide()
        layout = qt.QVBoxLayout()
        layout.addWidget(self._plot)
        layout.addWidget(self._motors)

        centralWidget = qt.QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.addCurve = self._plot.addCurve

    def _motorsLayout(self):
        # If dataset data is reshaped
        # Creates widget to move through the motors dimensions
        layout = qt.QHBoxLayout()
        cb_label = qt.QLabel("Static motor:")
        self._cb = qt.QComboBox()
        self._cb.setCurrentIndex(0)
        # Default: all of the rocking curves are shown
        self._cb.addItem("None")
        browser_label = qt.QLabel("Motor index:")
        self._browser = HorizontalSliderWithBrowser()
        self._browser.setRange(0, 0)
        # Browser only activated with choosen dimension
        self._browser.setEnabled(False)

        # Connect browser
        self._browser.valueChanged[int].connect(self.sigFrameChanged)
        # Connect combobox
        self._cb.currentIndexChanged.connect(self.sigMotorChanged)

        layout.addWidget(cb_label)
        layout.addWidget(self._cb)
        layout.addWidget(browser_label)
        layout.addWidget(self._browser)

        return layout

    def getPlot(self):
        return self._plot

    def getBrowser(self):
        return self._browser

    def getDimensionsCB(self):
        return self._cb

    def clear(self):
        self._plot.clear()

    def showMotors(self, show=True):
        self._motors.setVisible(show)

    def addDimension(self, dimension):
        self._cb.addItem(dimension)

    def resetDimensions(self):
        oldState = self._cb.blockSignals(True)
        self._cb.clear()
        self._cb.addItem("None")
        self._cb.blockSignals(oldState)
