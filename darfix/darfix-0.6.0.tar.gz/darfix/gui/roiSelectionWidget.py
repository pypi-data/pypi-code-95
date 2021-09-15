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
__date__ = "26/04/2021"

# import os

import logging
import numpy

from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot.StackView import StackViewMainWindow
from silx.gui.plot.items.roi import RectangleROI
from silx.gui.plot.tools.roi import RegionOfInterestManager, RegionOfInterestTableWidget

import darfix
from darfix.core.dataset import Operation
from .operationThread import OperationThread


_logger = logging.getLogger(__file__)


class ROISelectionWidget(qt.QWidget):
    """
    Widget that allows the user to pick a ROI in any image of the dataset.
    """
    sigComputed = qt.Signal(list, list)

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        self.roi = None
        self._update_dataset = None
        self.indices = None
        self.bg_indices = None
        self.bg_dataset = None
        self._original_dataset = True

        self.setLayout(qt.QVBoxLayout())
        self._sv = StackViewMainWindow()
        _buttons = qt.QDialogButtonBox(parent=self)
        self._okB = _buttons.addButton(_buttons.Ok)
        self._applyB = _buttons.addButton(_buttons.Apply)
        self._abortB = _buttons.addButton(_buttons.Abort)
        self._resetB = _buttons.addButton(_buttons.Reset)
        self._abortB.hide()

        self._applyB.clicked.connect(self.applyRoi)
        self._okB.clicked.connect(self.apply)
        self._resetB.clicked.connect(self.resetStack)
        self._abortB.clicked.connect(self.abort)

        self._sv.setColormap(Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME,
                                      normalization=darfix.config.DEFAULT_COLORMAP_NORM))
        self.layout().addWidget(self._sv)
        self.layout().addWidget(_buttons)

        plot = self._sv.getPlot()
        self._roiManager = RegionOfInterestManager(plot)
        self._roiTable = RegionOfInterestTableWidget()
        self._roiTable.setRegionOfInterestManager(self._roiManager)

        self._roi = RectangleROI()
        self._roi.setLabel('ROI')
        self._roi.setGeometry(origin=(0, 0), size=(10, 10))
        self._roi.setEditable(True)
        self._roiManager.addRoi(self._roi)
        self._roiTable.setColumnHidden(4, True)

        # Add the region of interest table and the buttons to a dock widget
        widget = qt.QWidget()
        layout = qt.QVBoxLayout()
        widget.setLayout(layout)
        layout.addWidget(self._roiTable)

        def roiDockVisibilityChanged(visible):
            """Handle change of visibility of the roi dock widget.

            If dock becomes hidden, ROI interaction is stopped.
            """
            if not visible:
                self._roiManager.stop()

        dock = qt.QDockWidget('Image ROI')
        dock.setWidget(widget)
        dock.visibilityChanged.connect(roiDockVisibilityChanged)
        plot.addTabbedDockWidget(dock)

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

    def setStack(self, dataset=None):
        """
        Sets new data to the stack.
        Mantains the current frame showed in the view.

        :param Dataset dataset: if not None, data set to the stack will be from the given dataset.
        """
        if dataset is None:
            dataset = self.dataset
        first_frame_shape = dataset.get_data()[0].shape
        self.setRoi(center=(first_frame_shape[1] / 2, first_frame_shape[0] / 2),
                    size=(first_frame_shape[1] / 5, first_frame_shape[0] / 5))
        nframe = self._sv.getFrameNumber()
        self._sv.setStack(dataset.get_data())
        self._sv.setFrameNumber(nframe)

    def setRoi(self, roi=None, origin=None, size=None, center=None):
        """
        Sets a region of interest of the stack of images.

        :param RectangleROI roi: A region of interest.
        :param Tuple origin: If a roi is not provided, used as an origin for the roi
        :param Tuple size: If a roi is not provided, used as a size for the roi.
        :param Tuple center: If a roi is not provided, used as a center for the roi.
        """
        if roi is not None and (size is not None or center is not None or origin is not None):
            _logger.warning("Only using provided roi, the rest of parameters are omitted")

        if roi is not None:
            self._roi = roi
        else:
            self._roi.setGeometry(origin=origin, size=size, center=center)

    def getRoi(self):
        """
        Returns the roi selected in the stackview.

        :rtype: silx.gui.plot.items.roi.RectangleROI
        """
        return self._roi

    def applyRoi(self):
        """
        Function to apply the region of interest at the data of the dataset
        and show the new data in the stack. Dataset data is not yet replaced.
        A new roi is created in the middle of the new stack.
        """
        if not self._update_dataset.in_memory:
            self._abortB.show()
        self._applyB.setEnabled(False)
        self._okB.setEnabled(False)
        self.roi = RectangleROI()
        self.roi.setGeometry(origin=self.getRoi().getOrigin(), size=self.getRoi().getSize())
        self.thread = OperationThread(self, self._update_dataset.apply_roi)
        roi_dir = self._update_dataset.dir if not self._original_dataset else None
        self.thread.setArgs(size=numpy.flip(self.roi.getSize()),
                            center=numpy.flip(self.roi.getCenter()),
                            roi_dir=roi_dir)
        self.thread.finished.connect(self._updateData)
        self.thread.start()

    def abort(self):
        self._abortB.setEnabled(False)
        self._update_dataset.stop_operation(Operation.ROI)

    def _updateData(self):
        """
        Updates the stack with the data computed in the thread
        """
        self.thread.finished.disconnect(self._updateData)
        self._abortB.hide()
        self._abortB.setEnabled(True)
        self._applyB.setEnabled(True)
        self._okB.setEnabled(True)
        if self.thread.data:
            self._update_dataset = self.thread.data
            self._original_dataset = False
            assert self._update_dataset is not None
            self.setStack(self._update_dataset)
            self.resetROI()
        else:
            print("\nCorrection aborted")

    def apply(self):
        """
        Function that replaces the dataset data with the data shown in the stack of images.
        If the stack has a roi applied, it applies the same roi to the dark frames of the dataset.
        Signal emitted with the roi parameters.
        """
        if self.roi:
            self.sigComputed.emit(self.roi.getOrigin().tolist(), self.roi.getSize().tolist())
        else:
            self.sigComputed.emit([], [])

    def getDataset(self):
        bg_dataset = (self.bg_dataset.apply_roi(size=numpy.flip(self.roi.getSize()),
                                                center=numpy.flip(self.roi.getCenter()))
                      if self.bg_dataset is not None else None)
        return self._update_dataset, self.indices, self.bg_indices, bg_dataset

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

    def resetROI(self):
        """
        Sets the region of interest in the middle of the stack, with size 1/5 of the image.
        """
        frame_shape = numpy.array(self._update_dataset.get_data(0).shape)
        center = numpy.flip(frame_shape) / 2
        size = numpy.flip(frame_shape) / 5
        self.setRoi(center=center, size=size)

    def resetStack(self):
        """
        Restores stack with the dataset data.
        """
        self.roi = None
        self._update_dataset = self.dataset
        self._original_dataset = True
        self.setStack(self.dataset)

    def clearStack(self):
        """
        Clears stack.
        """
        self._sv.setStack(None)
        self._roi.setGeometry(origin=(0, 0), size=(10, 10))
