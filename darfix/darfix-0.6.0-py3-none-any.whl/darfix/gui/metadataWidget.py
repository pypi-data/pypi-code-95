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
__date__ = "08/04/2020"


import numpy

from silx.gui import qt

from darfix.core.dimension import _METADATA_TYPES


class MetadataWidget(qt.QMainWindow):

    def __init__(self, parent=None):
        """
        Widget used to show the metadata in a table.
        """
        super(MetadataWidget, self).__init__(parent)
        self.setWindowTitle("Metadata")

        metadataTypeLabel = qt.QLabel("metadata type: ")
        self._metadataTypeCB = qt.QComboBox()
        for metaType in _METADATA_TYPES:
            self._metadataTypeCB.addItem(metaType)

        metadataTypeWidget = qt.QWidget(self)
        metadataTypeWidget.setLayout(qt.QHBoxLayout())
        metadataTypeWidget.layout().addWidget(metadataTypeLabel)
        metadataTypeWidget.layout().addWidget(self._metadataTypeCB)

        self._table = qt.QTableWidget()

        mainWidget = qt.QWidget(self)
        mainWidget.setLayout(qt.QVBoxLayout())
        mainWidget.layout().addWidget(metadataTypeWidget)
        mainWidget.layout().addWidget(self._table)

        self.mainWidget = mainWidget
        self.setCentralWidget(mainWidget)
        self._metadataTypeCB.currentTextChanged.connect(self._updateView)

    def setDataset(self, dataset, indices=None, bg_indices=None, bg_dataset=None):
        self._dataset = dataset
        self._updateView()

    def clearTable(self):
        self._table.clear()

    def _updateView(self, metadata_type=None):
        """
        Updates the view to show the correponding metadata.

        :param Union[None, int] metadata_type: Kind of metadata.
        """
        if metadata_type is None:
            metadata_type = self._metadataTypeCB.currentText()
        metadata_type = _METADATA_TYPES[metadata_type]

        self._table.clear()
        # v_header = [str(i) for i in range(self.__experiment.nslices)]
        metadata = self._dataset.get_data().metadata
        self._table.setRowCount(len(metadata))
        # self._table.setVerticalHeaderLabels(v_header)

        columnCount = None
        for row, metadata_frame in enumerate(metadata):
            keys = metadata_frame.get_keys(kind=metadata_type)
            if not row:
                if columnCount is None:
                    self._table.setColumnCount(len(keys))
                    self._table.setHorizontalHeaderLabels(keys)
                elif columnCount != len(metadata_frame):
                    raise ValueError('Metadata keys are incoherent')

            for column, key in enumerate(keys):
                _item = qt.QTableWidgetItem()
                txt = metadata_frame.get_value(kind=metadata_type, name=key)
                if type(txt) is numpy.ndarray and txt.size == 1:
                    txt = txt[0]
                if hasattr(txt, 'decode'):
                    txt = txt.decode('utf-8')
                else:
                    txt = str(txt)
                _item.setText(txt)
                _item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
                self._table.setItem(row, column, _item)
