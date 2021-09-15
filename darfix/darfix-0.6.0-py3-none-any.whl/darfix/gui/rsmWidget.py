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


class PixelSize(_Enum):
    """
    Different pixel sizes
    """
    Basler = 0.051
    PcoEdge_2x = 0.00375
    PcoEdge_10x = 0.00075


class RSMWidget(qt.QMainWindow):
    """
    Widget to compute Reciprocal Space Map
    """
    sigComputed = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        self._rotate = False
        self._moments = None
        self._pixelSize = None

        widget = qt.QWidget()
        layout = qt.QGridLayout()

        pixelSizeLabel = qt.QLabel("Pixel size: ")
        self._pixelSizeCB = qt.QComboBox()
        self._pixelSizeCB.addItems(PixelSize.names())
        self._rotateCB = qt.QCheckBox("Rotate RSM", self)
        self._okButton = qt.QPushButton("Ok")
        self._okButton.setEnabled(False)
        self._okButton.pressed.connect(self._saveRSM)
        layout.addWidget(pixelSizeLabel, 0, 0)
        layout.addWidget(self._pixelSizeCB, 0, 1)
        layout.addWidget(self._rotateCB, 1, 1)
        layout.addWidget(self._okButton, 2, 0, 1, 2)
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
        self._okButton.setEnabled(True)

    def getDataset(self):
        return self.dataset, self.indices, self.bg_indices, self.bg_dataset

    @property
    def pixelSize(self):
        return self._pixelSize

    @pixelSize.setter
    def pixelSize(self, pixelSize):
        self._pixelSize = pixelSize
        self._pixelSizeCB.setCurrentText(str(pixelSize))

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, rotate):
        self._rotate = rotate
        self._rotateCB.setChecked(rotate)

    def _saveRSM(self):
        self._pixelSize = self._pixelSizeCB.currentText()
        self._rotate = self._rotateCB.isChecked()
        self.dataset.compute_transformation(PixelSize[self._pixelSize].value,
                                            kind="rsm",
                                            rotate=self._rotate)
        self.sigComputed.emit()
