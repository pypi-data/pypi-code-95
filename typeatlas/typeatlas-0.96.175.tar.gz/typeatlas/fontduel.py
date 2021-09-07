# -*- coding: utf-8 -*-
#
#    TypeAtlas Font Duel
#    Copyright (C) 2018-2021 Milko Krachounov
#
#    This file is part of TypeAtlas
#
#    TypeAtlas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TypeAtlas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TypeAtlas.  If not, see <http://www.gnu.org/licenses/>.
#

"""Font Duel comparison widgets and tools."""

from typeatlas.compat import QtCore, QtGui, QtWidgets, QtModelProxies
from typeatlas.compat import Qt, Slot, Signal, setResizeMode
from typeatlas.fontmodels import FontDelegate, FontFilterModel, FontItemRole
from typeatlas.fontmodels import MutableFontListModel
from typeatlas.fontmodels import SampleTextRole, FontResizeProxyModel
from typeatlas.fontsampler import FontSamplerToolbox
from typeatlas.guicommon import FontRenderingChoice
from typeatlas.langutil import _, N_, H_, textlang
from typeatlas.uitools import iconSize, defaultFontPointSize, getIcon
from typeatlas.uitools import FlippableListView
from typeatlas.guicommon import TrashDropWidget
from typeatlas.options import Options
from typeatlas.util import MaybeLazy, generic_type
from typeatlas import fontgrid, opentype, datastore
import typeatlas
from html import escape as htesc
from collections import namedtuple
from operator import itemgetter, attrgetter, methodcaller


IterableOf = generic_type('Iterable')
SequenceOf = generic_type('Sequence')
MappingOf = generic_type('Mapping')
Union = generic_type('Union')


class GlyphStackFontView(QtWidgets.QWidget):

    """A glyph stack view that displays two fonts overlayed over
    one another. Displays a stack of all fonts in a font model."""

    def __init__(self, fontModel: QtCore.QAbstractItemModel, *args,
                       pointSize: int=96, sampleText: str='AbQqRr', **kwargs):
        super().__init__(*args, **kwargs)
        self.model = fontModel
        self.pointSize = pointSize
        self.sampleText = sampleText

        fontModel.rowsInserted.connect(self.repaint)
        fontModel.rowsRemoved.connect(self.repaint)
        fontModel.modelReset.connect(self.repaint)

        self.hoveredIndex = None

    @Slot(QtCore.QModelIndex)
    def indexHovered(self, index: QtCore.QModelIndex):
        """Make the hovered item red."""
        self.hoveredIndex = index
        self.repaint()

    @Slot(str)
    def setSampleText(self, text: str):
        """Set the sample text used to test fonts."""
        self.sampleText = text
        self.repaint()

    @Slot(int)
    def setPointSize(self, size: int):
        """Change the display font point size."""
        self.pointSize = size
        self.repaint()

    def paintEvent(self, event: QtGui.QPaintEvent):

        style = self.style()
        palette = self.palette()

        parent = QtCore.QModelIndex()

        painter = QtGui.QPainter()
        painter.begin(self)

        for row in range(0, self.model.rowCount(parent)):
            index = self.model.index(row, 0, parent)

            font = index.data(Qt.FontRole)
            if font is None:
                continue

            font = QtGui.QFont(font)
            font.setPointSize(self.pointSize)

            metrics = QtGui.QFontMetrics(font)

            point = QtCore.QPointF(self.rect().bottomLeft())
            point += QtCore.QPointF(0, -metrics.descent())

            path = QtGui.QPainterPath()
            path.addText(point, font, self.sampleText)

            painter.save()
            if index == self.hoveredIndex:
                painter.setPen(Qt.red)
            else:
                painter.setPen(palette.color(self.foregroundRole()))

            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
            painter.restore()

        painter.end()


class GlyphStackWidget(QtWidgets.QWidget):

    """A page with a glyph stack that displays two fonts overlayed over
    one another, and has options to change the view. Displays a stack of
    all fonts in a font model."""

    def __init__(self, model: QtCore.QAbstractItemModel, *args,
                       renderingChoice: FontRenderingChoice=None,
                       options: Options=None,
                       histories: datastore.Histories=None, **kwargs):
        super().__init__(*args, **kwargs)

        if options is None:
            options = Options.getInstance()
        if renderingChoice is None:
            renderingChoice = FontRenderingChoice()
        if histories is None:
            histories = datastore.Histories.getInstance()

        self.histories = histories

        self.renderingChoice = renderingChoice
        self.view = GlyphStackFontView(model)
        self.toolbox = FontSamplerToolbox(self, glyphStack=True)
        self.view.setPointSize(renderingChoice.glyphStackSize)
        self.view.setSampleText(self.toolbox.defaultSampleText)
        renderingChoice.glyphStackSizeChanged.connect(self.view.setPointSize)

        toolbar = QtWidgets.QToolBar()
        toolbar.setIconSize(options.toolbarIconSize)
        self.toolbox.populateToolbar(toolbar)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(toolbar)
        self.layout().addWidget(self.view)

    @Slot(str)
    def setSampleText(self, text):
        self.view.setSampleText(text)


class HoverableListView(QtWidgets.QListView):

    """A list view that allows you to hover over items, emitting the
    hoverChanged(index) signal.

    FIXME: Qt QAbstractItemView already has an 'entered' signal.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self._lastHoverIndex = None

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        index = self.indexAt(event.pos())
        if index != self._lastHoverIndex:
            self.hoverChanged.emit(index)
            self._lastHoverIndex = index
        return super().mouseMoveEvent(event)

    def leaveEvent(self, event: QtCore.QEvent):
        if self._lastHoverIndex and self._lastHoverIndex.isValid():
            self._lastHoverIndex = index = QtCore.QModelIndex()
            self.hoverChanged.emit(index)
        return super().leaveEvent(event)

    hoverChanged = Signal(QtCore.QModelIndex)


class TableRow(object):

    """A table row for font items.

    The name specifies the header for the row. If lazy, it receives the
    model as an argument.

    For each font column, the row will display the information about
    the specific item. The text, icon (and callables for other roles
    passed in custom) can be callables receiveing the fontlist.Font
    item as first argument.

    The itemFieldName specifies the row name for the item in a given
    column. That does not make sense, but consider PANOSE field names
    that depend on the family type, so one column will display the 'serif'
    and another will display the 'tool' of the font (both being a subfamily
    of sorts).
    """

    def __init__(self, name: MaybeLazy[str]=None,
                       text: MaybeLazy[str]=None,
                       icon: MaybeLazy[Union[QtGui.QIcon, str]]=None,
                       custom: MappingOf[int, MaybeLazy[object]]=(),
                       translate: bool=True,
                       itemFieldName: MaybeLazy[str]=None):
        self.name = name
        self.roleGetters = dict(custom)
        if text is not None:
            self.roleGetters[Qt.DisplayRole] = text
        if icon is not None:
            self.roleGetters[Qt.DecorationRole] = icon

        self.translate = translate
        self.itemFieldName = itemFieldName

    def data(self, fontItem, role=Qt.DisplayRole):
        getter = self.roleGetters.get(role)
        if getter is None:
            return None
        if not callable(getter):
            return getter
        try:
            result = getter(fontItem)
        except (TypeError, ValueError, AttributeError, LookupError):
            return None

        if isinstance(result, (str, bytes)):
            if role == Qt.DecorationRole:
                return getIcon(result)
            if role in [Qt.DisplayRole, Qt.ToolTipRole] and self.translate:
                return _(result)

        elif role == Qt.DisplayRole and result is not None:
            if isinstance(result, bool):
                return _('yes') if result else _('no')
            return str(result)

        return result


defaultTableRows = [
    TableRow(N_('Family'), attrgetter('family'), translate=False),
    TableRow(N_('Style'), attrgetter('style'), translate=False),
    TableRow(N_('Generic family'), attrgetter('genericfamily')),
    TableRow(N_('PANOSE class'), attrgetter('panoseclass.class_name')),
    TableRow(N_('PANOSE subclass'), attrgetter('panoseclass.subclass_name')),
    TableRow(N_('IBM class'), attrgetter('ibmclass.class_name')),
    TableRow(N_('IBM subclass'), attrgetter('ibmclass.subclass_name')),
    TableRow(N_('Monospace'), attrgetter('monospace')),
    TableRow(N_('Weight'), attrgetter('weight')),
    TableRow(N_('Slant'), attrgetter('slant')),
    TableRow(N_('Width'), attrgetter('width')),
    TableRow(N_('Decorative'), attrgetter('decorative')),
    TableRow(N_('Vertical'), attrgetter('verticallayout')),
    TableRow(N_('Font format'),
             attrgetter('font_format_info.name'),
             attrgetter('font_format_info.icon')),
    TableRow(N_('File format'),
             attrgetter('file_format_info.name'),
             attrgetter('file_format_info.icon')),
    TableRow(N_('PANOSE number'), lambda item: item.panoseclass.string()),
]


def _panoseTableRow(pos):
    return TableRow(lambda model: model.panoseFieldNames()[pos].fieldname,
                    lambda item: item.panoseclass[pos].text(translate=_),
                    itemFieldName=lambda item: item.panoseclass[pos].fieldname,
                    translate=False)


defaultTableRows.extend(_panoseTableRow(pos) for pos in range(10))


class CompareFontModel(QtCore.QAbstractItemModel):

    """Compare model for comparing fonts in a table, one font per column.
    Uses the rows defined by TableRow objects in defaultTableRows.
    """

    def __init__(self, fontModel: QtCore.QAbstractItemModel,
                       tableRows: IterableOf[TableRow]=defaultTableRows,
                       *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fontModel = fontModel
        self.tableRows = list(tableRows)
        self._cachedFieldNames = None
        self._cachedRefValues = None

        fontModel.rowsAboutToBeInserted.connect(self._fontsAboutToBeInserted)
        fontModel.rowsInserted.connect(self._fontsInserted)
        fontModel.rowsAboutToBeRemoved.connect(self._fontsAboutToBeRemoved)
        fontModel.rowsRemoved.connect(self._fontsRemoved)
        fontModel.modelAboutToBeReset.connect(self.modelAboutToBeReset)
        fontModel.modelReset.connect(self.modelReset)

        fontModel.modelAboutToBeReset.connect(self._clearCache)
        fontModel.modelReset.connect(self._resetHeader)

    def panoseFieldNames(self) -> SequenceOf[opentype.PanoseProperty]:
        """Get the PANOSE fields, together with their name. Use the
        fieldname attribute to get the actual name."""
        if self._cachedFieldNames is not None:
            return self._cachedFieldNames

        family = opentype.PANOSE_UNCLASSIFIED
        for row in range(self.fontModel.rowCount()):
            fontIndex = self.fontModel.index(row, 0, QtCore.QModelIndex())
            fontItem = fontIndex.data(FontItemRole)
            panclass = fontItem.panoseclass
            if panclass and panclass.family.value:
                family = panclass.family.value
                break

        self._cachedFieldNames = opentype.get_panose_fields(family)
        return self._cachedFieldNames

    def referenceValues(self) -> MappingOf[int, str]:
        """Return the reference values (that is, the value of the first
        column) for each row to compare against."""
        if self._cachedRefValues is not None:
           return self._cachedRefValues

        referenceValues = {}

        for col in range(self.columnCount()):
            for row in range(self.rowCount()):
                index = self.index(row, col, QtCore.QModelIndex())
                value = index.data(Qt.DisplayRole)
                referenceValues[row] = value

            break

        self._cachedRefValues = referenceValues
        return self._cachedRefValues

    @Slot()
    def _clearCache(self):
        """Clear the field name and reference cache."""
        self._cachedFieldNames = None
        self._cachedRefValues = None

    @Slot()
    def _resetHeader(self):
        """Reset the header if the PANOSE family changed."""
        self.headerDataChanged.emit(Qt.Vertical, 0, len(self.tableRows))

    @Slot()
    def _clearCacheResetHeader(self):
        """Fonts changed, so reset both the cache, and the now-changed headers."""
        self._clearCache()
        self._resetHeader()

    @Slot(QtCore.QModelIndex, int, int)
    def _fontsAboutToBeInserted(self, parent, start, end):
        if parent.isValid():
            return
        self.beginInsertColumns(QtCore.QModelIndex(), start, end)

    @Slot(QtCore.QModelIndex, int, int)
    def _fontsInserted(self, parent, start, end):
        self._clearCache()
        if parent.isValid():
            return
        self.endInsertColumns()

        if start == 0:
            self._resetHeader()

    @Slot(QtCore.QModelIndex, int, int)
    def _fontsAboutToBeRemoved(self, parent, start, end):
        if parent.isValid():
            return
        self.beginRemoveColumns(QtCore.QModelIndex(), start, end)

    @Slot(QtCore.QModelIndex, int, int)
    def _fontsRemoved(self, parent, start, end):
        self._clearCache()
        if parent.isValid():
            return
        self.endRemoveColumns()

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self.fontModel.rowCount()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self.tableRows)
        return 0

    def hasChildren(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return True
        return False

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return QtCore.QModelIndex()
        return self.createIndex(row, column, None)

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        return QtCore.QModelIndex()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role in [Qt.DisplayRole, Qt.DecorationRole, Qt.FontRole]:
                index = self.fontModel.index(section, 0, QtCore.QModelIndex())
                return index.data(role)
        elif orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                name = self.tableRows[section].name
                if callable(name):
                    name = name(self)
                return _(name)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        fontIndex = self.fontModel.index(index.column(), 0,
                                         QtCore.QModelIndex())
        fontItem = fontIndex.data(FontItemRole)
        result = self.tableRows[index.row()].data(fontItem, role)

        if not result and role == Qt.FontRole:
            refValues = self.referenceValues()
            if refValues:
                refValue = refValues.get(index.row())
                if refValue != index.data(Qt.DisplayRole):
                    font = QtGui.QFont()
                    font.setBold(True)
                    return font

        return result


class FontDuelSampleWidget(QtWidgets.QWidget):

    """Displays large font samples in a list view provided by the
    font model, for use with the font duel comparisons and its
    MutableFontListModel.

    This widget displays individual styles. The one in fontsampler
    displays families, with one style per family, based on the style
    selector.

    This is a custom selection, and the other one is filtered.
    """

    def __init__(self, model: QtCore.QAbstractItemModel,
                       renderingChoice: FontRenderingChoice=None,
                       options: Options=None,
                       histories: datastore.Histories=None,
                       *args, **kwargs):

        super().__init__(*args, **kwargs)

        if renderingChoice is None:
            renderingChoice = FontRenderingChoice()
        if options is None:
            options = Options.getInstance()
        if histories is None:
            histories = datastore.Histories.getInstance()

        self.histories = histories

        self.model = model
        self.view = grid = FlippableListView()
        self.renderingChoice = renderingChoice
        self.renderingChoice.samplesChanged.connect(self.view.reset)

        delegate = fontgrid.GridCellDelegate(grid,
                                             abbreviateHeader=True,
                                             headerRole=Qt.DisplayRole,
                                             sampleRole=SampleTextRole,
                                             sampleRendererRole=None,
                                             sizeThreshold=-1)

        grid.setMovement(QtWidgets.QListView.Snap)
        self.setColumnFlow()
        grid.setLayoutMode(QtWidgets.QListView.Batched)
        #grid.setGridSize(QtCore.QSize(40, 40))
        grid.setItemDelegateForColumn(0, delegate)
        grid.setResizeMode(QtWidgets.QListView.Adjust)
        grid.setModel(self.model)

        self.toolbox = FontSamplerToolbox(self)
        toolbar = QtWidgets.QToolBar()
        toolbar.setIconSize(options.toolbarIconSize)
        options.toolbarIconSizeChanged.connect(toolbar.setIconSize)
        self.toolbox.populateToolbar(toolbar)
        self.model.setSampleText(self.toolbox.defaultSampleText)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(toolbar)
        self.layout().addWidget(grid)

    @Slot(bool)
    def setColumnFlow(self, checked=False):
        """Make the fonts flow in columns"""
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setViewMode(QtWidgets.QListView.IconMode)
        self.view.setFlow(QtWidgets.QListView.TopToBottom)
        self.view.setWrapping(True)
        self.view.setFlipScroll(True)

    @Slot(bool)
    def setRowFlow(self, checked=False):
        """Make the fonts flow in rows"""
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setViewMode(QtWidgets.QListView.IconMode)
        self.view.setFlow(QtWidgets.QListView.LeftToRight)
        self.view.setWrapping(True)
        self.view.setFlipScroll(False)

    @Slot(bool)
    def setListView(self, checked=False):
        """Make the fonts flow vertically in a list."""
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setViewMode(QtWidgets.QListView.ListMode)
        self.view.setFlow(QtWidgets.QListView.TopToBottom)
        self.view.setWrapping(False)
        self.view.setFlipScroll(False)

    @Slot(str)
    def setSampleText(self, text: str):
        """Set the sample text."""
        #self.model.beginResetModel()
        self.model.setSampleText(text)
        #self.model.endResetModel()
        self.view.reset()


class FontInfoTable(QtWidgets.QTableView):

    """A font information table widget that can be used to display
    the information about the provided fonts.

    The families provided to the constructor are all available families,
    the fonts provided to setFontItem() are the ones to display in
    the info table."""

    def __init__(self, families: 'IterableOf[typeatlas.fontlist.FontFamily]'=(),
                       featureSets: 'typeatlas.fontlist.FeatureSets'=None,
                       *args, **kwargs):

        super().__init__(*args, **kwargs)
        model = MutableFontListModel(families, featureSets=featureSets,
                                     sampleModel=True)
        listModel = FontResizeProxyModel(pointSize=defaultFontPointSize())
        listModel.setSourceModel(model)
        self.compareModel = compareModel = CompareFontModel(listModel)
        self.fontModel = model
        self.setModel(compareModel)
    
    @Slot(object)
    @Slot(object, list)
    def setFontItem(self, *args, **kwargs):
        """Set the font items. See the help of MutableFontListModel."""
        self.fontModel.setFontItem(*args, **kwargs)


class FontDuel(QtWidgets.QMainWindow):

    """The main window of the font duel.

    This widget emits the closed signal, so it can be opened by TypeAtlas'
    main library.

    The families provided to the constructor are all available families,
    the fonts dragged into the widget are the ones to display.
    """

    def __init__(self, families: 'IterableOf[typeatlas.fontlist.FontFamily]'=(),
                       featureSets: 'typeatlas.fontlist.FeatureSets'=None,
                       renderingChoice: FontRenderingChoice=None,
                       options: Options=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(_('TypeAtlas Duel of the Fonts'))
        self.setWindowIcon(getIcon('typeatlas-duel'))

        if renderingChoice is None:
            renderingChoice = FontRenderingChoice()
        if options is None:
            options = Options.getInstance()

        windowHeight = options.fontDuelSize.height()
        self.resize(options.fontDuelSize)

        view = HoverableListView()
        view.setViewMode(view.ListMode)
        view.setFlow(QtWidgets.QListView.TopToBottom)
        view.setWrapping(True)

        model = MutableFontListModel(families, featureSets=featureSets,
                                     sampleModel=True)

        listModel = FontResizeProxyModel(pointSize=defaultFontPointSize())
        listModel.setSourceModel(model)

        compareModel = CompareFontModel(listModel)

        sampleWidget = FontDuelSampleWidget(model,
                                            renderingChoice=renderingChoice,
                                            options=options)

        stack = GlyphStackWidget(listModel, renderingChoice=renderingChoice,
                                                options=options)

        comparison = QtWidgets.QTableView()
        comparison.setModel(compareModel)
        setResizeMode(comparison.horizontalHeader(),
                      QtWidgets.QHeaderView.ResizeToContents)

        view.viewport().setAcceptDrops(True)
        view.setDropIndicatorShown(True)
        view.setDragEnabled(True)
        view.setMovement(QtWidgets.QListView.Snap)
        view.setDragDropMode(view.DragDrop)
        #view.setSelectionMode(view.SingleSelection)
        view.setSelectionMode(view.ExtendedSelection)
        view.setResizeMode(QtWidgets.QListView.Adjust)
        view.setModel(listModel)

        view.hoverChanged.connect(stack.view.indexHovered)

        trash = TrashDropWidget(stretch=True, mimeTypes=[
            'text/plain', 'text/html',
            'application/x-qabstractitemmodeldatalist',
        ])

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(stack, _('Stack view'))
        tabs.addTab(sampleWidget, _('Samples'))
        tabs.addTab(comparison, _('Features'))

        bottomLayout = QtWidgets.QHBoxLayout()
        bottomLayout.addWidget(view, 1)
        bottomLayout.addWidget(trash)

        bottom = QtWidgets.QWidget()
        bottom.setLayout(bottomLayout)


        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(Qt.Vertical)

        splitter.addWidget(tabs)
        splitter.addWidget(bottom)
        splitter.setSizes([windowHeight * 0.8, windowHeight * 0.2])

        self.setCentralWidget(splitter)

    closed = Signal()

    def closeEvent(self, event):
        r = super().closeEvent(event )
        if event.isAccepted():
            self.closed.emit()
        return r

