# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017-2019 European Synchrotron Radiation Facility
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

import numpy

from silx.gui import qt
from silx.utils.enum import Enum as _Enum

from .operationThread import OperationThread
from .displayComponentsWidget import DisplayComponentsWidget


class Method(_Enum):
    """
    Different blind source separation approaches that can be applied
    """
    PCA = "The process of computing the principal components \n" \
          "and using them to perform a change of basis on the data"
    NNICA = "Find components independent from each other and non-negative"
    NMF = "Non-negative matrix factorization factorizes the data matrix into \n" \
          "two matrices, with the property that all three matrices have no negative elements"
    NNICA_NMF = "Apply Non-negative ICA followed by NMF"


class BSSWidget(qt.QMainWindow):
    """
    Widget to apply blind source separation.
    """

    sigComputed = qt.Signal(Method, int)

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)

        # Method widget
        methodLabel = qt.QLabel("Method: ")
        self.methodCB = qt.QComboBox()
        for member in Method.members():
            self.methodCB.addItem(member.name)
            self.methodCB.setItemData(self.methodCB.count() - 1, member.value, qt.Qt.ToolTipRole)
        # Number of components
        nComponentsLabel = qt.QLabel("Num comp:")
        self.nComponentsLE = qt.QLineEdit("1")
        self.nComponentsLE.setValidator(qt.QIntValidator())
        # Compute BSS with the number of components
        self.computeButton = qt.QPushButton("Compute")
        self.computeButton.setEnabled(False)
        self.computeButton.clicked.connect(self._computeBSS)
        # Detect optimal number of components
        self.detectButton = qt.QPushButton("Detect number of components")
        self.detectButton.setEnabled(False)
        self.detectButton.clicked.connect(self._detectComp)

        # Add widgets to layout
        layout = qt.QGridLayout()
        layout.addWidget(methodLabel, 0, 0, 1, 1)
        layout.addWidget(self.methodCB, 0, 1, 1, 1)
        layout.addWidget(nComponentsLabel, 0, 2, 1, 1)
        layout.addWidget(self.nComponentsLE, 0, 3, 1, 1)
        layout.addWidget(self.computeButton, 0, 4, 1, 1)
        layout.addWidget(self.detectButton, 1, 4, 1, 1)
        # Top Widget with the type of bss and the number of components to compute
        top_widget = qt.QWidget(self)
        top_widget.setLayout(layout)

        # Widget to display the components
        self._displayComponentsWidget = DisplayComponentsWidget()
        self._displayComponentsWidget.hide()

        # Main widget is a Splitter with the top widget and the displayComponentsWidget
        self.splitter = qt.QSplitter(qt.Qt.Vertical)
        self.splitter.addWidget(top_widget)
        self.splitter.addWidget(self._displayComponentsWidget)
        self.setCentralWidget(self.splitter)

    def hideButton(self):
        self._computeB.hide()

    def showButton(self):
        self._computeB.show()

    def setDataset(self, dataset, indices=None, bg_indices=None, bg_dataset=None):
        """
        Dataset setter.

        :param Dataset dataset: dataset
        """
        self.dataset = dataset
        self.indices = indices
        self.bg_indices = bg_indices
        self.bg_dataset = bg_dataset
        self.computeButton.setEnabled(True)
        self.detectButton.setEnabled(True)

    def _computeBSS(self):
        """
        Computes blind source separation with the chosen method.
        """
        self.computeButton.setEnabled(False)
        self.detectButton.setEnabled(False)
        self.nComponentsLE.setEnabled(False)
        method = Method[self.methodCB.currentText()]
        n_comp = int(self.nComponentsLE.text())
        self.sigComputed.emit(method, n_comp)
        if method == Method.PCA:
            self._thread = OperationThread(self, self.dataset.pca)
        elif method == Method.NNICA:
            self._thread = OperationThread(self, self.dataset.nica)
        elif method == Method.NMF:
            self._thread = OperationThread(self, self.dataset.nmf)
        elif method == Method.NNICA_NMF:
            self._thread = OperationThread(self, self.dataset.nica_nmf)
        else:
            raise ValueError('BSS method not managed')

        # Set arguments and start thread
        self._thread.setArgs(n_comp, indices=self.indices)
        self._thread.finished.connect(self._displayComponents)
        self._thread.start()

    def _displayComponents(self):
        self._thread.finished.disconnect(self._displayComponents)
        comp, self.W = self._thread.data
        n_comp = int(self.nComponentsLE.text())
        if comp.shape[0] < n_comp:
            n_comp = comp.shape[0]
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Information)
            msg.setText("Found only {0} components".format(n_comp))
            msg.setStandardButtons(qt.QMessageBox.Ok)
            msg.exec_()
        shape = self.dataset.get_data()[0].shape
        self.comp = comp.reshape(n_comp, shape[0], shape[1])
        self._displayComponentsWidget.show()
        self.computeButton.setEnabled(True)
        self.nComponentsLE.setEnabled(True)
        self.detectButton.setEnabled(True)
        if self.bg_indices is not None:
            # If filter data is activated, the matrix W has reduced dimensionality, so reshaping is not possible
            # Create empty array with shape the total number of frames
            W = numpy.zeros((self.dataset.nframes, n_comp))
            # Set actual values of W where threshold of filter is True
            W[self.indices] = self.W
            self.W = W
        self._displayComponentsWidget.setComponents(self.comp, self.W, self.dataset.get_dimensions_values(), self.dataset.data.shape[:2])

    def _detectComp(self):
        self.detectButton.setEnabled(False)
        self.computeButton.setEnabled(False)
        self._thread = OperationThread(self, self.dataset.pca)
        self._thread.setArgs(return_vals=True)
        self._thread.finished.connect(self._setNumComp)
        self._thread.start()

    def _setNumComp(self):
        self._thread.finished.disconnect(self._setNumComp)
        vals = self._thread.data
        vals /= numpy.sum(vals)
        components = len(vals[vals > 0.01])
        self.detectButton.setEnabled(True)
        self.computeButton.setEnabled(True)
        self.nComponentsLE.setText(str(components))

    def getDisplayComponentsWidget(self):
        return self._displayComponentsWidget
