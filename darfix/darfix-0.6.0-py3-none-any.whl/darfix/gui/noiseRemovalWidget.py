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
__date__ = "20/07/2021"

import logging

from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot.StackView import StackViewMainWindow

import darfix
from darfix.core.dataset import Operation
from darfix.core.imageOperations import Method

from .operationThread import OperationThread

_logger = logging.getLogger(__file__)


class _ParametersDock(qt.QDockWidget):

    def __init__(self, parent=None):
        """
        Dock widget containing the input parameters for the noise removal operations.
        """
        qt.QDockWidget.__init__(self, parent)
        widget = qt.QWidget()
        self.layout = qt.QGridLayout()

        # Background subtraction
        bsLabel = qt.QLabel("Background Substraction")
        # Font for operations titles
        font = qt.QFont()
        font.setBold(True)
        bsLabel.setFont(font)
        self.layout.addWidget(bsLabel, 0, 0, 1, 2)
        self.bsMethodsCB = qt.QComboBox(self)
        for method in Method.values():
            self.bsMethodsCB.addItem(method)
        self.bsBackgroundCB = qt.QComboBox(self)
        self.computeBS = qt.QPushButton("Compute")
        self.abortBS = qt.QPushButton("Abort")
        self.abortBS.hide()
        methodLabel = qt.QLabel("Method:")
        bgLabel = qt.QLabel("Background:")
        methodLabel.setMargin(0)
        # Step widget
        self.stepWidget = qt.QWidget()
        stepLayout = qt.QHBoxLayout()
        stepLayout.addWidget(qt.QLabel("Step:"))
        self.step = qt.QLineEdit("1")
        self.step.setSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.Preferred)
        stepLayout.setContentsMargins(0, 0, 0, 0)
        stepLayout.addWidget(self.step)
        self.stepWidget.setLayout(stepLayout)
        # Chunks widget
        self.chunksWidget = qt.QWidget()
        chunksLayout = qt.QHBoxLayout()
        chunksLabel = qt.QLabel("Chunks:")
        self.verticalChunkSize = qt.QLineEdit("100")
        self.verticalChunkSize.setValidator(qt.QIntValidator())
        self.horizontalChunkSize = qt.QLineEdit("100")
        self.horizontalChunkSize.setValidator(qt.QIntValidator())
        chunksLayout.addWidget(chunksLabel)
        chunksLayout.addWidget(self.verticalChunkSize)
        chunksLayout.addWidget(self.horizontalChunkSize)
        chunksLayout.setContentsMargins(0, 0, 0, 0)
        self.chunksWidget.setLayout(chunksLayout)

        self.inDiskCheckbox = qt.QCheckBox("Use chunks to compute median")
        self.inDiskWidget = qt.QWidget()
        inDiskLayout = qt.QVBoxLayout()
        inDiskLayout.addWidget(self.stepWidget)
        inDiskLayout.addWidget(self.chunksWidget)
        inDiskLayout.addWidget(self.inDiskCheckbox, alignment=qt.Qt.AlignRight)
        self.chunksWidget.hide()
        self.inDiskCheckbox.stateChanged.connect(self._toggleChunks)
        inDiskLayout.setContentsMargins(0, 0, 0, 0)
        self.inDiskWidget.setLayout(inDiskLayout)

        self.layout.addWidget(methodLabel, 1, 0, 1, 1)
        self.layout.addWidget(bgLabel, 2, 0, 1, 1)
        self.layout.addWidget(self.bsMethodsCB, 1, 1, 1, 1)
        self.layout.addWidget(self.bsBackgroundCB, 2, 1, 1, 1)
        self.layout.addWidget(self.inDiskWidget, 3, 0, 1, 2)
        self.layout.addWidget(self.computeBS, 4, 1, 1, 1)
        self.layout.addWidget(self.abortBS, 4, 0, 1, 1)
        self.computeBS.hide()
        self.abortBS.hide()
        self.inDiskWidget.hide()
        # Hot pixel removal
        hpLabel = qt.QLabel("Hot Pixel Removal")
        hpLabel.setFont(font)
        self.layout.addWidget(hpLabel, 0, 2, 1, 2)
        ksizeLabel = qt.QLabel("Kernel size:")
        self.layout.addWidget(ksizeLabel, 1, 2, 1, 1)
        self.hpSizeCB = qt.QComboBox(self)
        self.hpSizeCB.addItem("3")
        self.hpSizeCB.addItem("5")
        self.computeHP = qt.QPushButton("Compute")
        self.abortHP = qt.QPushButton("Abort")
        self.layout.addWidget(self.hpSizeCB, 1, 3, 1, 1)
        self.layout.addWidget(self.computeHP, 4, 3, 1, 1)
        self.layout.addWidget(self.abortHP, 4, 2, 1, 1)
        self.computeHP.hide()
        self.abortHP.hide()
        # Threshold removal
        tpLabel = qt.QLabel("Threshold Removal")
        tpLabel.setFont(font)
        self.layout.addWidget(tpLabel, 0, 4, 1, 2)
        bottomLabel = qt.QLabel("Bottom threshold:")
        self.layout.addWidget(bottomLabel, 1, 4, 1, 1)
        self.bottomLE = qt.QLineEdit("0")
        self.bottomLE.setValidator(qt.QIntValidator())
        self.bottomLE.setSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.Preferred)
        self.computeTP = qt.QPushButton("Compute")
        self.abortTP = qt.QPushButton("Abort")
        self.layout.addWidget(self.bottomLE, 1, 5, 1, 1)
        self.layout.addWidget(self.computeTP, 4, 5, 1, 1)
        self.layout.addWidget(self.abortTP, 4, 4, 1, 1)
        self.computeTP.hide()
        self.abortTP.hide()

        self.layout.setHorizontalSpacing(10)
        widget.setLayout(self.layout)
        self.setWidget(widget)

    def _toggleChunks(self, checked):
        widgets = [self.chunksWidget, self.stepWidget]

        widgets[1 if checked else 0].hide()
        widgets[0 if checked else 1].show()


class NoiseRemovalDialog(qt.QDialog):
    """
    Dialog with `NoiseRemovalWidget` as main window and standard buttons.
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
        self.mainWindow = NoiseRemovalWidget(parent=self)
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


class NoiseRemovalWidget(qt.QMainWindow):
    """
    Widget to apply noise removal from a dataset.
    For now it can apply both background subtraction and hot pixel removal.
    For background subtraction the user can choose the background to use:
    dark frames, low intensity data or all the data. From these background
    frames, an image is computed either using the mean or the median.
    """

    computingSignal = qt.Signal(bool)

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)

        self._update_dataset = None
        self.indices = None
        self.bg_indices = None
        self.bg_dataset = None
        self.setWindowFlags(qt.Qt.Widget)

        self._parametersDock = _ParametersDock()
        self._parametersDock.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self._sv = StackViewMainWindow()
        self._sv.setColormap(Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME,
                                      normalization=darfix.config.DEFAULT_COLORMAP_NORM))

        self._size = None
        self._method = None
        self._background = self._parametersDock.bsBackgroundCB.currentText()
        self._bottom_threshold = self._parametersDock.bottomLE.text()
        self._step = self._parametersDock.step.text()
        self._chunks = [int(self._parametersDock.verticalChunkSize.text()),
                        int(self._parametersDock.horizontalChunkSize.text())]
        self.setCentralWidget(self._sv)
        self.addDockWidget(qt.Qt.BottomDockWidgetArea, self._parametersDock)

        # Add connections
        self._parametersDock.computeBS.clicked.connect(self.__computeBS)
        self._parametersDock.computeHP.clicked.connect(self.__computeHP)
        self._parametersDock.computeTP.clicked.connect(self.__computeTP)
        self._parametersDock.abortBS.clicked.connect(self.__abortBS)
        self._parametersDock.abortHP.clicked.connect(self.__abortHP)
        self._parametersDock.abortTP.clicked.connect(self.__abortTP)
        self._parametersDock.bsMethodsCB.currentTextChanged.connect(self._toggleMethod)
        self._parametersDock.bsBackgroundCB.currentIndexChanged.connect(self._toggleInDiskWidget)

    def setDataset(self, dataset, indices=None, bg_indices=None, bg_dataset=None):
        """
        Dataset setter. Saves the dataset and updates the stack with the dataset
        data

        :param Dataset dataset: dataset
        """
        self.dataset = dataset
        self._update_dataset = dataset
        self.indices = indices
        self.setStack()
        self.bg_indices = bg_indices
        self.bg_dataset = bg_dataset

        self._parametersDock.computeBS.show()
        self._parametersDock.computeHP.show()
        self._parametersDock.computeTP.show()

        """
        Sets the available background for the user to choose.
        """
        self._parametersDock.bsBackgroundCB.clear()
        if bg_dataset is not None:
            self._parametersDock.bsBackgroundCB.addItem("Dark data")
        if bg_indices is not None:  # TODO: modify
            self._parametersDock.bsBackgroundCB.addItem("Low intensity data")
        self._parametersDock.bsBackgroundCB.addItem("Data")

    def __computeBS(self):
        """
        Function that starts the thread to compute the background
        subtraction.
        """
        self._background = self._parametersDock.bsBackgroundCB.currentText()
        if self._background == "Dark data":
            bg = self.bg_dataset
        elif self._background == "Low intensity data":
            bg = self.bg_indices
        else:
            bg = None

        if self._parametersDock.inDiskWidget.isVisible():
            if self._parametersDock.inDiskCheckbox.isChecked():
                self._step = None
                self._chunks = [int(self._parametersDock.verticalChunkSize.text()),
                                int(self._parametersDock.horizontalChunkSize.text())]
            else:
                self._chunks = None
                self._step = int(self._parametersDock.step.text())

        self._thread = OperationThread(self, self._update_dataset.apply_background_subtraction)
        self._method = self._parametersDock.bsMethodsCB.currentText()
        self._thread.setArgs(bg, self._method, self.indices, self._step, self._chunks)
        self._thread.finished.connect(self._updateData)
        if not self._update_dataset.in_memory:
            self._parametersDock.abortBS.show()
        self._thread.start()
        self._setComputingState(True)

    def __computeHP(self):
        """
        Function that starts the thread to compute the hot pixel
        removal.
        """
        self._size = self._parametersDock.hpSizeCB.currentText()
        self._thread = OperationThread(self, self._update_dataset.apply_hot_pixel_removal)
        self._thread.setArgs(int(self._size), self.indices)
        self._thread.finished.connect(self._updateData)
        if not self._update_dataset.in_memory:
            self._parametersDock.abortHP.show()
        self._thread.start()
        self._setComputingState(True)

    def __computeTP(self):
        """
        Function that starts the thread to compute the threshold
        removal.
        """
        self._bottom_threshold = self._parametersDock.bottomLE.text()
        self._thread = OperationThread(self, self._update_dataset.apply_threshold_removal)
        self._thread.setArgs(int(self._bottom_threshold))
        self._thread.finished.connect(self._updateData)
        if not self._update_dataset.in_memory:
            self._parametersDock.abortTP.show()
        self._thread.start()
        self._setComputingState(True)

    def __abortBS(self):
        self._parametersDock.abortBS.setEnabled(False)
        self._update_dataset.stop_operation(Operation.BS)

    def __abortHP(self):
        self._parametersDock.abortHP.setEnabled(False)
        self._update_dataset.stop_operation(Operation.HP)

    def __abortTP(self):
        self._parametersDock.abortTP.setEnabled(False)
        self._update_dataset.stop_operation(Operation.THRESHOLD)

    def _setComputingState(self, state):

        self._parametersDock.computeBS.setEnabled(not state)
        self._parametersDock.computeHP.setEnabled(not state)
        self._parametersDock.computeTP.setEnabled(not state)

        self.computingSignal.emit(state)

    def _updateData(self):
        """
        Updates the stack with the data computed in the thread
        """
        try:
            self._thread.finished.disconnect(self._updateData)
        except TypeError as e:
            _logger.warning(e)
        self._parametersDock.abortBS.setEnabled(True)
        self._parametersDock.abortHP.setEnabled(True)
        self._parametersDock.abortTP.setEnabled(True)
        self._parametersDock.abortBS.hide()
        self._parametersDock.abortHP.hide()
        self._parametersDock.abortTP.hide()
        self._setComputingState(False)
        if self._thread.data is not None:
            self._update_dataset = self._thread.data
            self.setStack(self._update_dataset)
        else:
            print("\nComputation aborted")

    def _toggleMethod(self, text):
        if text == Method.mean.value:
            self._parametersDock.inDiskWidget.hide()
        elif text == Method.median.value:
            self._toggleInDiskWidget(self._parametersDock.bsBackgroundCB.currentIndex())

    def _toggleInDiskWidget(self, index):
        if self._parametersDock.bsMethodsCB.currentText() == Method.median.value:
            if self.bg_dataset is None:
                self._parametersDock.inDiskWidget.hide() if self.dataset.in_memory else \
                    self._parametersDock.inDiskWidget.show()
            elif not (index or self.bg_dataset.in_memory) or (index and not self.dataset.in_memory):
                self._parametersDock.inDiskWidget.show()
            else:
                self._parametersDock.inDiskWidget.hide()
        else:
            self._parametersDock.inDiskWidget.hide()

    def getDataset(self):
        return self._update_dataset, self.indices, self.bg_indices, self. bg_dataset

    def resetStack(self):
        self._update_dataset = self.dataset
        self.setStack()

    def clearStack(self):
        self._sv.setStack(None)

    def getStack(self):
        return self._sv.getStack(False, True)[0]

    def setStack(self, dataset=None):
        """
        Sets new data to the stack.
        Mantains the current frame showed in the view.

        :param Dataset dataset: if not None, data set to the stack will be from the given dataset.
        """
        if dataset is None:
            dataset = self.dataset
        nframe = self._sv.getFrameNumber()
        self._sv.setStack(dataset.get_data(self.indices))
        self._sv.setFrameNumber(nframe)

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
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size
        self._parametersDock.hpSizeCB.setCurrentText(size)

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        self._method = method
        self._parametersDock.bsMethodsCB.setCurrentText(method)

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, step):
        self._step = step
        if step is not None:
            self._parametersDock.step.setText(str(step))

    @property
    def chunks(self):
        return self._chunks

    @chunks.setter
    def chunks(self, chunks):
        self._chunks = chunks
        if chunks is not None:
            self._parametersDock.verticalChunkSize.setText(str(chunks[0]))
            self._parametersDock.horizontalChunkSize.setText(str(chunks[1]))

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, background):
        if self._parametersDock.bsBackgroundCB.findText(background) >= 0:
            self._background = background
            self._parametersDock.bsBackgroundCB.setCurrentText(background)

    @property
    def bottom_threshold(self):
        return self._bottom_threshold

    @bottom_threshold.setter
    def bottom_threshold(self, bottom):
        self._bottom_threshold = bottom
        self._parametersDock.bottomLE.setText(bottom)
