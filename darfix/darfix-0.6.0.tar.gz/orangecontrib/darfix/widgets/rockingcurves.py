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


from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input
from silx.gui.colors import Colormap
from darfix.gui.rockingCurvesWidget import RockingCurvesWidget


class RockingCurvesWidgetOW(OWWidget):
    """
    Widget that computes the background substraction from a dataset
    """

    name = "rocking curves"
    icon = "icons/curves.png"
    want_main_area = False

    # Inputs
    class Inputs:
        dataset = Input("dataset", tuple)
        colormap = Input("colormap", Colormap)

    int_thresh = Setting(str())
    dimension = Setting(list)

    def __init__(self):
        super().__init__()

        self._widget = RockingCurvesWidget(parent=self)
        self._widget.sigFitted.connect(self._fit)
        self.controlArea.layout().addWidget(self._widget)
        if self.int_thresh:
            self._widget.intThresh = self.int_thresh

    @Inputs.dataset
    def setDataset(self, dataset):
        if dataset:
            self._widget.setDataset(*dataset)
            self.open()

    @Inputs.colormap
    def setColormap(self, colormap):
        self._widget.setStackViewColormap(colormap)

    def _fit(self):
        self.int_thresh = self._widget.intThresh
        self.dimension = self._widget.dimension
