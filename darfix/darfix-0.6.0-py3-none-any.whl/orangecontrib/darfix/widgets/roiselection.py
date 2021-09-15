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
__date__ = "11/12/2020"


# import numpy

from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from silx.gui.colors import Colormap
# from silx.gui import qt
from darfix.gui.roiSelectionWidget import ROISelectionWidget


class RoiSelectionWidgetOW(OWWidget):

    name = "roi selection"
    icon = "icons/roi.png"
    want_main_area = False

    # Inputs/Outputs
    class Inputs:
        dataset = Input("dataset", tuple)
        colormap = Input("colormap", Colormap)

    class Outputs:
        dataset = Output("dataset", tuple)
        colormap = Output("colormap", Colormap)

    # Settings
    roi_origin = Setting(list(), schema_only=True)
    roi_size = Setting(list(), schema_only=True)

    def __init__(self):
        super().__init__()

        self._widget = ROISelectionWidget(parent=self)
        # self._button = qt.QPushButton('Ok', parent=self)
        # self._button.setEnabled(False)
        self.controlArea.layout().addWidget(self._widget)
        # self.controlArea.layout().addWidget(self._button)
        self._widget.sigComputed.connect(self._sendSignal)

        # self._button.pressed.connect(self._createRoi)

    @Inputs.dataset
    def setDataset(self, dataset):
        if dataset:
            self._widget.setDataset(*dataset)
        else:
            self._widget.clearStack()
            # Emit None
            self.Outputs.dataset.send(dataset)

        # Set saved roi
        if len(self.roi_origin) and len(self.roi_size):
            self._widget.setRoi(origin=self.roi_origin, size=self.roi_size)

        self.open()

    @Inputs.colormap
    def setColormap(self, colormap):
        self._widget.setStackViewColormap(colormap)

    def _sendSignal(self, roi_origin=[], roi_size=[]):
        """
        Emits the signal with the new dataset.
        """
        self.close()
        self.roi_origin = roi_origin
        self.roi_size = roi_size
        self.Outputs.dataset.send(self._widget.getDataset())
        self.Outputs.colormap.send(self._widget.getStackViewColormap())
