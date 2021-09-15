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
__date__ = "10/08/2021"

from matplotlib.colors import hsv_to_rgb
import numpy

from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D
from silx.image.marchingsquares import find_contours
from silx.math.medianfilter import medfilt2d
from silx.utils.enum import Enum as _Enum
from silx.io.dictdump import dicttonx

import darfix
from .operationThread import OperationThread


class Method(_Enum):
    """
    Different maps to show
    """
    COM = "Center of mass"
    FWHM = "FWHM"
    SKEWNESS = "Skewness"
    KURTOSIS = "Kurtosis"
    ORI_DIST = "Orientation distribution"
    MOSAICITY = "Mosaicity"


class GrainPlotWidget(qt.QMainWindow):
    """
    Widget to show a series of maps for the analysis of the data.
    """
    sigComputed = qt.Signal()

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)

        self._methodCB = qt.QComboBox()
        self._methodCB.addItems(Method.values())
        for i in range(len(Method)):
            self._methodCB.model().item(i).setEnabled(False)
        self._methodCB.currentTextChanged.connect(self._updatePlot)
        self._plotWidget = qt.QWidget()
        plotsLayout = qt.QHBoxLayout()
        self._plotWidget.setLayout(plotsLayout)
        self._contoursPlot = Plot2D(parent=self)
        widget = qt.QWidget(parent=self)
        layout = qt.QVBoxLayout()
        self._levelsWidget = qt.QWidget()
        levelsLayout = qt.QGridLayout()
        levelsLabel = qt.QLabel("Number of levels:")
        self._levelsLE = qt.QLineEdit("20")
        self._levelsLE.setToolTip("Number of levels to use when finding the contours")
        self._levelsLE.setValidator(qt.QIntValidator())
        self._computeContoursB = qt.QPushButton("Compute")
        self._centerDataCheckbox = qt.QCheckBox("Center angle values")
        self._centerDataCheckbox.stateChanged.connect(self._checkboxStateChanged)
        levelsLayout.addWidget(levelsLabel, 0, 0, 1, 1)
        levelsLayout.addWidget(self._levelsLE, 0, 1, 1, 1)
        levelsLayout.addWidget(self._centerDataCheckbox, 0, 2, 1, 1)
        levelsLayout.addWidget(self._computeContoursB, 1, 2, 1, 1)
        levelsLayout.addWidget(self._contoursPlot, 2, 0, 1, 3)
        self._levelsWidget.setLayout(levelsLayout)
        self._mosaicityPlot = Plot2D(parent=self)
        self._exportButton = qt.QPushButton("Export maps")
        self._exportButton.setEnabled(False)
        self._exportButton.clicked.connect(self.exportMaps)
        layout.addWidget(self._methodCB)
        layout.addWidget(self._levelsWidget)
        layout.addWidget(self._plotWidget)
        layout.addWidget(self._mosaicityPlot)
        layout.addWidget(self._exportButton)
        self._plotWidget.hide()
        self._mosaicityPlot.hide()
        self._mosaicityPlot.getColorBarWidget().hide()
        widget.setLayout(layout)
        widget.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.setCentralWidget(widget)

    def setDataset(self, dataset, indices=None, bg_indices=None, bg_dataset=None):
        """
        Dataset setter.

        :param Dataset dataset: dataset
        """
        self.dataset = dataset
        self.indices = indices
        self.bg_indices = bg_indices
        self.bg_dataset = bg_dataset
        for i in range(len(Method)):
            self._methodCB.model().item(i).setEnabled(False)
        scale = 100
        if self.dataset.transformation:
            px = self.dataset.transformation[0][0][0]
            py = self.dataset.transformation[1][0][0]
            xscale = (self.dataset.transformation[0][-1][-1] - px) / len(self.dataset.transformation[0][0])
            yscale = (self.dataset.transformation[1][-1][-1] - py) / len(self.dataset.transformation[1][0])
            self.origin = (px, py)
            self.scale = (xscale, yscale)
        if self.dataset.dims.ndim > 1:
            self._curves = {}
            self.ori_dist, self.hsv_key = self.dataset.compute_mosaicity_colorkey()
            xdim = self.dataset.dims.get(1)
            ydim = self.dataset.dims.get(0)
            xscale = (xdim.unique_values[-1] - xdim.unique_values[0]) / (xdim.size - 1)
            yscale = (ydim.unique_values[-1] - ydim.unique_values[0]) / (ydim.size - 1)

            self._contoursPlot.addImage(hsv_to_rgb(self.hsv_key), xlabel=xdim.name,
                                        ylabel=ydim.name, scale=(xscale / scale, yscale / scale))
            self._contoursPlot.getColorBarWidget().hide()
            self._curvesColormap = Colormap(name='temperature',
                                            vmin=numpy.min(self.ori_dist),
                                            vmax=numpy.max(self.ori_dist))
            self._computeContoursB.clicked.connect(self._computeContours)
            self._methodCB.model().item(4).setEnabled(True)
            self._methodCB.setCurrentIndex(4)
        self._thread = OperationThread(self, self.dataset.apply_moments)
        self._thread.setArgs(self.indices)
        self._thread.finished.connect(self._updateData)
        self._thread.start()
        for i in reversed(range(self._plotWidget.layout().count())):
            self._plotWidget.layout().itemAt(i).widget().setParent(None)

        self._plots = []
        for axis, dim in self.dataset.dims:
            self._plots += [Plot2D(parent=self)]
            self._plots[-1].setGraphTitle(dim.name)
            self._plots[-1].setDefaultColormap(Colormap(name='viridis'))
            self._plotWidget.layout().addWidget(self._plots[-1])

    def _updateData(self):
        """
        Updates the plots with the data computed in the thread
        """
        self._thread.finished.disconnect(self._updateData)
        if self._thread.data is not None:
            self._moments = self._thread.data
            self._updatePlot(self._methodCB.currentText())
            rg = len(Method) if self.dataset.dims.ndim > 1 else 4
            for i in range(rg):
                self._methodCB.model().item(i).setEnabled(True)
            self._methodCB.setCurrentIndex(0)
            self._exportButton.setEnabled(True)
        else:
            print("\nComputation aborted")

    def _checkboxStateChanged(self, state):
        """
        Update widgets linked to the checkbox state
        """
        scale = 100
        xdim = self.dataset.dims.get(1)
        ydim = self.dataset.dims.get(0)
        xsize = xdim.size - 1
        ysize = ydim.size - 1
        xscale = (xdim.unique_values[-1] - xdim.unique_values[0]) / xsize
        yscale = (ydim.unique_values[-1] - ydim.unique_values[0]) / ysize
        origin = (- xscale * xsize / 2, - yscale * ysize / 2) if state else (0., 0.)
        self._contoursPlot.addImage(hsv_to_rgb(self.hsv_key), xlabel=xdim.name, ylabel=ydim.name,
                                    origin=origin, scale=(xscale / scale, yscale / scale))

        self._contoursPlot.remove(kind='curve')

    def _computeContours(self):
        self._contoursPlot.remove(kind='curve')

        if self.ori_dist is not None:
            polygons = []
            levels = []
            for i in numpy.linspace(numpy.min(self.ori_dist), numpy.max(self.ori_dist), int(self._levelsLE.text())):
                polygons.append(find_contours(self.ori_dist, i))
                levels.append(i)

            colors = self._curvesColormap.applyToData(levels)
            xdim = self.dataset.dims.get(1)
            ydim = self.dataset.dims.get(0)
            self._curves = {}
            for ipolygon, polygon in enumerate(polygons):
                # iso contours
                for icontour, contour in enumerate(polygon):
                    if len(contour) == 0:
                        continue
                    # isClosed = numpy.allclose(contour[0], contour[-1])
                    x = contour[:, 1]
                    y = contour[:, 0]
                    rescale_x = (xdim.unique_values[-1] - xdim.unique_values[0]) / (xdim.size - 1)
                    rescale_y = (ydim.unique_values[-1] - ydim.unique_values[0]) / (ydim.size - 1)
                    x *= rescale_x
                    y *= rescale_y
                    if self._centerDataCheckbox.isChecked():
                        xcenter = (xdim.unique_values[-1] - xdim.unique_values[0]) / 2
                        x -= xcenter
                        ycenter = (ydim.unique_values[-1] - ydim.unique_values[0]) / 2
                        y -= ycenter
                    legend = "poly{}.{}".format(icontour, ipolygon)
                    self._curves[legend] = {
                        "points": (x.copy(), y.copy()),
                        "color": colors[ipolygon]
                    }
                    self._contoursPlot.addCurve(x=x, y=y, linestyle="-", linewidth=2.0,
                                                legend=legend, resetzoom=False,
                                                color=colors[ipolygon])

    def _computeMosaicity(self):

        norms0 = (self._moments[0][0] - numpy.min(self._moments[0][0])) / numpy.ptp(self._moments[0][0])
        norms1 = (self._moments[1][0] - numpy.min(self._moments[1][0])) / numpy.ptp(self._moments[1][0])

        mosaicity = numpy.stack((norms0, norms1, numpy.ones(self._moments[0].shape[1:])), axis=2)
        return mosaicity

    def _updatePlot(self, method):
        method = Method(method)
        self._levelsWidget.hide()
        self._mosaicityPlot.hide()
        if method == Method.ORI_DIST:
            self._levelsWidget.show()
            self._plotWidget.hide()
        elif method == Method.FWHM:
            self._plotWidget.show()
            for i, plot in enumerate(self._plots):
                plot.addImage(darfix.config.FWHM_VAL * self._moments[i][1])
        elif method == Method.COM:
            self._plotWidget.show()
            if self.dataset.transformation is not None:
                for i, plot in enumerate(self._plots):
                    plot.addImage(self._moments[i][0], origin=self.origin, scale=self.scale, xlabel='µm', ylabel='µm')
            else:
                for i, plot in enumerate(self._plots):
                    plot.addImage(self._moments[i][0], xlabel='pixels', ylabel='pixels')
        elif method == Method.SKEWNESS:
            self._plotWidget.show()
            for i, plot in enumerate(self._plots):
                plot.addImage(self._moments[i][2])
        elif method == Method.KURTOSIS:
            self._plotWidget.show()
            for i, plot in enumerate(self._plots):
                plot.addImage(self._moments[i][3])
        elif method == Method.MOSAICITY:
            self._plotWidget.hide()
            if self.dataset.transformation:
                self._mosaicityPlot.addImage(hsv_to_rgb(self._computeMosaicity()),
                                             origin=self.origin, scale=self.scale,
                                             xlabel='µm', ylabel='µm')
            else:
                self._mosaicityPlot.addImage(hsv_to_rgb(self._computeMosaicity()))

            self._mosaicityPlot.show()

    def _opticolor(self, img, minc, maxc):
        img = img.copy()
        Cnn = img[~numpy.isnan(img)]
        sortC = sorted(Cnn)
        Imin = sortC[int(numpy.floor(len(sortC) * minc))]
        Imax = sortC[int(numpy.floor(len(sortC) * maxc))]
        img[img > Imax] = Imax
        img[img < Imin] = Imin

        return medfilt2d(img)

    def exportMaps(self):
        """
        Creates dictionay with maps information and exports it to a nexus file
        """
        if self.dataset and self.dataset.dims.ndim > 1:
            nx = {
                "entry": {
                    "MOSAICITY": {
                        ">" + Method.MOSAICITY.name: "../maps/" + Method.MOSAICITY.name,
                        "@signal": Method.MOSAICITY.name,
                        "@NX_class": "NXdata"
                    },
                    "maps": {
                        Method.MOSAICITY.name: hsv_to_rgb(self._computeMosaicity()),
                        Method.MOSAICITY.name + "@interpretation": "rgba-image",
                        "@NX_class": "NXcollection"
                    },
                    Method.ORI_DIST.name: {
                        "key": {
                            "image": hsv_to_rgb(self.hsv_key),
                            "scale": self._contoursPlot.getImage().getScale(),
                            "xlabel": self._contoursPlot.getImage().getXLabel(),
                            "ylabel": self._contoursPlot.getImage().getYLabel(),
                            "image@interpretation": "rgba-image",
                        },
                        "curves": self._curves
                    },
                    "@NX_class": "NXentry",
                    "@default": "data",
                },
                "@NX_class": "NXroot",
                "@default": "entry"
            }

            for axis, dim in self.dataset.dims:
                nx["entry"]["maps"].update(
                    {
                        Method.COM.name: self._moments[axis][0],
                        Method.FWHM.name: self._moments[axis][1],
                        Method.SKEWNESS.name: self._moments[axis][2],
                        Method.KURTOSIS.name: self._moments[axis][3]
                    }
                )
        else:
            nx = {
                "entry": {
                    "data": {
                        ">" + Method.COM.name: "../maps/" + Method.COM.name,
                        "@signal": Method.COM.name,
                        "@NX_class": "NXdata"
                    },
                    "maps": {
                        Method.COM.name: self._moments[0][0],
                        Method.FWHM.name: self._moments[0][1],
                        Method.SKEWNESS.name: self._moments[0][2],
                        Method.KURTOSIS.name: self._moments[0][3],
                        "@NX_class": "NXcollection"
                    },
                    "@NX_class": "NXentry",
                    "@default": "data",
                },
                "@NX_class": "NXroot",
                "@default": "entry"
            }

        fileDialog = qt.QFileDialog()

        fileDialog.setFileMode(fileDialog.AnyFile)
        fileDialog.setAcceptMode(fileDialog.AcceptSave)
        fileDialog.setOption(fileDialog.DontUseNativeDialog)
        fileDialog.setDefaultSuffix(".h5")
        if fileDialog.exec_():
            dicttonx(nx, fileDialog.selectedFiles()[0])
