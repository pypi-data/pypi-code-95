# -*- coding: utf-8 -*-
#
#    TypeAtlas Font Sampler
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

from typeatlas.compat import QtCore, QtGui, QtWidgets, QtModelProxies
from typeatlas.compat import Qt, Slot, Signal, setResizeMode
from typeatlas.guicommon import FontRenderingChoice
from typeatlas.fontmodels import FontDelegate, FontFilterModel, FontItemRole
from typeatlas.fontmodels import FontListModel, SampleTextRole
from typeatlas.options import Options
from typeatlas.uitools import Toolbox, FlippableListView
from typeatlas.uitools import getIcon, getImage, getIconHtml, qFontToCss
from typeatlas.uitools import QuickSearch
from typeatlas import fontgrid, fontlist, datastore
from typeatlas.langutil import LanguageDatabase
from typeatlas.langutil import _, N_, H_, textlang
from typeatlas.util import generic_type

from collections.abc import Iterator

IterableOf = generic_type('Iterable')
SequenceOf = generic_type('Sequence')


class FontSamplerToolbox(Toolbox):

    """Actions  applicable to font sampler and font duel samples.

    These allow you to change the sample, resize the font (to the provided
    list of sizes). If glyphStack=True, default to the size for a glyph
    stack.

    The sampler should be a FontSampler, or any widget with optional
    setBold, setColumnFlow, setRowFlow, setListView methods.
    """

    def __init__(self, sampler: QtWidgets.QWidget, sampleText: str=N_('AbQqRr'),
                       fontSizes: SequenceOf[int]=None,
                       glyphStack: bool=False, *args, **kwargs):
        self.sampler = sampler
        self.renderingChoice = sampler.renderingChoice
        if fontSizes is None:
            if not glyphStack:
                fontSizes = QtGui.QFontDatabase.standardSizes()
            else:
                fontSizes = [6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,
                             26, 28, 36, 48, 64, 72, 96, 128, 192, 256, 384,
                             512, 768]
        self.fontSizes = fontSizes
        self.glyphStack = glyphStack
        self.defaultSampleText = sampleText
        super().__init__(*args, **kwargs)

    @property
    def actionParent(self) -> QtCore.QObject:
        return self.sampler

    def __getattr__(self, attr):
        return getattr(self.sampler, attr)

    def actionDefinitions(self) -> Iterator:
        if hasattr(self.sampler, 'setColumnFlow'):
            with self.group(exclusive=True):
                yield self.action(self.setColumnFlow, _('Column flow'),
                                  icon='view-list-icons',
                                  checkable=True, checked=True)
                yield self.action(self.setRowFlow, _('Row flow'),
                                  icon='format-justify-left',
                                  checkable=True)
                yield self.action(self.setListView, _('List'),
                                  icon='view-list-details',
                                  checkable=True)

            yield self.separator()

        if hasattr(self.sampler, 'setBold'):
            yield self.action(self.sampler.setBold, _('Bold'),
                              icon='format-text-bold', checkable=True)
            yield self.action(self.sampler.setItalic, _('Italic'),
                              icon='format-text-italic', checkable=True)
            yield self.action(self.sampler.setCondensed, _('Condensed'),
                              checkable=True)
            yield self.separator()

        with self.group('size'):
            yield self.action(self.smaller, _('Smaller'),
                              icon='format-font-size-less')
            yield self.action(self.larger, _('Larger'),
                              icon='format-font-size-more')

        yield self.separator()

        histories = self.sampler.histories
        sample = QuickSearch(placeholderText=_('Enter sample...'),
                             history=histories.get_history('sampler-sample'))
        sample.searchTriggered.connect(self.setSampleText)
        sample.setText(self.defaultSampleText)

        sampleAction = QtWidgets.QWidgetAction(self.actionParent)
        sampleAction.setDefaultWidget(sample)
        self.sampleAction = sampleAction
        self.sampleWidget = sample
        yield sampleAction

    def _jumpToSize(self, offset: int):
        """Increase or decrease the font size the given number of times.
        Decrease if negative. Jumps with through the provided or available
        font sizes."""
        sizes = self.fontSizes
        if self.glyphStack:
            size = self.renderingChoice.glyphStackSize
        else:
            size = self.renderingChoice.sampleSize

        if len(sizes) < 2:
            return

        i = min(range(len(sizes)), key=lambda i: abs(sizes[i] - size))
        try:
            size = sizes[i + offset]
        except IndexError:
            return

        if self.glyphStack:
            self.renderingChoice.setGlyphStackSize(size)
        else:
            self.renderingChoice.setSampleSize(size)

    @Slot()
    def larger(self):
        """Make the font larger."""
        self._jumpToSize(+1)

    @Slot()
    def smaller(self):
        """make the font smaller."""
        self._jumpToSize(-1)


class FontSampler(QtWidgets.QMainWindow):

    """Displays large font samples in a list view, using the provided
    list of font families.

    This widget displays families, with one style per family based on
    a StyleSelector. The similar widget in fontduel displays individual
    styles selected by the user.

    This is filtered, and the other one is a custom selection.

    This window has a closed signal, to be used with the TypeAtlas
    library.
    """

    def __init__(self, fontFamilies: IterableOf[fontlist.FontLike],
                       parent: QtWidgets.QWidget=None, sample: str='A',
                       fontDb: QtGui.QFontDatabase=None,
                       langDb: LanguageDatabase=None,
                       options: Options=None,
                       featureSets: fontlist.FeatureSets=None,
                       renderingChoice: FontRenderingChoice=None,
                       histories: datastore.Histories=None):
        super().__init__(parent)

        if renderingChoice is None:
            renderingChoice = FontRenderingChoice()
        self.renderingChoice = renderingChoice

        if options is None:
            options = Options.getInstance()
        if histories is None:
            histories = datastore.Histories.getInstance()

        self.options = options
        self.histories = histories

        self.resize(options.fontSamplerSize)

        self.setWindowTitle(_("TypeAtlas Sampler"))
        self.setWindowIcon(getIcon('typeatlas-sampler'))

        if fontDb is None:
            fontDb = QtGui.QFontDatabase()
        if langDb is None:
            langDb = LanguageDatabase.getInstance()

        layout = QtWidgets.QVBoxLayout()
        w = QtWidgets.QWidget()
        self.setCentralWidget(w)
        w.setLayout(layout)

        self.boxLayout = layout

        self.fontFamilies = fontFamilies
        self.fontDb = fontDb

        self.bold = False
        self.italic = False
        self.condensed = False

        self.view = grid = FlippableListView()
        self.renderingChoice.samplesChanged.connect(self.view.reset)

        self.model = FontListModel(self.fontFamilies, fontDb=self.fontDb,
                                   sampleModel=True, hideStyles=True,
                                   featureSets=featureSets,
                                   renderingChoice=self.renderingChoice)

        self.filterModel = FontFilterModel(langDb=langDb)
        self.filterModel.setSourceModel(self.model)

        self.toolbox = FontSamplerToolbox(self)
        self.model.setSampleText(self.toolbox.defaultSampleText)
        self.filterModel.filter.setContainsChars(self.toolbox.defaultSampleText)

        main = self.addToolBar('main')
        main.setIconSize(options.toolbarIconSize)
        options.toolbarIconSizeChanged.connect(main.setIconSize)

        delegate = fontgrid.GridCellDelegate(grid, fontDb=self.fontDb,
                                             abbreviateHeader=True,
                                             headerRole=Qt.DisplayRole,
                                             sampleRole=SampleTextRole,
                                             sampleRendererRole=None,
                                             sizeThreshold=-1)

        grid.setModel(self.filterModel)
        grid.setMovement(QtWidgets.QListView.Snap)
        self.setColumnFlow()
        grid.setLayoutMode(QtWidgets.QListView.Batched)
        #grid.setGridSize(QtCore.QSize(40, 40))
        grid.setItemDelegateForColumn(0, delegate)
        grid.setResizeMode(QtWidgets.QListView.Adjust)
        self.boxLayout.addWidget(grid)


        self.toolbox.populateToolbar(main)

        self._resetStyle()
        self.setColumnFlow()

    def _resetStyle(self):
        """Update the style selector and reset the view."""
        weight = fontlist.WEIGHT_BOLD if self.bold else fontlist.WEIGHT_NORMAL
        slant = fontlist.SLANT_ITALIC if self.italic else fontlist.SLANT_NORMAL
        width = (fontlist.WIDTH_CONDENSED
                    if self.condensed
                    else fontlist.WIDTH_NORMAL)
        sel = fontlist.StyleSelector(weight=weight, slant=slant, width=width)
        self.model.setStyleSelector(sel)
        self.view.reset()

    @Slot(bool)
    def setBold(self, checked=False):
        """Toggle the bold state."""
        # FIXME: CHeck actual button state
        self.bold = not self.bold
        self._resetStyle()

    @Slot(bool)
    def setItalic(self, checked=False):
        """Toggle the italic state."""
        self.italic = not self.italic
        self._resetStyle()

    @Slot(bool)
    def setCondensed(self, checked=False):
        """Toggle the condensed state."""
        self.condensed = not self.condensed
        self._resetStyle()

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
        self.filterModel.filter.setContainsChars(text)
        self.view.reset()

    closed = Signal()

    def closeEvent(self, event):
        r = super().closeEvent(event )
        if event.isAccepted():
            self.closed.emit()
        return r
