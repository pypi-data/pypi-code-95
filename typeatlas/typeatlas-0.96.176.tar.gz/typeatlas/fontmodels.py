# -*- coding: utf-8 -*-
#
#    TypeAtlas Font Models
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


"""Models for displaying font lists.

This includes the FontListModel, FontFilterModel, a MutableFontListModel
and more font models than anyone would ever want or need. We have models of
models within our models. You *will* need to be medicated.
"""

from typeatlas.compat import QtCore, QtGui, QtWidgets, QtModelProxies
from typeatlas.compat import Qt, Slot, Signal, setResizeMode, QT_VERSION
from typeatlas.guicommon import FontRenderingChoice, GroupNameDialog
from typeatlas.uitools import getIcon, getImage, getIconHtml, qFontToCss
from typeatlas.uitools import getSelectableIconPair
from typeatlas.uitools import generalWidth, generalHeight, Toolbox
from typeatlas.uitools import includeExcludeCheckboxCss
from typeatlas.uitools import checkStateToBool, boolToCheckState
from typeatlas.uitools import CheckboxItemModelMixin, ListItemModel
from typeatlas.uitools import CheckableStyledObjectListModel
from typeatlas.uitools import StyledObjectListModel
from typeatlas.uitools import ItemSearchRole, ItemItemRole
from typeatlas.uitools import QuickSearch
from typeatlas.options import Options
from typeatlas.foreign.flowlayout import FlowLayout, HorizontalFlowLayout
from typeatlas.foreign.flowlayout import FlowLayoutSizePolicy
from typeatlas.langutil import _, N_, H_, U_, textlang
from typeatlas.util import OrderedSet, MethodDispatchMap, EMPTY_SET
from typeatlas.util import warnmsg, errmsg, debugmsg, warnmsgf
from typeatlas.util import generic_type, STRIKE
from typeatlas.event import ObWeakRef
from typeatlas.blockmath import toblocks
from typeatlas import fontlist, opentype, filtering, qfontlist, datastore

from html import escape as htesc
from collections import defaultdict, namedtuple
from collections.abc import Iterator, Callable, Set, Mapping
from itertools import chain

import typeatlas

import re
import os
import os.path

import json
import traceback
import pprint

IterableOf = generic_type('Iterable')
SequenceOf = generic_type('Sequence')
TupleOf = generic_type('Tuple')
Union = generic_type('Union')
Optional = generic_type('Optional')


FontItemRole = Qt.UserRole
SampleTextRole = Qt.UserRole + 1

FilterItemRole = Qt.UserRole
FilterRole = Qt.UserRole + 1


ENABLE_COMPLEX_FILTERS = True


_NOTHING = object()


class FontItemMimeData(QtCore.QMimeData):

    """A subclass of mime data that can be used to internally drag
    and drop fonts, as it carries the selected fontlist.FontLike
    items.

    Use isFontItemMimeData() to determine if you got such mime data.
    """

    isFontItemMimeData = True

    _fontItems = None

    def setFontItems(self, fontItems: SequenceOf[fontlist.FontLike]):
        self._fontItems = fontItems

    def fontItems(self) -> SequenceOf[fontlist.FontLike]:
        return self._fontItems


def isFontItemMimeData(data: QtCore.QMimeData) -> bool:
    """Return True if this is FontItemMimeData that carries
    fontItems."""

    #return hasattr(data, 'fontItems')
    return getattr(data, 'isFontItemMimeData', False)


class FontFileIconProvider(QtWidgets.QFileIconProvider):

    """Icon provider that provides custom TypeAtlas icons for the
    various font file types, for use in a QFileSystemModel."""

    def icon(self, typeOrInfo):

        if isinstance(typeOrInfo, QtCore.QFileInfo):

            filename = typeOrInfo.fileName()

            while filename:
                filename, ext = os.path.splitext(filename)
                ext = ext.lstrip('.')
                if ext in fontlist.compression_extensions:
                    continue
                if ext in fontlist.file_extensions:
                    return getIcon('font-file-' +
                                   fontlist.file_extensions[ext].icon)
                break

        return super().icon(typeOrInfo)

    def type(self, info):

        filename = info.fileName()

        while filename:
            filename, ext = os.path.splitext(filename)
            ext = ext.lstrip('.')
            if ext in fontlist.compression_extensions:
                continue
            if ext in fontlist.file_extensions:
                return _(fontlist.file_extensions[ext].description)
            break

        return super().type(info)


class FontListModel(QtCore.QAbstractItemModel):

    """Define a model of fonts, defined by the provided families.

    This model defines the following new roles:
        FontItemRole    The font item, an fontlist.FontLike
        SampleTextRole  A role returning a fixed string provided as
                        sampleText to the constructor or with
                        setSampleText() for displaying a sample
                        for fonts. Used by e.g. GridCellDelegate

    If sampleModel=True is passed, this is used to display samples, not
    fonts (this changed the preferred font size to pick out from the
    options).

    If hideStyles=True is selected, the styles are not shown (the model
    is no longer a tree), but you can select which style to display with
    the provided styleSelector, which can be set with setStyleSelector().
    """

    def __init__(self, families: IterableOf[fontlist.FontLike],
                       fontDb: QtGui.QFontDatabase=None,
                       sampleText: str='A', parent: QtWidgets.QWidget=None,
                       renderingChoice: FontRenderingChoice=None,
                       sampleModel: bool=False,
                       styleSelector: fontlist.StyleSelector=None,
                       hideStyles: bool=False,
                       options: Options=None,
                       featureSets: fontlist.FeatureSets=None):
        super(FontListModel, self).__init__(parent)
        if options is None:
            options = Options.getInstance()

        self.options = options
        if renderingChoice is None:
            renderingChoice = FontRenderingChoice()

        self.renderingChoice = renderingChoice
        if sampleModel:
            self.renderingChoice.samplesChanged.connect(self._renderingChanged)
        else:
            self.renderingChoice.listChanged.connect(self._renderingChanged)
        if fontDb is None:
            fontDb = QtGui.QFontDatabase()
        self.fontDb = fontDb
        self.writingSystems = [(ws, self.fontDb.writingSystemName(ws))
                               for ws in self.fontDb.writingSystems()]
        self.families = list(families)
        self.sampleText = sampleText
        self.styleSelector = styleSelector
        self.hideStyles = hideStyles
        self.sampleModel = sampleModel

        if featureSets is None:
            featureSets = fontlist.FeatureSets(self.families)
        self.featureSets = featureSets

        self.family_row_by_name = dict((family.family, (i, family))
                                       for i, family
                                            in enumerate(self.families))

    def setFamilies(self, families: IterableOf[fontlist.FontLike],
                          featureSets: fontlist.FeatureSets=None):
        """Set the families to be displayed."""
        self.beginResetModel()
        self.families = list(families)
        if featureSets is None:
            featureSets = fontlist.FeatureSets(self.families)
        self.featureSets = featureSets
        self.family_row_by_name = dict((family.family, (i, family))
                                       for i, family
                                            in enumerate(self.families))
        self.endResetModel()

    def setStyleSelector(self, styleSelector: fontlist.StyleSelector=None):
        """Set the style selector used to pick font when styles are hidden."""
        self.styleSelector = styleSelector
        self._renderingChanged()

    @Slot(str)
    def setSampleText(self, text: str):
        """Set the sample text."""
        self.sampleText = text
        self._renderingChanged()

    @Slot()
    def _renderingChanged(self):
        """The rendering changed."""

        ## FIXME: Why is this disabled?

        #self.beginResetModel()
        #self.endResetModel()
        #for index in modelIterate(self):
        #    self.dataChanged.emit(index, index)

        ## FIXME: This is slow, view.reset() does it faster
        #for topleft, bottomright in modelIterateChildrenRect(self, maxDepth=1):
        #   self.dataChanged.emit(topleft, bottomright)

        ## TODO: This seems to work just fine
        #root = QtCore.QModelIndex()
        #cols = self.columnCount(root)
        #rows = self.rowCount(root)
        #tl = self.index(0, 0, root)
        #br = self.index(rows - 1, cols - 1, root)
        #self.dataChanged.emit(tl, br)

        pass

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        item = index.internalPointer()

        if item.is_family:
            return QtCore.QModelIndex()

        else:
            try:
                row, family = self.family_row_by_name[item.family]
            except KeyError:
                return QtCore.QModelIndex()
            return self.createIndex(row, 0, family)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if parent.isValid():
            family = parent.internalPointer()
        else:
            family = None

        try:
            if family is None:
                item = self.families[row]
            else:
                item = family.styles[row]
        except IndexError:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(row, column, item)

    def hasChildren(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return True
        if self.hideStyles:
            return False
        return parent.internalPointer().is_family

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            # FIXME: If this returns 0, all children disappear. WHY?
            # Documentation says it *must* return 0.
            return 1
        return 1

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self.families)

        item = parent.internalPointer()
        if not item.is_family:
            return 0
        else:
            return len(item.styles)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return _('Font name')

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            if self.hideStyles:
                if self.styleSelector:
                    item = self.styleSelector.select(item)
                if item.substitutingfamily:
                    return '%s (%s)' % (item.translate('fullname', textlang()),
                                        item.substituting)
                return item.translate('fullname', textlang())

            if item.is_family:
                if item.substitutingfamily:
                    return '%s (%s)' % (item.translate('family', textlang()),
                                        item.substitutingfamily)
                return item.translate('family', textlang())
            else:
                if item.substitutingstyle:
                    return '%s (%s)' % (item.style, item.substitutingstyle)
                return item.translate('style', textlang())
        elif role == Qt.EditRole:
            if self.hideStyles:
                if self.styleSelector:
                    item = self.styleSelector.select(item)
                return item.fullname
            return item.family if item.is_family else item.style
        elif role == Qt.DecorationRole:
            if self.styleSelector:
                item = self.styleSelector.select(item)
            return getIcon('font-item-' + item.icon)
        elif role == Qt.FontRole:
            if self.styleSelector:
                item = self.styleSelector.select(item)

            if self.sampleModel:
                size = self.renderingChoice.sampleSize
            else:
                size = self.renderingChoice.listSize

            ## I think Qt already does this.
            #if not self.fontDb.isSmoothlyScalable(item.family, item.style):
            #    sizes = self.fontDb.smoothSizes(item.family, item.style)
            #    if sizes:
            #        size = min(sizes, key=lambda sz: abs(sz - size))

            font = self.fontDb.font(item.family, item.style, size)
            font.setStyleHint(QtGui.QFont.AnyStyle,
                              self.renderingChoice.antialiasStyle)
            font.setHintingPreference(self.renderingChoice.hintingPreference)
            return font

        elif role == Qt.ToolTipRole:
            if self.styleSelector:
                item = self.styleSelector.select(item)

            font = index.data(Qt.FontRole)
            sample = ''
            for ws in self.fontDb.writingSystems(font.family()):
                sample = self.fontDb.writingSystemSample(ws)
                break

            texts = [
                     #getIconHtml(item.icon, self.options.tooltipIconSize),
                     htesc(item.translate('family', textlang())) + ' ' +
                     htesc(item.translate('style', textlang())),
                     '<span style="%s; font-size: %dpt;">%s</span>' % (
                                 qFontToCss(font), 
                                 self.renderingChoice.charBoxSize, 
                                 htesc(sample)),
                     htesc(self.getFontTypeText(item)),
                     htesc(self.getStyleInfoText(item)),
                     htesc(self.getWritingSystemsText(item))]
            texts.extend(str(fi) for fi in item.files(find_metrics=False))

            return '<br>'.join(texts)

        elif role == FontItemRole:
            return item

        elif role == SampleTextRole:
            return self.sampleText

        return None

    def getFontTypeText(self, item):
        text = []
        if item.outline:
            text.append(_('Outline'))
        else:
            text.append(_('Bitmap'))

        if item.scalable:
            text.append(_('Scalable'))

        return '. '.join(text)

    def getLanguageListText(self, item):
        return ', '.join(sorted(item.lang))

    def getWritingSystemsText(self, item):
        fontDb = self.fontDb
        return ', '.join(fontDb.writingSystemName(ws)
                         for ws in sorted(getattr(item, 'writingSystems', ())))

    def getStyleInfoText(self, item):

        familyStyle = []

        panoseclass = getattr(item, 'panoseclass', None)
        ibmclass = getattr(item, 'ibmclass', None)

        if panoseclass and panoseclass.class_id:
            familyStyle.append('%s (%s) [PAN]'
                                    % (_(panoseclass.class_name),
                                       _(panoseclass.subclass_name)))

        if ibmclass and ibmclass.class_id:
            familyStyle.append('%s (%s) [IBM]'
                                    % (_(ibmclass.class_name),
                                       _(ibmclass.subclass_name)))

        familyStyle = '; '.join(familyStyle)
        if familyStyle:
            familyStyle += '. '
        familyStyle += _(item.genericfamily or N_('unclassified')).capitalize()
        familyStyle += '.'

        if item.monospace:
            familyStyle += " %s." % (_('Monospace'), )

        text = [familyStyle,
                _("Width {width}, slant {slant}, weight {weight}.").format(
                        width=item.width, slant=item.slant, weight=item.weight)]
        if item.decorative:
            text.append(_('Decorative.'))
        #if item.verticallayout:
        #    text.append(_('Vertical.'))

        return ' '.join(text)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag()
        return (super(FontListModel, self).flags(index)
                    | Qt.ItemIsEditable | Qt.ItemIsSelectable
                    | Qt.ItemIsDragEnabled)

    def mimeData(self, indexes):
        if not indexes:
            return None

        markup = []
        text  = []

        items = []
        urls = OrderedSet()

        for index in indexes:
            item = index.data(FontItemRole)
            font = index.data(Qt.FontRole)

            items.append(item)
            markup.append('<span style="%s">%s</span>'
                                    % (qFontToCss(font),
                                       H_("REPLACEME")))
            text.append(item.translate('family', textlang()))

            # Better drag the file directly from the QLabel
            #for fi in item.files():
            #    if fi.file:
            #        if item.remote:
            #            url = QtCore.QUrl(item.file)
            #        else:
            #            url = QtCore.QUrl.fromLocalFile(item.file)
            #        urls.add(url)

        mime = FontItemMimeData()
        mime.setText('\n'.join(text))
        mime.setHtml('<br>'.join(markup))
        mime.setFontItems(items)

        #if urls:
        #    mime.setUrls(list(urls))

        return mime

    def mimeTypes(self):
        # We do not support 'application/x-qabstractitemmodeldatalist'
        # in this establishment.
        return ['text/plain', 'text/html']

    def dropMimeData(self, data, action, row, column, parent):
        return False

    def supportedDragActions(self):
        return Qt.CopyAction

    def supportedDropActions(self):
        # Qt lack documentation and sanity - this method returns *drag*
        # actions. The more suprirsing an API is, the better. LOL.
        return Qt.CopyAction


class MutableFontListModel(FontListModel):

    """A mutable font list model: You can drop fonts here. You can set
    the selected fonts here.

    You construct the model providing all available fonts (and it
    is still empty), then fonts are added either through drag & drop of
    FontItemMimeData, or through setFontItem() which replaces the model
    fonts with the current and selected list of items.

    This is used by the font duel, and by the FontInfoTable widget.
    """

    def __init__(self, families: IterableOf[fontlist.FontLike]=None,
                       featureSets: fontlist.FeatureSets=None, **kwargs):

        families = list(families)
        if featureSets is None:
            featureSets = fontlist.FeatureSets(families)

        super().__init__(families=[], featureSets=featureSets,
                         hideStyles=True, **kwargs)

        self.familyStash = {}
        self.fullnameStash = {}
        self.styleStash = defaultdict(dict)

        items = set(families)

        while items:
            item = items.pop()
            if item.is_family:
                items.update(item.styles)
                for family in item.search_families():
                    self.familyStash[family] = item
            else:
                for family, style in item.search_familystyle_tuples():
                    self.styleStash[family][style] = item
                for fullname in item.search_fullnames():
                    self.fullnameStash[fullname] = item

        self.styleStash = dict(self.styleStash)

    def setFamilies(self, *args, **kwargs):
        """This model forbids setting the families."""
        raise NotImplementedError
    
    @Slot(object)
    @Slot(object, list)
    def setFontItem(self, item: fontlist.FontLike,
                          selected: IterableOf[fontlist.FontLike]=()):
        """Set the current font item, and the selected font item.
        This replaces the items of the model with those."""
        if not selected:
            selected = [item]

        self.beginResetModel()
        self.families[:] = selected
        self.endResetModel()

    def dropMimeData(self, data, action, row, column, parent, testonly=False):

        fontItems = []

        if not isFontItemMimeData(data):
            if data.hasText():
                if testonly:
                    return True
                for name in data.text().splitlines(False):
                    if name in self.fullnameStash:
                        fontItems.append(self.fullnameStash[name])
                    elif name in self.familyStash:
                        fontItems.append(self.familyStash[name])
                    elif name in self.styleStash:
                        fontItem = next(iter(self.styleStash[name].values()))
                        fontItems.append(fontItem)

        else:
            if testonly:
                return True
            fontItems = data.fontItems()

        if not fontItems:
            return False

        if not testonly:
            if parent.isValid():
                row = parent.row() + 1

            row = max(0, max(len(self.families), row))

            self.beginInsertRows(QtCore.QModelIndex(),
                                 row, row + len(fontItems) - 1)
            self.families[row:row] = fontItems
            self.endInsertRows()

        return True

    def canDropMimeData(self, data, action, row, column, parent):
        return self.dropMimeData(data, action, row, column, parent,
                                 testonly=True)

    def supportedDragActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def flags(self, index):
        flags = super().flags(index)
        if not index.isValid():
            return flags | Qt.ItemIsDropEnabled
        return flags

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return False

        first = row
        last = row + count - 1

        first = max(0, first)
        last = min(len(self.families), last)

        if not (first <= last):
            return False

        self.beginRemoveRows(parent, first, last)
        del self.families[first:last + 1]
        self.endRemoveRows()

        return True


class FontResizeProxyModel(QtModelProxies.QIdentityProxyModel):

    """A proxy that resizes the fonts in a model to a given size.

    Currently, it works on the Qt.FontRole on all models that
    provide one.
    """

    def __init__(self, *args, pointSize: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.pointSize = pointSize

    def data(self, index, role=Qt.DisplayRole):
        result = super().data(index, role)
        if result and role == Qt.FontRole:
            result.setPointSize(self.pointSize)
        return result


class FontDelegate(QtWidgets.QStyledItemDelegate):

    """A delegate for rendering a font in a list of fonts.

    This draws the font name using the font itself, if it is not
    a symbol font or a non-latin font, or shows a sample to the right
    of the font name otherwise.
    """

    def __init__(self, view: QtWidgets.QAbstractItemView=None,
                       fontDb: QtGui.QFontDatabase=None, *args, **kwargs):
        super(FontDelegate, self).__init__(*args, **kwargs)
        self.view = view
        if fontDb is None:
            fontDb = QtGui.QFontDatabase()
        self.fontDb = fontDb

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)

        font = option.font
        if not font:
            return super(FontDelegate, self).paint(painter, option, index)

        writingSystems = self.fontDb.writingSystems(font.family())

        changeFont = QtGui.QFontDatabase.Latin not in writingSystems

        excludeWs = set([])
        if not changeFont:
            excludeWs.update([QtGui.QFontDatabase.Latin,
                              QtGui.QFontDatabase.Cyrillic,
                              QtGui.QFontDatabase.Greek,
                              QtGui.QFontDatabase.Vietnamese])

        sample = None
        for ws in reversed(writingSystems):
            if ws not in excludeWs:
                sample = self.fontDb.writingSystemSample(ws)
                break

        if self.view is None:
            style = QtWidgets.QApplication.style()
        else:
            style = self.view.style()
        metrics = option.fontMetrics
        palette = option.palette
        painter.save()

        rect = style.subElementRect(style.SE_ItemViewItemText, option)

        sampleFont = option.font

        if changeFont:
            defaultFont = QtWidgets.QApplication.font()
            sampleHint = sampleFont.styleHint()
            sampleStrategy = sampleFont.styleStrategy()
            hintingPreference = sampleFont.hintingPreference()
            sampleFont = self.fontDb.font(sampleFont.family(),
                                          sampleFont.styleName(),
                                          sampleFont.pointSize())
            sampleFont.setStyleHint(sampleHint, sampleStrategy)
            sampleFont.setHintingPreference(hintingPreference)
            option.font = self.fontDb.font(defaultFont.family(),
                                           defaultFont.styleName(),
                                           sampleFont.pointSize())

        style.drawControl(style.CE_ItemViewItem, option, painter, None)

        painter.setFont(sampleFont)

        if sample:
            enabled = False
            if option.state & style.State_Enabled:
                enabled = True

            if option.state & style.State_Selected:
                role = palette.HighlightedText
            else:
                role = palette.Text

            style.drawItemText(painter,
                               style.itemTextRect(metrics, rect,
                                                  Qt.AlignRight, enabled,
                                                  sample),
                               Qt.AlignRight, palette, enabled, sample, role)

        painter.restore()


class SelectLangDialog(QtWidgets.QScrollArea):

    """Language filter select dialog. This has been superseded by
    SelectLangDialog2. It automatically deals with updating the filters."""

    def __init__(self, langDb: 'typeatlas.langutil.LanguageDatabase',
                       filterInstance: 'FontFilterModelFilters',
                       parent: QtWidgets.QWidget=None):
        super(SelectLangDialog, self).__init__(parent)
        self.setWindowTitle(_("Select languages"))
        self.filterInstance = filterInstance

        self.checkboxLang = {}
        self.langCheckbox = {}
        layout = HorizontalFlowLayout()

        featureSets = filterInstance.featureSets()

        self.appearsWith = featureSets.lang_appears_with
        self.appearsWithout = featureSets.lang_appears_without
        self.absentTogether = featureSets.lang_absent_together_with

        langState = filterInstance.filterLanguages or {}

        standardCheckboxes = filterInstance.options.standardCheckboxes
        filterInstance.options.standardCheckboxesChanged.connect(
            self._standardCheckboxesChanges)
        checkBoxStylesheet = includeExcludeCheckboxCss()

        for lang in langDb.sort_languages(featureSets.languages):
            countryflag = langDb.guess_country_flag(lang)

            checkbox = QtWidgets.QCheckBox()
            checkbox.setText("%s (%s)" % (langDb.language_name(lang), lang))

            if countryflag is not None:
                checkbox.setIcon(getIcon('flags/' + countryflag))
            checkbox.setTristate(True)
            if not standardCheckboxes:
                checkbox.setStyleSheet(checkBoxStylesheet)
            ## Default value
            #checkbox.setCheckState(Qt.PartiallyChecked)
            checkbox.setCheckState(boolToCheckState.get(langState.get(lang),
                                                        Qt.PartiallyChecked))
            checkbox.stateChanged.connect(self.stateChanged)
            layout.addWidget(checkbox)

            self.checkboxLang[checkbox] = lang
            self.langCheckbox[lang] = checkbox

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        #widget.setSizePolicy(FlowLayoutSizePolicy(layout))
        widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                             QtWidgets.QSizePolicy.Minimum)
        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.resize(generalWidth(refSize=900),
                    generalHeight(refSize=800))

    @Slot(int)
    def stateChanged(self, state):
        """A language checkbox changed."""
        checkbox = self.sender()
        if not checkbox.isEnabled():
            return
        lang = self.checkboxLang.get(checkbox)
        if lang is None:
            return

        if self.filterInstance.filterLanguages is None:
            self.filterInstance.filterLanguages = {}

        filterLanguages = self.filterInstance.filterLanguages
        appearsWith = self.appearsWith
        appearsWithout = self.appearsWithout
        absentTogether = self.absentTogether

        if state == Qt.PartiallyChecked:
            filterLanguages.pop(lang, None)
        elif state == Qt.Checked:
            if not all(appearsWith(lang, selLang) if selected else
                       appearsWithout(lang, selLang)
                            for selLang, selected in filterLanguages.items()
                       if selLang != lang):
                checkbox.nextCheckState()
                return

            filterLanguages[lang] = True
        else:
            if not all(appearsWithout(selLang, lang) if selected else
                       absentTogether(selLang, lang)
                            for selLang, selected in filterLanguages.items()
                       if selLang != lang):
                checkbox.nextCheckState()
                return
            filterLanguages[lang] = False

        for otherCheckbox, otherLang in self.checkboxLang.items():
            if otherCheckbox is checkbox or otherLang in filterLanguages:
                continue

            if not all(appearsWith(otherLang, selLang) if selected else
                       appearsWithout(otherLang, selLang)
                            for selLang, selected in filterLanguages.items()):
                otherCheckbox.setEnabled(False)
                otherCheckbox.setCheckState(Qt.Unchecked)

            elif not all(appearsWithout(selLang, otherLang) if selected else
                         absentTogether(selLang, otherLang)
                            for selLang, selected in filterLanguages.items()):
                otherCheckbox.setEnabled(False)
                otherCheckbox.setCheckState(Qt.Checked)

            elif otherLang not in filterLanguages:
                otherCheckbox.setCheckState(Qt.PartiallyChecked)
                otherCheckbox.setEnabled(True)

            else:
                otherCheckbox.setCheckState(Qt.Checked
                                                if filterLanguages[otherLang]
                                                else Qt.Unchecked)
                otherCheckbox.setEnabled(True)

        self.filterInstance.filterCompleteWidgetEdit()

    @Slot(bool)
    def _standardCheckboxesChanges(self, value: bool=False):
        """The preferred rendering of include/exclude tristate checkboxes
        changed."""
        if value:
            stylesheet = ''
        else:
            stylesheet = includeExcludeCheckboxCss()
        for checkbox in self.langCheckbox.values(stylesheet):
            checkbox.setStyleSheet(stylesheet)


class EditableFontGroupModel(CheckableStyledObjectListModel):

    """A checkable item sequence model made of font groups that are
    editable (like tag or category), so drag & drop works."""

    def mimeTypes(self):
        return ['text/plain', 'text/html',
                'application/x-qabstractitemmodeldatalist']

    def dropMimeData(self, data, action, row, column, parent, testonly=False):

        fontItems = []

        # Drop only on groups
        if row >= 0 or column >= 0 or not parent.isValid():
            return False

        if not isFontItemMimeData(data):
            return False

        fontItems = data.fontItems()
        if not fontItems:
            return False

        groupItem = self.itemAtIndex(parent)
        if groupItem is None or groupItem.container is None:
            return False

        if not testonly:
            families = OrderedSet(fi.family for fi in fontItems)
            for family in families:
                groupItem.container.add(family, groupItem.key)

        return True

    def flags(self, index):
        flags = super().flags(index)
        if index.isValid():
            flags |= Qt.ItemIsDropEnabled
        return flags

    def canDropMimeData(self, data, action, row, column, parent):
        return self.dropMimeData(data, action, row, column, parent,
                                 testonly=True)

    def supportedDragActions(self):
        return Qt.CopyAction

    def supportedDropActions(self):
        return Qt.CopyAction


class ItemValuesDialogBase(QtWidgets.QWidget):

    """A base for dialogs that allow filter selection of driven by
    item-value instances.

    These can be either checkboxed (language select, category select,
    tag select), or simple item views (delete searches, deleted interfaces).

    You need to provide the properties in the subclass.

    If familiesEditable=True is set, you can drop fonts on the model,
    as EditableFontGroupModel will be used. The fonts will be added
    to tag or category.

    If itemsRemovable=True is set or itemsEditable=True is set,
    you will be able to remove and delete items from the dialog.

    If itemsHaveContainer=True is set, it means those are datastore
    categories, tags, searches or other items with a container.

    #The itemAdapter is passed to the ListItemModel.

    This widget emits the closed signal, so it can be opened by TypeAtlas'
    main library.
    """

    filterKey = 'nonexistents'
    dialogIconName = 'typeatlas'
    dialogTitleText = 'select something dialog'
    searchPlaceholderText = 'Search something...'

    refWidth = 900
    refHeight = 800

    familiesEditable = False
    itemsRemovable = False
    itemsEditable = False
    itemsHaveContainer = False

    def __init__(self, filterInstance: 'FontFilterModelFilters'=None,
                       itemValues: filtering.ItemValues=None,
                       options: Options=None,
                       parent: QtWidgets.QWidget=None,
                       itemAdapter: Callable=None):
        super().__init__(parent)
        self.setWindowTitle(_(self.dialogTitleText))
        self.setWindowIcon(getIcon(self.dialogIconName))

        self.filterInstance = filterInstance
        layout = QtWidgets.QVBoxLayout()

        if itemValues is None:
            itemConnector = filterInstance.noisyItemConnector()
            itemValues = itemConnector.item_values(self.filterKey)

        self.itemValues = itemValues

        if itemValues.type & filtering.ITEM_TYPE_BOOLEAN:
            if self.familiesEditable:
                factory = EditableFontGroupModel
            else:
                factory = CheckableStyledObjectListModel

            model = factory(itemValues.items, itemValues.values,
                            itemValues.fixed,
                            isTristate=itemValues.type &
                                       filtering.ITEM_FLAG_TRISTATE,
                            rowsRemovable=self.itemsRemovable,
                            itemAdapter=itemAdapter)
        else:
            model = StyledObjectListModel(itemValues.items,
                                          rowsRemovable=self.itemsRemovable,
                                          itemAdapter=itemAdapter)

        self.proxyModel = proxyModel = QtCore.QSortFilterProxyModel()
        proxyModel.setFilterRole(ItemSearchRole)
        proxyModel.setSourceModel(model)
        proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.textWidget = search = QuickSearch(
                placeholderText=_(self.searchPlaceholderText))
        search.searchTriggered.connect(self._filterTextChanged)

        self.view = view = QtWidgets.QListView()
        view.setModel(proxyModel)

        if options is None:
            if filterInstance is not None:
                options = filterInstance.options
            else:
                options = Options.getInstance()

        if not options.standardCheckboxes:
            view.setStyleSheet(includeExcludeCheckboxCss())
        options.standardCheckboxesChanged.connect(
                                self._standardCheckboxesChanges)

        view.setViewMode(view.ListMode)
        view.setFlow(QtWidgets.QListView.TopToBottom)
        view.setResizeMode(QtWidgets.QListView.Adjust)
        view.setWrapping(True)
        if self.familiesEditable:
            view.setDragDropMode(view.DropOnly)
            view.setAcceptDrops(True)
            view.setDropIndicatorShown(True)

        layout.addWidget(search)
        layout.addWidget(view)

        if self.itemsEditable or self.itemsRemovable:
            buttons = QtWidgets.QDialogButtonBox()
            if self.itemsEditable:
                but = buttons.addButton(_("Edit..."), buttons.ActionRole)
                but.clicked.connect(self._editCurrentItem)
            if self.itemsRemovable:
                but = buttons.addButton(_("Delete..."), buttons.ActionRole)
                but.clicked.connect(self._deleteSelectedItems)
            layout.addWidget(buttons)

        self.setLayout(layout)

        self.resize(generalWidth(refSize=self.refWidth),
                    generalHeight(refSize=self.refHeight))

    @Slot()
    def _deleteSelectedItems(self):
        """User has clicked the delete button. Ask them do they really mean
        it, and do it."""

        if not self.itemsRemovable:
            raise RuntimeError("rows not removable for %r" % (self, ))
        
        if self.itemsHaveContainer:
            container = self.itemValues.items.container
            label = container.factory.type_label_plural
        else:
            label = self.filterKey

        but = QtWidgets.QMessageBox.question(
                  self, _("Confirm deletion of {}").format(_(label)),
                  _("Are you sure you want to delete the selected {}?").format(
                      _(label)))
        if but != QtWidgets.QMessageBox.Yes:
            return

        selected = self.view.selectionModel().selectedIndexes()
        if not selected:
            current = self.view.selectionModel().currentIndex()
            if not current.isValid():
                return
            selected = [current]
        rowBlocks = toblocks(index.row() for index in selected)
        for block in reversed(list(rowBlocks)):
            self.proxyModel.removeRows(block.start, 
                                       block.end - block.start + 1)

        self.saveChangedItems()

    def showOverwriteError(self, groupName: str, newName: str):
        """Display an error when overwriting."""
        if self.itemsHaveContainer:
            container = self.itemValues.items.container
            label = container.factory.type_label_plural
        else:
            label = self.filterKey

        QtWidgets.QMessageBox.critical(
            self, _("{} already exists").format(_(label).title()),
            _("The name you entered for {} already exists: {}").format(
                        _(label, newName)))

    def saveChangedItems(self):
        """Reimplement this in a subclass for custom item editor."""
        if not self.itemsHaveContainer:
            return
        self.itemValues.items.container.save()

    def editItem(self, index: QtCore.QModelIndex,
                       groupName: str, newName: str=None,
                       icon: str=None, color: str=None):
        """Complete the edition of the selected item's icon, color and maybe
        name.

        Reimplement this in a subclass for custom item editor."""
        if not self.itemsHaveContainer:
            # TODO: String items may be editable with setData
            raise RuntimeError("rows not editable without a "
                               "container for %r" % (self, ))
        container = self.itemValues.items.container

        if newName is None:
            newName = groupName

        if newName != groupName:
            try:
                container.rename(groupName, newName)
            except KeyError as exc:
                if exc.args[0] != newName:
                    raise
                # TODO: Error here
                self.showOverwriteError(groupName, newName)
                return

        container.define(newName, icon, color)

    @Slot()
    def _editCurrentItem(self):
        """User asked to edit the current item. Ask them what to, and
        do it."""
        if not self.itemsEditable:
            raise RuntimeError("rows not editable for %r" % (self, ))
        
        if (not self.itemsHaveContainer and
            type(self).editItem == ItemValuesDialogBase.editItem):

            # TODO: String items may be editable with setData
            raise RuntimeError("rows not editable without a "
                               "container for %r" % (self, ))

        #selected = self.view.selectionModel().selectedIndexes()
        selected = None
        if not selected:
            current = self.view.selectionModel().currentIndex()
            if not current.isValid():
                return
            selected = [current]

        container = None
        if self.itemsHaveContainer:
            container = self.itemValues.items.container

        # TODO: We *can* edit the name, though.
        kwargs = dict(groupContainer=container, nameEditable=False)

        for index in selected:
            groupName = index.data(Qt.DisplayRole)
            dialog = GroupNameDialog(groupName=groupName, **kwargs)

            if not self.itemsHaveContainer:
                item = index.data(ItemItemRole)
                dialog.setIcon(item.icon())
                color = item.color()
                dialog.setColor(QtGui.QColor(color)
                                    if color is not None
                                    else None)

            if not dialog.exec_():
                continue

            self.editItem(index, groupName, dialog.groupName, dialog.icon,
                          dialog.colorName())

        self.saveChangedItems()

    @Slot(str)
    def _filterTextChanged(self, text: str):
        """Our filter text changed, filter the items."""
        self.proxyModel.setFilterFixedString(text.strip())

    @Slot(bool)
    def _standardCheckboxesChanges(self, value: bool=False):
        """The preferred rendering of include/exclude tristate checkboxes
        changed."""
        if value:
            stylesheet = ''
        else:
            stylesheet = includeExcludeCheckboxCss()
        self.view.setStyleSheet(stylesheet)

    closed = Signal()

    def closeEvent(self, event):
        r = super().closeEvent(event)
        if event.isAccepted():
            self.closed.emit()
        return r



class SelectLangDialog2(ItemValuesDialogBase):

    """Language filter select dialog. It automatically deals with
    updating the filters. Fancier than the SelectLangDialog (it
    has a filter)."""

    filterKey = 'languages'
    dialogTitleText = N_("Select languages")
    searchPlaceholderText = N_('Search languages...')

    refWidth = 900
    refHeight = 800

    def __init__(self, langDb, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SelectTagsDialog(ItemValuesDialogBase):

    """Tag filter select dialog. It automatically deals with
    updating the filters."""

    filterKey = 'tags'
    dialogTitleText = N_("Select tags")
    searchPlaceholderText = N_('Search tags...')

    refWidth = 900
    refHeight = 800

    familiesEditable = True
    itemsRemovable = True
    itemsEditable = True
    itemsHaveContainer = True


class SelectCategoriesDialog(ItemValuesDialogBase):

    """Categories filter select dialog. It automatically deals with
    updating the filters."""

    filterKey = 'categories'
    dialogTitleText = N_("Select categories")
    searchPlaceholderText = N_('Search categories...')

    refWidth = 900
    refHeight = 800

    familiesEditable = True
    itemsRemovable = True
    itemsEditable = True
    itemsHaveContainer = True


class EditSearchesDialog(ItemValuesDialogBase):

    """A dialog for editing the saved searches."""

    filterKey = 'searches'
    dialogTitleText = N_("Edit searches")
    searchPlaceholderText = N_('Search searches...')

    refWidth = 900
    refHeight = 800

    itemsRemovable = True
    itemsEditable = True
    itemsHaveContainer = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SelectWritingSystemDialog(QtWidgets.QScrollArea):

    """Writing system filter select dialog. It automatically deals with
    updating the filters."""

    def __init__(self, filterInstance, parent=None):
        super(SelectWritingSystemDialog, self).__init__(parent)
        self.setWindowTitle(_("Select writing systems"))
        self.filterInstance = filterInstance
        self.checkboxWritingSystem = {}
        self.writingSystemCheckbox = {}

        widget = QtWidgets.QWidget()
        self.setWidget(widget)
        self.setWidgetResizable(True)

        layout = QtWidgets.QVBoxLayout()

        writingSystems = filterInstance.writingSystems()
        fontDb = filterInstance.fontDb()
        wsState = filterInstance.filterWritingSystems or {}

        standardCheckboxes = filterInstance.options.standardCheckboxes
        filterInstance.options.standardCheckboxesChanged.connect(
            self._standardCheckboxesChanges)

        for ws, name in sorted(writingSystems):
            checkbox = QtWidgets.QCheckBox()
            checkbox.setText("%s (%s)" % (name, fontDb.writingSystemSample(ws)))
            checkbox.setTristate(True)
            if not standardCheckboxes:
                checkbox.setStyleSheet(includeExcludeCheckboxCss())
            ## Default value
            #checkbox.setCheckState(Qt.PartiallyChecked)
            checkbox.setCheckState(boolToCheckState.get(wsState.get(ws),
                                                        Qt.PartiallyChecked))
            checkbox.stateChanged.connect(self.stateChanged)
            layout.addWidget(checkbox)

            self.checkboxWritingSystem[checkbox] = ws
            self.writingSystemCheckbox[ws] = checkbox

        widget.setLayout(layout)
        self.resize(generalWidth(refSize=300),
                    generalHeight(refSize=800))

    @Slot(int)
    def stateChanged(self, state):
        """A writing system checkbox changed."""
        checkbox = self.sender()
        ws = self.checkboxWritingSystem.get(checkbox)
        if ws is None:
            return

        if self.filterInstance.filterWritingSystems is None:
            self.filterInstance.filterWritingSystems = {}

        if state == Qt.PartiallyChecked:
            self.filterInstance.filterWritingSystems.pop(ws, None)
        else:
            self.filterInstance.filterWritingSystems[ws] = state == Qt.Checked
        self.filterInstance.filterCompleteWidgetEdit()

    @Slot(bool)
    def _standardCheckboxesChanges(self, value: bool=False):
        """The preferred rendering of include/exclude tristate checkboxes
        changed."""
        if value:
            stylesheet = ''
        else:
            stylesheet = includeExcludeCheckboxCss()
        for checkbox in self.writingSystemCheckbox.values():
            checkbox.setStyleSheet(stylesheet)


class SelectFeaturesDialog(QtWidgets.QScrollArea):

    """Family and class filter select dialog. It automatically deals with
    updating the filters. This selects fonts by generic family, IBM and
    PANOSE class, font format type, whether the font is monospace, etc."""

    def __init__(self, filterInstance, parent=None):
        super(SelectFeaturesDialog, self).__init__(parent)
        self.setWindowTitle(_("Select font style family and features"))
        self.filterInstance = filterInstance

        self.genericFamilyByCheckbox = {}
        self.checkboxByGenericFamily = {}
        self.fontFormatByCheckbox = {}
        self.checkboxByFontFormat = {}

        self.ibmClassByCheckbox = {}
        self.ibmSubclassByCheckbox = {}
        self.checkboxByIbmClass = {}
        self.checkboxByIbmSubclass = {}
        self.ibmClassCheckboxes = defaultdict(list)
        self.ibmClassBox = {}

        self.panoseClassByCheckbox = {}
        self.panoseSubclassByCheckbox = {}
        self.checkboxByPanoseClass = {}
        self.checkboxByPanoseSubclass = {}
        self.comboByPanoseProperty = {}
        self.comboIdxByPanosePropChoice = {}

        self.panoseClassCheckboxes = defaultdict(list)
        self.panoseClassComboboxes = defaultdict(list)
        self.panoseClassBox = {}

        layout = QtWidgets.QGridLayout()

        self.genericFamilyBox = QtWidgets.QGroupBox(_('Generic family'))
        self.genericFamilyLayout = FlowLayout()
        self.genericFamilyBox.setLayout(self.genericFamilyLayout)

        self.fontFormatBox = QtWidgets.QGroupBox(_('Font format'))
        self.fontFormatLayout = FlowLayout()
        self.fontFormatBox.setLayout(self.fontFormatLayout)

        featureSets = filterInstance.featureSets()

        selectedGenericFamilies = filterInstance.filterGenericFamily or ()

        for genericfamily in featureSets.genericfamilies:
            label = _(genericfamily or N_('unclassified')).capitalize()
            checkbox = QtWidgets.QCheckBox(label)
            checkbox.setIcon(getIcon(genericfamily))
            checkbox.setChecked(genericfamily in selectedGenericFamilies)
            checkbox.stateChanged.connect(self.stateChanged)
            self.genericFamilyByCheckbox[checkbox] = genericfamily
            self.checkboxByGenericFamily[genericfamily] = checkbox
            self.genericFamilyLayout.addWidget(checkbox)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(sep.VLine)
        self.genericFamilyLayout.addWidget(sep)

        checkbox = QtWidgets.QCheckBox(_('Monospace'))
        checkbox.setIcon(getIcon('monospace'))
        checkbox.setTristate(True)
        if not filterInstance.options.standardCheckboxes:
            checkbox.setStyleSheet(includeExcludeCheckboxCss())

        filterInstance.options.standardCheckboxesChanged.connect(
            self._standardCheckboxesChanges)

        ## Default value
        #checkbox.setCheckState(Qt.PartiallyChecked)
        checkbox.setCheckState(boolToCheckState.get(filterInstance.filterMonospace,
                                                    Qt.PartiallyChecked))
        checkbox.stateChanged.connect(self.stateChanged)
        self.genericFamilyLayout.addWidget(checkbox)
        self.monospaceCheckbox = checkbox

        selectedFontFormats = filterInstance.filterFontFormat or ()

        for fontformat, info in featureSets.font_formats.items():
            label = info.name
            checkbox = QtWidgets.QCheckBox(info.name)
            if info.category_icon:
                checkbox.setIcon(getIcon(info.category_icon))
            checkbox.setChecked(fontformat in selectedFontFormats)
            checkbox.stateChanged.connect(self.stateChanged)
            self.fontFormatByCheckbox[checkbox] = fontformat
            self.checkboxByFontFormat[fontformat] = checkbox
            self.fontFormatLayout.addWidget(checkbox)

        button = QtWidgets.QPushButton(_("Only OpenType"))
        button.setIcon(getIcon('otf'))
        self.fontFormatLayout.addWidget(button)

        @button.clicked.connect
        def callback(*args):
            for checkbox, fontformat in self.fontFormatByCheckbox.items():
                if fontformat in ['TrueType', 'CFF']:
                    checkbox.setCheckState(Qt.Checked)
                else:
                    checkbox.setCheckState(Qt.Unchecked)

        self.panoseclassesBox = QtWidgets.QGroupBox(_('PANOSE class'))
        self.panoseclassesLayout = QtWidgets.QVBoxLayout()
        self.panoseclassesBox.setLayout(self.panoseclassesLayout)

        self.panoseClassLayout = FlowLayout()
        self.panoseSubclassLayout = QtWidgets.QStackedLayout()
        self.panoseclassesLayout.addLayout(self.panoseClassLayout)
        self.panoseclassesLayout.addLayout(self.panoseSubclassLayout)

        self.panoseNoSubclass = QtWidgets.QWidget()
        self.panoseSubclassLayout.addWidget(self.panoseNoSubclass)

        selectedPanoseClass = filterInstance.filterPanoseClass or ()
        selectedPanoseSubclass = filterInstance.filterPanoseSubclass or ()
        selectedPanoseProperties = filterInstance.filterPanoseProperties or {}

        for class_id, class_name in sorted(opentype.PANOSE_CLASSES.items()):
            checkbox = QtWidgets.QCheckBox(_(class_name))
            #checkbox.setTristate(True)
            #checkbox.setCheckState(Qt.PartiallyChecked)
            checkbox.setChecked(class_id in selectedPanoseClass)
            checkbox.stateChanged.connect(self.stateChanged)
            self.panoseClassByCheckbox[checkbox] = class_id
            self.checkboxByPanoseClass[class_id] = checkbox
            self.panoseClassLayout.addWidget(checkbox)

            classBox = QtWidgets.QGroupBox(_("%s subclass") % (_(class_name), ))
            classFlowLayout = FlowLayout()
            classLayout = QtWidgets.QGridLayout()
            classLayout.addLayout(classFlowLayout, 0, 0, 1, 2)
            classBox.setLayout(classLayout)
            subclasses = opentype.PANOSE_CLASS_SUBCLASSES.get(class_id, {})
            subclasses = chain(opentype.PANOSE_GENERIC_SUBCLASSES.items(),
                               subclasses.items())
            icons = opentype.PANOSE_CLASS_ICONS.get(class_id, {})
            for subclass_id, subclass_name in sorted(subclasses):
                iconname = icons.get(subclass_id)
                checkbox = QtWidgets.QCheckBox(_(subclass_name))
                if iconname:
                    checkbox.setToolTip(getIconHtml(iconname, 32))

                #checkbox.setTristate(True)
                #checkbox.setCheckState(Qt.PartiallyChecked)
                if selectedPanoseClass == {class_id}:
                    checkbox.setChecked(subclass_id in selectedPanoseSubclass)

                checkbox.stateChanged.connect(self.stateChanged)
                self.panoseSubclassByCheckbox[checkbox] = subclass_id
                self.checkboxByPanoseSubclass[class_id, subclass_id] = checkbox
                self.panoseClassCheckboxes[class_id].append(checkbox)
                classFlowLayout.addWidget(checkbox)

            properties = opentype.get_panose_fields(class_id).properties()

            for i, prop in enumerate(properties, 1):

                propLabel = QtWidgets.QLabel()
                propLabel.setTextFormat(Qt.PlainText)
                propLabel.setText(_(prop.fieldname))
                propCombo = QtWidgets.QComboBox()
                propCombo.addItem(_('Any'), None)
                propCombo.setProperty('panosePropertyPos', prop.pos)
                self.comboByPanoseProperty[class_id, prop.pos] = propCombo
                self.comboIdxByPanosePropChoice[class_id, prop.pos, None] = 0
                self.panoseClassComboboxes[class_id].append(propCombo)

                for j, (choice, text) in enumerate(
                                    prop.choices_text(translate=_).items(), 1):

                    propCombo.addItem(text, choice)
                    choiceKey = class_id, prop.pos, choice
                    self.comboIdxByPanosePropChoice[choiceKey] = j

                if selectedPanoseClass == {class_id}:
                    if prop.pos in selectedPanoseProperties:
                        choice = selectedPanoseProperties[choice]
                        choiceKey = class_id, prop.pos, choice
                        j = self.comboIdxByPanosePropChoice.get(choiceKey)
                        if j is not None:
                            propCombo.setCurrentIndex(j)

                propCombo.currentIndexChanged.connect(self.comboIndexChanged)

                classLayout.addWidget(propLabel, i, 0, 1, 1)
                classLayout.addWidget(propCombo, i, 1, 1, 1)

            self.panoseClassBox[class_id] = classBox
            self.panoseSubclassLayout.addWidget(classBox)

        self.ibmclassesBox = QtWidgets.QGroupBox(_('IBM class'))
        self.ibmclassesLayout = QtWidgets.QVBoxLayout()
        self.ibmclassesBox.setLayout(self.ibmclassesLayout)

        self.ibmClassLayout = FlowLayout()
        self.ibmSubclassLayout = QtWidgets.QStackedLayout()
        self.ibmclassesLayout.addLayout(self.ibmClassLayout)
        self.ibmclassesLayout.addLayout(self.ibmSubclassLayout)

        self.ibmNoSubclass = QtWidgets.QWidget()
        self.ibmSubclassLayout.addWidget(self.ibmNoSubclass)

        selectedIbmClass = filterInstance.filterIbmClass or ()
        selectedIbmSubclass = filterInstance.filterIbmSubclass or ()

        for class_id, class_name in sorted(opentype.IBM_CLASSES.items()):
            checkbox = QtWidgets.QCheckBox(_(class_name))
            #checkbox.setTristate(True)
            #checkbox.setCheckState(Qt.PartiallyChecked)
            checkbox.setChecked(class_id in selectedIbmClass)
            checkbox.stateChanged.connect(self.stateChanged)
            self.ibmClassByCheckbox[checkbox] = class_id
            self.checkboxByIbmClass[class_id] = checkbox
            self.ibmClassLayout.addWidget(checkbox)

            classBox = QtWidgets.QGroupBox(_("%s subclass") % (_(class_name), ))
            classLayout = FlowLayout()
            classBox.setLayout(classLayout)

            subclasses = opentype.IBM_CLASS_SUBCLASSES.get(class_id, {})
            subclasses = chain(subclasses.items(),
                               [(subid + class_id * 256, value)
                                for subid, value
                                    in opentype.IBM_GENERIC_SUBCLASSES.items()])

            for subclass_id, subclass_name in sorted(subclasses):
                checkbox = QtWidgets.QCheckBox(_(subclass_name))

                #checkbox.setTristate(True)
                #checkbox.setCheckState(Qt.PartiallyChecked)
                if selectedIbmClass == {class_id}:
                    checkbox.setChecked(subclass_id in selectedIbmSubclass)

                checkbox.stateChanged.connect(self.stateChanged)
                self.ibmSubclassByCheckbox[checkbox] = subclass_id
                self.checkboxByIbmSubclass[class_id, subclass_id] = checkbox
                self.ibmClassCheckboxes[class_id].append(checkbox)
                classLayout.addWidget(checkbox)
            self.ibmClassBox[class_id] = classBox
            self.ibmSubclassLayout.addWidget(classBox)

        layout.addWidget(self.genericFamilyBox, 0, 0, 1, 2)
        layout.addWidget(self.panoseclassesBox, 1, 1, 1, 1)
        layout.addWidget(self.ibmclassesBox, 1, 0, 1, 1)
        layout.addWidget(self.fontFormatBox, 2, 0, 1, 2)
        self.setLayout(layout)
        self.resize(generalWidth(refSize=800),
                    generalHeight(refSize=800))

    @Slot(int)
    def stateChanged(self, state):
        """A feature changebox changed."""
        checkbox = self.sender()

        fontFormat = self.fontFormatByCheckbox.get(checkbox)
        if fontFormat is not None:

            if self.filterInstance.filterFontFormat is None:
                self.filterInstance.filterFontFormat = set()

            if state == Qt.Checked:
                self.filterInstance.filterFontFormat.add(fontFormat)
            else:
                self.filterInstance.filterFontFormat.discard(fontFormat)

            self.filterInstance.filterCompleteWidgetEdit()
            return

        genericFamily = self.genericFamilyByCheckbox.get(checkbox)
        if genericFamily is not None:

            if self.filterInstance.filterGenericFamily is None:
                self.filterInstance.filterGenericFamily = set()

            if state == Qt.Checked:
                self.filterInstance.filterGenericFamily.add(genericFamily)
            else:
                self.filterInstance.filterGenericFamily.discard(genericFamily)

            self.filterInstance.filterCompleteWidgetEdit()
            return

        if checkbox is self.monospaceCheckbox:
            if state == Qt.PartiallyChecked:
                self.filterInstance.filterMonospace = None
            else:
                self.filterInstance.filterMonospace = state == Qt.Checked
            self.filterInstance.filterCompleteWidgetEdit()
            return

        panoseClass = self.panoseClassByCheckbox.get(checkbox)
        if panoseClass is not None:
            if self.filterInstance.filterPanoseClass is None:
                self.filterInstance.filterPanoseClass = set()

            if state == Qt.Checked:
                self.filterInstance.filterPanoseClass.add(panoseClass)
            else:
                self.filterInstance.filterPanoseClass.discard(panoseClass)

            if len(self.filterInstance.filterPanoseClass) == 1:
                chosenClass = next(iter(self.filterInstance.filterPanoseClass))
                self.filterInstance.filterPanoseSubclass = {
                    self.panoseSubclassByCheckbox[checkbox]
                    for checkbox in self.panoseClassCheckboxes[chosenClass]
                    if checkbox.isChecked()
                }
                self.filterInstance.filterPanoseProperties = {
                    combo.property('panosePropertyPos'):
                            combo.itemData(combo.currentIndex())
                    for combo in self.panoseClassComboboxes[chosenClass]
                    if combo.currentIndex()
                }
                self.panoseSubclassLayout.setCurrentWidget(
                    self.panoseClassBox.get(chosenClass, self.panoseNoSubclass))
            else:
                self.filterInstance.filterPanoseSubclass = None
                self.filterInstance.filterPanoseProperties = None
                self.panoseSubclassLayout.setCurrentWidget(
                    self.panoseNoSubclass)
            self.filterInstance.filterCompleteWidgetEdit()
            return

        panoseSubclass = self.panoseSubclassByCheckbox.get(checkbox)
        if panoseSubclass is not None:
            if state:
                self.filterInstance.filterPanoseSubclass.add(panoseSubclass)
            else:
                self.filterInstance.filterPanoseSubclass.discard(panoseSubclass)
            self.filterInstance.filterCompleteWidgetEdit()
            return

        ibmClass = self.ibmClassByCheckbox.get(checkbox)
        if ibmClass is not None:
            if self.filterInstance.filterIbmClass is None:
                self.filterInstance.filterIbmClass = set()

            if state == Qt.Checked:
                self.filterInstance.filterIbmClass.add(ibmClass)
            else:
                self.filterInstance.filterIbmClass.discard(ibmClass)

            if len(self.filterInstance.filterIbmClass) == 1:
                self.filterInstance.filterIbmSubclass = {
                    self.ibmSubclassByCheckbox[checkbox]
                    for checkbox in self.ibmClassCheckboxes[ibmClass]
                    if checkbox.isChecked()
                }
                self.ibmSubclassLayout.setCurrentWidget(
                    self.ibmClassBox.get(ibmClass, self.ibmNoSubclass))
            else:
                self.filterInstance.filterIbmSubclass = None
                self.ibmSubclassLayout.setCurrentWidget(
                    self.ibmNoSubclass)
            self.filterInstance.filterCompleteWidgetEdit()
            return

        ibmSubclass = self.ibmSubclassByCheckbox.get(checkbox)
        if ibmSubclass is not None:
            if state:
                self.filterInstance.filterIbmSubclass.add(ibmSubclass)
            else:
                self.filterInstance.filterIbmSubclass.discard(ibmSubclass)
            self.filterInstance.filterCompleteWidgetEdit()
            return

    @Slot(int)
    def comboIndexChanged(self, index: int):
        """A PANOSE property combo box changed."""
        combo = self.sender()
        pos = combo.property('panosePropertyPos')
        value = combo.itemData(index)

        filterProperties = self.filterInstance.filterPanoseProperties

        if filterProperties is None:
            self.filterInstance.filterPanoseProperties = filterProperties = {}

        if value is None:
            filterProperties.pop(pos, None)
        else:
            filterProperties[pos] = value

        self.filterInstance.filterCompleteWidgetEdit()

    @Slot(bool)
    def _standardCheckboxesChanges(self, value: bool=False):
        """The preferred rendering of include/exclude tristate checkboxes
        changed."""
        if value:
            stylesheet = ''
        else:
            stylesheet = includeExcludeCheckboxCss()
        self.monospaceCheckbox.setStyleSheet(stylesheet)


class FontFilterModelFilters(Toolbox):

    """The active filters, together with a list of actions to add
    to the main toolbar for filtering (implementing the Toolbox interface
    for that)."""

    filterText = ''
    filterScalable = None
    filterOutline = None
    filterLanguages = None
    filterWritingSystems = None

    filterGenericFamily = None
    filterMonospace = None
    filterFontFormat = None

    filterPanoseClass = None
    filterPanoseSubclass = None
    filterPanoseProperties = None

    filterIbmClass = None
    filterIbmSubclass = None

    filterContainsChars = None
    filterContainsAll = True

    filterChanged = Signal()

    searchFilePath = False
    searchFileName = False

    def __init__(self, langDb: 'typeatlas.langutil.LanguageDatabase',
                       filterModel: 'FontFilterModel',
                       parent: QtCore.QObject=None,
                       options: Options=None,
                       histories: datastore.Histories=None):
        if histories is None:
            histories = datastore.Histories.getInstance()
        if options is None:
            options = Options.getInstance()
        self.histories = histories
        self.options = options
        self.langDb = langDb
        self.filterModel = filterModel

        self.searchBarFilterText = ''
        self.searchBarExtraFilters = {}

        super().__init__(parent)

    def filterCompleteWidgetEdit(self):
        """We are done editing a filter widget somewhere. We call this."""
        self.filterChanged.emit()

    def windowParent(self):
        return self.filterModel.parent()

    def featureSets(self) -> fontlist.FeatureSets:
        return self.filterModel.sourceModel().featureSets

    def writingSystems(self) -> IterableOf[int]:
        return self.filterModel.sourceModel().writingSystems

    def fontDb(self) -> QtGui.QFontDatabase:
        return self.filterModel.sourceModel().fontDb

    def _lineEditActions(self):
        """The line edit actions, allowing one to search in file paths
        and file names. This may not be needed, since there's a syntax
        for that in the filters. See filtering.NameFilter"""
        if not ENABLE_COMPLEX_FILTERS:
            return
        yield self.action(self.setSearchFilePath,
                          _('File path'),
                          icon=getSelectableIconPair('folder'),
                          checkable=True, key='setSearchFilePath')
        yield self.action(self.setSearchFileName,
                          _('File name'),
                          icon=getSelectableIconPair('text-x-generic'),
                          checkable=True, key='setSearchFileName')

    def actionDefinitions(self) -> Iterator:

        text = QuickSearch(placeholderText=_('Search fonts...'),
                           history=self.histories.get_history('font-name'))
        text.searchTriggered.connect(self._filterTextChanged)
        if ENABLE_COMPLEX_FILTERS:
            text.setToolTip(_("Enter search ords or search patterns to find in names, "
                               "including filename and filepath special keywords:")+'\n'
                              'sans deja\n'
                              'noto*serif\n'
                              'filename:deja\n'
                              'path:/home')

        if hasattr(text.lineEdit, 'setClearButtonEnabled'):
            for action in self._lineEditActions():
                text.lineEdit.addAction(action, text.lineEdit.TrailingPosition)

        self.textWidget = text
        self.textAction = QtWidgets.QWidgetAction(self.actionParent)
        self.textAction.setDefaultWidget(text)
        yield self.textAction

        if not hasattr(text.lineEdit, 'setClearButtonEnabled'):
            yield from self._lineEditActions()

        yield self.action(self.writingSystemsClicked,
                          _("&Writing..."), icon='select-writing-system')
        yield self.action(self.languagesClicked,
                          _("&Languages..."), icon='select-language')
        yield self.action(self.classClicked,
                          _("&Class..."), icon='font-class')

        if ENABLE_COMPLEX_FILTERS:
            yield self.action(self.tagsClicked,
                              _("&Tags..."), icon='select-tags')
            yield self.action(self.categoriesClicked,
                              _("&Categories..."), icon='select-categories')

    def getFilterWidget(self, getLayout: bool=False) -> QtWidgets.QWidget:
        """DEPRECATED?

        Get the filter widget. This returns a toolbar, or a layouted
        custom widget, depending on the first argument. This includes the
        main filter. Currently, we prefer to populate the main window's
        toolbar than using this semi-obsolete method."""

        if not getLayout:
            options = self.options
            toolbar = QtWidgets.QToolBar()
            toolbar.setIconSize(options.toolbarIconSize)
            options.toolbarIconSizeChanged.connect(toolbar.setIconSize)
            self.populateToolbar(toolbar)
            return toolbar

        layout = QtWidgets.QHBoxLayout()

        text = QtWidgets.QLineEdit()
        text.textChanged.connect(self.setFilterText)
        text.setPlaceholderText(_('Search fonts...'))
        if hasattr(text, 'setClearButtonEnabled'):
            text.setClearButtonEnabled(True)
        layout.addWidget(text)

        #for slot, label, icon in [(self.scalableStateChanged,
        #                           _('Scalable'), 'scalable'),
        #                          (self.outlineStateChanged,
        #                           _('Outline'), 'outline')]:
        #    checkbox = QtWidgets.QCheckBox()
        #    checkbox.setTristate(True)
        #    checkbox.setCheckState(Qt.PartiallyChecked)
        #    checkbox.stateChanged.connect(slot)
        #    checkbox.setIcon(getIcon(icon))
        #    checkbox.setText(label)
        #    layout.addWidget(checkbox)

        wsButton = QtWidgets.QPushButton(_("&Writing..."))
        wsButton.clicked.connect(self.writingSystemsClicked)
        layout.addWidget(wsButton)

        langButton = QtWidgets.QPushButton(_("&Languages..."))
        langButton.clicked.connect(self.languagesClicked)
        layout.addWidget(langButton)

        classButton = QtWidgets.QPushButton(getIcon('font-class'),
                                            _("&Class..."))
        classButton.clicked.connect(self.classClicked)
        layout.addWidget(classButton)

        if getLayout:
            return layout

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                             QtWidgets.QSizePolicy.Fixed)
        return widget

    @Slot(str)
    def _filterTextChanged(self, text):
        """The filter text changed in the QuickSearch. Set the filter text."""
        self.setFilterText(text)

    @Slot(bool)
    def setSearchFilePath(self, checked=False):
        """We changed whether we should search in file paths."""
        self.searchFilePath = checked
        if checked:
            self.filterFilePath = self.filterText
        else:
            self.filterFilePath = None

    @Slot(bool)
    def setSearchFileName(self, checked=False):
        """We changed whether we should search in file names."""
        self.searchFileName = checked
        if checked:
            self.filterFileName = self.filterText
        else:
            self.filterFileName = None

    @Slot(str, bool)
    def setContainsChars(self, text: str, containsAll: bool=True):
        """Set the characters to require in a font. This is used
        by the font sampler. Call this to limit the fonts to the
        ones that contain these characters. By default, all characters
        are required."""
        if not text:
            self.filterContainsChars = None
        else:
            self.filterContainsChars = frozenset(ord(c) for c in text
                                                 if not c.isspace())
        self.filterContainsAll = containsAll
        self.filterCompleteWidgetEdit()

    @Slot(str)
    def setFilterText(self, text: str):
        """Manually set the filter text."""
        text = text.casefold()

        extraFilters = None
        if ENABLE_COMPLEX_FILTERS:
            text, extraFilters = filtering.split_filter_text(text)

        self.searchBarFilterText = text
        self.searchBarExtraFilters = extraFilters

        if ENABLE_COMPLEX_FILTERS:
            self._applyExtraFilters()

        # FIXME: The condition is a workarround for bug h48k0dfgb
        if self.filterText != text:
            self.filterText = text
        if self.searchFileName:
            self.filterFileName = text
        if self.searchFilePath:
            self.filterFilePath = text
        self.filterCompleteWidgetEdit()

    @Slot(int)
    def scalableStateChanged(self, state: bool):
        """The scalable button changed. We *have* a scalale button?"""
        if state == Qt.PartiallyChecked:
            self.filterScalable = None
        else:
            self.filterScalable = state == Qt.Checked
        self.filterCompleteWidgetEdit()

    def getFilterDialog(self, name: str,
                              parent: QtWidgets.QWidget=None,
                              separateInstance: bool=False):
        """Get the given filter dialog. If separateInstance=True is given,
        or a parent is provided, a new filter dialog is created.

        The latter is useful for editing searches with the 'searches' dialog,
        which is not really a filter dialog."""
        attr = re.sub(r'-([a-z])',
                      lambda m: m.group(1).upper(), name) + 'Dialog'

        if parent is None:
            parent = self.windowParent()
        else:
            separateInstance = True

        if not separateInstance:
            dialog = getattr(self, attr, None)
            if dialog is not None:
                return dialog

        if name == 'writing-system':
            dialog = SelectWritingSystemDialog(self, parent)
            attr2 = 'writingSystemDialog'

        elif name == 'languages':
            if ENABLE_COMPLEX_FILTERS and QT_VERSION >= 5:
                factory = SelectLangDialog2
            else:
                factory = SelectLangDialog
            dialog = factory(self.langDb, self, parent)
            attr2 = 'languagesDialog'

        elif name == 'tags':
            dialog = SelectTagsDialog(self, parent)
            attr2 = 'tagsDialog'

        elif name == 'categories':
            dialog = SelectCategoriesDialog(self, parent)
            attr2 = 'categoriesDialog'

        elif name == 'class':
            dialog = SelectFeaturesDialog(self, parent)
            attr2 = 'classDialog'

        elif name == 'searches':
            dialog = EditSearchesDialog(self, parent)
            attr2 = 'searchesDialog'

        if separateInstance:
            return dialog

        assert attr == attr2, "%r != %r" % (attr, attr2)

        setattr(self, attr, dialog)
        return dialog

    def toggleFilterDialog(self, name: str, visible: bool=None):
        """Hide, show or toggle the given filter dialog. If a boolean
        passed, it is the new visible state"""

        dockAttr = re.sub(r'-([a-z])',
                          lambda m: m.group(1).upper(), name) + 'Dock'

        widget = getattr(self, dockAttr, None)
        if widget is None:
            widget = self.getFilterDialog(name)

        if visible is None:
            visible = widget.isHidden()

        if visible:
            if widget.isHidden():
                widget.show()
        else:
            if not widget.isHidden():
                widget.close()

    def dockifyFilterDialog(self, name: str, dockWidget: QtWidgets.QDockWidget):
        """Provide notice that we put the filter dialog in the given dock
        widget. The actual docking is something done manually."""
        dockAttr = re.sub(r'-([a-z])',
                          lambda m: m.group(1).upper(), name) + 'Dock'

        oldDock = getattr(self, dockAttr, None)
        if oldDock is not None:
            raise RuntimeError("already dockified: " + name +
                               ":: " + repr(oldDock))
        setattr(self, dockAttr, dockWidget)

    def undockifyFilterDialog(self, name: str):
        """Provide notice that we have removed the filter dialog from the given dock
        widget. The actual undocking is something done manually."""
        dockAttr = re.sub(r'-([a-z])',
                          lambda m: m.group(1).upper(), name) + 'Dock'
        setattr(self, dockAttr, None)

    @Slot(bool)
    def writingSystemsClicked(self, checked=False):
        """Open the writing systems filter dialog."""
        self.toggleFilterDialog('writing-system')

    @Slot(bool)
    def languagesClicked(self, checked=False):
        """Open the languages filter dialog."""
        self.toggleFilterDialog('languages')

    @Slot(bool)
    def tagsClicked(self, checked=False):
        """Open the tags filter dialog."""
        self.toggleFilterDialog('tags')

    @Slot(bool)
    def categoriesClicked(self, checked=False):
        """Open the categories filter dialog."""
        self.toggleFilterDialog('categories')

    @Slot(bool)
    def classClicked(self, checked=False):
        """Open the family, features and class filter dialog."""
        self.toggleFilterDialog('class')

    @Slot(int)
    def outlineStateChanged(self, state):
        """The outline checkbox changed. So, online or scalable is the one
        we want to show?"""
        if state == Qt.PartiallyChecked:
            self.filterOutline = None
        else:
            self.filterOutline = state == Qt.Checked
        self.filterCompleteWidgetEdit()

    def filterAcceptsFontItem(self, item: fontlist.FontLike) -> bool:
        """Return if we accept the font item."""
        if self.filterContainsChars:
            require = all if self.filterContainsAll else any
            font = self.fontDb().font(item.family, item.style, 16)

            if hasattr(QtGui, 'QRawFont') and False:
                supportsChar = QtGui.QRawFont.fromFont(font).supportsCharacter
                if not require(supportsChar(c)
                               for c in self.filterContainsChars):
                    return False

            elif item.charset:
                charRange = item.charset
                if not require((c in charRange)
                                for c in self.filterContainsChars):
                    return False

            else:
                charRange = item.get_charset()
                if charRange is not None:
                    if not require((c in charRange)
                                   for c in self.filterContainsChars):
                        return False

                ##fontInfoExtended = item.extended()
                ##if fontInfoExtended is not None and fontInfoExtended.cmap:
                ##    fontCmap = fontInfoExtended.cmap
                ##    if not require((c in fontCmap)
                ##                   for c in self.filterContainsChars):
                ##        return False

        if item.is_family and self.filterText not in item.family.casefold():
            return False

        styles = item.styles if item.is_family else [item]

        if self.filterOutline is not None:
            if not any(self.filterOutline == bool(style.outline)
                       for style in styles):
                return False

        if self.filterScalable is not None:
            if not any(self.filterScalable == bool(style.scalable)
                       for style in styles):
                return False

        if self.filterWritingSystems and item.is_family:
            for ws, state in self.filterWritingSystems.items():
                if state:
                    if ws not in item.writingSystems:
                        return False
                else:
                    if ws in item.writingSystems:
                        return False

        if self.filterLanguages:
            for lang, state in self.filterLanguages.items():
                if state:
                    if not any(lang in style.lang for style in styles):
                        return False

                else:
                    if all(lang in style.lang for style in styles):
                        return False

        if self.filterMonospace is not None:
            if not any(bool(style.monospace) == bool(self.filterMonospace)
                       for style in styles):
                return False

        if self.filterGenericFamily:
            if not any(style.genericfamily in self.filterGenericFamily
                       for style in styles):
                return False

        if self.filterFontFormat:
            if not any(style.fontformat in self.filterFontFormat
                       for style in styles):
                return False

        if self.filterIbmClass:
            if not any(style.ibmclass and
                       style.ibmclass.class_id in self.filterIbmClass
                       for style in styles):
                return False

            if (len(self.filterIbmClass) == 1 and
                self.filterIbmSubclass and
                not any(style.ibmclass.subclass_id in self.filterIbmSubclass
                        for style in styles)):
                    return False

        if self.filterPanoseClass:
            if not any(style.panoseclass and
                       style.panoseclass.class_id
                                in self.filterPanoseClass
                       for style in styles):
                return False

            if (len(self.filterPanoseClass) == 1 and
                self.filterPanoseSubclass and
                not any(style.panoseclass.subclass_id
                                in self.filterPanoseSubclass
                        for style in styles)):
                    return False

            if (len(self.filterPanoseClass) == 1 and
                self.filterPanoseProperties and
                not any(all(style.panoseclass[pos].value == value
                            for pos, value
                                in self.filterPanoseProperties.items())
                        for style in styles)):
                    return False

        return True


@filtering.register('writingsystem')
class WritingSystemFilter(filtering.FontFilter):

    """Writing system filter. The ws is required if the value is True,
    or forbidden if the value is False."""

    key_attrname = 'writingSystem'

    def __init__(self, writingSystem: Union[int, str], value: bool=True):
        if isinstance(writingSystem, str):
            writingSystem = qfontlist.stringToWritingSystem(writingSystem)
        self.writingSystem = writingSystem
        self.value = bool(value)

    @property
    def prio(self) -> int:
        if self.writingSystem == QtGui.QFontDatabase.Latin:
            return (filtering.PRIO_MINOR_CUTOFF
                        if self.value
                            else filtering.PRIO_TOTAL_CUTOFF)
        return (filtering.PRIO_MAJOR_CUTOFF
                    if self.value
                        else filtering.PRIO_MINOR_CUTOFF)

    def label(self, styled: bool=False) -> str:
        label = QtGui.QFontDatabase.writingSystemName(self.writingSystem)
        if not styled:
            return ('+' if self.value else '-') + label
        return label

    def style(self) -> Set:
        return set() if self.value else set([STRIKE])

    def icon(self) -> Optional[str]:
        return None

    def accept(self, item: fontlist.FontLike) -> bool:
        ws = self.writingSystem
        if self.value:
            ## Currently, the code sets the family and styles to the same
            ## writing systems.
            #return any(ws in style.writingSystems for style in item.styles)
            return ws in item.writingSystems
        else:
            #return not all(ws in style.writingSystems for style in item.styles)
            return ws not in item.writingSystems

    def _identity(self) -> object:
        return ('writingsystem', self.writingSystem, self.value)

    def generate_key(self) -> str:
        return QtGui.QFontDatabase.writingSystemName(self.writingSystem)

    def factory_arguments(self) -> TupleOf[tuple, Mapping]:
        return (qfontlist.writingSystemToString(self.writingSystem),
                self.value), {}


@filtering.register('writingsystems')
class WritingSystemsFilterGroup(filtering.FilterConjunctiveGroup,
                                filtering.FontFilter):

    """A filter with a conjuctive group of writing systems."""

    child_cls = WritingSystemFilter

    def label(self, styled: bool=False) -> str:
        return _("Writing systems")

    def icon(self) -> Optional[str]:
        return 'select-writing-system'

    def todict(self, *args, **kwargs) -> Mapping:
        result = super().todict(*args, **kwargs)
        if 'values' in result:
            result['values'] = [(qfontlist.writingSystemToString(key), value)
                                for key, value in result['values']]
        return result

    def restoredict(self, data: Mapping, *args, **kwargs):
        data = dict(data)
        if 'values' in data:
            data['values'] = [(qfontlist.stringToWritingSystem(key), value)
                              for key, value in data['values']]
        return super().restoredict(data, *args, **kwargs)


class AdvancedFontFilterModelFilters(FontFilterModelFilters):

    """A complex implementation of FontFilterModelFilters, which uses
    the fitlering module.

    The active filters, together with a list of actions to add
    to the main toolbar for filtering (implementing the Toolbox interface
    for that)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filterGroup = filtering.FilterConjunctiveGroup()
        self.filterMapping = self.filters = self.filterGroup.filter_mapping()
        self.filterGroup.branch_changed.connect(self._filterGroupChanged)

        self._disableGroupChanges = False
        self._noisyItemConnector = None

    def noisyItemConnector(self) -> filtering.NoisyGroupItemConnector:
        """Return a connector that listens for changes in a fitler tree, and
        allows you to connect to the items in a specific part of the subtree.
        """
        if self._noisyItemConnector is None:
            self._noisyItemConnector = filtering.NoisyGroupItemConnector(
                    self.filterGroup, self.featureSets())
        return self._noisyItemConnector

    def _filterGroupChanged(self, branchChange: filtering.BranchChange=None):
        """There was a change in a filter branch. Update checkboxes."""
        recursion = False
        if self._disableGroupChanges:
            try:
                allowRecursion = branchChange.__allowRecursion
            except AttributeError:
                allowRecursion = False

            if not allowRecursion:
                errmsg("Recursed back to _filterGroupChanged!!", branchChange)
                return

            recursion = True

        debugmsg(branchChange)

        if not recursion:
            self._disableGroupChanges = True
        try:
            key = branchChange.key_tuple()

            fired = False

            # WARNING: First do the *deeper* level, then the outer
            # level, so that the child knows that the children have
            # been handled
            handler = self._changedMap.get(key[1:3])
            if handler is not None:
                fired = True
                handler(branchChange)

            handler = self._changedMap.get(key[1:2])
            if handler is not None:
                fired = True
                handler(branchChange)

            if len(key) == 2 and key[1] in filtering.name_filter_keys:
                fired = True
                self._recomputeExtraFilterText()

            if not fired:
                warnmsg("No handler for", branchChange)

        finally:
            if not recursion:
                self._disableGroupChanges = False

        #try:
        #    print(json.dumps(self.filterGroup.todict(), indent=True, ensure_ascii=False))
        #except:
        #    traceback.print_exc()

        self.filterChanged.emit()

    def _callCallbacksForChildren(self, branchChange: filtering.BranchChange,
                                        depth: int=None,
                                        allowed=[filtering.ADDED, filtering.REMOVED,
                                                 filtering.REPLACED]):
        """Also call the callbacks for the children of the branch."""

        if branchChange.leaf().action not in allowed:
            return

        if depth is not None:
            if len(branchChange.key_tuple()) != depth - 1:
                return

        for change in branchChange.find_lower_descendants():
            change.__allowRecursion = True
            self._filterGroupChanged(change)

    def filterCompleteWidgetEdit(self):
        # Do nothing. The filtering module emits the needed singal.
        pass

    def filterAcceptsFontItem(self, item: fontlist.FontLike) -> bool:
        return bool(self.filterGroup.accept(item))

    filterLanguages = filtering.standard_property('languages')
    filterWritingSystems = filtering.standard_property('writingsystems')
    filterFontFormat = filtering.standard_property(
                                'fontformats',
                                accept_when_empty=True)
    filterGenericFamily = filtering.standard_property(
                                'genericfamilies',
                                accept_when_empty=True)

    def _selectedPanoseFamily(self) -> int:
        """Return the current panose family."""
        families = self.filterPanoseClass
        if families and len(families) == 1:
            for family in families:
                return family
        return opentype.PANOSE_UNCLASSIFIED

    filterPanoseClass = filtering.standard_property(
                                'panosefamilies',
                                accept_when_empty=True)
    filterPanoseSubclass = filtering.standard_property(
                                'panose-subfamilies',
                                accept_when_empty=True,
                                method_kwargs=dict(
                                    family=_selectedPanoseFamily))
    filterPanoseProperties = filtering.standard_property(
                                'panose-properties',
                                method_kwargs=dict(
                                    family=_selectedPanoseFamily))
    filterIbmClass = filtering.standard_property(
                                'ibmclasses',
                                accept_when_empty=True)
    filterIbmSubclass = filtering.standard_property(
                                'ibmsubclasses',
                                accept_when_empty=True)

    filterText = filtering.standard_property('names.family')
    filterFileName = filtering.standard_property('names.filename')
    filterFilePath = filtering.standard_property('names.filepath')

    filterRequireFileName = filtering.standard_property('filename')
    filterRequireFilePath = filtering.standard_property('filepath')

    filterScalable = filtering.standard_property('scalable')
    filterOutline = filtering.standard_property('outline')

    filterMonospace = filtering.standard_property('monospace')

    filterContainsChars = filtering.standard_property('charset')
    filterContainsAll = filtering.standard_property('charset',
                                                    'contains_all')

    def _applyExtraFilters(self):
        """Apply any filters for the file path or filename defined in the
        the text of the filter box."""
        extraFilters = self.searchBarExtraFilters
        filters = self.filterMapping

        for key in filtering.name_filter_keys:
            if key in extraFilters:
                value = extraFilters[key]
                nameFilter = filters.get(key)
                if nameFilter is not None:
                    if nameFilter.name == value:
                        continue
                filters.standard_filter(key, value)

            elif key in filters:
                del filters[key]

    def _recomputeExtraFilterText(self):
        """Fix the text for the extra filters when the filters are changed from
        filtering's side."""

        extraFilters = self.searchBarExtraFilters

        filters = self.filterMapping
        realExtraFilters = {key: filters[key].name
                            for key in filtering.name_filter_keys
                            if key in filters}

        if realExtraFilters != extraFilters:
            text = filtering.unsplit_filter_text(self.searchBarFilterText,
                                                 realExtraFilters)
            self.textWidget.setText(text)

    _changedMap = MethodDispatchMap()

    @_changedMap.add(('languages',))
    def _handleLanguagesChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("Languages changed", branchChange)
        key = branchChange.key_tuple()
        if len(key) < 3:
            self._callCallbacksForChildren(branchChange, 3)
            return
        lang = branchChange.leading_filter().language
        dialog = getattr(self, 'languagesDialog', None)
        if dialog is None or not hasattr(dialog, 'langCheckbox'):
            return

        checkbox = dialog.langCheckbox.get(lang)
        if checkbox is None:
            warnmsgf(U_("No checkbox for language %s"), lang)
            return

        currentState = checkbox.checkState()
        expectedState = boolToCheckState.get(self.filterLanguages.get(lang))
        if expectedState is None:
            return
        if currentState != expectedState:
            checkbox.setCheckState(expectedState)

    @_changedMap.add(('writingsystems',))
    def _handleWritingSystemsChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("Writing systems changed", branchChange)
        key = branchChange.key_tuple()
        if len(key) < 3:
            self._callCallbacksForChildren(branchChange, 3)
            return
        ws = branchChange.leading_filter().writingSystem
        dialog = getattr(self, 'writingSystemDialog', None)
        if dialog is None:
            return

        checkbox = dialog.writingSystemCheckbox.get(ws)
        if checkbox is None:
            warnmsgf(U_("No checkbox for writing system %s"), ws)
            return

        currentState = checkbox.checkState()

        filterWritingSystems = self.filterWritingSystems
        if filterWritingSystems is None:
            warnmsgf("BUG: filterWritingSystems is None?")
            return

        expectedState = boolToCheckState.get(filterWritingSystems.get(ws))
        if expectedState is None:
            return
        if currentState != expectedState:
            checkbox.setCheckState(expectedState)

    @_changedMap.add(('fontformats',))
    def _handleFontFormatsChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("Font formats changed", branchChange)
        key = branchChange.key_tuple()
        if len(key) < 3:
            self._callCallbacksForChildren(branchChange, 3)
            return
        formatName = branchChange.leading_filter().value
        dialog = getattr(self, 'classDialog', None)
        if dialog is None:
            return

        checkbox = dialog.checkboxByFontFormat.get(formatName)
        if checkbox is None:
            warnmsgf(U_("No checkbox for format %s"), formatName)
            return

        currentState = bool(checkbox.isChecked())
        expectedState = formatName in (self.filterFontFormat or EMPTY_SET)
        if currentState != expectedState:
            checkbox.setChecked(expectedState)

    @_changedMap.add(('genericfamilies',))
    def _handleGenericFamiliesChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("Generic families changed", branchChange)
        key = branchChange.key_tuple()
        if len(key) < 3:
            self._callCallbacksForChildren(branchChange, 3)
            return
        genericFamily = branchChange.leading_filter().value
        dialog = getattr(self, 'classDialog', None)
        if dialog is None:
            return

        checkbox = dialog.checkboxByGenericFamily.get(genericFamily)
        if checkbox is None:
            warnmsgf(U_("No checkbox for generic family %s"), genericFamily)
            return

        currentState = bool(checkbox.isChecked())
        expectedState = genericFamily in (self.filterGenericFamily or EMPTY_SET)
        if currentState != expectedState:
            checkbox.setChecked(expectedState)

    @_changedMap.add(('panosefamilies',))
    def _handlePanoseFamiliesChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("PANOSE families changed", branchChange)
        key = branchChange.key_tuple()
        if len(key) < 3:
            self._callCallbacksForChildren(branchChange, 3)
            return
        family = branchChange.leading_filter().family
        dialog = getattr(self, 'classDialog', None)
        if dialog is None:
            return

        checkbox = dialog.checkboxByPanoseClass.get(family)
        if checkbox is None:
            warnmsgf(U_("No checkbox for PANOSE family %s"), family)
            return

        currentState = bool(checkbox.isChecked())
        expectedState = family in (self.filterPanoseClass or EMPTY_SET)
        if currentState != expectedState:
            checkbox.setChecked(expectedState)

    @_changedMap.add(('panose-subfamilies',))
    def _handlePanoseSubfamiliesChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("PANOSE subfamilies changed", branchChange)

        key = branchChange.key_tuple()
        if len(key) < 3:
            self._callCallbacksForChildren(branchChange, 3)
            return

        filter = branchChange.leading_filter()
        family = filter.family
        subfamily = filter.value

        if family == opentype.PANOSE_UNCLASSIFIED:
            return

        dialog = getattr(self, 'classDialog', None)
        if dialog is None:
            return

        checkbox = dialog.checkboxByPanoseSubclass.get((family, subfamily))
        if checkbox is None:
            warnmsgf(U_("No checkbox for PANOSE subclass %s:%s"),
                     family, subfamily)
            return

        currentState = bool(checkbox.isChecked())
        expectedState = subfamily in (self.filterPanoseSubclass or EMPTY_SET)
        if currentState != expectedState:
            checkbox.setChecked(expectedState)

    @_changedMap.add(('panose-properties',))
    def _handlePanosePropertiesChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("PANOSE properties changed", branchChange)

        key = branchChange.key_tuple()
        if len(key) < 3:
            self._callCallbacksForChildren(branchChange, 3)
            return

        filter = branchChange.leading_filter()
        family = filter.family
        pos = filter.pos
        if branchChange.leaf().action == filtering.REMOVED:
            value = None
        else:
            value = filter.value

        if family == opentype.PANOSE_UNCLASSIFIED:
            return

        assert value == self.filterPanoseProperties.get(pos), \
                [value, self.filterPanoseProperties.get(pos)]

        dialog = getattr(self, 'classDialog', None)
        if dialog is None:
            return

        combo = dialog.comboByPanoseProperty.get((family, pos))
        if combo is None:
            warnmsgf(U_("No combobox for PANOSE property %s:%s"),
                     family, pos)
            return

        if combo.itemData(combo.currentIndex()) != value:
            self.filterPanoseProperties
            choiceKey = family, pos, value
            j = dialog.comboIdxByPanosePropChoice.get(choiceKey)

            if j is None:
                warnmsgf(U_("No combobox for choice PANOSE property value "
                            "%s:%s"), family, pos, value)
                return

            combo.setCurrentIndex(j)

    @_changedMap.add(('ibmclasses',))
    def _handleIbmClassesChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("IBM classes changed", branchChange)
        key = branchChange.key_tuple()
        if len(key) < 3:
            self._callCallbacksForChildren(branchChange, 3)
            return
        class_id = branchChange.leading_filter().value
        dialog = getattr(self, 'classDialog', None)
        if dialog is None:
            return

        checkbox = dialog.checkboxByIbmClass.get(class_id)
        if checkbox is None:
            warnmsgf(U_("No checkbox for IBM class %s"), class_id)
            return

        currentState = bool(checkbox.isChecked())
        expectedState = class_id in (self.filterIbmClass or EMPTY_SET)
        if currentState != expectedState:
            checkbox.setChecked(expectedState)

    @_changedMap.add(('ibmsubclasses',))
    def _handleIbmSubclassesChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("IBM subclasses changed", branchChange)

        key = branchChange.key_tuple()
        if len(key) < 3:
            self._callCallbacksForChildren(branchChange, 3)
            return

        if not self.filterIbmClass or len(self.filterIbmClass) != 1:
            return

        class_id = next(iter(self.filterIbmClass))
        subclass_id = branchChange.leading_filter().value

        if class_id == opentype.IBM_UNCLASSIFIED:
            return

        dialog = getattr(self, 'classDialog', None)
        if dialog is None:
            return

        checkbox = dialog.checkboxByIbmSubclass.get((class_id, subclass_id))
        if checkbox is None:
            warnmsgf(U_("No checkbox for IBM subclass %s:%s"),
                     class_id, subclass_id)
            return

        currentState = bool(checkbox.isChecked())
        expectedState = subclass_id in (self.filterIbmSubclass or EMPTY_SET)
        if currentState != expectedState:
            checkbox.setChecked(expectedState)

    @_changedMap.add(('names',))
    def _handleNamesChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("Name changed", branchChange)

        if len(branchChange.key_tuple()) < 3:
            self._callCallbacksForChildren(branchChange, 3)
            return

        # FIXME: .strip().casefold() can be removed if when I stop changing
        # the details here
        #currentText = (self.textWidget.text() or '').strip().casefold()
        currentText = self.searchBarFilterText
        filterText = (self.filterText or '').strip().casefold()

        # We execute this after we've changed the currentText successfully
        if filterText != currentText:
            return

        # Only setting here, no unsetting
        if not currentText:
            return

        filterFileName = (self.filterFileName or '').strip().casefold()
        filterFilePath = (self.filterFilePath or '').strip().casefold()

        if filterFileName == currentText:
            checkbox = self.actionByKey['setSearchFileName']
            if not checkbox.isChecked():
                checkbox.setChecked(True)

        if filterFilePath == currentText:
            checkbox = self.actionByKey['setSearchFilePath']
            if not checkbox.isChecked():
                checkbox.setChecked(True)

    @_changedMap.add(('names', 'family'))
    def _handleFamilyNameChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("Family name changed", branchChange)

        # FIXME: .strip().casefold() can be removed if when I stop changing
        # the details here
        #currentText = (self.textWidget.text() or '').strip().casefold()
        currentText = self.searchBarFilterText
        filterText = (self.filterText or '').strip().casefold()

        if filterText != currentText:
            if ENABLE_COMPLEX_FILTERS:
                #extraFilters = self.searchBarExtraFilters
                filters = self.filterMapping
                realExtraFilters = {key: filters[key].name
                                    for key in filtering.name_filter_keys
                                    if key in filters}

                filterText = filtering.unsplit_filter_text(filterText,
                                                           realExtraFilters)

            self.textWidget.setText(filterText)

    @_changedMap.add(('names', 'filename'))
    def _handleFileNameChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("File name changed", branchChange)

        #currentText = (self.textWidget.text() or '').strip().casefold()
        currentText = self.searchBarFilterText
        filterFileName = (self.filterFileName or '').strip().casefold()

        # Only unsetting here
        if not filterFileName and currentText:
            checkbox = self.actionByKey['setSearchFileName']
            if checkbox.isChecked():
                checkbox.setChecked(False)

    @_changedMap.add(('names', 'filepath'))
    def _handleFilePathChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("File path changed", branchChange)

        #currentText = (self.textWidget.text() or '').strip().casefold()
        currentText = self.searchBarFilterText
        filterFilePath = (self.filterFilePath or '').strip().casefold()

        # Only unsetting here
        if not filterFilePath and currentText:
            checkbox = self.actionByKey['setSearchFilePath']
            if checkbox.isChecked():
                checkbox.setChecked(False)

    @_changedMap.add(('scalable',))
    def _handleScalableChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("Scalable changed", branchChange)
        pass

    @_changedMap.add(('outline',))
    def _handleOutlineChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("Outline changed", branchChange)
        pass

    @_changedMap.add(('monospace',))
    def _handleMonospaceChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("Monospace changed", branchChange)

        dialog = getattr(self, 'classDialog', None)
        if dialog is None:
            return
        checkbox = dialog.monospaceCheckbox
        currentState = checkbox.checkState()
        expectedState = boolToCheckState.get(self.filterMonospace)
        if expectedState is None:
            return
        if currentState != expectedState:
            checkbox.setCheckState(expectedState)

    @_changedMap.add(('charset',))
    def _handleCharsetChanged(self, branchChange: filtering.BranchChange=None):
        #debugmsg("Charset changed", branchChange)
        pass


class FontFilterModel(QtModelProxies.QSortFilterProxyModel):

    """A font filter model that uses the filterAcceptsFontItem method
    of a FontFilterModelFilters to filter fonts."""

    def __init__(self, filterInstance: FontFilterModelFilters=None,
                       langDb: 'typeatlas.langutil.LanguageDatabase'=None,
                       parent: QtCore.QObject=None,
                       options: Options=None,
                       histories: datastore.Histories=None):
        super().__init__(parent)
        self.langDb = langDb
        if filterInstance is None:
            if ENABLE_COMPLEX_FILTERS:
                factory = AdvancedFontFilterModelFilters
            else:
                factory = FontFilterModelFilters
            filterInstance = factory(langDb=langDb, filterModel=self,
                                     parent=self, options=options,
                                     histories=histories)
        self.filter = filterInstance

        filterInstance.filterChanged.connect(self.filterChanged)

    @Slot()
    def filterChanged(self):
        """We changed the filter. Invalidate it."""
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):

        #if source_parent.isValid():
        #    container = source_parent.data(FontItemRole).styles
        #else:
        #    container = self.sourceModel().families
        #item = container[source_row]

        source_index = self.sourceModel().index(source_row, 0, source_parent)
        item = source_index.data(FontItemRole)
        return self.filter.filterAcceptsFontItem(item)


class _FilterItem(object):

    """Filter item in the FilterListModel."""

    inserting = False
    removing = False
    depth = 0

    def __init__(self, filter: filtering.Filter,
                       parent: 'Optional[_FilterItem]',
                       row: Optional[int]):
        self.filter = filter
        self.parent = parent
        if filter.is_group:
            self.children = filter.filter_sequence()
        else:
            self.children = None
        self.lastRow = row
        if parent is not None:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "%s(%r, %r, %r)" % (type(self).__name__,
                                   self.filter, self.parent,
                                   self.lastRow)

    def getRow(self) -> Optional[int]:
        """Get the row of the item. This automatically recomputes if the
        item has been moved."""
        row = self.lastRow

        if self.parent is None:
            return 0

        # Check that the row is still correct and didn't change
        siblings = self.parent.children
        if not siblings:
            return None

        if row < len(siblings) and siblings[row] is self.filter:
            return row

        try:
            row = siblings.index(self.filter)
        except ValueError:
            return None
        else:
            self.lastRow = row
            return row

    def getFullKey(self) -> str:
        """Get a key used to serialize filters partially."""

        # For us, the root item has no key, since it is where we restore at
        if self.parent is None:
            return None

        key = self.filter.get_key()
        parentKey = self.parent.getFullKey()
        if parentKey is None:
            return key

        return "%s.%s" % (parentKey, key)

    def connectSignals(self, filterList: 'FilterListModel'):
        """Connect all signals of this filter's children with
        the filter list."""
        self._toggleSignals(filterList, True)

    def disconnectSignals(self, filterList: 'FilterListModel'):
        """Disconnect all signals of this filter's children with
        the filter list."""
        self._toggleSignals(filterList, False)

    def _toggleSignals(self, filterList: 'FilterListModel',
                             doConnect: bool=True):
        """Connect/disconnect all signals of this filter's children with
        the filter list."""

        children = self.children
        if children is None:
            return

        links = [
            (children.insert_pending, filterList._insertPending),
            (children.remove_pending, filterList._removePending),

            (children.inserted, filterList._insertCompleted),
            (children.removed, filterList._removeCompleted),
        ]

        for signal, slot in links:
            if doConnect:
                signal.connect(slot, pass_self=True)
            else:
                signal.disconnect(slot, pass_self=True)


class FilterListModel(QtCore.QAbstractItemModel):

    """A model of active filters, allowing you to delete them or
    remove them."""

    def __init__(self, filterRoot: filtering.FilterGroup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filterRoot = filterRoot
        self._itemByFilter = {}
        self.rootItem = self._makeFilterItem(self.filterRoot, None, None)

    childrenChanged = Signal(QtCore.QModelIndex, object)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self.rootItem

        if not parentItem.filter.is_group:
            return QtCore.QModelIndex()

        try:
            filter = parentItem.children[row]
        except IndexError:
            return QtCore.QModelIndex()
        else:
            result = self.createIndex(row, column,
                                      self._makeFilterItem(filter,
                                                           parentItem, row))
            return result

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        item = index.internalPointer()
        if item.parent is None or item.parent is self.rootItem:
            return QtCore.QModelIndex()

        result = self.createIndex(item.parent.getRow(), 0, item.parent)
        return result

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return _('Filter description')

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None

        item = index.internalPointer()
        filter = item.filter

        if role == Qt.DisplayRole:
            return filter.label(styled=True)

        elif role == Qt.DecorationRole:
            icon = filter.icon()
            if icon is not None:
                return getIcon(icon)

        elif role == Qt.FontRole:
            style = filter.style()
            if style:
                font = QtGui.QFont()
                if STRIKE in style:
                    font.setStrikeOut(True)
                return font

        elif role == FilterItemRole:
            return item

        elif role == FilterRole:
            return item.filter

        return None

    def hasChildren(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return True
        return parent.internalPointer().filter.is_group

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            # FIXME: If this returns 0, all children disappear. WHY?
            # Documentation says it *must* return 0.
            return 1
        return 1

    def rowCount(self, parent=QtCore.QModelIndex()):

        if parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self.rootItem

        if not parentItem.filter.is_group:
            return 0

        return len(parentItem.filter.filters)

    def _makeFilterItem(self, filter: filtering.Filter,
                              parent: Optional[_FilterItem],
                              row: Optional[int]) -> _FilterItem:
        """Create a model item for this filter."""
        oldItem = self._findFilterItem(filter)
        if oldItem is not None:
            if oldItem.parent is parent:
                oldItem.lastRow = row
                return oldItem

        self._itemByFilter[id(filter)] = item = _FilterItem(filter, parent, row)

        if oldItem is None:
            item.connectSignals(self)

        return item

    def _findFilterItem(self, filter: filtering.Filter) -> Optional[_FilterItem]:
        """Locate the item for this filter."""
        item = self._itemByFilter.get(id(filter))
        if item is not None and item.filter is not filter:
            del self._itemByFilter[id(filter)]
            return None
        return item

    def _insertRemoveAction(self, siblings: filtering.FilterSequence,
                                  row: int, filter: filtering.Filter,
                                  insert: bool=True, completed: bool=False):

        """Modify the model as filters were inserted or removed."""

        if completed:
            debugmsg('---', 'insert' if insert else 'remove', row, filter)

        parentItem = self._findFilterItem(siblings.group)
        if parentItem is None:
            return

        if insert:
            method = 'InsertRows'
            actionAttr = 'inserting'
        else:
            method = 'RemoveRows'
            actionAttr = 'removing'

        if parentItem is self.rootItem:
            parentIndex = QtCore.QModelIndex()
        else:
            parentIndex = self.createIndex(parentItem.getRow(), 0, parentItem)

        if not completed:
            ##return self.beginResetModel()
            setattr(parentItem, actionAttr, True)
            getattr(self, 'begin' + method)(parentIndex, row, row)

        else:
            ##return self.endResetModel()
            if not getattr(parentItem, actionAttr):
                return
            setattr(parentItem, actionAttr, False)
            getattr(self, 'end' + method)()

        if not insert:
            self._itemByFilter.pop(id(filter), None)

        if completed:
            self.childrenChanged.emit(parentIndex, parentItem)
            if filter.is_group:
                index = self.index(row, 0, parentIndex)
                self.childrenChanged.emit(index, index.internalPointer())

    def _insertPending(self, *args, **kwargs):
        self._insertRemoveAction(*args, insert=True, completed=False, **kwargs)

    def _insertCompleted(self, *args, **kwargs):
        self._insertRemoveAction(*args, insert=True, completed=True, **kwargs)

    def _removePending(self, *args, **kwargs):
        self._insertRemoveAction(*args, insert=False, completed=False, **kwargs)

    def _removeCompleted(self, *args, **kwargs):
        self._insertRemoveAction(*args, insert=False, completed=True, **kwargs)


class FilterListToolbox(Toolbox):

    """A filter list actions."""

    def __init__(self, view: QtWidgets.QAbstractItemView):
        self.view = view
        super(FilterListToolbox, self).__init__()

        selModel = self.view.selectionModel()

        #selModel.currentChanged.connect(self._currentChanged)
        #self._currentChanged(selModel.currentIndex())
        selModel.selectionChanged.connect(self._selectionChanged)
        self._selectionChanged(selModel.selection(),
                               QtModelProxies.QItemSelection())

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.dataChanged.connect(self._clipboardChanged)
        self._clipboardChanged()

    def actionDefinitions(self) -> Iterator:

        yield self.action(self.copyAll, _('Copy all'),  icon='edit-copy',
                          shortcut='Ctrl+C')
        yield self.action(self.paste, _('Paste'), icon='edit-paste',
                          shortcut='Ctrl+V', key='paste')
        yield self.separator()
        with self.group('selected'):
            yield self.action(self.copySelected, _('Copy selected'),
                              shortcut='Ctrl+Shift+C')
            yield self.action(self.removeSelected, _('Remove'), icon='list-remove',
                              shortcut='Del')
        yield self.separator()
        yield self.action(self.clear, _('Clear'), icon='edit-clear')

    @Slot()
    def copyAll(self):
        """Copy all the filters to clipboard."""
        model = self.view.model()

        text = json.dumps(model.filterRoot.todict(),
                          indent=True, ensure_ascii=False)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)

    @Slot()
    def copySelected(self):
        """Copy the selected filters to clipboard."""
        selected = self.view.selectionModel().selectedIndexes()
        if not selected:
            return

        model = selected[0].model()

        keys = []

        for index in selected:
            filterItem = index.data(FilterItemRole)
            if filterItem is None or filterItem.parent is None:
                continue
            if not filterItem.parent.filter.is_group:
                continue
            key = filterItem.getFullKey()
            if key is None:
                continue
            keys.append(key)

        text = json.dumps(model.filterRoot.todict(keys),
                          indent=True, ensure_ascii=False)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)

    @Slot()
    def removeSelected(self):
        """Remove the selected filters to clipboard."""
        selected = self.view.selectionModel().selectedIndexes()
        if not selected:
            return

        model = selected[0].model()

        removeList = []

        for index in selected:
            filterItem = index.data(FilterItemRole)
            if filterItem is None or filterItem.parent is None:
                continue
            if not filterItem.parent.filter.is_group:
                continue
            removeList.append((filterItem.parent.filter, filterItem.filter))

        for parent, filter in removeList:
            try:
                parent.remove(filter)
            except KeyError:
                pass

    @Slot()
    def clear(self):
        """Clear the filters, removing all of them."""
        self.view.model().filterRoot.clear()

    @Slot()
    def paste(self):
        """Paste filters from clipboard."""
        model = self.view.model()

        clipboard = QtWidgets.QApplication.clipboard()
        text = clipboard.text()

        model.filterRoot.restoredict(json.loads(text))

    #@Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    #def _currentChanged(self, current, previous):
    #    pass

    @Slot(QtModelProxies.QItemSelection, QtModelProxies.QItemSelection)
    def _selectionChanged(self, selected, deselected):
        """Activate and reactive actions on selection, depedning if we
        have such selection."""
        selModel = self.view.selectionModel()
        current = selModel.currentIndex()
        # The signal only gives us the newly selected
        selected = selModel.selection()
        if selected.indexes():
            self.enableActions(group='selected')
        else:
            self.disableActions(group='selected')

    @Slot()
    def _clipboardChanged(self):
        """Activate and reactive paste action, depedning if we have clipboard."""
        clipboard = QtWidgets.QApplication.clipboard()
        if clipboard.mimeData().hasText():
            self.enableActions(action='paste')
        else:
            self.disableActions(action='paste')
