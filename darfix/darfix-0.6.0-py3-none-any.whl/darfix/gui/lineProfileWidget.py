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
__date__ = "30/11/2020"


import numpy

from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import Plot1D, Plot2D

import darfix
from darfix.gui.datasetSelectionWidget import FilenameSelectionWidget


class LineProfileWidget(qt.QMainWindow):
    """
    Widget that shows how the intensity looks like in a line profile.
    The user can choose a pixel and the intensity along its x axis is showed.
    """
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        widget = qt.QWidget(parent=self)
        layout = qt.QGridLayout()
        self._filename = FilenameSelectionWidget(parent=self)
        self._filename.filenameChanged.connect(self.setImage)
        self._plot2d = Plot2D(parent=self)
        self._plot2d.setDefaultColormap(Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME,
                                                 normalization="linear"))
        self._plot2d.sigPlotSignal.connect(self._mouseSignal)
        self._plot1d = Plot1D(parent=self)
        layout.addWidget(self._filename, 0, 0, 1, 2)
        layout.addWidget(self._plot2d, 1, 0)
        layout.addWidget(self._plot1d, 1, 1)
        widget.setLayout(layout)
        widget.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.setCentralWidget(widget)

    def setImage(self):
        """
        Set image
        """
        filename = self._filename.getFilename()
        self._image = numpy.load(filename)
        self._plot2d.addImage(self._image)

    def _mouseSignal(self, info):
        """
        Method called when a signal from the plot is called
        """
        if info['event'] == 'mouseClicked':
            py = info['y']
            self._plot2d.addCurve((0, self._image.shape[1]), (py, py), legend='y', color='g')
            line_profile = self._image[int(py), :]
            self._plot1d.addCurve(numpy.arange(len(line_profile)), line_profile, color="g")
