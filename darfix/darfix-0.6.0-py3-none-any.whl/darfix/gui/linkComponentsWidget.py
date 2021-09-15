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
__date__ = "07/06/2021"


import numpy
from pathlib import Path

from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import ScatterView, StackView
from silx.gui.plot.items import Scatter
import darfix
from darfix.core.componentsMatching import ComponentsMatching, Method
from darfix.gui.datasetSelectionWidget import FilenameSelectionWidget
from darfix.io.utils import read_components
import logging

_logger = logging.getLogger(__file__)


class LinkComponentsWidget(qt.QWidget):
    """
    Widget to compare two stacks of images. Each of these stacks represents the
    components of a dataset.
    """
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        self._displayComponents = [False, False]
        self._displayMatches = True
        self.final_matches = None

        # Method Widget
        methodsLabel = qt.QLabel("Matching method:")
        self._methodsCB = qt.QComboBox(parent=self)
        for method in Method.values():
            self._methodsCB.addItem(method)
        self.layout().addWidget(methodsLabel, 1, 0, 1, 1)
        self.layout().addWidget(self._methodsCB, 1, 1, 1, 1)

        # Compute button and checkbox widgets
        self._methodsCB.currentTextChanged.connect(self._comboBoxChanged)
        self._computeB = qt.QPushButton("Compute")
        self._computeB.setEnabled(False)
        self._checkbox = qt.QCheckBox("Link features", self)
        self._checkbox.setChecked(True)
        self._checkbox.setToolTip("If checked, lines between matches will be drawn")
        self._checkbox.stateChanged.connect(self._checkBoxToggled)
        widget = qt.QWidget(parent=self)
        layout = qt.QHBoxLayout()
        layout.addWidget(self._checkbox)
        layout.addWidget(self._computeB)
        widget.setLayout(layout)
        self.layout().addWidget(widget, 1, 3, 1, 1, qt.Qt.AlignRight)

        # Stack 1
        self._sv1 = StackView(parent=self)
        self._sv1.setColormap(Colormap(
            name=darfix.config.DEFAULT_COLORMAP_NAME,
            normalization=darfix.config.DEFAULT_COLORMAP_NORM))
        self._sv1.sigFrameChanged.connect(self._changeComp1)
        self._sv1.hide()
        self._scatter1 = ScatterView(parent=self)
        self._scatter1.hide()
        self._scatter1.getScatterItem().setVisualization(Scatter.Visualization.SOLID)
        stack1Label = qt.QLabel("Path for stack 1: ")
        self._stack1Filename = FilenameSelectionWidget(parent=self)
        self._stack1Filename.filenameChanged.connect(self._setStack1)
        self.layout().addWidget(stack1Label, 0, 0)
        self.layout().addWidget(self._stack1Filename, 0, 1)
        self.layout().addWidget(self._sv1, 3, 0, 1, 2)
        self.layout().addWidget(self._scatter1, 4, 0, 1, 2)

        # Stack 2
        self._sv2 = StackView(parent=self)
        self._sv2.setColormap(Colormap(
            name=darfix.config.DEFAULT_COLORMAP_NAME,
            normalization='linear'))
        self._sv2.sigFrameChanged.connect(self._changeComp2)
        self._sv2.hide()
        self._scatter2 = ScatterView(parent=self)
        self._scatter2.hide()
        self._scatter2.getScatterItem().setVisualization(Scatter.Visualization.SOLID)
        stack2Label = qt.QLabel("Path for stack 2: ")
        self._stack2Filename = FilenameSelectionWidget(parent=self)
        self._stack2Filename.filenameChanged.connect(self._setStack2)
        self.layout().addWidget(stack2Label, 0, 2)
        self.layout().addWidget(self._stack2Filename, 0, 3)
        self.layout().addWidget(self._sv2, 3, 2, 1, 2)
        self.layout().addWidget(self._scatter2, 4, 2, 1, 2)

        # Linked stack
        self._linked_sv = StackView(parent=self)
        self._linked_sv.setColormap(Colormap(
            name=darfix.config.DEFAULT_COLORMAP_NAME,
            normalization='linear'))
        self._linked_sv.sigFrameChanged.connect(self._changeComp1)
        self._linked_sv.hide()
        self.layout().addWidget(self._linked_sv, 2, 0, 1, 4)

    def _setStack1(self):
        """
        Update stack 1 components
        """
        filename = self._stack1Filename.getFilename()
        self.final_matches = None

        if not Path(filename).is_file():
            if filename != '':
                msg = qt.QMessageBox()
                msg.setIcon(qt.QMessageBox.Warning)
                msg.setText("Filename not valid")
                msg.exec_()
            return

        self.dimensions1, self.components1, self.W1 = read_components(filename)

        self._linked_sv.hide()
        self._sv1.setStack(self.components1)
        self._displayComponents[0] = True
        self._sv1.show()
        self._scatter1.show()
        keys = list(self.dimensions1.keys())
        self._scatter1.getPlotWidget().setGraphXLabel(keys[0])
        self._scatter1.getPlotWidget().setGraphYLabel(keys[1])
        self._scatter1.setData(
            self.dimensions1[keys[0]].astype(numpy.float),
            self.dimensions1[keys[1]].astype(numpy.float), self.W1.T[0])
        self._scatter1.resetZoom()
        self._scatter1.setColormap(Colormap(name='jet', normalization='linear'))

        if all(self._displayComponents):
            self._sv2.show()
            self._componentsMatching = ComponentsMatching(
                components=[self.components1, self._sv2.getStack(False, True)[0]])

    def _setStack2(self):
        """
        Update stack 2 components
        """
        filename = self._stack2Filename.getFilename()
        self.final_matches = None

        if filename == '':
            return

        self.dimensions2, self.components2, self.W2 = read_components(filename)

        self._linked_sv.hide()
        self._sv2.setStack(self.components2)
        self._displayComponents[1] = True
        self._sv2.show()
        self._scatter2.show()
        keys = list(self.dimensions2.keys())
        self._scatter2.getPlotWidget().setGraphXLabel(keys[0])
        self._scatter2.getPlotWidget().setGraphYLabel(keys[1])
        self._scatter2.setData(
            self.dimensions2[keys[0]].astype(numpy.float),
            self.dimensions2[keys[1]].astype(numpy.float), self.W2.T[0])
        self._scatter2.setColormap(Colormap(name='jet', normalization='linear'))
        self._scatter2.resetZoom()

        if all(self._displayComponents):
            self._sv1.show()
            self._componentsMatching = ComponentsMatching(
                components=[self._sv1.getStack(False, True)[0], self.components2])

        self._computeB.setEnabled(True)
        self._computeB.pressed.connect(self._linkComponents)

    def _checkBoxToggled(self, linkFeatures):
        """
        Slot to toggle state in function of the checkbox state.
        """
        self._displayMatches = linkFeatures

    def _comboBoxChanged(self, text):

        method = Method(text)
        if method == Method.orb_feature_matching:
            self._checkbox.setEnabled(True)
            self._displayMatches = self._checkbox.checkState()
        else:
            self._checkbox.setEnabled(False)
            self._displayMatches = False

    def _linkComponents(self):
        """
        Link components from stack 1 and 2.
        """
        self.final_matches, matches = self._componentsMatching.match_components(
            method=Method(self._methodsCB.currentText()))
        self._sv1.hide()
        self._sv2.hide()

        draws = numpy.array(self._componentsMatching.draw_matches(self.final_matches,
                            matches, displayMatches=self._displayMatches))
        self._linked_sv.setStack(draws)
        self._linked_sv.show()
        self._changeComp1(0)

    def _changeComp1(self, index):
        if index >= 0:
            values = numpy.array(list(self.dimensions1.values())).astype(numpy.float)
            if self.dimensions1:
                self._scatter1.setData(values[0], values[1], self.W1.T[index])
            if self.final_matches and index in self.final_matches:
                self._scatter2.show()
                values = numpy.array(list(self.dimensions2.values())).astype(numpy.float)
                self._scatter2.setData(values[0], values[1], self.W2.T[self.final_matches[index]])
            else:
                self._scatter2.hide()

    def _changeComp2(self, index):
        if index >= 0:
            values = numpy.array(list(self.dimensions2.values())).astype(numpy.float)
            if self.dimensions2:
                self._scatter2.setData(values[0], values[1], self.W2.T[index])
