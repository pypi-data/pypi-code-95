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


from Orange.widgets.settings import Setting
from silx.gui import qt
from Orange.widgets.widget import OWWidget, Input, Output
from darfix.gui.magnificationWidget import MagnificationWidget
from darfix.gui.rsmWidget import RSMWidget


class TransformationWidgetOW(OWWidget):
    """
    Widget that computes the background substraction from a dataset
    """

    name = "transformation"
    # icon = "icons/pca.png"
    want_main_area = False

    # Inputs
    class Inputs:
        dataset = Input("dataset", tuple)

    # Outputs
    class Outputs:
        dataset = Output("dataset", tuple)

    magnification = Setting(float(), schema_only=True)
    pixelSize = Setting(str(), schema_only=True)
    kind = Setting(bool(), schema_only=True)
    rotate = Setting(bool(), schema_only=True)

    def __init__(self):
        super().__init__()
        qt.QLocale.setDefault(qt.QLocale("en_US"))
        self._widget = None
        # Add combobox to choose between RSM and magnification (in one dimension case)
        self._methodCB = qt.QComboBox(self)
        self._methodCB.addItems(["RSM", "Magnification"])
        self._methodCB.hide()
        self.controlArea.layout().addWidget(self._methodCB)
        self._methodCB.currentTextChanged.connect(self._changeWidget)

    @Inputs.dataset
    def setDataset(self, dataset):
        if self._widget:
            self.controlArea.layout().removeWidget(self._widget)
            self._widget.hide()
        if dataset:
            self._dataset = dataset
            if not dataset[0].dims.ndim:
                msg = qt.QMessageBox()
                msg.setIcon(qt.QMessageBox.Warning)
                msg.setText("This widget has to be used before selecting any region of \
                             interest and after selecting the dimensions")
                msg.exec_()
            else:
                if dataset[0].dims.ndim == 1:
                    self._methodCB.show()
                    self._changeWidget("RSM")
                else:
                    self._methodCB.hide()
                    self._widget = MagnificationWidget(parent=self)
                    if self.magnification:
                        self._widget.magnification = self.magnification
                    self._widget.sigComputed.connect(self._sendSignal)
                    self.controlArea.layout().addWidget(self._widget)
                    self._widget.setDataset(*dataset)
        else:
            # Emit None
            self.Outputs.dataset.send(dataset)

        self.open()

    def _changeWidget(self, method):
        """
        Change the widget displayed on the window
        """
        if self._widget:
            self.controlArea.layout().removeWidget(self._widget)
            self._widget.hide()
        if method == "RSM":
            self._widget = RSMWidget(parent=self)
            if self.pixelSize:
                self._widget.pixelSize = self.pixelSize
                self._widget.rotate = self.rotate
        else:
            self._widget = MagnificationWidget(parent=self)
            if self.magnification:
                self._widget.magnification = self.magnification
        self._widget.sigComputed.connect(self._sendSignal)
        self.controlArea.layout().addWidget(self._widget)
        self._widget.setDataset(*self._dataset)

    def _sendSignal(self):
        """
        Emits the signal with the new dataset.
        """
        if hasattr(self._widget, 'magnification'):
            self.magnification = self._widget.magnification
            self.kind = False
        elif hasattr(self._widget, 'pixelSize'):
            self.pixelSize = self._widget.pixelSize
            self.rotate = self._widget.rotate
            self.kind = True
        self.close()
        self.Outputs.dataset.send(self._widget.getDataset())
