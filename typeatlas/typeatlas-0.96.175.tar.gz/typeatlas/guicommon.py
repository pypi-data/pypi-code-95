# -*- coding: utf-8 -*-
#
#    TypeAtlas GUI Common Functions/Widgets
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

"""Common GUI widgets used across TypeAtlas."""

from typeatlas.compat import QtCore, QtGui, QtWidgets, QtModelProxies
from typeatlas.compat import Qt, Slot, Signal, setResizeMode
from typeatlas.uitools import Toolbox, iconSize, getIcon, DragDropWidget
from typeatlas.uitools import getIconHtml, getImage
from typeatlas.uitools import generalWidth, generalHeight
from typeatlas.uitools import TYPING_DELAY
from typeatlas.options import Options
from typeatlas.charinfo import CharacterDatabase, all_character_codes
from typeatlas.langutil import LanguageDatabase
from typeatlas.langutil import _, N_, H_, textlang
from typeatlas import blockmath, charinfo, osinfo, annotations
from functools import partial
from itertools import groupby
from operator import attrgetter
from collections import OrderedDict, Counter
from collections.abc import Callable, Sequence, Iterator
from typeatlas.util import OrderedSet, format_size, generic_type
import typeatlas
import os


Union = generic_type('Union')
Optional = generic_type('Optional')
IterableOf = generic_type('Iterable')
SequenceOf = generic_type('Sequence')


class CustomComboBox(QtWidgets.QComboBox):

    """A combo box with extra features, such as it can be made narrow,
    as required by the unicode block and script combo boxes. It provides
    signals that are emitted before and after showing the popup, which
    is also needed for the aforementioned combo boxes.."""

    popupAboutToShown = Signal()
    popupShown = Signal()

    narrow = False

    def setNarrow(self, narrow: bool=True,
                        sizeTextHint: str='Six words long'):
        """Make the combo box narrow, using the text hint to determine the
        size. On show, the size may be reset to actual contents."""
        self.narrow = narrow
        if narrow:
            metrics = QtGui.QFontMetrics(QtGui.QFont())

            self.setSizeAdjustPolicy(self.AdjustToMinimumContentsLength)
            # That's actually ignored?
            self.setMinimumSize(QtCore.QSize(metrics.width(sizeTextHint),
                                             metrics.height()))
        else:
            self.setSizeAdjustPolicy(self.AdjustToContentsOnFirstShow)
            self.setMinimumSize(QtCore.QSize(0, 0))

    def showPopup(self):
        """Show the popup."""
        if self.narrow:
            self.view().setMinimumWidth(self.view().sizeHintForColumn(0))
        self.popupAboutToShown.emit()
        super().showPopup()
        self.popupShown.emit()



class FontRenderingChoice(Toolbox):

    """Menu items for setting the font rendering. Since this uses the options,
    some modules incorrectly use this class to carry the options instance
    around."""

    def __init__(self, options: Options=None):
        if options is None:
            options = Options.getInstance()
        self.antialiasStyle = QtGui.QFont.PreferDefault
        self.hintingPreference = QtGui.QFont.PreferDefaultHinting

        self.listSize = options.listFontSize
        self.sampleSize = options.sampleFontSize
        self.glyphStackSize = options.glyphStackFontSize
        self.previewSize = options.previewFontSize
        self.gridSize = options.gridFontSize
        self.charBoxSize = options.charBoxFontSize

        self.options = options
        self.antialiasingItems = [
            (QtGui.QFont.PreferDefault, _('Default antialiasing')),
            (QtGui.QFont.NoAntialias, _('No antialiasing')),
        ]
        if hasattr(QtGui.QFont, 'NoSubpixelAntialias'):
            self.antialiasingItems.append(
                (QtGui.QFont.NoSubpixelAntialias, _('No subpixel rendering')))
        self.antialiasingItems.append(
            (QtGui.QFont.PreferAntialias, _('Antialiasing')))

        self.hintingItems = [
            (QtGui.QFont.PreferDefaultHinting, _('Default hinting')),
            (QtGui.QFont.PreferNoHinting, _('No hinting')),
            (QtGui.QFont.PreferVerticalHinting, _('Vertical hinting')),
            (QtGui.QFont.PreferFullHinting, _('Full hinting')),
        ]

        #self.antialiasStyle = QtGui.QFont.NoAntialias

        self._antialiasingActions = {}
        self._hintingActions = {}

        super(FontRenderingChoice, self).__init__()

        options.listFontSizeChanged.connect(self.setListSize)
        options.sampleFontSizeChanged.connect(self.setSampleSize)
        options.glyphStackFontSizeChanged.connect(self.setGlyphStackSize)
        options.previewFontSizeChanged.connect(self.setPreviewSize)
        options.gridFontSizeChanged.connect(self.setGridSize)
        options.charBoxFontSizeChanged.connect(self.setCharBoxSize)

    def actionDefinitions(self) -> Iterator:
        with self.group(exclusive=True):
            for i, (value, label) in enumerate(self.antialiasingItems):
                yield self.action(partial(self._antialiasChanged, i), label,
                                  checkable=True, checked=not i)
        yield self.separator()

        with self.group(exclusive=True):
            for i, (value, label) in enumerate(self.hintingItems):
                yield self.action(partial(self._hintingChanged, i), label,
                                  checkable=True, checked=not i)

    changed = Signal()

    listChanged = Signal()
    listSizeChanged = Signal(int)

    previewChanged = Signal()
    previewSizeChanged = Signal(int)

    samplesChanged = Signal()
    sampleSizeChanged = Signal(int)

    glyphStackChanged = Signal()
    glyphStackSizeChanged = Signal(int)

    gridChanged = Signal()
    gridSizeChanged = Signal(int)

    charBoxChanged = Signal()
    charBoxSizeChanged = Signal(int)

    @Slot(int)
    def setListSize(self, size: int):
        """Set the font size in the font list."""
        self.listSize = size
        self.listSizeChanged.emit(size)
        self.listChanged.emit()

    @Slot(int)
    def setPreviewSize(self, size: int):
        """Set the font size in the sample preview pane."""
        self.previewSize = size
        self.previewSizeChanged.emit(size)
        self.previewChanged.emit()

    @Slot(int)
    def setSampleSize(self, size: int):
        """Set the font size in sample font list"""
        self.sampleSize = size
        self.sampleSizeChanged.emit(size)
        self.samplesChanged.emit()

    @Slot(int)
    def setGlyphStackSize(self, size: int):
        """Set the font size in the glyph stack in font duel"""
        self.glyphStackSize = size
        self.glyphStackSizeChanged.emit(size)
        self.glyphStackChanged.emit()

    @Slot(int)
    def setGridSize(self, size: int):
        """Set the font size in the font grid"""
        self.gridSize = size
        self.gridSizeChanged.emit(size)
        self.gridChanged.emit()

    @Slot(int)
    def setCharBoxSize(self, size: int):
        """Set the font size in the character box below the font grid"""
        self.charBoxSize = size
        self.charBoxSizeChanged.emit(size)
        self.charBoxChanged.emit()

    def populateToolbarWithCombos(self, toolbar: QtWidgets.QToolBar):
        """Add antialiasing combo boxes to a toolbar. Why???"""
        antialiasWidget = QtWidgets.QComboBox()
        for item in self.antialiasingItems:
            antialiasWidget.addItem(item[1])
        antialiasWidget.currentIndexChanged.connect(self._antialiasChanged)

        hintingWidget = QtWidgets.QComboBox()
        for item in self.hintingItems:
            hintingWidget.addItem(item[1])
        hintingWidget.currentIndexChanged.connect(self._hintingChanged)
        toolbar.addWidget(antialiasWidget)
        toolbar.addWidget(hintingWidget)

    @Slot(int, bool)
    def _antialiasChanged(self, index: int, checked: bool=False):
        """The antialiasing has changed. Emit all signals"""
        self.antialiasStyle = self.antialiasingItems[index][0]
        self.changed.emit()
        self.previewChanged.emit()
        self.listChanged.emit()
        self.samplesChanged.emit()
        self.gridChanged.emit()

    @Slot(int, bool)
    def _hintingChanged(self, index: int, checked: bool=False):
        """The hinting has changed. Emit all signals"""
        self.hintingPreference = self.hintingItems[index][0]
        self.changed.emit()
        self.previewChanged.emit()
        self.listChanged.emit()
        self.samplesChanged.emit()
        self.gridChanged.emit()


class TrashDropWidget(DragDropWidget):

    """A trash icon drop widget. Dropping things here deletes them."""

    def __init__(self, *args, dropEnabled=True, stretch=False, **kwargs):
        super().__init__(*args, dropEnabled=dropEnabled, **kwargs)
        self.iconLabel = QtWidgets.QLabel()
        self.textLabel = QtWidgets.QLabel()

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.iconLabel)
        self.layout().addWidget(self.textLabel)

        self.iconSize = iconSize(refSize=32)
        self.icon = getIcon('user-trash')

        self.iconLabel.setPixmap(self.icon.pixmap(self.iconSize))
        self.textLabel.setText(_('Trash'))

        if stretch:
            self.layout().addStretch(1)

    def setIcon(self, icon: QtGui.QIcon):
        """Set the icon of the trash can. QIcon.fromTheme('user-trash') is
        a good choice, and is the default."""
        self.icon = icon
        self.iconLabel.setPixmap(self.icon.pixmap(self.iconSize))

    def setIconSize(self, size: int):
        """Set the icon size. The default would be 32 pixels on
        a 96 DPI screen."""
        self.iconSize = size
        self.iconLabel.setPixmap(self.icon.pixmap(self.iconSize))

    def setLabelText(self, text: str):
        """Set the text label. Defaults to localized 'Trash'."""
        self.textLabel.setText(text)

    def supportedDropActions(self):
        if self.dropEnabled():
            return Qt.MoveAction
        else:
            return Qt.IgnoreAction


def _add_key_value_to_grid(grid: QtWidgets.QGridLayout,
                           name: str, value: str,
                           icon: Union[QtGui.QIcon, str]=None, *,
                           options: Options,
                           moreInfoSlot: Callable=None):
    """Add key and value row to a grid layout, with an optional icon.

    Options are required to get the font size. If a moreInfoSlot callable
    is provided, it will be called when an ellipsis button is pressed.

    Used by the AnnotationWidget.
    """

    i = grid.rowCount()

    nameLabel = QtWidgets.QLabel()
    valueLabel = QtWidgets.QLabel()

    nameLabel.setTextFormat(Qt.PlainText)
    valueLabel.setTextFormat(Qt.PlainText)

    nameLabel.setText(name + ':')
    valueLabel.setText(value)


    nameLabel.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

    if icon is None or (not icon and icon == ''):
        grid.addWidget(nameLabel, i, 0, 1, 1)
        valuePos = (i, 1, 1, 2)
    else:
        if isinstance(icon, str):
            icon = getIcon(icon)
        iconLabel = QtWidgets.QLabel()
        iconLabel.setPixmap(icon.pixmap(options.infoIconSize))

        grid.addWidget(nameLabel, i, 0, 1, 1)
        grid.addWidget(iconLabel, i, 1, 1, 1)
        valuePos = (i, 2, 1, 1)

    if moreInfoSlot is None:
        grid.addWidget(valueLabel, *valuePos)

    else:
        more = QtWidgets.QPushButton('...')
        more.clicked.connect(moreInfoSlot)
        #more.setMinimumSize(QtCore.QSize(0, 0))
        more.setFlat(True)

        valueLayout = QtWidgets.QHBoxLayout()
        valueLayout.addWidget(valueLabel, 1)
        valueLayout.addWidget(more)

        grid.addLayout(valueLayout, *valuePos)


def _add_separator_to_grid(grid: QtWidgets.QGridLayout):
    """Add a separator row to the grid layout. Used by the
    AnnotationWidget."""

    sep = QtWidgets.QFrame()
    sep.setFrameShape(sep.HLine)
    grid.addWidget(sep, grid.rowCount(), 0, 1, 3)


class AnnotationWidget(QtWidgets.QWidget):

    """A widget displaying an annotation, usually pertaining
    to a font item."""

    def __init__(self, item: 'typeatlas.fontlist.FontLike',
                       info: annotations.Annotation,
                       isFileType: bool=False, *a, options: Options, **kw):
        super().__init__(*a, **kw)

        add = partial(_add_key_value_to_grid, options=options)
        add_separator = _add_separator_to_grid

        annotation = info.annotation
        grid = QtWidgets.QGridLayout()
        self.setLayout(grid)

        self.setWindowTitle(annotation.get_name(translate=_, decorated=True))
        self.setWindowIcon(getIcon(info.icon))

        trademarks = set()
        category = getattr(annotation, 'category', None)

        for relText, subannotation in annotation.relations(translate=_):

            if relText:
                add_separator(grid)

                note = QtWidgets.QLabel()
                note.setTextFormat(Qt.PlainText)
                note.setText(relText)
                grid.addWidget(note, grid.rowCount(), 0, 1, 3)

            nameTuples = subannotation.get_name_tuples(annotations.long,
                                                       translate=_,
                                                       decorated=True)

            for i, (header, text, nameOb) in enumerate(nameTuples):
                add(grid, header, text,
                    icon=subannotation.icon if not i else None)

            for noteText in subannotation.get_notes(translate=_):
                note = QtWidgets.QLabel()
                note.setTextFormat(Qt.PlainText)
                note.setText(noteText)
                grid.addWidget(note, grid.rowCount(), 0, 1, 3, Qt.AlignCenter)

            trademarks.update(subannotation.get_trademarks(translate=_))

        if category is not None:
            categories = annotation.categories()
        else:
            categories = ()

        for category in categories:
            add_separator(grid)
            add(grid, category.get_header(translate=_),
                        category.get_name(annotations.long, translate=_))

            if category.illustration:
                image = getImage(category.illustration)
                pixmap = image.pixmap(iconSize(refSize=256))
                illustration = QtWidgets.QLabel()
                illustration.setPixmap(pixmap)
                grid.addWidget(illustration, grid.rowCount(), 0, 1, 3,
                               Qt.AlignCenter)
            trademarks.update(category.get_trademarks(translate=_))

        if trademarks:
            add_separator(grid)
            for trademark in trademarks:
                note = QtWidgets.QLabel()
                note.setTextFormat(Qt.PlainText)
                note.setText(trademark)
                grid.addWidget(note, grid.rowCount(), 0, 1, 3, Qt.AlignCenter)

        grid.addWidget(QtWidgets.QWidget(), grid.rowCount(), 0, 1, 3)
        grid.setColumnStretch(grid.columnCount() - 1, 1)
        grid.setRowStretch(grid.rowCount() - 1, 1)


HIDE_FIRST_TAB = '''
            QTabBar::tab:first {
                max-width: 0px;
            }
        '''


class _TabRow(QtWidgets.QTabBar):

    """A tab row of a multi-tab widget. The first tab of this is a
    fake hidden tab widget."""

    def minimumTabSizeHint(self, index):
        if index == 0:
            res = QtCore.QSize(0, 0)
        else:
            res = super().minimumTabSizeHint(index)
        return res

    def tabSizeHint(self, index):
        if index == 0:
            res = QtCore.QSize(0, 0)
        else:
            res = super().tabSizeHint(index)
        return res

    _wheelMoved = Signal(QtGui.QWheelEvent)
    _mouseLeft = Signal(QtCore.QEvent)

    def wheelEvent(self, event):
        self._wheelMoved.emit(event)

    def leaveEvent(self, event):
        self._mouseLeft.emit(event)


class MultiRowTabWidget(QtWidgets.QWidget):

    """A multi-row tab widget.

    Despite Qt's opposition to such, the use of multi-row tab widgets by
    Microsoft (e.g. as seen in Microsoft Office 4.3) is nice. More
    importantly and less subjectively, it is less horrible than *hiding*
    the extra tabs and having to scroll to get to them, which totally
    hides the numbers of tabs available.

    Unfortunately, this widget tends to be ugly-ish with most themes, so
    we are not using it. Additionally, the rows need to be layed out manually.
    Perhaps it's easy to write a wrapper that does it automatically, depending
    on size.
    """

    currentChanged = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._wheelTurn = 0

        self.currentRow = 0
        self.stack = QtWidgets.QStackedWidget()
        self.tabBars = []
        self.addTabBar()

    def addTabBar(self) -> int:
        """Add a new tab bar and return its row"""
        bar = _TabRow()
        bar.addTab('')
        bar.setExpanding(False)
        #bar.setShape(bar.TriangularNorth)
        bar.setStyleSheet(HIDE_FIRST_TAB)
        self.tabBars.append(bar)

        bar.currentChanged.connect(self._tabChanged)
        #bar.tabBarClicked.connect(self._tabClicked)
        bar._wheelMoved.connect(self._tabBarWheelMoved)
        bar._mouseLeft.connect(self._mouseLeftTabBar)

        self._relayout()
        return len(self.tabBars) - 1

    @Slot(int)
    def _tabClicked(self, tabIndex: int):
        """A tab was clicked. Reset wheel."""
        self._wheelTurn = 0

    @Slot(int)
    def _tabChanged(self, tabIndex: int):
        """The current tab changed. Reset wheel, change page,
        and optionally reorder bars."""
        self._wheelTurn = 0

        if not tabIndex:
            return

        col = tabIndex - 1
        bar = self.sender()
        row = self.tabBars.index(bar)
        if row != self.currentRow:
            oldBar = self.tabBars[self.currentRow]
            oldBar.setCurrentIndex(0)
            #oldBar.setDrawBase(False)
            self.currentRow = row
            #self.tabBars[row].setDrawBase(True)
            self._relayout()
        page = bar.tabData(tabIndex)

        self.stack.setCurrentWidget(page)
        self.currentChanged.emit(self.sindexOf(page))

    @Slot(QtCore.QEvent)
    def _mouseLeftTabBar(self, event: QtCore.QEvent):
        """Mouse left the tab bar. Reset wheel."""
        self._wheelTurn = 0

    @Slot(QtGui.QWheelEvent)
    def _tabBarWheelMoved(self, event: QtGui.QWheelEvent):
        """Wheel moved over tab bar. Switch tabs if needed."""
        try:
            delta = event.delta()

        except AttributeError:
            angleDelta = event.angleDelta()
            if angleDelta.isNull():
                return
            delta = max([angleDelta.y(), angleDelta.x()], key=abs)

        if not delta:
            return

        delta += self._wheelTurn
        self._wheelTurn = 0

        sign = +1 if delta > 0 else -1

        steps, remainder = divmod(abs(delta), 120)
        steps = int(steps)
        if steps:
            pageCount = self.count()
            if pageCount:
                self.setCurrentIndex((self.currentIndex() -
                                      sign * steps) % pageCount)

        self._wheelTurn = sign * remainder

    def currentIndex(self) -> int:
        """Get the index of the current selected tab page."""
        return self.stack.currentIndex()

    def count(self) -> int:
        """Get the total number of tab pages."""
        return self.stack.count()

    @Slot(int)
    def setCurrentIndex(self, index: int):
        """Set the index of the current selected tab page."""
        widget = self.widget(index)
        if not widget:
            return
        self.setCurrentWidget(widget)

    def widget(self, index: int) -> QtWidgets.QWidget:
        """Return the tab page at the given index."""
        return self.stack.widget(index)

    def indexOf(self, widget: QtWidgets.QWidget) -> int:
        """Get the index of the given widget."""
        return self.stack.indexOf(widget)

    @Slot(QtWidgets.QWidget)
    def setCurrentWidget(self, widget: QtWidgets.QWidget):
        """Set the current tab page by widget."""
        for bar in self.tabBars:
            for i in range(1, bar.count()):
                if bar.tabData(i) == widget:
                    bar.setCurrentIndex(i)
                    break

    def tabBar(self, row: int=0) -> _TabRow:
        """Return the tab bar for the given row, creating it
        if it does not exist yet.."""
        while row >= len(self.tabBars):
            self.addTabBar()
        return self.tabBars[row]

    def addTab(self, page: QtWidgets.QWidget, *args,
                     row: int=0, **kwargs) -> int:
        """Add a tab to a given row. The arguments are the
        same as for QTabWidget.addTab(), except for the row keyword
        argument."""

        bar = self.tabBar(row)
        index = self.stack.addWidget(page)

        tabIndex = bar.addTab(*args, **kwargs)
        bar.setTabData(tabIndex, page)

        if self.currentRow != row:
            bar.setCurrentIndex(0)
            #bar.setDrawBase(False)
        elif bar.count() == 2:
            bar.setCurrentIndex(1)

        return index

    def _relayout(self):
        """Re-order the widget layout, optionally creating it.
        This happens quite often as the current tab needs to be
        at the bottom of it."""

        if not self.layout():
            self.setLayout(QtWidgets.QVBoxLayout())
            self.layout().setContentsMargins(0, 0, 0, 0)
            self.layout().setSpacing(0)
        while self.layout().takeAt(0):
            pass

        for bar in reversed(self.tabBars[:self.currentRow]):
            self.layout().addWidget(bar)

        for bar in reversed(self.tabBars[self.currentRow:]):
            self.layout().addWidget(bar)

        self.layout().addWidget(self.stack, 1)


class FontInfoWidget(QtWidgets.QTabWidget):

    """Font information widget (dialog). Emits closed() signal
    so it can be used in TypeAtlas window list."""

    def __init__(self, item: 'typeatlas.fontlist.FontLike',
                       options: Options=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setTabPosition(self.West)

        if options is None:
            options = Options.getInstance()

        add = partial(_add_key_value_to_grid, options=options)
        add_separator = _add_separator_to_grid

        extended = item.extended()
        fontCmap = extended.cmap

        if fontCmap is not None:
            chars = sorted(fontCmap)
        elif hasattr(QtGui, 'QRawFont') and False:
            font = QtGui.QFontDatabase().font(item.family, item.style, 16)
            rawFont = QtGui.QRawFont.fromFont(font)
            allChars = all_character_codes()
            chars = list(filter(rawFont.supportsCharacter, allChars))
        else:
            chars = list(all_character_codes())

        charblocks = list(blockmath.toblocks_inorder(chars))

        fileinfos = list(item.files(details=True, stat=True))

        # ==== Tab 1 ====
        summary = QtWidgets.QWidget()
        self.addTab(summary, _('Summary'))
        summary.setLayout(QtWidgets.QVBoxLayout())

        title = QtWidgets.QHBoxLayout()
        summary.layout().addLayout(title)

        icon = QtWidgets.QLabel()
        label = QtWidgets.QLabel()

        title.addWidget(icon)
        title.addWidget(label, 1)
        icon.setPixmap(getIcon(item.icon).pixmap(options.tooltipIconSize))
        label.setTextFormat(Qt.PlainText)
        if item.is_family:
            titleText = item.translate('family', textlang())
        else:
            titleText = item.translate('fullname', textlang())
        self.setWindowTitle(titleText)
        self.setWindowIcon(getIcon('font-item-' +
                                   item.file_format_info.icon))
        label.setText(titleText)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        grid = QtWidgets.QGridLayout()
        summary.layout().addLayout(grid)

        add(grid, _('Type'), _('Font style') if item.is_style else
                             _('Font family'),
            icon='font-item-style' if item.is_style else
                 'font-item-family')
        add(grid, _('Family'), item.translate('family', textlang()))
        add(grid, _('Style') if item.is_style else
                  _('Main style'), item.translate('style', textlang()))
        add(grid, _('Generic family'), _(item.genericfamily) or
                                       _('Unclassified'),
                                       icon=item.genericfamily)

        if item.panoseclass or item.ibmclass:
            add_separator(grid)

        if item.panoseclass:
            add(grid, _('PANOSE class'), _(item.panoseclass.class_name))
            add(grid, _('PANOSE subclass'), _(item.panoseclass.subclass_name))

        if item.ibmclass:
            add(grid, _('IBM class'), _(item.ibmclass.class_name))
            add(grid, _('IBM subclass'), _(item.ibmclass.subclass_name))

        add_separator(grid)


        fontFormat = item.font_format_info
        fileFormat = item.file_format_info

        more = None
        if fontFormat.annotation:
            moreWidget = AnnotationWidget(item, fontFormat, False,
                                          options=options)
            more = moreWidget.show
            self.formatMoreWidget = moreWidget
        add(grid, _('Font format'), fontFormat.name, fontFormat.icon,
            moreInfoSlot=more)

        more = None
        if fileFormat.annotation:
            moreWidget = AnnotationWidget(item, fileFormat, True,
                                          options=options)
            more = moreWidget.show
            self.fileMoreWidget = moreWidget
        add(grid, _('File format'), fileFormat.name, fileFormat.icon,
            moreInfoSlot=more)

        add_separator(grid)

        add(grid, _('Character count'), str(len(chars)))

        if item.is_family:
            add(grid, _('Style count'), str(len(item.styles)))

        if fileinfos:
            add(grid, _('Files'), str(len(fileinfos)))
            add(grid, _('Size'), format_size(sum(fi.stat.st_size
                                                 for fi in fileinfos
                                                 if fi.stat)))

        grid.addWidget(QtWidgets.QWidget(), grid.rowCount(), 0, 1, 3)
        grid.setColumnStretch(grid.columnCount() - 1, 1)
        grid.setRowStretch(grid.rowCount() - 1, 1)

        # ==== Tab 2 ====

        files = QtWidgets.QTableWidget()
        tableItem = QtWidgets.QTableWidgetItem
        self.addTab(files, _('Files'))

        if item.is_style:
            offset = 0
            files.setColumnCount(5)
        else:
            offset = 1
            files.setColumnCount(6)

        setResizeMode(files.horizontalHeader(),
                      QtWidgets.QHeaderView.ResizeToContents)

        #fileIcon = getIcon('font-x-generic')
        files.setHorizontalHeaderItem(0, tableItem(_('File')))
        files.setHorizontalHeaderItem(1, tableItem(_('No.')))
        files.setHorizontalHeaderItem(2, tableItem(_('Size')))
        if not item.is_style:
            files.setHorizontalHeaderItem(3, tableItem(_('Style')))
        files.setHorizontalHeaderItem(3 + offset, tableItem(_('Purpose')))
        files.setHorizontalHeaderItem(4 + offset, tableItem(_('Directory')))

        for i, fi in enumerate(fileinfos):

            if fi.metrics:
                fileIcon = getIcon('font-file-metrics')
            else:
                fileIcon = getIcon('font-file-' +
                                   fi.style.file_format_info.icon)

            files.insertRow(i)
            files.setItem(i, 0, tableItem(fileIcon, os.path.basename(fi.file)))
            files.setItem(i, 1, tableItem(str(fi.index)))
            if fi.stat:
                files.setItem(i, 2, tableItem(format_size(fi.stat.st_size)))
            if not item.is_style:
                styleName = fi.style.translate('style', textlang())
                files.setItem(i, 3, tableItem(styleName))
            files.setItem(i, 3 + offset, tableItem(_(fi.purpose)))
            files.setItem(i, 4 + offset, tableItem(os.path.dirname(fi.file)))

        # ==== Tab 3 ====
        if item.panoseclass:
            panose = QtWidgets.QWidget()
            self.addTab(panose, _('PANOSE information'))
            grid = QtWidgets.QGridLayout()
            panose.setLayout(grid)

            for panprop in item.panoseclass:
                add(grid, _(panprop.fieldname), panprop.text(translate=_))

            grid.addWidget(QtWidgets.QWidget(), grid.rowCount(), 0, 1, 3)
            grid.setColumnStretch(grid.columnCount() - 1, 1)
            grid.setRowStretch(grid.rowCount() - 1, 1)

    closed = Signal()

    def closeEvent(self, event):
        r = super().closeEvent(event )
        if event.isAccepted():
            self.closed.emit()
        return r


class CharInfoWidget(QtWidgets.QTabWidget):

    """Character information widget. Emits closed() signal
    so it can be used in TypeAtlas window list."""

    def __init__(self, fontItem: 'typeatlas.fontlist.FontLike',
                       char: int, options: Options=None,
                       charDb: CharacterDatabase=None,
                       fontDb: QtGui.QFontDatabase=None,
                       langDb: LanguageDatabase=None,
                       *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setTabPosition(self.West)

        if options is None:
            options = Options.getInstance()
        if charDb is None:
            charDb = CharacterDatabase.getInstance()
        if langDb is None:
            langDb = LanguageDatabase.getInstance()
        if fontDb is None:
            fontDb = QtGui.QFontDatabase()

        add = partial(_add_key_value_to_grid, options=options)
        add_separator = _add_separator_to_grid

        font = fontDb.font(fontItem.family, fontItem.style,
                           options.gridFontSize)

        info = charDb.get(char, autofill=True)

        plane = charDb.get_plane(char)
        script = charDb.find_script_name(langDb, char)
        symbol = chr(char)
        display = symbol
        if getattr(info, 'display', None):
            display = chr(info.display)

        extended = fontItem.extended()
        if extended and extended.cmap:
            fontCmap = extended.cmap
            fontCharName = fontCmap.get(char) or ''
        else:
            fontCmap = None
            fontCharName = ''

        titleText = (getattr(info, 'name', '') or
                     getattr(info, 'old_name', '') or
                     fontCharName or '0x%x' % (char, ))

        self.setWindowTitle(titleText.title())
        self.setWindowIcon(getIcon(info.category_icon))

        # ==== Tab 1 ====
        summary = QtWidgets.QWidget()
        self.addTab(summary, _('Summary'))
        summary.setLayout(QtWidgets.QVBoxLayout())

        title = QtWidgets.QHBoxLayout()
        summary.layout().addLayout(title)

        icon = QtWidgets.QLabel()
        label = QtWidgets.QLabel()

        title.addWidget(icon)
        title.addWidget(label, 1)
        icon.setFont(font)
        icon.setTextFormat(Qt.PlainText)
        icon.setText(display)

        label.setTextFormat(Qt.PlainText)
        label.setText(titleText)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        grid = QtWidgets.QGridLayout()
        summary.layout().addLayout(grid)

        add_separator(grid)

        if info:
            if info.name:
                add(grid, _('Unicode name'), info.name)
            if info.old_name:
                add(grid, _('Old unicode name'), info.old_name)

        if fontCharName:
            add(grid, _('Character name in font'), fontCharName)
        add(grid, _('In font'), fontItem.translate('fullname', textlang()))

        add_separator(grid)


        if info and info.block:
            add(grid, _('Block'), info.block.name)
        if script:
            add(grid, _('Script'), script)
        if plane:
            add(grid, _('Plane'), _('Plane %d') % (plane.number, ) + ' ' +
                                   _(plane.description))

        add_separator(grid)

        add(grid, _('Hex code'), '0x%x' % (char, ))
        add(grid, _('Character'), display)
        if info:
            add(grid, _('Category'), info.category_name(translate=_),
                                     icon=info.category_icon)

        text = []
        if info:
            for alias in info.aliases:
                text.append('= ' + alias)
            for alias in info.formalaliases:
                text.append(charinfo.formal_alias + ' ' + alias)

        if text:
            aliases = QtWidgets.QGroupBox(_('Aliases'))
            summary.layout().addWidget(aliases)
            aliases.setLayout(QtWidgets.QVBoxLayout())
            aliasText = QtWidgets.QLabel()
            aliases.layout().addWidget(aliasText)
            aliasText.setTextFormat(Qt.PlainText)
            aliasText.setText('\n'.join(text))

        grid.addWidget(QtWidgets.QWidget(), grid.rowCount(), 0, 1, 3)
        grid.setColumnStretch(grid.columnCount() - 1, 1)
        grid.setRowStretch(grid.rowCount() - 1, 1)

        # ==== Tab 2 ====
        if info:
            for variation in info.variations:
                text.append(_('Variation', ': ') + variation)
            for crossref in info.crossrefs:
                text.append(charinfo.cross_reference + ' ' + crossref)

        if text:
            crossrefs = QtWidgets.QTextEdit()
            self.addTab(crossrefs, _('Names and references'))
            crossrefs.setPlainText('\n'.join(text))

    closed = Signal()

    def closeEvent(self, event):
        r = super().closeEvent(event)
        if event.isAccepted():
            self.closed.emit()
        return r



GROUP = N_('group')

EDIT = N_('edit')
CREATE = N_('create')


class GroupNameDialog(QtWidgets.QDialog):

    """A dialog for creating and editing groups (categories, tags,
    searches).

    Providing custom arguments, it can be used with any items having
    a name, icon and color, such as interface configurations. Then
    you need to provide groupTypeName, and the optional list of
    items as availableGroups.

    If nameEditable=False is passed, edint the name is disabled.
    """

    def __init__(self, *args,
                 groupContainer: 'typeatlas.datastore.FontGroupsContainer'=None,
                 action: str=CREATE, groupTypeName: str=None,
                 availableGroups: Sequence=None,
                 replacesOldGroup: bool=False,
                 nameEditable: bool=True,
                 groupName: str=None,
                 **kwargs):

        super().__init__(*args, **kwargs)

        if groupTypeName is None:
            if groupContainer is not None:
                groupTypeName = groupContainer.factory.type_label
            else:
                groupTypeName = GROUP

        if availableGroups is None:
            if groupContainer is not None:
                availableGroups = list(groupContainer.info.values())
            else:
                availableGroups = ()

        # TODO: For searches, check that name already exists
        # TODO: Signals here, and in the filter widget for search saving/editing
        # TODO: Edit is the same as replace, and it should be different
        self.buttons = buttons = QtWidgets.QDialogButtonBox()

        self.color = None
        self.icon = None
        self.replacesOldGroup = replacesOldGroup

        self.groupTypeName = groupTypeName

        self.setWindowTitle(_('Save {}').format(_(groupTypeName)))

        buttons.addButton(_('&Save'), buttons.AcceptRole)
        buttons.addButton(_('&Cancel'), buttons.RejectRole)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.nameCombo = combo = QtWidgets.QComboBox()
        self.nameCombo.setEditable(True)

        self.availableGroups = {}
        for i, grouping in enumerate(availableGroups):
            if grouping.icon:
                combo.addItem(getIcon(grouping.icon), grouping.name, grouping)
            else:
                combo.addItem(grouping.name, grouping)

            self.availableGroups[grouping.name] = i, grouping

        self.nameCombo.setCurrentIndex(-1)
        self.nameCombo.clearEditText()

        combo.currentIndexChanged.connect(self.nameIndexChanged)
        combo.editTextChanged.connect(self.nameTextChanged)

        self.grouping = None

        self.iconPreview = QtWidgets.QLabel()
        self.colorPreview = QtWidgets.QLabel()

        self.iconButton = QtWidgets.QPushButton(_("Icon..."))
        self.iconButton.clicked.connect(self.selectIcon)
        self.fontIconButton = QtWidgets.QPushButton("Symbol...")
        self.fontIconButton.clicked.connect(self.selectFontIcon)
        self.iconClear = QtWidgets.QPushButton(_("Clear"))
        self.iconClear.clicked.connect(self.setIcon)

        self.colorButton = QtWidgets.QPushButton(_("Color..."))
        self.colorButton.clicked.connect(self.selectColor)
        self.colorClear = QtWidgets.QPushButton(_("Clear"))
        self.colorClear.clicked.connect(self.setColor)

        self.nameCombo.lineEdit().setPlaceholderText(_('Name...'))

        self.setLayout(QtWidgets.QGridLayout())
        self.layout().addWidget(self.nameCombo, 0, 0, 1, 7)

        self.layout().addWidget(self.iconPreview, 1, 0, 1, 1)
        self.layout().addWidget(self.iconButton, 1, 1, 1, 1)
        self.layout().addWidget(self.fontIconButton, 1, 2, 1, 1)
        self.layout().addWidget(self.iconClear, 1, 3, 1, 1)

        self.layout().addWidget(self.colorPreview, 1, 4, 1, 1)
        self.layout().addWidget(self.colorButton, 1, 5, 1, 1)
        self.layout().addWidget(self.colorClear, 1, 6, 1, 1)

        self.layout().addWidget(self.buttons, 2, 0, 1, 7)

        if groupName is not None:
            self.setName(groupName)

        if not nameEditable:
            self.nameCombo.setDisabled(True)

    nameChanged = Signal(str)
    iconChanged = Signal(str)
    colorChanged = Signal(QtGui.QColor)

    @property
    def groupName(self) -> str:
        """The name of the group (category, tag, search) or object
        being edited."""
        return self.nameCombo.currentText()

    @Slot()
    @Slot(str)
    def setName(self, name: str=''):
        """Set the name."""
        if name == self.nameCombo.currentText():
            return
        if not name:
            self.nameCombo.clearEditText()
        else:
            self.nameCombo.setEditText(name)
        self.nameChanged.emit(name)

    @Slot()
    @Slot(str)
    def setIcon(self, path: str=None):
        """Set the path to the icon. It can be taken from self.icon"""
        if path == self.icon:
            return
        if path is None:
            self.iconPreview.clear()
        else:
            icon = getIcon(path)
            self.iconPreview.setPixmap(icon.pixmap(iconSize(refSize=32)))

        self.icon = path
        self.iconChanged.emit(path)

    @Slot()
    @Slot(QtGui.QColor)
    def setColor(self, color: QtGui.QColor=None):
        """Set the color. It can be taken from self.color, or as string
        with self.colorName()."""
        if color == self.color:
            return
        if color is None:
            self.colorPreview.clear()
        else:
            pixmap = QtGui.QPixmap(iconSize(refSize=32))
            pixmap.fill(color)
            self.colorPreview.setPixmap(pixmap)
        self.color = color
        self.colorChanged.emit(color)

    def colorName(self) -> Optional[str]:
        """Get the color as a string. None if unset."""
        if self.color is None:
            return None
        return self.color.name()

    @Slot()
    def selectColor(self):
        """Open the color selection dialog"""
        color = QtWidgets.QColorDialog.getColor(
                        QtGui.QColor(), self,
                        _('Select %s color') % (_(self.groupTypeName), ))
        if color:
            self.setColor(color)

    @Slot()
    def selectIcon(self):
        """Open the icon selection dialog"""
        icon = IconSelectDialog.selectIcon(self, _('Select %s icon') % (
                                                        _(self.groupTypeName), ))
        if icon:
            self.setIcon(icon)

    @Slot()
    def selectFontIcon(self):
        """Open the emoji icon selection dialog"""
        from typeatlas.guiglyphs import CharSelectDialog
        charRes = CharSelectDialog.selectChar()
        if charRes is None:
            return

        if charRes.generic:
            self.setIcon('char:U+%X' % (charRes.codepoint, ))
        else:
            self.setIcon('char:U+%X:%s' % (charRes.codepoint,
                                           charRes.fontitem.family))

    @Slot(int)
    def nameIndexChanged(self, idx: int):
        """A combo item was selected. We take its name, color and
        icon."""
        grouping = self.nameCombo.itemData(idx)
        if grouping is None:
            return

        self.grouping = grouping
        self.setName(grouping.name)
        self.setIcon(grouping.icon)
        if grouping.color:
            self.setColor(QtGui.QColor(grouping.color))
        else:
            self.setColor()

    @Slot(str)
    def nameTextChanged(self, name: str):
        """The name was selected. If the item exists, take its icon and
        color."""
        groupingTuple = self.availableGroups.get(name)
        if groupingTuple is None:
            return

        i, grouping = groupingTuple
        self.setIcon(grouping.icon)
        if grouping.color:
            self.setColor(QtGui.QColor(grouping.color))
        else:
            self.setColor()
        self.nameCombo.setCurrentIndex(i)


class RemoveFromGroupDialog(QtWidgets.QDialog):

    """A dialog for font items from groups."""

    def __init__(self,
                 families: 'IterableOf[str]',
                 groupContainer: 'typeatlas.datastore.FontGroupsContainer',
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        groupTypeName = groupContainer.factory.type_label
        groupTypePlural = groupContainer.factory.type_label_plural
        #availableGroups = list(groupContainer.info.values())

        self.setWindowTitle(_('Remove {} for selected the fonts')
                                .format(_(groupTypePlural)))

        self.buttons = buttons = QtWidgets.QDialogButtonBox()

        buttons.addButton(_('&Remove'), buttons.AcceptRole)
        buttons.addButton(_('&Cancel'), buttons.RejectRole)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.groups = groups = set()
        self.sharedGroups = groupCounts = Counter()
        self.groupCounts = sharedGroups = None

        for family in families:
            familyGroups = groupContainer.by_family.get(family, ())
            if sharedGroups is None:
                sharedGroups = set(familyGroups)
            else:
                sharedGroups &= familyGroups

            groups |= familyGroups

            groupCounts.update(familyGroups)

        if sharedGroups is None:
            sharedGroups = set()

        self.tree = tree = QtWidgets.QTreeWidget()
        tree.setColumnCount(3)
        tree.setHeaderLabels([_(groupTypeName).capitalize(),
                              _('Fonts'), _('Count')])
        tree.setSelectionMode(tree.ExtendedSelection)

        for group in sorted(groups, key=groupCounts.get, reverse=True):
            item = QtWidgets.QTreeWidgetItem(
                [group,
                 _('All') if group in sharedGroups else _('Some'),
                 str(groupCounts[group])])

            icon = groupContainer.info[group].icon
            if icon:
                icon = getIcon(icon)
                if icon:
                    item.setIcon(0, icon)

            tree.addTopLevelItem(item)

        ## Can't search in QTreeWidget, unfortunately.
        #self.textWidget = search = QuickSearch(
        #    placeholderText=_('Search {}...').format(_(groupTypePlural)))
        #search.searchTriggered.connect(self._filterTextChanged)

        self.setLayout(QtWidgets.QVBoxLayout())

        self.layout().addWidget(tree)
        self.layout().addWidget(buttons)

    def selectedGroups(self) -> SequenceOf[str]:
        """Return a list of the selected groups."""
        selected = self.tree.selectionModel().selectedIndexes()
        if not selected:
            current = self.tree.selectionModel().currentIndex()
            if current.isValid():
                selected = [current]

        # We have multiple columns selected, but only need the first one,
        # and need it returned only once.
        return list(OrderedSet(index.siblingAtColumn(0).data(Qt.DisplayRole)
                               for index in selected))

    #@Slot(str)
    #def _filterTextChanged(self, text):
    #    self.proxyModel.setFilterFixedString(text.strip())


class IconSelectDialog(QtWidgets.QDialog):

    """A widget for selecting icons."""

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        
        self.iconsByCategory = OrderedDict()

        groupAttr = attrgetter('context')

        for context, iconInfos in groupby(sorted(osinfo.find_icons(),
                                                 key=groupAttr), groupAttr):
            self.iconsByCategory[context] = list(iconInfos)

        self.buttons = buttons = QtWidgets.QDialogButtonBox()

        buttons.addButton(_('&OK'), buttons.AcceptRole)
        buttons.addButton(_('&Cancel'), buttons.RejectRole)
        self.browseButton = buttons.addButton(_('&Browse...'), buttons.ActionRole)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.clicked.connect(self._buttonClicked)

        self.listWidget = QtWidgets.QListWidget()
        self.comboBox = QtWidgets.QComboBox()

        self.setLayout(QtWidgets.QVBoxLayout())

        self.layout().addWidget(self.comboBox)
        self.layout().addWidget(self.listWidget)
        self.layout().addWidget(self.buttons)

        self.comboBox.addItems(list(self.iconsByCategory))
        self.comboBox.activated.connect(self._comboActivated)

        self.listWidget.setViewMode(self.listWidget.IconMode)

        size = iconSize(refSize=32)
        self.listWidget.setIconSize(size)
        self.listWidget.setGridSize(size * 2)

        self.listWidget.setMovement(self.listWidget.Static)
        self.listWidget.setLayoutMode(self.listWidget.Batched)
        self.listWidget.currentItemChanged.connect(self._iconChanged)
        self.listWidget.setResizeMode(self.listWidget.Adjust)
        self.listWidget.setWordWrap(True)
        self.listWidget.setSortingEnabled(True)

        if self.iconsByCategory:
            self.comboBox.setCurrentIndex(0)
            self._comboActivated(0)

        self.resize(generalWidth(refSize=500),
                    generalHeight(refSize=600))

        self.result = None

    @classmethod
    def selectIcon(cls, parent: QtWidgets.QWidget=None,
                        title: str=None) -> Optional[str]:
        """Execute the dialog in modal mode and return icon name."""
        dialog = cls(parent)
        dialog.setWindowTitle(title)
        if dialog.exec_():
            return dialog.result
        return None

    @Slot(QtWidgets.QAbstractButton)
    def _buttonClicked(self, button: QtWidgets.QAbstractButton):
        """A button in the button box was clicked. If it is the browse
        button, open the a file dialog to select an image."""
        if button is self.browseButton:
            (path, nameFilter) = QtWidgets.QFileDialog.getOpenFileName(
                                    self, self.windowTitle())
            if path:
                self.result = path
                self.accept()

    @Slot(int)
    def _comboActivated(self, index: int):
        """Combo was selected, move to a different font category."""
        category = self.comboBox.itemText(index)
        self.listWidget.clear()

        for iconItem in self.iconsByCategory.get(category, ()):
            name = iconItem.name
            icon = getIcon(name)
            self.listWidget.addItem(QtWidgets.QListWidgetItem(icon, name))

    @Slot(QtWidgets.QListWidgetItem, QtWidgets.QListWidgetItem)
    def _iconChanged(self, current: QtWidgets.QListWidgetItem,
                           previous: QtWidgets.QListWidgetItem):
        """The icon was changed, update the result."""
        self.result = current.text()

