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

__authors__ = ["H. Payno", "J. Garriga"]
__license__ = "MIT"
__date__ = "24/09/2019"


from silx.gui import qt
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from darfix.core import utils
from darfix.core.dataset import Dimension
from darfix.gui.dimensionsWidget import DimensionWidget
from functools import partial
import logging

_logger = logging.getLogger(__file__)


class DimensionWidgetOW(OWWidget):
    """
    Widget used to define the calibration of the experimentation (select motor
    positions...)
    """
    name = "dimension definition"
    id = "orange.widgets.darfix.dimensiondefinition"
    description = "Define the dimension followed during the acquisition"
    icon = "icons/param_dims.svg"

    priority = 4
    category = "esrfWidgets"
    keywords = ["dataset", "calibration", "motor", "angle", "geometry"]

    # Inputs
    class Inputs:
        dataset = Input("dataset", tuple)

    # Outputs
    class Outputs:
        dataset = Output("dataset", tuple)

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    _dims = Setting(dict(), schema_only=True)

    def __init__(self):
        super().__init__()
        layout = gui.vBox(self.mainArea, 'dimensions').layout()
        self._widget = DimensionWidget(parent=self)
        layout.addWidget(self._widget)

        # buttons
        types = qt.QDialogButtonBox.Ok
        self.buttons = qt.QDialogButtonBox(parent=self)
        self.buttons.setStandardButtons(types)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.validate)
        self.buttons.button(qt.QDialogButtonBox.Ok).setEnabled(False)

        # connect Signal/SLOT
        _callbackValid = partial(self.buttons.button(qt.QDialogButtonBox.Ok).setEnabled, True)
        self._widget.fitSucceed.connect(_callbackValid)
        _callbackInvalid = partial(self.buttons.button(qt.QDialogButtonBox.Ok).setDisabled, True)
        self._widget.fitFailed.connect(_callbackInvalid)

        # expose API
        self.setDims = self._widget.setDims

    @property
    def _ndim(self):
        return self._widget.ndim

    @property
    def _dataset(self):
        return self._widget.dataset

    @Inputs.dataset
    def setDataset(self, dataset):
        """
        Input signal to set the dataset.
        """
        self.buttons.button(qt.QDialogButtonBox.Ok).setEnabled(False)
        if dataset is not None:
            try:
                self._widget.setDataset(*dataset)
                # load properties
                _dims = utils.convertDictToDim(self._dims)
                self._widget.setDims(_dims)
            except ValueError as e:
                qt.QMessageBox.warning(self,
                                       'Fail to setup dimension definition',
                                       str(e))
            else:
                self.show()

    def validate(self):
        """
        Tries to fit the dimensions into the dataset.
        """
        self.Outputs.dataset.send(self._widget.getDataset())
        self.updateProperties()
        OWWidget.accept(self)

    def updateProperties(self):
        """
        Save dimensions to Settings.
        """
        self._dims = {}
        if self._widget.ndim == 0:
            return
        else:
            for _dim in self._widget.dims.values():
                assert isinstance(_dim, Dimension)
                axis = _dim.axis
                self._dims[axis] = _dim.to_dict()
