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

__authors__ = ["H. Payno", "J. Garriga"]
__license__ = "MIT"
__date__ = "26/04/2021"

import numpy
from functools import partial

from silx.gui import qt
from darfix.core.dataset import Dataset
from darfix.core.dimension import Dimension, _METADATA_TYPES, _METADATA_TYPES_I, DEFAULT_METADATA
import logging

_logger = logging.getLogger(__file__)


class DimensionMapping(qt.QWidget):
    """
    Widget used to define the number of dimension and with which values they are
    mapped
    """
    _V_HEADERS = ['Axis', 'Kind', 'Name', 'Size', 'Tolerance', '', '']

    fitSucceed = qt.Signal()
    """Signal emitted when the fit succeeds"""
    fitFailed = qt.Signal()
    """Signal emitted when the fit fails"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        self._table = qt.QTableWidget(parent=self)
        self._table.setColumnCount(len(self._V_HEADERS))
        self._table.setHorizontalHeaderLabels(self._V_HEADERS)
        header = self._table.horizontalHeader()
        if qt.qVersion() < "5.0":
            setResizeMode = header.setResizeMode
        else:
            setResizeMode = header.setSectionResizeMode
        for iColumn in range(len(self._V_HEADERS)):
            if iColumn in (1, 2):
                setResizeMode(iColumn, qt.QHeaderView.Stretch)
            else:
                setResizeMode(iColumn, qt.QHeaderView.ResizeToContents)
        self._table.verticalHeader().hide()
        self._dims = {}

        self.layout().addWidget(self._table, 0, 0, 6, 6)
        self._addButton = qt.QPushButton('add', parent=self)
        self.layout().addWidget(self._addButton, 6, 5, 1, 1)

        # connect Signal/SLOT
        self._addButton.pressed.connect(self.addDim)

    def clear(self):
        widgets = list(self._dims.values())
        for widget in widgets:
            self.removeDim(widget)

    @property
    def ndim(self):
        return len(self._dims)

    @property
    def dims(self):
        return self._dims

    def addDim(self, axis=None, dim=None):
        """

        :param axis: which axis is defining this dimension
        :param `Dimension` dim: definition of the dimension to add
        """
        if axis is None:
            axis = self._getNextFreeAxis()
        row = self._table.rowCount()
        self._table.setRowCount(row + 1)
        widget = _DimensionItem(parent=self, table=self._table, row=row)
        widget.removed.connect(self.removeDim)
        if dim is not None:
            widget.setDim(dim)
        widget.axis = axis
        self._dims[row] = widget
        return widget

    def removeDim(self, row):
        """
        Remove dimension.

        :param Union[int,`_DimensionItem`]: row or item to remove
        """
        if isinstance(row, _DimensionItem):
            iRow = row._row
        else:
            iRow = row
        self._table.removeRow(iRow)
        self._dims[iRow].removed.disconnect(self.removeDim)
        self._dims[iRow].setAttribute(qt.Qt.WA_DeleteOnClose)
        self._dims[iRow].close()
        del self._dims[iRow]
        ini_rows = sorted(list(self._dims.keys()))
        for row in ini_rows:
            if row <= iRow:
                continue
            widget = self._dims[row]
            new_row = row - 1
            assert new_row >= 0
            widget.embedInTable(table=self._table, row=new_row)
            widget.axis = self._getNextFreeAxis()
            self._dims[new_row] = widget
            del self._dims[row]

        self.fitFailed.emit()

    def _getNextFreeAxis(self):
        """
        :return int: next unused axis
        """
        res = 0
        usedAxis = []
        [usedAxis.append(_dim.axis) for _dim in self._dims.values()]
        while res in usedAxis:
            res = res + 1
        return res


class DimensionWidget(DimensionMapping):
    """
    Widget to define dimensions and try to fit those with dataset
    """

    def __init__(self, parent=None):
        DimensionMapping.__init__(self, parent)
        self._dataset = None
        self._update_dataset = None
        self.indices = None
        self.bg_indices = None
        self.bg_dataset = None
        self.metadata_type = _METADATA_TYPES['default']
        self.tolerance = 1e-9

        metadataTypeLabel = qt.QLabel("Metadata type: ")
        toleranceLabel = qt.QLabel("Tolerance: ")
        self._metadataTypeCB = qt.QComboBox()
        for metaType in _METADATA_TYPES:
            self._metadataTypeCB.addItem(metaType)
        self._toleranceLE = qt.QLineEdit(str(self.tolerance))
        self._toleranceLE.setToolTip("Tolerance for which the values in the dimensions will be considered unique")
        validator = qt.QDoubleValidator()
        validator.setBottom(0)
        self._toleranceLE.setValidator(validator)
        self._autoDetect = qt.QPushButton('Find dimensions', parent=self)
        self._autoDetect.setToolTip("Automatically find all dimensions that "
                                    "change through the dataset. \n"
                                    "It is considered that a dimension changes "
                                    "if the number of unique values is greater "
                                    "than one.\nThe metadata type is needed to "
                                    "choose which values to compare, and the "
                                    "threshold to know when two values are "
                                    "considered to be different.\nThe threshold"
                                    " is only used in values that are numbers.")
        self._fitButton = qt.QPushButton('Fit', parent=self)
        self._fitButton.setToolTip("Try to reshape data into given dimensions")
        self._clearButton = qt.QPushButton('Clear', parent=self)

        self.layout().addWidget(metadataTypeLabel, 6, 0, 1, 1)
        self.layout().addWidget(self._metadataTypeCB, 6, 1, 1, 1)
        self.layout().addWidget(toleranceLabel, 6, 2, 1, 1)
        self.layout().addWidget(self._toleranceLE, 6, 3, 1, 1)
        self.layout().addWidget(self._clearButton)
        self.layout().addWidget(self._fitButton)
        self.layout().addWidget(self._autoDetect, 6, 4, 1, 1)

        # connect Signal/SLOT
        self._fitButton.pressed.connect(self.fit)
        self._clearButton.pressed.connect(self.clear)
        self._autoDetect.pressed.connect(self._find_dimensions)
        self._metadataTypeCB.currentTextChanged.connect(self._updateKind)
        self._toleranceLE.textChanged.connect(self._updateTolerance)

    @property
    def dataset(self):
        return self._dataset

    def getDataset(self):
        return self._update_dataset, self.indices, self.bg_indices, self. bg_dataset

    def _updateKind(self, metadata_type=None):
        if metadata_type is None:
            metadata_type = self._metadataTypeCB.currentText()
        self.metadata_type = _METADATA_TYPES[metadata_type]

    def _updateTolerance(self, tolerance=None):
        if tolerance is None:
            tolerance = self._toleranceLE.text()
        try:
            self.tolerance = float(tolerance)
        except ValueError:
            _logger.warning("Wrong tolerance")

    def clear(self):
        super().clear()
        if self.dataset is None:
            _logger.warning('No dataset to be fitted')
            return
        self.dataset.clear_dims()

    def setDataset(self, dataset, indices=None, bg_indices=None, bg_dataset=None):
        """

        :param dataset: the dataset for which we want to define the
                           dimensions.
        :type dataset: `Dataset`
        """
        assert isinstance(dataset, Dataset)
        self._dataset = dataset
        self._update_dataset = dataset
        self.indices = indices
        self.bg_indices = bg_indices
        self.bg_dataset = bg_dataset
        if dataset.nframes > 0:
            for widget in self._dims.values():
                widget._setMetadata(self.dataset.get_data().metadata[0])

    def _find_dimensions(self):
        """
        Automatically find all dimensions that change through the dataset.
        It is considered that a dimension changes if the number of unique values
        is greater than one. The metadata type is needed to choose which values
        to compare, and the threshold to know when two values are considered to
        be different. The threshold is only used in values that are numbers.
        """
        self.dataset.find_dimensions(self.metadata_type, self.tolerance)
        super().clear()
        for dim in self.dataset.dims:
            self.addDim(dim[0], dim[1])

    def fit(self):
        """
        Fit dimensions into the data.

        :returns: return status of the fit and fail reason, if any
        :rtype: Union[bool,str,None]
        """
        if self.dataset is None:
            _logger.warning('No dataset to be fitted')
            return

        qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
        msg = qt.QMessageBox()
        try:
            if self.dims:
                self.dataset.clear_dims()
                for dimension in self.dims.values():
                    axis = dimension.axis
                    dimension = dimension.dim
                    values = numpy.unique([data.get_value(kind=dimension.kind,
                                           name=dimension.name)[0] for data in self.dataset.get_data().metadata])
                    dimension.set_unique_values(values)
                    self.dataset.add_dim(axis=axis, dim=dimension)
            else:
                raise ValueError("Cannot fit without dimensions")
            super().clear()
            for dim in self.dataset.dims:
                self.addDim(dim[0], dim[1])
            self._update_dataset = self.dataset.reshape_data()
        except Exception as e:
            self.dataset.clear_dims()
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setText("Error: {0}".format(e))
            msg.setWindowTitle("Fit failed!")
            self.fitFailed.emit()
            return False, e
        else:
            self.fitSucceed.emit()
            msg.setIcon(qt.QMessageBox.Information)
            msg.setText("Dimensions {} could be fit".format(', '.join(self.dataset.dims.get_names())))
            msg.setWindowTitle("Fit succeeded!")
            return True, None
        finally:
            qt.QApplication.restoreOverrideCursor()
            msg.setStandardButtons(qt.QMessageBox.Ok)
            msg.exec_()

    def setDims(self, dims):
        """

        :param dict dims: axis as key and `Dimension` as value.
        """
        self.clear()
        assert type(dims) is dict
        for axis, dim in dims.items():
            assert type(axis) is int
            assert isinstance(dim, Dimension)
            self.addDim(axis=axis, dim=dim)
            if self.dataset is not None and len(self.dataset.data.metadata) > 0:
                if not dim.unique_values:
                    values = numpy.unique(
                        [data.get_value(kind=dim.kind, name=dim.name)[0]
                         for data in self.dataset.data.metadata])
                    dim.set_unique_values(values)
            self.dataset.add_dim(axis=axis, dim=dim)

    def addDim(self, axis=None, dim=None):
        """

        :param axis: which axis is defining this dimension
        :param `Dimension` dim: definition of the dimension to add
        """
        widget = super().addDim(axis, dim)
        if self.dataset is not None and len(self.dataset.data.metadata) > 0:
            widget._setMetadata(self.dataset.data.metadata[0])

        return widget


class _DimensionItem(Dimension, qt.QWidget):
    """Widget use to define a dimension"""
    removed = qt.Signal(qt.QObject)
    """Signal emitted when the Item should be removed"""

    dimValueChanged = qt.Signal()
    """Signal emitted when the dimension definition is changed"""

    axisChanged = qt.Signal(int, int)
    """Signal emitted when the axis value is changed: id (row), new_value_value
    """

    class _SizeWidget(qt.QWidget):
        valueChanged = qt.Signal(int)
        """Signal emitted when the value of the Spin box change but decorelated
        with the active state
        """

        def __init__(self, parent):
            qt.QWidget.__init__(self, parent)
            self.setLayout(qt.QVBoxLayout())
            self._sizeSP = qt.QSpinBox(parent=self)
            """_sizeSP will be used to define the size. Will be editable if the
            size editable (so if dimension is set from a relative parameter)
            """
            self.layout().addWidget(self._sizeSP)

            self.layout().setContentsMargins(0, 0, 0, 0)
            self._active = False
            self._sizeSP.hide()
            # expose API
            self.setMinimum = self._sizeSP.setMinimum

            # connect Signal/SLOT
            self._sizeSP.valueChanged.connect(self._valueHasChanged)

        @property
        def value(self):
            return self._sizeSP.value

        def setValue(self, size, editable=True):
            """

            :param int or None size: the size of the dimension. If None, not
                                     define yet
            :param editable: the size will be editable if given by the use (so)
                             if is relative.
            """
            if size is None:
                self._sizeSP.hide()
                self._sizeLabel.hide()
            else:
                assert type(size) is int
                self._sizeSP.show()
                self._sizeSP.setMaximum(max(99, 2 * size))
                self._sizeSP.setValue(size)
                self.setEnabled(editable)

        def setEnabled(self, editable):
            self._sizeSP.setEnabled(editable)

        def toggle(self, checked):
            self._active = checked
            if checked:
                self._sizeSP.show()
            else:
                self._sizeSP.hide()

        def _valueHasChanged(self, value):
            self.valueChanged.emit(value)

    def __init__(self, parent, table, row):
        """

        :param QTableWidget table: if has to be embed in a table the
                                           parent table
        :param int row: row position in the QTableWidget. Also used as ID
        """
        qt.QWidget.__init__(self, parent)
        Dimension.__init__(self, kind=DEFAULT_METADATA, name='')

        self.__metadata = None

        # axis
        self._axis = qt.QSpinBox(parent=self)
        self._axis.setMinimum(0)
        # kind
        self._kindCB = qt.QComboBox(parent=self)
        for _kindName in _METADATA_TYPES:
            self._kindCB.addItem(_kindName)
        # name
        self._namesCB = qt.QComboBox(parent=self)
        # size
        self._sizeWidget = self._SizeWidget(parent=self)
        self._sizeWidget.setMinimum(0)
        self._setSize(0)
        # tolerance
        self._toleranceLE = qt.QLineEdit(parent=self)
        validator = qt.QDoubleValidator()
        validator.setBottom(0)
        self._toleranceLE.setValidator(validator)
        self._setTolerance(1e-9)
        # rm button
        style = qt.QApplication.style()
        icon = style.standardIcon(qt.QStyle.SP_BrowserStop)
        self._rmButton = qt.QPushButton(icon=icon, parent=self)
        icon = style.standardIcon(qt.QStyle.SP_FileDialogContentsView)
        self._infoButton = qt.QPushButton(icon=icon, parent=self)
        self._infoButton.hide()

        # connect Signal/slot
        self._rmButton.pressed.connect(self.remove)
        self._axis.valueChanged.connect(self._axisHasChanged)
        self._kindCB.currentIndexChanged.connect(self._dimHasChanged)
        self._sizeWidget.valueChanged.connect(self._dimHasChanged)
        self._namesCB.currentIndexChanged.connect(self._dimHasChanged)
        self._kindCB.currentIndexChanged.connect(self._updateNames)
        self._infoButton.pressed.connect(self.showUniqueNames)

        _callback = partial(self._sizeWidget.setValue, 0)
        self._toleranceLE.editingFinished.connect(_callback)

        # update values from `Dim` class
        self._kindCB.currentTextChanged.connect(self.set_kind)
        self._namesCB.currentTextChanged.connect(self.set_name)
        self._sizeWidget.valueChanged.connect(self.set_size)

        self.embedInTable(table=table, row=row)
        self.__row = row

    def _axisHasChanged(self, value):
        self.axisChanged.emit(self._row, value)

    def _dimHasChanged(self, *args, **kwargs):
        self.dimValueChanged.emit()

    def remove(self):
        self.removed.emit(self)

    def showUniqueNames(self):
        title = "%s - %s" % (_METADATA_TYPES_I[self.kind], self.name)
        ptp = float(self.unique_values[-1]) - float(self.unique_values[0])
        unique_values_str = []
        [unique_values_str.append(str(val)) for val in self.unique_values]
        msg = 'Unique values: [' + ', '.join(unique_values_str) + ']\n Ptp: ' + str(ptp)
        qt.QMessageBox.information(self, title, msg)

    def setUniqueValues(self, values):
        super().set_unique_values(values)
        if values is None:
            self._infoButton.hide()
        else:
            self._infoButton.show()

    def setDim(self, dim):
        assert isinstance(dim, Dimension)
        _kind = _METADATA_TYPES_I[dim.kind]
        idx = self._kindCB.findText(_kind)
        assert idx >= 0
        self._kindCB.setCurrentIndex(idx)
        idx = self._namesCB.findText(dim.name)
        if idx >= 0:
            self._namesCB.setCurrentIndex(idx)
        else:
            self._namesCB.addItem(dim.name)
        if dim.size is not None:
            self._sizeWidget.setValue(dim.size)
        self._setTolerance(str(dim.tolerance))
        self.setUniqueValues(dim.unique_values)

    @property
    def _row(self):
        return self.__row

    @property
    def axis(self):
        return self._axis.value()

    @axis.setter
    def axis(self, axis):
        assert type(axis) is int
        self._axis.setValue(axis)

    @property
    def kind(self):
        assert self._kindCB.currentText() in _METADATA_TYPES
        return _METADATA_TYPES[self._kindCB.currentText()]

    @property
    def dim(self):
        return Dimension(name=self.name, kind=self.kind, size=self.size, tolerance=self.tolerance)

    @property
    def size(self):
        return self._sizeWidget.value()

    @property
    def name(self):
        return self._namesCB.currentText()

    @property
    def tolerance(self):
        return float(self._toleranceLE.text())

    def _setSize(self, size):
        Dimension.set_size(self, size)
        self._sizeWidget.setValue(size=size)

    def setNames(self, names):
        self._namesCB.clear()
        for name in sorted(list(names)):
            self._namesCB.addItem(name)

    def _setTolerance(self, tolerance):
        self._toleranceLE.setText(str(tolerance))

    def embedInTable(self, table, row):
        self.__row = row
        for column, widget in enumerate((self._axis, self._kindCB, self._namesCB, self._sizeWidget,
                                         self._toleranceLE, self._infoButton, self._rmButton)):
            table.setCellWidget(row, column, widget)

    def _updateNames(self, *args, **kwargs):
        """Update names for the current kind"""
        if self.__metadata is not None:
            _lastActiveName = self.name
            self.setNames(self.__metadata.get_keys(self.kind))
            idx = self._namesCB.findText(_lastActiveName)
            if idx >= 0:
                self._namesCB.setCurrentIndex(idx)

    def _setMetadata(self, metadata):
        self.__metadata = metadata
        self._updateNames()
