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
from Orange.widgets.widget import OWWidget, Input, Output
from silx.gui import qt
from silx.gui.colors import Colormap
from darfix.gui.shiftCorrectionWidget import ShiftCorrectionDialog


class ShiftCorrectionWidgetOW(OWWidget):
    """
    Widget to make the shift correction of a dataset.
    """

    name = "shift correction"
    icon = "icons/shift_correction.svg"
    want_main_area = False

    # Inputs
    class Inputs:
        dataset = Input("dataset", tuple)
        colormap = Input("colormap", Colormap)

    # Outputs
    class Outputs:
        dataset = Output("dataset", tuple)
        colormap = Output("colormap", Colormap)

    # Settings
    shift = Setting(list(), schema_only=True)

    def __init__(self):
        super().__init__()
        qt.QLocale.setDefault(qt.QLocale("en_US"))

        self._widget = ShiftCorrectionDialog(parent=self)
        self._widget.okSignal.connect(self._sendSignal)
        self.controlArea.layout().addWidget(self._widget)

        if self.shift:
            self._widget.shift = self.shift

    @Inputs.dataset
    def set_dataset(self, dataset):
        if dataset:
            self._widget.setDataset(*dataset)
            self.open()
        else:
            self._widget.clearStack()
            # Emit None
            self.Outputs.dataset.send(dataset)

    @Inputs.colormap
    def setColormap(self, colormap):
        self._widget.setStackViewColormap(colormap)

    def _sendSignal(self):
        """
        Function to emit the new dataset.
        """
        self.shift = self._widget.shift
        self.Outputs.dataset.send(self._widget.mainWindow.getDataset())
        self.Outputs.colormap.send(self._widget.mainWindow.getStackViewColormap())
        self.close()
