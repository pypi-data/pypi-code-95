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
__date__ = "05/07/2021"

# import os
import numpy

from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot.StackView import StackViewMainWindow

import darfix
from darfix.core.dataset import Operation

from .operationThread import OperationThread
from .utils import ChooseDimensionDock


class ShiftCorrectionDialog(qt.QDialog):
    """
    Dialog with `ShiftCorrectionWidget` as main window and standard buttons.
    """

    okSignal = qt.Signal()

    def __init__(self, parent=None):
        qt.QDialog.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)
        types = qt.QDialogButtonBox.Ok
        self._buttons = qt.QDialogButtonBox(parent=self)
        self._buttons.setStandardButtons(types)
        self._buttons.setEnabled(False)
        resetB = self._buttons.addButton(self._buttons.Reset)
        self.mainWindow = ShiftCorrectionWidget(parent=self)
        self.mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self.mainWindow)
        self.layout().addWidget(self._buttons)

        self._buttons.accepted.connect(self.okSignal.emit)
        resetB.clicked.connect(self.mainWindow.resetStack)
        self.mainWindow.computingSignal.connect(self._toggleButton)

    def setDataset(self, dataset, indices=None, bg_indices=None, bg_dataset=None):

        if dataset is not None:
            self._buttons.setEnabled(True)
            self.mainWindow.setDataset(dataset, indices, bg_indices, bg_dataset)

    def _toggleButton(self, state):
        self._buttons.button(qt.QDialogButtonBox.Ok).setEnabled(not state)


class ShiftCorrectionWidget(qt.QMainWindow):
    """
    A widget to apply shift correction to a stack of images
    """
    computingSignal = qt.Signal(bool)

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)

        self.setWindowFlags(qt.Qt.Widget)
        self._shift = numpy.array([0, 0])
        self._filtered_shift = None
        self._dimension = None
        self._update_dataset = None
        self.indices = None
        self.bg_indices = None
        self.bg_dataset = None

        self._inputDock = _InputDock()
        self._inputDock.widget.correctionB.setEnabled(False)

        self._sv = StackViewMainWindow()
        self._sv.setColormap(Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME,
                                      normalization="linear"))
        self.setCentralWidget(self._sv)
        self._chooseDimensionDock = ChooseDimensionDock(self)
        spacer1 = qt.QWidget(parent=self)
        spacer1.setLayout(qt.QVBoxLayout())
        spacer1.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        spacer2 = qt.QWidget(parent=self)
        spacer2.setLayout(qt.QVBoxLayout())
        spacer2.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self._chooseDimensionDock.widget.layout().addWidget(spacer1)
        self._inputDock.widget.layout().addWidget(spacer2)
        self._chooseDimensionDock.hide()
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._chooseDimensionDock)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._inputDock)

        self._inputDock.widget.correctionB.clicked.connect(self.correct)
        self._inputDock.widget.abortB.clicked.connect(self.abort)
        self._inputDock.widget.dxLE.editingFinished.connect(self._updateShiftValue)
        self._inputDock.widget.dyLE.editingFinished.connect(self._updateShiftValue)
        self._inputDock.widget._findShiftB.clicked.connect(self._findShift)
        self._chooseDimensionDock.widget.filterChanged.connect(self._filterStack)
        self._chooseDimensionDock.widget.stateDisabled.connect(self._wholeStack)

    def setDataset(self, dataset, indices=None, bg_indices=None, bg_dataset=None):
        """
        Dataset setter. Saves the dataset and updates the stack with the dataset
        data

        :param Dataset dataset: dataset
        """
        self.dataset = dataset
        self._update_dataset = dataset
        self.indices = indices
        self.bg_indices = bg_indices
        self.bg_dataset = bg_dataset
        self._inputDock.widget.correctionB.setEnabled(True)
        if len(self.dataset.data.shape) > 3:
            self._chooseDimensionDock.show()
            self._chooseDimensionDock.widget.setDimensions(self._update_dataset.dims)
        if not self._chooseDimensionDock.widget._checkbox.isChecked():
            self._wholeStack()

    def getDataset(self):
        return self._update_dataset, self.indices, self.bg_indices, self.bg_dataset

    def correct(self):
        """
        Function that starts the thread to compute the shift given
        at the input widget
        """
        dx = self._inputDock.widget.getDx()
        dy = self._inputDock.widget.getDy()
        self.shift = numpy.array([dy, dx])
        if self._filtered_shift is None or self._inputDock.widget.checkbox.isChecked():
            frames = numpy.arange(self._update_dataset.get_data(indices=self.indices, dimension=self._dimension).shape[0])
            self.thread_correction = OperationThread(self, self._update_dataset.apply_shift)
            self.thread_correction.setArgs(numpy.outer(self.shift, frames), self._dimension, indices=self.indices)
        else:
            self.thread_correction = OperationThread(self, self._update_dataset.apply_shift_along_dimension)
            self.thread_correction.setArgs(self._filtered_shift, self._dimension[0], indices=self.indices)
        self.thread_correction.finished.connect(self._updateData)
        self._inputDock.widget.correctionB.setEnabled(False)
        self._inputDock.widget.abortB.show()
        self.thread_correction.start()
        self.computingSignal.emit(True)

    def abort(self):
        self._inputDock.widget.abortB.setEnabled(False)
        self._update_dataset.stop_operation(Operation.SHIFT)

    def resetStack(self):
        self._update_dataset = self.dataset
        self.setStack()

    def updateProgress(self, progress):
        self.sigProgressChanged.emit(progress)

    def _findShift(self):
        if self._filtered_shift is not None:
            self.thread_detection = OperationThread(self, self._update_dataset.find_shift_along_dimension)
            self.thread_detection.setArgs(self._dimension[0], indices=self.indices)
        else:
            self.thread_detection = OperationThread(self, self._update_dataset.find_shift)
            self.thread_detection.setArgs(self._dimension, indices=self.indices)
        self._inputDock.widget._findShiftB.setEnabled(False)
        self.thread_detection.finished.connect(self._updateShift)
        self.thread_detection.start()
        self.computingSignal.emit(True)

    def _updateShiftValue(self):
        if self._filtered_shift is not None:
            self._filtered_shift[self._dimension[1]] = [self._inputDock.widget.getDy(), self._inputDock.widget.getDx()]

    def _updateShift(self):
        self._inputDock.widget._findShiftB.setEnabled(True)
        self.thread_detection.finished.disconnect(self._updateShift)
        if self._filtered_shift is None:
            self.shift = numpy.round(self.thread_detection.data[:, 1], 5)
        else:
            self._filtered_shift = numpy.round(self.thread_detection.data[:, :, 1], 5)
            self.shift = self._filtered_shift[self._dimension[1][0]]
        self.computingSignal.emit(False)

    def _updateData(self):
        """
        Updates the stack with the data computed in the thread
        """
        self.thread_correction.finished.disconnect(self._updateData)
        self._inputDock.widget.abortB.hide()
        self._inputDock.widget.abortB.setEnabled(True)
        self._inputDock.widget.correctionB.setEnabled(True)
        self.computingSignal.emit(False)
        if self.thread_correction.data:
            self._update_dataset = self.thread_correction.data
            assert self._update_dataset is not None
            self.setStack(self._update_dataset)
        else:
            print("\nCorrection aborted")

    def setStack(self, dataset=None):
        """
        Sets new data to the stack.
        Mantains the current frame showed in the view.

        :param Dataset dataset: if not None, data set to the stack will be from the given dataset.
        """
        if dataset is None:
            dataset = self.dataset
        nframe = self._sv.getFrameNumber()
        self._sv.setStack(dataset.get_data(self.indices, self._dimension) if dataset is not None else None)
        self._sv.setFrameNumber(nframe)

    def clearStack(self):
        self._sv.setStack(None)
        self._inputDock.widget.correctionB.setEnabled(False)

    def _filterStack(self, dim=0, val=0):
        self._dimension = [dim, val]

        data = self._update_dataset.get_data(self.indices, self._dimension)
        if self.dataset.dims.ndim == 2:
            stack_size = self.dataset.dims.get(dim[0]).size
            reset_shift = self._filtered_shift is None or self._filtered_shift.shape[0] != stack_size
            self._inputDock.widget.checkbox.show()
            self._filtered_shift = numpy.zeros((stack_size, 2)) if reset_shift else self._filtered_shift
            self.shift = self._filtered_shift[val[0]]
        if data.shape[0]:
            self._sv.setStack(data)
        else:
            self._sv.setStack(None)

    def _wholeStack(self):
        self._dimension = None
        self._filtered_shift = None
        self.shift = numpy.array([0, 0])
        self._inputDock.widget.checkbox.hide()
        self.setStack(self._update_dataset)

    def getStack(self):
        """
        Stack getter

        :returns: StackViewMainWindow:
        """
        return self._sv

    def getStackViewColormap(self):
        """
        Returns the colormap from the stackView

        :rtype: silx.gui.colors.Colormap
        """
        return self._sv.getColormap()

    def setStackViewColormap(self, colormap):
        """
        Sets the stackView colormap

        :param colormap: Colormap to set
        :type colormap: silx.gui.colors.Colormap
        """
        self._sv.setColormap(colormap)

    @property
    def shift(self):
        return self._shift

    @shift.setter
    def shift(self, shift):
        self._shift = shift
        self._inputDock.widget.setDx(shift[1])
        self._inputDock.widget.setDy(shift[0])


class _InputDock(qt.QDockWidget):

    def __init__(self, parent=None):
        qt.QDockWidget.__init__(self, parent)
        self.widget = _InputWidget()
        self.setWidget(self.widget)


class _InputWidget(qt.QWidget):
    """
    Widget used to obtain the double parameters for the shift correction.
    """
    def __init__(self, parent=None):
        super(_InputWidget, self).__init__(parent)

        self._findShiftB = qt.QPushButton("Find shift")
        labelx = qt.QLabel("Horizontal shift:")
        labely = qt.QLabel("Vertical shift:")
        self.dxLE = qt.QLineEdit("0.0")
        self.dyLE = qt.QLineEdit("0.0")
        self.correctionB = qt.QPushButton("Correct")
        self.abortB = qt.QPushButton("Abort")
        self.abortB.hide()
        self.checkbox = qt.QCheckBox("Apply only to selected value")
        self.checkbox.setChecked(False)
        self.checkbox.hide()

        self.dxLE.setValidator(qt.QDoubleValidator())
        self.dyLE.setValidator(qt.QDoubleValidator())

        layout = qt.QGridLayout()

        layout.addWidget(self._findShiftB, 0, 0, 1, 2)
        layout.addWidget(labelx, 1, 0)
        layout.addWidget(labely, 2, 0)
        layout.addWidget(self.dxLE, 1, 1)
        layout.addWidget(self.dyLE, 2, 1)
        layout.addWidget(self.correctionB, 4, 0, 1, 2)
        layout.addWidget(self.abortB, 4, 0, 1, 2)
        layout.addWidget(self.checkbox, 3, 1)

        self.setLayout(layout)

    def setDx(self, dx):
        """
        Set the shift in the x axis
        """
        self.dxLE.setText(str(dx))

    def getDx(self):
        """
        Get the shift in the x axis

        :return float:
        """
        return float(self.dxLE.text())

    def setDy(self, dy):
        """
        Set the shift in the x axis
        """
        self.dyLE.setText(str(dy))

    def getDy(self):
        """
        Get the shift in the y axis

        :return float:
        """
        return float(self.dyLE.text())
