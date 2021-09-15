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
__date__ = "20/11/2020"

import logging
_logger = logging.getLogger(__file__)
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Output

from silx.gui import qt

from darfix.gui.operationThread import OperationThread
from darfix.gui.datasetSelectionWidget import DatasetSelectionWidget


class DataSelectionWidgetOW(OWWidget):
    """
    Widget to select the data to be used in the dataset.
    """

    name = "data selection"
    icon = "icons/upload.svg"
    want_main_area = False

    # Outputs
    class Outputs:
        dataset = Output("dataset", tuple)

    # Settings
    filenames = Setting(list(), schema_only=True)
    raw_filename = Setting(str(), schema_only=True)
    dark_filename = Setting(str(), schema_only=True)
    in_disk = Setting(bool(), schema_only=True)

    def __init__(self):
        super().__init__()

        self._widget = DatasetSelectionWidget()
        types = qt.QDialogButtonBox.Ok
        _buttons = qt.QDialogButtonBox(parent=self)
        _buttons.setStandardButtons(types)

        self.controlArea.layout().addWidget(self._widget)
        self.controlArea.layout().addWidget(_buttons)

        _buttons.accepted.connect(self._getDataset)

        self.__updatingData = False
        self.setDataset()

    def setDataset(self):
        self._widget.setRawFilenames(self.filenames)
        self._widget.setRawFilename(self.raw_filename)
        self._widget.setDarkFilename(self.dark_filename)
        if self.in_disk:
            self._widget._inDiskCB.setChecked(True)

    def _getDataset(self):
        if self.__updatingData:
            _logger.warning("Another dataset is being loaded, please wait \
                            until it has finished")
            return

        _logger.warning('create new dataset and emit them')
        # Create and start thread
        self._thread = OperationThread(self, self._widget.loadDataset)
        self._thread.finished.connect(self._sendSignal)
        self._thread.start()

        self.updateSettings()
        self.__updatingData = True
        self.information("Downloading dataset")

    def _sendSignal(self):
        """
        Function to emit the new dataset.
        Finishes the `downloading` state.
        """
        self._thread.finished.disconnect(self._sendSignal)
        self.__updatingData = False
        self.information()
        if self._thread.data:
            self.Outputs.dataset.send(self._widget.getDataset())
            self.close()

    def updateSettings(self):
        """
        Function to update the settings saved into the widget.
        """
        self.filenames = self._widget.getRawFilenames()
        self.raw_filename = self._widget.getRawFilename()
        self.dark_filename = self._widget.getDarkFilename()
        self.in_disk = self._widget._inDiskCB.isChecked()
