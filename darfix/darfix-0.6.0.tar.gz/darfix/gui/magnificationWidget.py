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
__date__ = "16/07/2021"


from silx.gui import qt
from silx.utils.enum import Enum as _Enum


class Value(_Enum):
    """
    Methods available to compute the background.
    """
    PIXEL_2X = 3.75
    PIXEL_10X = 0.75


class MagnificationWidget(qt.QMainWindow):
    """
    Widget to apply magnification transformation to the data axes.
    """
    sigComputed = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        widget = qt.QWidget()
        layout = qt.QVBoxLayout()

        self._magnification = Value.PIXEL_2X.value
        self._checkbox2x = qt.QCheckBox("2x magnification")
        self._checkbox10x = qt.QCheckBox("10x magnification")
        self._checkboxManual = qt.QCheckBox("Manual magnification:")
        self._manualLE = qt.QLineEdit(parent=self)
        self._manualLE.setEnabled(False)
        validator = qt.QDoubleValidator()
        validator.setBottom(0)
        self._manualLE.setValidator(validator)
        self._okButton = qt.QPushButton("Ok")
        self._okButton.setEnabled(False)
        self._okButton.pressed.connect(self._saveMagnification)
        layout.addWidget(self._checkbox2x)
        layout.addWidget(self._checkbox10x)
        layout.addWidget(self._checkboxManual)
        layout.addWidget(self._manualLE)
        layout.addWidget(self._okButton)

        # self._okButton.pressed.connect(self._saveMagnification)
        self._checkbox2x.stateChanged.connect(self._check2x)
        self._checkbox10x.stateChanged.connect(self._check10x)
        self._checkboxManual.stateChanged.connect(self._checkManual)

        self._checkbox2x.setChecked(True)
        widget.setLayout(layout)

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

        if not self.dataset.dims:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setText("This widget has to be used before selecting any region of \
                         interest and after selecting the dimensions")
            msg.exec_()
        else:
            self._okButton.setEnabled(True)

    @property
    def magnification(self):
        return self._magnification

    @magnification.setter
    def magnification(self, magnification):
        self._magnification = magnification
        if self.magnification == Value.PIXEL_2X.value:
            self._check2x(True)
            self._checkbox2x.setChecked(True)
        elif self.magnification == Value.PIXEL_10X.value:
            self._checkbox10x.setChecked(True)
            self._check10x(True)
        else:
            self._manualLE.setText(str(self._magnification))
            self._checkManual(True)
            self._checkboxManual.setChecked(True)

    def getDataset(self):
        return self.dataset, self.indices, self.bg_indices, self.bg_dataset

    def _checkManual(self, checked):
        if checked:
            self._checkbox2x.setChecked(False)
            self._checkbox10x.setChecked(False)
            self._manualLE.setEnabled(True)
        else:
            self._manualLE.setEnabled(False)

    def _check2x(self, checked):
        if checked:
            self._checkbox10x.setChecked(False)
            self._checkboxManual.setChecked(False)
            self._manualLE.setEnabled(False)

    def _check10x(self, checked):
        if checked:
            self._checkbox2x.setChecked(False)
            self._checkboxManual.setChecked(False)
            self._manualLE.setEnabled(False)

    def _saveMagnification(self):

        if self._checkbox2x.isChecked():
            magnification = Value.PIXEL_2X.value
        elif self._checkbox10x.isChecked():
            magnification = Value.PIXEL_10X.value
        else:
            magnification = self._manualLE.text()
            if magnification == "":
                msg = qt.QMessageBox()
                msg.setIcon(qt.QMessageBox.Warning)
                msg.setText("Magnification value has to be entered when choosing manual")
                msg.exec_()
                return
        self._magnification = float(magnification)

        self.dataset.compute_transformation(self.magnification)

        self.sigComputed.emit()
