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


from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from silx.gui.colors import Colormap
from darfix.gui.blindSourceSeparationWidget import BSSWidget


class BlindSourceSeparationWidgetOW(OWWidget):
    """
    Widget that computes the background substraction from a dataset
    """

    name = "blind source separation"
    icon = "icons/bss.png"
    want_main_area = False

    # Settings
    method = Setting(str(), schema_only=True)
    n_comp = Setting(int(), schema_only=True)

    # Inputs
    class Inputs:
        dataset = Input("dataset", tuple)
        colormap = Input("colormap", Colormap)

    # Outputs
    class Outputs:
        dataset = Output("dataset", tuple)
        colormap = Output("colormap", Colormap)

    def __init__(self):
        super().__init__()

        self._widget = BSSWidget(parent=self)
        self._widget.sigComputed.connect(self._updateSettings)
        self.controlArea.layout().addWidget(self._widget)

    def _updateSettings(self, method, n_comp):
        self.method = method.name
        self.n_comp = n_comp

    @Inputs.dataset
    def setDataset(self, dataset):
        if dataset:
            self._widget.setDataset(*dataset)
            self.open()
        self.Outputs.dataset.send(dataset)
        self.Outputs.colormap.send(self._widget.getDisplayComponentsWidget().getStackViewColormap())

    @Inputs.colormap
    def setColormap(self, colormap):
        self._widget.getDisplayComponentsWidget().setStackViewColormap(colormap)
