# -*- coding: utf-8 -*-
#
#    TypeAtlas GUI
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

import os.path
import re
import sys
import urllib.parse
import textwrap
import time
import datetime
import binascii
from typeatlas.compat import QtCore, QtGui, QtWidgets, QtModelProxies
from typeatlas.compat import Qt, Slot, Signal, setResizeMode
from typeatlas.compat import configuredStyle, qtGetBytes
from typeatlas import compat, proginfo
from typeatlas import fontlist, fontgrid, qfontlist, opentype
from typeatlas import blockmath, external
from typeatlas.fontmodels import FontDelegate, FontFilterModel, FontItemRole
from typeatlas.fontmodels import FontListModel, SampleTextRole
from typeatlas.fontmodels import FontFileIconProvider
from typeatlas.fontmodels import FilterListModel, FilterListToolbox
from typeatlas.fontmodels import ENABLE_COMPLEX_FILTERS
from typeatlas.fontmodels import ItemValuesDialogBase
from typeatlas.fontduel import FontDuel, FontInfoTable
from typeatlas.fontsampler import FontSampler
from typeatlas.foreign.flowlayout import FlowLayout, HorizontalFlowLayout
from typeatlas.foreign.flowlayout import FlowLayoutSizePolicy
from typeatlas.langutil import langorder, filter_samples
from typeatlas.langutil import install_locales
from typeatlas.samples import load_samples, load_glass, load_nonfree
from typeatlas.samples import SampleInfo
from typeatlas.langutil import LanguageDatabase, NATIVE_NAME, LOCALE_NAME
from typeatlas.langutil import AUTO_LOCALE_NAME
from typeatlas.charinfo import CharacterDatabase
from typeatlas.about import AboutDialogs
from typeatlas.uitools import modelIterate, modelIterateChildrenRect, Toolbox
from typeatlas.uitools import getIcon, getImage, getIconHtml, qFontToCss
from typeatlas.uitools import QtExecutor, Downloader, DragDropLabel
from typeatlas.uitools import generalWidth, generalHeight
from typeatlas.uitools import setDefaultFontFamilies
from typeatlas.uitools import layoutIterate, matchingInverseColor
from typeatlas.uitools import ItemItemRole
from typeatlas.guicommon import FontRenderingChoice, FontInfoWidget
from typeatlas.guicommon import CustomComboBox, GroupNameDialog
from typeatlas.guicommon import RemoveFromGroupDialog
from typeatlas import guicommon
from typeatlas.osinfo import StorageLocations
from typeatlas.options import Options, OptionsWidget
from typeatlas.datastore import Categorization, MetadataCache
from typeatlas import datastore, filtering, uitools, fontmodels
from itertools import chain, zip_longest, count
from functools import partial
from collections import OrderedDict, defaultdict, namedtuple
from collections.abc import Sequence, Mapping, Iterator, Callable
from typeatlas.util import OrderedSet, debugmsg, errmsg, generic_type

from typeatlas.langutil import _, N_, H_, textlang
from html import escape as htesc

try:
    import psutil
except ImportError:
    psutil = None


IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')
SequenceOf = generic_type('Sequence')
SetOf = generic_type('Set')
Union = generic_type('Union')
Optional = generic_type('Optional')


MISSING_CHARSET_THRESHOLD = 0.90
DEFAULT_FONTLIST_PROPORTION = 0.40

TYPEATLAS_WINDOW_STATE_VERSION = 1

_menu_item_nums = count()


CustomSample = namedtuple('CustomSample', 'lang text')


class DockInfo(object):

    """Information about an open dock, which deals with restoring
    the state of the docks, such as proportions after resize and 
    per-widget state.
    
    Holds the name and the widgets, remembers the proportion, etc.

    If the dock is None, it means that the dock is not docked, and a 
    regular window is used.

    If saveDockInnerState and restoreDockInnerState are provided,
    they are callables used to restore the state of the widget.
    """

    size = 100
    proportion = 1 - DEFAULT_FONTLIST_PROPORTION
    wasTabSelected = False

    def __init__(self, name: str, 
                       dock: Optional[QtWidgets.QDockWidget],
                       widget: QtWidgets.QWidget,
                       defaultArea: int=Qt.RightDockWidgetArea,
                       defaultTabbed: bool=False, defaultFloating: bool=False,
                       defaultHidden: bool=False,
                       saveDockInnerState: Callable=None,
                       restoreDockInnerState: Callable=None):
        self.name = name
        self.dock = dock
        self.widget = widget
        self.defaultArea = defaultArea
        self.defaultTabbed = defaultTabbed
        self.defaultFloating = defaultFloating
        self.defaultHidden = defaultHidden
        self._saveDockInnerState = saveDockInnerState
        self._restoreDockInnerState = restoreDockInnerState

    def __repr__(self):
        return '<%s: %r %r %r at 0x%x>' % (type(self).__name__,
                                           self.name, self.dock, self.widget,
                                           id(self))

    def saveDockInnerState(self) -> Optional[Mapping]:
        """Provide options save state for when used as dock"""
        if self._saveDockInnerState is not None:
            return self._saveDockInnerState()
        save = getattr(self.widget, 'saveDockInnerState', None)
        if save is not None:
            return save()
        return None

    def restoreDockInnerState(self, state: Mapping, strict: bool=False):
        """Restore the save state from the options."""
        if state is None:
            return False

        if self._restoreDockInnerState is not None:
            return self._restoreDockInnerState(state, strict=strict)
        restore = getattr(self.widget, 'restoreDockInnerState', None)
        if restore is not None:
            return restore(state, strict=strict)

        msg = '{!r} does not support restore'.format(self.widget)

        if strict:
            raise TypeError(msg)

        errmsg(msg)
        return False


class MainWindowSaveState(object):

    """Saver and restorer for the main window. It can take it 
    to and from the options, to and from a savable dictionary for 
    saved arrangements, and to and from the main window itself
    for restoration.
   
    The attributes are the size of window, the state as saved/
    restored by Qt's saveState()/restoreState(), the arrangement
    name used by arrangeDocks(), the splitter state as provided
    by Qt, and the docks and pane sizes dictionaries.
    """

    version = TYPEATLAS_WINDOW_STATE_VERSION

    size = state = arrangement = None

    def __init__(self, size: QtCore.QSize=None, 
                       state: bytes=b'', arrangement: str='',
                       splitterState: bytes=b'', 
                       docks: Mapping=(), paneSizes: Mapping=()):
        self.size = size
        self.state = state
        self.arrangement = arrangement
        self.splitterState = splitterState
        self.docks = dict(docks)
        self.paneSizes = dict(paneSizes)

    @classmethod
    def fromdict(cls, data: Mapping) -> 'MainWindowSaveState':
        """Get the state from a saved dictionary."""
        kwargs = {}

        if data.get("size") is not None:
            kwargs['size'] = QtCore.QSize(*data['size'])
        if data.get("state") is not None:
            kwargs['state'] = binascii.a2b_base64(data['state'])
        if data.get("arrangement") is not None:
            kwargs['arrangement'] = data['arrangement']
        if data.get("splitter-state") is not None:
            kwargs['splitterState'] = binascii.a2b_base64(data['splitter-state'])
        if data.get("docks") is not None:
            kwargs['docks'] = data['docks']
        if data.get("pane-sizes") is not None:
            kwargs['paneSizes'] = paneSizes=data['pane-sizes']

        return cls(**kwargs)

    def todict(self) -> Mapping:
        """Save the state into a dictionary savable in JSON."""
        result = {}
        if self.size is not None:
            result['size'] = [self.size.width(), self.size.height()]
        if self.state is not None:
            result['state'] = binascii.b2a_base64(
                                            self.state,
                                            newline=False).decode('ascii')
        if self.arrangement is not None:
            result['arrangement'] = self.arrangement
        if self.splitterState is not None:
            result['splitter-state'] = binascii.b2a_base64(
                                            self.splitterState,
                                            newline=False).decode('ascii')
        if self.docks is not None:
            result['docks'] = self.docks
        if self.paneSizes is not None:
            result['pane-sizes'] = self.paneSizes
        return result

    @classmethod
    def fromWindow(cls, window: QtWidgets.QMainWindow=None) -> 'MainWindowSaveState':
        """Get the state from a window."""
        if window is None:
            return cls()

        docks = {}
        for name, dock in window.dockByName.items():
            state = dock.saveDockInnerState()
            if state is not None:
                docks[name] = state

        if window.useSplitterUi:
            sizes = {}
            splitterState = qtGetBytes(window.splitter.saveState())

        else:
            sizes = {}
            splitterState = b''
            for name, dock in window.dockByName.items():
                values = vars(dock)
                if 'size' in values and 'proportion' in values:
                    sizes[name] = [dock.proportion, dock.size]

        return cls(window.size(),
                   qtGetBytes(window.saveState(cls.version)),
                   window.interfaceArrangementName,
                   splitterState=splitterState,
                   docks=docks, paneSizes=sizes)

    @classmethod
    def fromOptions(cls, options: Options) -> 'MainWindowSaveState':
        """Get the state from the options."""
        return cls(options.typeAtlasSize,
                   options.typeAtlasState,
                   options.typeAtlasArrangement,
                   splitterState=options.typeAtlasSplitterState,
                   docks=options.typeAtlasDockInnerState,
                   paneSizes=options.typeAtlasPaneSizes)


    def saveIntoOptions(self, options: Options, permanent: bool=True):
        """Save the state into the options."""
        if self.size is not None:
            options.typeAtlasSize = self.size
        if self.state is not None:
            options.typeAtlasState = self.state
        if self.arrangement is not None:
            options.typeAtlasArrangement = self.arrangement
        if self.splitterState is not None:
            options.typeAtlasSplitterState = self.splitterState
        if self.docks is not None:
            options.typeAtlasDockInnerState = self.docks
        if self.paneSizes is not None:
            options.typeAtlasPaneSizes = self.paneSizes

    def restoreWindowState(self, window: QtWidgets.QMainWindow):
        """Restore the state in the given window."""
        if self.size is not None:
            window.resize(self.size)
        if self.arrangement:
            window.arrangeDocks(self.arrangement)
        if self.state:
            window.restoreState(self.state, self.version)
        if self.docks is not None:
            for name, state in self.docks.items():
               dock = window.dockByName.get(name)
               if dock is None:
                   continue
               dock.restoreDockInnerState(state, strict=False)
            window.rememberDockSizes()
        if window.useSplitterUi:
            if self.splitterState is not None:
                window.splitter.restoreState(self.splitterState)
        else:
            if self.paneSizes is not None:
                for name, (proportion, size) in self.paneSizes.items():
                    dock = window.dockByName.get(name)
                    if dock is None:
                        continue
                    dock.proportion = proportion
                    dock.size = size

    def __eq__(self, other):
        return (self.size == other.size and
                self.state == other.state and
                self.arrangement == other.arrangement and
                self.docks == other.docks)


class FileBrowser(QtWidgets.QWidget):

    """A file browser widget."""

    def __init__(self, path: str='~', 
                       parent: QtWidgets.QWidget=None, *args, **kwargs):

        super(FileBrowser, self).__init__(parent, *args, **kwargs)

        options = Options.getInstance()

        self.path = os.getcwd()

        self.model = QtWidgets.QFileSystemModel()
        self.model.setIconProvider(FontFileIconProvider())
        self.dirModel = QtWidgets.QFileSystemModel()
        self.dirModel.setFilter(QtCore.QDir.AllDirs |
                                QtCore.QDir.NoDotAndDotDot)
        self.dirModel.setRootPath('/')

        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)

        self.completer = QtWidgets.QCompleter()
        self.completer.setModel(self.dirModel)

        self.storageLocations = StorageLocations()

        self.pathLineCombo = CustomComboBox()
        self.pathLineCombo.setEditable(True)
        self.pathLineCombo.setSizeAdjustPolicy(
                self.pathLineCombo.AdjustToMinimumContentsLength)
        self.pathLineCombo.setSizePolicy(
                QtWidgets.QSizePolicy.MinimumExpanding,
                QtWidgets.QSizePolicy.Fixed)
        self.pathLineCombo.setCompleter(self.completer)
        self.pathLineCombo.popupAboutToShown.connect(self._updateComboItems)
        self.pathLineCombo.currentIndexChanged.connect(self._comboChanged)
        self.pathLineEdit = self.pathLineCombo.lineEdit()


        self.pathLineEdit.editingFinished.connect(self._pathEdited)

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.addWidget(self.pathLineCombo)
        self.toolbar.addAction(getIcon('go-up'), '..', self._goUp)
        self.toolbar.addAction(getIcon('go-home'), '~', self._goHome)
        self.toolbar.addAction(getIcon('system'), '/', self._goRoot)
        self.toolbar.setIconSize(options.toolbarIconSize)
        options.toolbarIconSizeChanged.connect(self.toolbar.setIconSize)

        self.tree.activated.connect(self._go)

        executor = QtExecutor(parent=self)

        self.toolbox = DirectoryToolbox(self.tree, executor)
        self.toolbox.disableActions()
        self.toolbox.addContextMenu(self.tree)

        selModel = self.tree.selectionModel()
        selModel.currentChanged.connect(self._fileChanged)

        for col in range(1, self.model.columnCount()):
            self.tree.header().hideSection(col)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.tree)

        self.layout = layout
        self.setLayout(layout)
        self.setPath(path)

    @Slot(QtCore.QModelIndex)
    def _go(self, index):
        """Go to the directory from the specified index."""
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.setPath(path)

    @Slot()
    def _goRoot(self):
        """Go to the root directory."""
        self.setPath('/')

    @Slot()
    def _goHome(self):
        """Go to the home directory."""
        self.setPath('~')

    @Slot()
    def _goUp(self):
        """Go up one level."""
        self.setPath('..')

    @Slot()
    def _pathEdited(self):
        """The path was edited by the user. Go there."""
        self.setPath(self.pathLineEdit.text())

    @Slot()
    def _updateComboItems(self):
        """Populate the path combo box with the discovered 
        storage locations from the OS."""
        self.pathLineCombo.clear()
        for location in self.storageLocations.locations():
            if location.icon:
                self.pathLineCombo.addItem(getIcon(location.icon),
                                           location.label, location)
            else:
                self.pathLineCombo.addItem(location.label, location)

    @Slot(int)
    def _comboChanged(self, index):
        """User selected a drive or location from a combo. Go to it."""
        location = self.pathLineCombo.itemData(index)
        if location is None:
            return
        self.setPath(location.path)

    #@Slot()
    #def _pathEditedCombo(self):
    #    self.setPath(self.pathLineCombo.currentText())

    def setPath(self, path: str):
        """Go to the provided path. Expands ~ as user home."""
        path = os.path.abspath(os.path.join(self.path, 
                                            os.path.expanduser(path)))
        if not os.path.exists(path):
            return
        self.model.setRootPath(path)
        self.tree.setRootIndex(self.model.index(path))
        self.pathLineEdit.setText(path)
        self.path = path

    @Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def _fileChanged(self, current, previous):
        """File selected. Enable/disable toolbox actions depending
        on the file type."""
        if not current.isValid():
            return
        path = current.data(QtWidgets.QFileSystemModel.FilePathRole)
        if os.path.isdir(path):
            self.toolbox.enableActions()
        else:
            self.toolbox.disableActions()


DEFAULT = object()


class TypeAtlasActionToolbox(Toolbox):

    """Actions for the main menu of type atlas, like utilities
    that we can open."""

    def __init__(self, atlasLibrary: 'TypeAtlasLibrary', *args, **kwargs):
        self.atlasLibrary = atlasLibrary
        super().__init__(*args, **kwargs)
        self.downloader = Downloader()

    @property
    def actionParent(self) -> QtCore.QObject:
        return self.atlasLibrary

    def actionDefinitions(self) -> Iterator:

        self.new = yield self.action(self.atlasLibrary.newTypeAtlasWindow,
                                     _('New window'), icon='window-new')

        yield self.separator()

        self.sampler = yield self.action(self.atlasLibrary.openSampler,
                                         _('Sampler'), icon='sampler')
        self.duel = yield self.action(self.atlasLibrary.openDuel,
                                       _('Duel'), icon='duel')
        self.glyphs = yield self.action(self.atlasLibrary.newGlyphAtlasWindow,
                                        _('Character map'),
                                        icon='glyphatlas')
        yield self.separator()
        yield self.action(self.downloadCharRegistry,
                          _('Download ISO language and country data'))
        for registry in self.atlasLibrary.charDb.registries():
            yield self.action(partial(self.downloadCharRegistry, registry),
                              _('Download %s') % (_(registry.name), ))
        yield self.separator()
        yield self.action(self.atlasLibrary.openOptions, _('&Options...'),
                          icon='software-properties')
        yield self.separator()
        self.quit = yield self.action(self.atlasLibrary.quit, _('&Quit'),
                                      icon='application-exit',
                                      shortcut='Ctrl+Q',
                                      shortcutContext=Qt.ApplicationShortcut)

    def downloadCharRegistry(self, registry: CharacterDatabase):
        """Download the characters for a given registry of characters,
        such as Unicode data."""
        self.downloader.downloadMany(registry.downloadables())

    def downloadISOLangData(self):
        """Download ISO language data."""
        self.downloader.downloadMany(self.atlasLibrary.langDb.downloadables())


class FontToolbox(Toolbox):

    """Actions for fonts. It operates on the selected fonts in the provided
    view."""

    def __init__(self, view: QtWidgets.QAbstractItemView, 
                       executor: external.Executor, 
                       categorization: Categorization=None):
        # FIXME: Pass atlasLibrary directly?
        if categorization is None:
            categorization = Categorization.getInstance()
        self.view = view
        self.executor = executor
        self.categorization = categorization
        self._properties = None
        super(FontToolbox, self).__init__()

    @property
    def actionParent(self) -> QtCore.QObject:
        return self.view

    def actionDefinitions(self) -> Iterator:
        self.copyFont = yield self.action(self.copyMimeData,
                                          _("Copy font"), icon='edit-copy',
                                          shortcut='Ctrl+C')
        yield self.copyFontName, _("Copy font name")
        yield (partial(self.copyFontName, 'family', localized=False),
               _("Copy font unlocalised name"))

        yield partial(self.copyFontName, 'style'), _("Copy font style")
        yield (partial(self.copyFontName, 'style', localized=False),
               _("Copy font unlocalised style"))

        yield partial(self.copyFontName, 'fullname'), _("Copy font full name")
        yield (partial(self.copyFontName, 'fullname', localized=False),
               _("Copy font unlocalised full name"))

        yield (partial(self.copyFontName, 'file', localized=False),
               _("Copy font filename"))

        yield self.separator()

        yield self.copyFontspecCode, _("Copy fontspec for LuaLaTeX or XeLaTeX")

        yield (partial(self.copyFontspecCode, useFilename=True),
               _("Copy fontspec code with full paths"))

        yield self.separator()

        yield self.tagFamilies, _("Tag families...")
        yield self.addFamiliesToCategory, _("Add families to category...")
        if ENABLE_COMPLEX_FILTERS:
            yield self.saveSearch, _("Save search as...")
        yield self.separator()
        yield self.untagFamilies, _("Untag families...")

        yield self.separator()

        yield self.openCurrent, _("Open with default application")

        for command in external.commands_providing(self.executor, 'font-open'):
            yield self.action(partial(self.openCurrent, command),
                              _(command.open.description),
                              icon=command.icon)

        yield self.separator()
        yield self.action(self.openProperties, _('Font properties...'),
                          icon='document-properties')

    def _addToGroup(self, groupType: datastore.FontGroupTypeKey, 
                          addSelected: bool=True, *args, **kwargs):
        """Add the fonts selected in the view to a user-selected group,
        or just create a group of that name with the provided kwargs
        if addSelected=False is passed.

        A dialog is opened for the choice of group parameters, and 
        then save the categorization.
        """
        groups = self.categorization.container(groupType)
        dialog = GroupNameDialog(groupContainer=groups)
        if dialog.exec_():
            groupName = dialog.groupName

            groups.define(groupName, dialog.icon, dialog.colorName(),
                          *args, **kwargs)

            if not addSelected:
                self.categorization.save()
                return

            selected = self.view.selectionModel().selectedIndexes()
            if not selected:
                current = self.view.selectionModel().currentIndex()
                if current.isValid():
                    selected = [current]

            if selected:
                for index in selected:
                    fontItem = index.data(FontItemRole)
                    groups.add(fontItem.family, groupName)

            self.categorization.save()

    @Slot()
    def tagFamilies(self):
        """Tag the given families, asking the user for the tag, and 
        save the tags."""
        self._addToGroup(datastore.FontTag)

    @Slot()
    def addFamiliesToCategory(self):
        """Add the given families to a category, for which the user
        is asked, and save the tags."""
        self._addToGroup(datastore.FontCategory)

    @Slot()
    def saveSearch(self):
        """Save the search, asking the user for a name."""
        self._addToGroup(datastore.FontSearch, addSelected=False,
                         filters=self.view.model().filter.filterGroup)

    def _removeFromGroup(self, groupType, removeSelected=True):
        """Remove elements from groups they are in. Ask the user
        which groups to remove, then save."""
        selected = self.view.selectionModel().selectedIndexes()
        if not selected:
            current = self.view.selectionModel().currentIndex()
            if not current.isValid():
                return
            selected = [current]

        families = OrderedSet(item.data(FontItemRole).family
                              for item in selected)

        groups = self.categorization.container(groupType)
        dialog = RemoveFromGroupDialog(families, groups)

        if dialog.exec_():
            for groupName in dialog.selectedGroups():
                for family in families:
                    groups.discard(family, groupName)

            self.categorization.save()

    @Slot()
    def untagFamilies(self):
        """Remove tags from the selected families. A dialog is
        opened to ask the user which tags to remove."""
        self._removeFromGroup(datastore.FontTag)

    @Slot()
    def removeFamiliesFromCategory(self):
        """Remove the selected families from categories. A dialog is
        opened to ask the user which categories to remove from."""
        self._removeFromGroup(datastore.FontCategory)
        
    @Slot()
    def openCurrent(self, command=None):
        """Open the current font"""
        current = self.view.selectionModel().currentIndex()
        if not current.isValid():
            return
        item = current.data(FontItemRole)
        if not item.file:
            return

        if command is None:
            #url = QtCore.QUrl('file://' + item.file)
            if item.remote:
                url = QtCore.QUrl(item.file)
            else:
                url = QtCore.QUrl.fromLocalFile(item.file)
            QtGui.QDesktopServices.openUrl(url)

        else:
            command.open(item)

    @Slot()
    def copyFontName(self, field='family', localized=True):
        """Copy the font name."""
        current = self.view.selectionModel().currentIndex()
        if not current.isValid():
            return
        item = current.data(FontItemRole)
        if localized:
            value = item.translate(field, textlang())
        else:
            value = getattr(item, field)

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(value)

    @Slot()
    def copyFontspecCode(self, useFilename=False, showAlts=True, useFontspec=True):
        """Copy XeLaTeX and LuaLaTeX code for the current font."""

        current = self.view.selectionModel().currentIndex()
        if not current.isValid():
            return

        escape = lambda s: re.sub(r'([{}\[\]])', r'\\\1', s)
        item = current.data(FontItemRole)

        lines = []
        if useFontspec:
            lines.append(r'%%\usepackage{fontspec}')

        if useFilename:

            dirname = os.path.dirname(item.file)
            basename = os.path.basename(item.file)

            if showAlts:
                lines.append(r'%%\newfontfamily\mycustomfont{%s}[...'
                                    % (escape(basename), ))
                lines.append(r'%%\newfontface\mycustomfont{%s}[...'
                                    % (escape(basename)))

            if item.is_style:
                lines.append(r'\setmainfont{%s}[Path=%s]' % (
                                escape(basename), escape(dirname)))
            else:

                selectors = {
                    'UprightFont':
                        fontlist.StyleSelector(),
                    'BoldFont':
                        fontlist.StyleSelector(weight=fontlist.WEIGHT_BOLD),
                    'ItalicFont':
                        fontlist.StyleSelector(slant=fontlist.SLANT_ITALIC),
                    'BoldItalicFont':
                        fontlist.StyleSelector(weight=fontlist.WEIGHT_BOLD,
                                               slant=fontlist.SLANT_ITALIC),
                }

                items = {key: selector.select(item)
                         for key, selector in selectors.items()}
                files = {key: os.path.relpath(item.file, dirname)
                         for key, item in items.items()}

                used = {files['UprightFont']}

                lines.append(r'\setmainfont{%s}[' % (escape(files['UprightFont']), ))
                lines.append(r'    Path=%s ,' % (escape(dirname), ))

                for key, stylefile in files.items():
                    if stylefile in used:
                        continue
                    lines.append(r'    %s=%s ,' % (key, escape(stylefile)))
                    used.add(stylefile)

                for style in item.styles:
                    stylefile = os.path.relpath(style.file, dirname)
                    if stylefile in used:
                        continue
                    lines.append(r'    %% ??%s??Font=%s ,'
                                    % (style.style, escape(stylefile)))

                lines.append(r']')

        else:
            if showAlts:
                lines.append(r'%%\newfontfamily\mycustomfont{%s}'
                                    % (escape(item.family), ))
                lines.append(r'%%\newfontface\mycustomfont{%s %s}'
                                    % (escape(item.family),
                                       escape(item.style)))
            lines.append(r'\setmainfont{%s}' % (escape(item.family), ))


        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText('\n'.join(lines))

    @Slot()
    def copyMimeData(self):
        """Copy the font in text formatted with it."""
        selected = self.view.selectionModel().selectedIndexes()
        if not selected:
            return
        model = selected[0].model()
        mime = model.mimeData(selected)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setMimeData(mime)

    @Slot()
    def openProperties(self):
        """Open the font properties dialog."""
        current = self.view.selectionModel().currentIndex()
        if not current.isValid():
            return

        if self._properties is not None:
            self._properties.hide()
            self._propertiesClosed()

        item = current.data(FontItemRole)

        self._properties = FontInfoWidget(item)
        self._properties.closed.connect(self._propertiesClosed)
        self._properties.show()

    @Slot()
    def _propertiesClosed(self):
        """The properties dialog was closed."""
        if self._properties is not None:
            self._properties.deleteLater()
            self._properties = None


class DirectoryToolbox(Toolbox):

    """Actions for navigating directories."""

    def __init__(self, view: QtWidgets.QTreeView, 
                       executor: external.Executor):
        self.view = view
        self.executor = executor
        super(DirectoryToolbox, self).__init__()

    @property
    def actionParent(self) -> QtCore.QObject:
        return self.view

    def actionDefinitions(self) -> Iterator:

        yield self.openCurrent, _("Open with system file manager")

        for command in external.commands_providing(self.executor,
                                                   'directory-open'):
            yield self.action(partial(self.openCurrent, command),
                              _(command.open.description),
                              icon=command.icon)

    @Slot()
    def openCurrent(self, command=None):
        """Open the current directory with the system file manager."""
        current = self.view.selectionModel().currentIndex()
        if not current.isValid():
            return

        path = current.data(QtWidgets.QFileSystemModel.FilePathRole)
        if not os.path.isdir(path):
            return

        if command is None:
            #url = QtCore.QUrl('file://' + urllib.parse.quote(path))
            url = QtCore.QUrl.fromLocalFile(path)
            QtGui.QDesktopServices.openUrl(url)
        else:
            command.open(path)


PREVIEW_LANGUAGES = 'languages'
PREVIEW_SIZES = 'sizes'
PREVIEW_LONG_TEXT = 'text'


class PreviewOptionsToolbox(Toolbox):

    """Actions for the preview pane, such as adjusting the font size,
    language(s), sample, mode."""

    def __init__(self, preview: 'FontPreview'):
        self.preview = preview
        self.renderingChoice = preview.renderingChoice
        self.mode = PREVIEW_LANGUAGES
        self.preferredLang = None
        self.customSample = None
        self.customSampleHistory = OrderedSet()

        super().__init__()
        self.disableActions(group='sampleText')

    def actionDefinitions(self) -> Iterator:

        with self.group('size'):
            yield self.action(self.smaller, _('Smaller'),
                              icon='format-font-size-less')
            yield self.action(self.larger, _('Larger'),
                              icon='format-font-size-more')

        with self.group('sampleText'):
            yield self.action(self.selectLanguage, _('Language'),
                              icon='select-language')
            yield self.action(self.selectSampleText, _('Custom sample'),
                              icon='select-sample')

        yield self.separator()

        with self.group('mode'):
            yield self.action(self.displayLanguages, _('Language samples'),
                              icon='font-language-samples')
            yield self.action(self.displaySizes, _('Size samples'),
                              icon='font-size-samples')
            yield self.action(self.displayLongSampleText, _('Long sample text'),
                              icon='font-long-sample')

        yield self.action(self.displayGUI, _('User interface demo'),
                          icon='font-sample-gui')

    def _jumpToSize(self, offset: int):
        """Increase or decrease the font size the given number of times.
        Decrease if negative. Jumps with through the available font sizes."""
        sizes = self.preview.fontsizes
        size = self.renderingChoice.previewSize

        if len(sizes) < 2:
            return

        i = min(range(len(sizes)), key=lambda i: abs(sizes[i] - size))
        try:
            size = sizes[i + offset]
        except IndexError:
            return

        self.renderingChoice.setPreviewSize(size)

    @Slot()
    def larger(self):
        """Make the font larger."""
        self._jumpToSize(+1)

    @Slot()
    def smaller(self):
        """make the font smaller."""
        self._jumpToSize(-1)

    @Slot()
    def selectLanguage(self):
        """Open a menu to select the language of the preview."""
        self.currentMenu = menu = QtWidgets.QMenu()

        menu.addAction(_('Default'), partial(self._setLanguage, None))

        langDb = self.preview.langDb
        fontLangs = self.preview.fontItem.lang
        for lang in langDb.languages_with_samples(fontLangs):
            countryflag = langDb.guess_country_flag(lang)
            label = langDb.language_name(lang)
            if countryflag:
                menu.addAction(getIcon('flags/' + countryflag), label,
                               partial(self._setLanguage, lang))
            else:
                menu.addAction(label, partial(self._setLanguage, lang))

        menu.exec_(QtGui.QCursor.pos())

    def _setLanguage(self, lang):
        """Set the preview lanauge."""
        self.customSample = None
        self.preferredLang = lang
        self.preview.updateSample()

    @Slot()
    def selectSampleText(self):
        """Open a dialog to choose text for the sample."""
        self.currentDialog = dialog = QtWidgets.QInputDialog()

        dialog.setInputMode(dialog.TextInput)
        dialog.setComboBoxEditable(True)
        history = list(reversed(self.customSampleHistory))
        if history:
            dialog.setComboBoxItems(history)
            dialog.setTextValue(history[0])
        dialog.textValueSelected.connect(self._setSampleText)

        dialog.setWindowTitle(_('Custom sample'))
        dialog.setLabelText(_('Sample'))

        dialog.setOkButtonText(_('Set text'))
        dialog.setCancelButtonText(_('Cancel'))

        dialog.exec_()

    def _setSampleText(self, sampleText: str):
        """Set the sample text."""
        self.customSampleHistory.discard(sampleText)
        self.customSampleHistory.add(sampleText)
        self.customSample = sampleText
        self.preview.updateSample()

    @Slot()
    def displaySizes(self):
        """Preview different sizes."""
        self.disableActions(group='size')
        self.enableActions(group='sampleText')
        self.mode = PREVIEW_SIZES
        self.preview.updateSample()

    @Slot()
    def displayLanguages(self):
        """Preview different languages."""
        self.enableActions(group='size')
        self.disableActions(group='sampleText')
        self.mode = PREVIEW_LANGUAGES
        self.preview.updateSample()

    @Slot()
    def displayLongSampleText(self):
        self.enableActions(group='size')
        self.enableActions(group='sampleText')
        self.mode = PREVIEW_LONG_TEXT
        self.preview.updateSample()

    @Slot()
    def displayGUI(self):
        """Show an example GUI with that font."""
        if getattr(self, '_window', None):
            self._window.deleteLater()
        window = ExampleWindow('* { %s }' % (qFontToCss(self.preview.font,
                                                        qt=True), ))
        window.show()
        self._window = window


class FontPreview(QtWidgets.QWidget):

    """A preview of the font(s)."""

    def __init__(self, fontDb: QtGui.QFontDatabase=None, 
                       langDb: LanguageDatabase=None, 
                       charDb: CharacterDatabase=None,
                       renderingChoice: FontRenderingChoice=None, 
                       options: Options=None,
                       parent: QtWidgets.QWidget=None):
        super().__init__(parent)

        if options is None:
            options = Options.getInstance()
        if renderingChoice is None:
            renderingChoice = FontRenderingChoice()
        if fontDb is None:
            fontDb = QtGui.QFontDatabase()
        if langDb is None:
            langDb = LanguageDatabase.getInstance()
        if charDb is None:
            charDb = CharacterDatabase.getInstance()

        renderingChoice.previewChanged.connect(self.updateRendering)

        self.fontDb = fontDb
        self.langDb = langDb
        self.charDb = charDb
        self.renderingChoice = renderingChoice

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setIconSize(options.toolbarIconSize)
        options.toolbarIconSizeChanged.connect(self.toolbar.setIconSize)
        options.sampleSelectionChanged.connect(self._sampleOptionChanged)
        options.showSampleNameChanged.connect(self._sampleOptionChanged)

        self.preview = QtWidgets.QTextEdit()
        self.preview.setReadOnly(False)
        self.preview.setAcceptRichText(False)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.preview)

        self.toolbox = PreviewOptionsToolbox(self)
        self.toolbox.populateToolbar(self.toolbar)

        self.font = QtGui.QFont()
        self.fontsizes = [12]
        self.fontItem = None
        self.selectedItems = []
        self.options = options

    @Slot(object)
    @Slot(object, list)
    def setFontItem(self, item: fontlist.FontLike, 
                          selected: SequenceOf[fontlist.FontLike]=[]):
        """Set the fonts for the preview: the current and the selected
        fonts in the view."""
        if item is None:
            return

        self.fontItem = item
        self.selectedItems = selected

        self.setFont(self._itemQFont(item))

        self.fontsizes = self.fontDb.smoothSizes(item.family, item.style)
        if not self.fontsizes:
            self.fontsizes = self.fontDb.standardSizes()
            if not self.fontsizes:
                self.fontsizes = [12]

        self.updateSample()

    def _itemQFont(self, item: fontlist.FontLike) -> QtGui.QFont:
        """Get the QFont for the font item."""
        font = self.fontDb.font(item.family, item.style,
                                self.renderingChoice.previewSize)
        font.setStyleHint(QtGui.QFont.AnyStyle,
                          self.renderingChoice.antialiasStyle)
        font.setHintingPreference(self.renderingChoice.hintingPreference)
        return font

    @Slot(QtGui.QFont)
    def setFont(self, font: QtGui.QFont):
        """Set the main sample display font."""
        self.font = font
        self.preview.setCurrentFont(font)

    def _samples(self, fontItem: fontlist.FontLike) -> IteratorOf[SampleInfo]:
        """Return samples for the given font item."""
        sampleSelection = self.options.sampleSelection
        result = self.langDb.samples_font(fontItem)
        if sampleSelection != 'most':
            result = filter_samples(result, one_per_script=True)
        return result

    def _sampleTexts(self, fontItem: fontlist.FontLike) -> IteratorOf[str]:
        """Return the sample texts for the given item."""
        return (sample.text for sample in self._samples(fontItem))

    def _oneSampleText(self, fontItem, multiple: bool=False) -> str:
        """Return one sample text for either one font or multiple
        fonts passed as first argument."""
        text = self.toolbox.customSample
        if text:
            return text

        lang = self.toolbox.preferredLang
        if lang is not None:
            #sample = self.langDb.sample_language(lang)
            text = self.langDb.sample_text_language(lang)
            if text:
                return text

        if multiple:
            sampleTexts = self.langDb.sample_texts_font_intersection(fontItem)
        else:
            sampleTexts = self.langDb.sample_texts_font(fontItem)

        return next(iter(sampleTexts), None)

    def _largeSampleText(self, fontItem, multiple: bool=False) -> Mapping:
        """Return one large sample for either one font or multiple
        fonts passed as first argument."""

        if multiple:
            fonts = fontItem
        else:
            fonts = [fontItem]

        lang = self.toolbox.preferredLang
        if lang is None or any(lang not in fi.lang for fi in fonts):
            if multiple:
                samples = self.langDb.samples_font_intersection(fontItem)
            else:
                samples = self.langDb.samples_font(fontItem)

            sample = next(samples, None)
            if sample is None:
                lang = 'zxx'
            else:
                lang = sample.lang

        extraSamples = []
        if self.toolbox.customSample:
            extraSamples = self.toolbox.customSample

        return self.langDb.sample_text_complex(lang, extra=extraSamples,
                                               chardb=self.charDb)

    def _setPlainText(self, text: str, lang: str=None):
        """Set the plain text for the preview."""
        self.preview.setPlainText(text)

    def _insertPlainText(self, text: str, lang: str=None):
        """Insert plain text."""
        ## Experimental code to plug the language into the HTML in
        ## hopes that Qt is smart enough to use opentype language glyphs.
        ## it is not.
        if False and lang is not None:
            font = self.preview.currentFont()
            css = qFontToCss(font, self.fontItem, qt=True)
            html = '<span style="%s; font-size: %dpt;" lang="%s">%s</span>' % (
                        htesc(css), font.pointSize(), htesc(lang),
                        htesc(text).replace('\n', '<br>\n'))

            self.preview.insertHtml(html)
            return

        self.preview.insertPlainText(text)

    @Slot()
    def updateSample(self):
        """Update the sample to the current selection."""
        if self.fontItem is None:
            return

        #samples = self.langDb.samples_font(self.fontItem)
        #sampleTexts = self.langDb.sample_texts_font(self.fontItem)

        hasMultipleFonts = any(item is not self.fontItem
                               for item in self.selectedItems)

        if hasMultipleFonts and self.toolbox.mode != PREVIEW_LONG_TEXT:
            self._setPlainText('')

            maxSampleFonts = self.options.maxSampleFonts

            infoFont = QtGui.QFont()

            font = QtGui.QFont(self.font)
            items = [self.fontItem]
            items.extend(item for item in self.selectedItems
                         if item is not self.fontItem)

            text = self._oneSampleText(items, multiple=True)
            use_different_text = not text

            for i, item in enumerate(items):
                if i != 0:
                    font = self._itemQFont(item)

                if i >= maxSampleFonts > 0:
                    return

                fullname = item.translate('fullname', textlang())

                if use_different_text:
                    text = self._oneSampleText(item)
                if text:
                    self.preview.setCurrentFont(infoFont)
                    self._insertPlainText(
                        _("Preview of %s") % (fullname, ) + '\n')
                    self.preview.setCurrentFont(font)
                    self._insertPlainText(text + '\n')

                else:
                    self.preview.setCurrentFont(infoFont)
                    self._insertPlainText(
                        _("No sample available for %s") % (fullname, ) + '\n')

        elif self.toolbox.mode == PREVIEW_LANGUAGES:

            ## We could instead use HTML, which would allow to specify
            ## language, should Qt ever support OpenType features.
            ## Qt 4 and 5 both seem to ignore this, although Qt 5
            ## uses the OpenType rendering for the system language.
            #
            # css = qFontToCss(self.font)
            #
            # innerHtml = '<br>\n'.join(
            #     '<span lang="%s">%s</span>' % (htesc(sample.lang),
            #                                    htesc(sample.text))
            #     for sample in samples)
            #
            # self.preview.setHtml('<span style="%s">%s</span>' % (
            #                         htesc(css), innerHtml))


            showSampleName = self.options.showSampleName
            if not showSampleName:
                #sampleTexts = self._sampleTexts(self.fontItem)
                #self.preview.setCurrentFont(self.font)
                #self._setPlainText('\n'.join(sampleTexts))

                samples = self._samples(self.fontItem)
                self._setPlainText('')
                for sample in samples:
                    self._insertPlainText(sample.text + '\n', sample.lang)

            else:
                samples = self._samples(self.fontItem)
                self._setPlainText('')
                for sample in samples:

                    infoFont = QtGui.QFont()

                    language = self.langDb.language_name(sample.code, AUTO_LOCALE_NAME)
                    script = self.langDb.script_name(sample.script, AUTO_LOCALE_NAME)
                    label = _("Sample for {language} using the {script} script").format(
                                language=language,
                                script=script)

                    self.preview.setCurrentFont(infoFont)

                    self._insertPlainText(label + '\n')

                    self.preview.setCurrentFont(self.font)
                    self._insertPlainText(sample.text + '\n', sample.lang)

        elif self.toolbox.mode == PREVIEW_SIZES:
            self._setPlainText('')

            text = self._oneSampleText(self.fontItem)
            if not text:
                return

            for size in self.fontsizes:
                font = QtGui.QFont(self.font)
                font.setPointSize(size)

                self.preview.setCurrentFont(font)
                self._insertPlainText(text + '\n')

        elif self.toolbox.mode == PREVIEW_LONG_TEXT:
            self._setPlainText('')
            font = QtGui.QFont(self.font)

            if hasMultipleFonts:
                items = [self.fontItem]
                items.extend(item for item in reversed(self.selectedItems)
                                if item is not self.fontItem)

                textData = self._largeSampleText(items, multiple=True)
                items = items[:3]

            else:
                textData = self._largeSampleText(self.fontItem)

            if hasMultipleFonts:
                font = self._itemQFont(items[1:3][-1])

            font.setPointSize(self.renderingChoice.previewSize * 1.5)
            self.preview.setCurrentFont(font)
            self._insertPlainText(textData['title'] + '\n\n')

            if hasMultipleFonts:
                font = self._itemQFont(items[1:2][-1])

            font.setPointSize(self.renderingChoice.previewSize)
            self.preview.setCurrentFont(font)
            self._insertPlainText(textData['subtitle'] + '\n\n')

            if hasMultipleFonts:
                font = QtGui.QFont(self.font)

            font.setPointSize(self.renderingChoice.previewSize * 0.75)
            self.preview.setCurrentFont(font)
            self._insertPlainText(textData['text'] + '\n\n')

        else:
            self._setPlainText(
                    _("12 Font Sample Texts You Wouldn't Believe Exist!"))

    @Slot()
    def updateRendering(self):
        """Update the rendering mode."""
        font = self.fontDb.font(self.font.family(),
                                self.font.styleName(),
                                self.renderingChoice.previewSize)

        font.setStyleHint(QtGui.QFont.AnyStyle,
                          self.renderingChoice.antialiasStyle)
        font.setHintingPreference(self.renderingChoice.hintingPreference)
        self.setFont(font)
        self.updateSample()

    @Slot(str)
    @Slot(bool)
    @Slot(object)
    def _sampleOptionChanged(self, value):
        """Sample options changed. Update it."""
        self.updateSample()


class EditSavedArrangementsDialog(ItemValuesDialogBase):

    """Edit the saved arrangements."""

    filterKey = N_('interface configurations')
    dialogTitleText = N_("Edit saved interface configurations")
    searchPlaceholderText = N_('Search configurations...')

    refWidth = 900
    refHeight = 800

    itemsRemovable = True
    itemsEditable = True
    itemsHaveContainer = False

    def __init__(self, arrangements: datastore.InterfaceArrangements, 
                       name: str='saved', *args, **kwargs):
        self.arrangements = arrangements
        self.arrangement_pile = arrangements.get_arrangements(name)
        itemValues = filtering.ItemValues(self.arrangement_pile,
                                          filtering.ITEM_TYPE_NONE)
        super().__init__(*args, itemValues=itemValues,
                                itemAdapter=uitools.DictItemAdapter,
                                **kwargs)

    def saveChangedItems(self):
        """Save the interface arrangements."""
        self.arrangements.save()

    def editItem(self, index: QtCore.QModelIndex,
                       groupName: str, newName: str=None,
                       icon: str=None, color: str=None):
        """Complete the edit of the selected arrangement's icon, color
        and name."""

        if not index.isValid():
            return

        if newName is None:
            newName = groupName

        arrangement = index.data(ItemItemRole)
        if arrangement is None:
            return

        if newName != groupName:

            for arrangement in self.arrangement_pile:
                #if newName == arrangement.get('label', ''):
                #    self.showOverwriteError(groupName, newName)
                #    return

                pass

            arrangement.data['label'] = newName

        arrangement.data['icon'] = icon
        arrangement.data['color'] = color

        # Trigger changed by editing the item
        pos = index.row()
        if pos < len(self.arrangement_pile):
            if self.arrangement_pile[pos] is arrangement.data:
                self.arrangement_pile[pos] = arrangement.data


class TypeAtlasLibrary(QtCore.QObject):

    """Manager of main TypeAtlas windows, shared attributes between
    those instances."""

    instance = None

    def __init__(self, splash: QtWidgets.QSplashScreen=None, 
                       *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.options = Options.getInstance()
        self.options.load()

        self.categorization = Categorization.getInstance()
        self.metadataCache = MetadataCache.getInstance()
        self.histories = datastore.Histories.getInstance()
        self.arrangements = datastore.InterfaceArrangements().getInstance()

        self.charDb = CharacterDatabase.getInstance()
        self.langDb = LanguageDatabase.getInstance()
        self.fontDb = QtGui.QFontDatabase()

        if splash is not None:
            splash.showMessage(_('Loading cache...'))
        debugmsg("Loading cache...")
        self.metadataCache.load()
        self.histories.load()
        self.arrangements.load()

        firstRun = not self.metadataCache.metadata

        if splash is not None:
            splash.showMessage(_('Loading font list...'))
        debugmsg("Loading font list...")

        self.executor = executor = QtExecutor(self.options.executablePaths,
                                              parent=self)
        self.finder = qfontlist.QtFontFinder(self.fontDb, executor=executor,
                                             metadata_cache=self.metadataCache)

        if splash is not None:
            self.finder.fontprogress = splash.setProgressStatus
            self.finder.fontprogressdone = splash.setProgressDone

        self.fontFamilies = list(self.finder.families())
        setDefaultFontFamilies(self.fontFamilies)
        self.categorization.load()

        if splash is not None:
            splash.showMessage(_('Filling detailed font info...'))
        debugmsg("Filling detailed font info list...")

        for i, family in enumerate(self.fontFamilies):
            if firstRun and splash is not None:
                splash.setProgressStatus(
                    i, len(self.fontFamilies),
                    message=_('First run: Parsing detailed font information: '
                              '{} out of {}').format(i, len(self.fontFamilies)))

            qfontlist.updateFamilyInfo(self.fontDb, family)
            for style in family.styles:
                self.finder.fill_detailed_info(style)

        if firstRun:
            splash.setProgressDone()

        if splash is not None:
            splash.showMessage(_('Building global feature table...'))
        debugmsg("Building global feature table...")
        self.fontFeatureSets = fontlist.FeatureSets(self.fontFamilies)

        if splash is not None:
            splash.showMessage(_('Attempting to guess family type...'))
        debugmsg("Attempting to guess family type...")
        self.finder.fill_generic_families(self.fontFamilies)

        debugmsg("Saving metadata cache...")
        self.metadataCache.autosave()

        if splash is not None:
            splash.showMessage(_('Populating unicode info...'))
        debugmsg("Populating unicode info...")
        self.charDb.add_registries()
        self.charDb.populate(download=False, deep=True)
        if splash is not None:
            splash.showMessage(_('Populating language info...'))
        debugmsg("Populating language info...")
        self.langDb.populate()

        debugmsg("DONE.")

        self.atlasToolbox = TypeAtlasActionToolbox(self)

        self.openWindows = OrderedSet()
        self.openTypeAtlasWindows = OrderedSet()
        self.optionsWindow = None

        self.samplerWasUsed = False

        self.typeAtlasFirstState = MainWindowSaveState.fromOptions(self.options)
        self.typeAtlasLastState = self.typeAtlasFirstState

    @classmethod
    def getInstance(cls, *args, create: bool=True, **kwargs):
        """Get the singleton instance of the class. If create=False is 
        passed, it is not created if it does not exist and None is 
        returned."""
        if cls.instance is None:
            if not create:
                return None
            cls.instance = cls(*args, **kwargs)
        return cls.instance

    @Slot()
    def quit(self):
        """Quit TypeAtlas."""
        if self.openTypeAtlasWindows:
            self._lastTypeAtlasClosed(next(iter(self.openTypeAtlasWindows)))

        if self.options.pending:
            self.options.rollback()

        optionState = MainWindowSaveState.fromOptions(self.options)
        if self.typeAtlasLastState != optionState:
            self.typeAtlasLastState.saveIntoOptions(self.options)
        if self.options.changed:
            self.options.save()
        self.arrangements.autosave()
        sys.exit(0)

    @Slot()
    def openSampler(self):
        """Open the font sampler."""

        # If the sampler had not been yet used, check that we have
        # charset for the fonts.
        if not self.samplerWasUsed:
            totalcount = 0
            goodcount = 0

            for family in self.fontFamilies:
                for style in family.styles:
                    totalcount += 1
                    if style.charset is not None:
                        goodcount += 1

            if goodcount < totalcount * MISSING_CHARSET_THRESHOLD:

                dialog = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Warning,
                    _("Character lists not loaded"),
                    _("The lists of characters supported by the individual "
                      "fonts is not loaded yet. This can be a very slow " "process if fontTools is not available. Do you wish "
                      "to continue with loading the lists?"),
                     QtWidgets.QMessageBox.Yes |
                     QtWidgets.QMessageBox.No)

                dialog.setWindowModality(Qt.WindowModal)
                if dialog.exec() != QtWidgets.QMessageBox.Yes:
                    return

                progress = QtWidgets.QProgressDialog(
                        _("Loading character lists..."),
                        _("Abort"), 0, totalcount)

                progress.setWindowModality(Qt.WindowModal)

                i = 0

                ## Already loaded.
                #self.metadataCache.load()

                for family in self.fontFamilies:
                    for style in family.styles:
                        if progress.wasCanceled():
                            return

                        style.get_charset()
                        i += 1
                        progress.setValue(i)

                self.metadataCache.autosave()

        sampler = FontSampler(self.fontFamilies,
                                   fontDb=self.fontDb,
                                   langDb=self.langDb,
                                   featureSets=self.fontFeatureSets)
        sampler.closed.connect(self._windowClosed)
        sampler.show()
        self.openWindows.add(sampler)
        self.samplerWasUsed = True
        return sampler

    @Slot()
    def openDuel(self):
        """Open the font duel."""
        duel = FontDuel(self.fontFamilies, featureSets=self.fontFeatureSets)
        duel.closed.connect(self._windowClosed)
        duel.show()
        self.openWindows.add(duel)
        return duel

    @Slot()
    def openOptions(self):
        """Open the edit options dialog."""
        if self.optionsWindow is None:
            optionsWidget = OptionsWidget(self.options)
            optionsWidget.closed.connect(self._optionsClosed)
            optionsWidget.show()
            self.optionsWindow = optionsWidget

        else:
            self.optionsWindow.show()

        return self.optionsWindow

    @Slot(QtWidgets.QWidget)
    def openCustomWindow(self, window):
        """Open a window of your choosing."""
        window.closed.connect(self._windowClosed)
        self.openWindows.add(window)
        window.show()
        return window

    @Slot()
    def newTypeAtlasWindow(self):
        """Open a new main TypeAtlas window."""
        window = TypeAtlas(self)
        window.closed.connect(self._windowClosed)
        window.show()
        self.openWindows.add(window)
        self.openTypeAtlasWindows.add(window)
        self.typeAtlasLastSettings = {}
        return window

    @Slot()
    def newGlyphAtlasWindow(self):
        """Open a new main GlyphAtlas window."""
        from typeatlas.guiglyphs import GlyphAtlas
        window = GlyphAtlas(self)
        window.closed.connect(self._windowClosed)
        window.show()
        self.openWindows.add(window)
        return window

    @Slot()
    def _windowClosed(self):
        """A window was close it. Clear it, prepare its state for
        saving, and save and quit if needed."""
        window = self.sender()
        self.openWindows.discard(window)
        self.openTypeAtlasWindows.discard(window)

        if not self.openTypeAtlasWindows:
            self._lastTypeAtlasClosed(window)

        window.deleteLater()
        if not self.openWindows:
            self.quit()

    def _lastTypeAtlasClosed(self, window: QtWidgets.QWidget):
        """The last typeatlas window was closed. Save its state."""
        self.typeAtlasLastState = MainWindowSaveState.fromWindow(window)

    @Slot()
    def _optionsClosed(self):
        """The options were closed."""
        self.optionsWindow = None



class ExampleWindow(QtWidgets.QMainWindow):

    """A GUI example window."""

    def __init__(self, stylesheet: str, translate: Callable=_, *args, **kwargs):
        super().__init__(*args, **kwargs)

        _ = translate

        self.setWindowTitle(_('User interface demo'))

        self.setStyleSheet(stylesheet)

        strings = [N_('&Demo'), N_('AaQqRr'), N_('E&xample'),
                   N_('Prime&r'), N_('Test &label')]
        enum = [N_('Example &1'), N_('Example &2'), N_('Example &3')]

        icons = ['document-open', 'document-save',
                 'edit-cut', 'edit-copy', 'edit-paste']

        menus = [self.menuBar().addMenu(_(string)) for string in strings[:-1]]
        englishMenu = self.menuBar().addMenu('English')
        englishMenu.addAction(getIcon('preferences-desktop-locale'), 'English')
        englishMenu.addSeparator()

        for i, (icon, string) in enumerate(zip(icons, strings)):
            if i == 2:
                englishMenu.addSeparator()
            englishMenu.addAction(getIcon(icon), string)
            for menu in menus:
                if i == 2:
                    menu.addSeparator()
                menu.addAction(getIcon(icon), _(string))

        menus[0].addSeparator()
        menus[0].addAction(_('Do nothing'))

        pages = [QtWidgets.QWidget() for label in enum]

        widget = QtWidgets.QTabWidget()
        for label, page in zip(enum, pages):
            widget.addTab(page, _(label))

        for page in pages:
            radioBox = QtWidgets.QGroupBox()
            radioBox.setLayout(QtWidgets.QVBoxLayout())
            radios = QtWidgets.QButtonGroup(self)
            radios.setExclusive(True)
            for i, string in enumerate(strings):
                radio = QtWidgets.QRadioButton()
                radio.setText(_(string))
                radios.addButton(radio)
                #radio.setCheckable(True)
                radio.setChecked(i == 1)
                radioBox.layout().addWidget(radio)

            checkbox = QtWidgets.QCheckBox()
            checkbox.setText(_(strings[2]))

            page.setLayout(QtWidgets.QGridLayout())
            page.layout().addWidget(radioBox, 0, 0, 1, 1)
            page.layout().addWidget(checkbox, 1, 0, 1, 1)
            for i, string in enumerate(strings):
                button = QtWidgets.QPushButton()
                button.setText(_(string))
                page.layout().addWidget(button, 2, i, 1, 1)

            progress = QtWidgets.QProgressBar()
            progress.setValue(73)
            page.layout().addWidget(progress, 0, 1, 1, 4)

            combobox = QtWidgets.QComboBox()
            for string in strings:
                combobox.addItem(_(string).replace('&', ''))
            page.layout().addWidget(combobox, 1, 1, 1, 2)

        self.setCentralWidget(widget)

    closed = Signal()

    def closeEvent(self, event):
        r = super().closeEvent(event )
        if event.isAccepted():
            self.closed.emit()
        return r


interfaceArrangements =  {
    'simple': {
        'label': N_('Simple interface'),
        'use-splitter': True,
    },
    'basic-customizable': {
        'label': N_('Basic customizable interface'),
        'use-splitter': False,
        'docked-filters': False,

    },
    'fully-customizable': {
        'label': N_('Fully customizable interface'),
        'use-splitter': False,
        'docked-filters': True,
    },
    'expansive': {
        'label': N_('Expansive interface'),
        'use-splitter': False,
        'docked-filters': True,
        'docks': {
            'samples': dict(area=Qt.BottomDockWidgetArea,
                            after='info-table', before='char-info',
                            hidden=False, floating=False, tabbed=False,
                            inner={'info-visible': False}),
            'characters': dict(area=Qt.RightDockWidgetArea,
                               hidden=False, floating=False, tabbed=True,
                               before='class',
                               inner={'char-bar-visible': False}),
            'info-table': dict(area=Qt.BottomDockWidgetArea,
                               before='samples', floating=False,
                               hidden=False, tabbed=False),
            'license': dict(hidden=True, tabbed=False),
            'char-info': dict(area=Qt.BottomDockWidgetArea,
                              after='samples', floating=False,
                              hidden=False, tabbed=False),
            'languages': dict(area=Qt.LeftDockWidgetArea,
                              before='tags', floating=False,
                              hidden=False, tabbed=False),
            'tags': dict(area=Qt.LeftDockWidgetArea,
                         before='filters', after='languages',
                         floating=False, hidden=False, tabbed=False),
            'filters': dict(area=Qt.LeftDockWidgetArea,
                            after='tags',
                            floating=False, hidden=False, tabbed=False),

            # Tabbed last so they can be added to a current pane
            'categories': dict(area=Qt.LeftDockWidgetArea,
                               after='tags',
                               floating=False, hidden=False, tabbed=True),

            'writing-system': dict(area=Qt.LeftDockWidgetArea,
                                   after='languages',
                                   floating=False, hidden=False, tabbed=True),

            'info-text': dict(area=Qt.RightDockWidgetArea,
                              hidden=False, floating=False, tabbed=True,
                              after='characters', before='class'),

            'class': dict(area=Qt.RightDockWidgetArea,
                          hidden=False, floating=False, tabbed=True,
                          after='info-text'),
        },
    },
}


class TypeAtlas(QtWidgets.QMainWindow):

    """TypeAtlas main window."""

    def __init__(self, atlasLibrary: TypeAtlasLibrary=None, 
                       parent: QtWidgets.QWidget=None, 
                       splash: QtWidgets.QSplashScreen=None):
        super(TypeAtlas, self).__init__(parent)

        if atlasLibrary is None:
            atlasLibrary = TypeAtlasLibrary.getInstance(splash)

        self.atlasLibrary = atlasLibrary
        vars(self).update(vars(atlasLibrary))

        #self.resize(self.options.typeAtlasSize)
        #atlasWidth = self.options.typeAtlasSize.width()

        self.setWindowTitle(_("TypeAtlas font explorer"))
        self.setWindowIcon(getIcon('typeatlas'))

        mainMenu = self.menuBar()
        self.fontsMenu = fontsMenu = mainMenu.addMenu(_("&Fonts"))
        self.editMenu = editMenu = mainMenu.addMenu(_("&Edit"))
        self.viewMenu = viewMenu = mainMenu.addMenu(_("&View"))
        self.groupsMenu = groupsMenu = mainMenu.addMenu(_("&Selections"))
        self.helpMenu = helpMenu = mainMenu.addMenu(_("&Help"))

        mainToolbar = self.addToolBar(_('Main toolbar'))
        mainToolbar.setIconSize(self.options.toolbarIconSize)
        mainToolbar.setObjectName('toolbar:main')
        self.options.toolbarIconSizeChanged.connect(mainToolbar.setIconSize)

        searchToolbar = self.addToolBar(_('Search toolbar'))
        searchToolbar.setIconSize(self.options.toolbarIconSize)
        searchToolbar.setObjectName('toolbar:search')
        self.options.toolbarIconSizeChanged.connect(searchToolbar.setIconSize)

        self.selectedFontItem = None

        self._tree = None
        self.renderingChoice = FontRenderingChoice()
        self.model = FontListModel(self.fontFamilies, fontDb=self.fontDb,
                                   renderingChoice=self.renderingChoice,
                                   featureSets=self.fontFeatureSets)
        for key, arrangement in interfaceArrangements.items():
            action = viewMenu.addAction(_(arrangement['label']),
                                        self._arrangeDockByAction)
            action.setData(key)

        self.savedInterfacesMenu = viewMenu.addMenu(_("Saved"))
        self.savedInterfacesMenu.aboutToShow.connect(
                            self._repopulateSavedInterfacesMenu)

        viewMenu.addSeparator()

        self.renderingChoice.populateMenu(viewMenu)

        self.filterModel = FontFilterModel(langDb=self.langDb)
        self.filterModel.setSourceModel(self.model)
        self.browser = self.model.treeView = QtWidgets.QTreeView()
        self.browser.setModel(self.filterModel)
        self.browser.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        self.browser.setDragEnabled(True)
        self.browser.setDragDropMode(self.browser.DragOnly)
        self.renderingChoice.listChanged.connect(self.browser.reset)

        self.standardModel = FontListModel([],
                                           fontDb=self.fontDb,
                                           renderingChoice=self.renderingChoice)
        self.standardFontBrowser = self.standardModel.treeView = QtWidgets.QTreeView()
        self.standardFontBrowser.setModel(self.standardModel)
        self.standardFontBrowser.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        self.standardFontBrowser.setDragEnabled(True)
        self.standardFontBrowser.setDragDropMode(self.browser.DragOnly)
        self.renderingChoice.listChanged.connect(self.standardFontBrowser.reset)

        standardLayout = QtWidgets.QVBoxLayout()
        self.chosenStandard = QtWidgets.QComboBox()
        self.standardBrowser = QtWidgets.QWidget()
        self.standardBrowser.setLayout(standardLayout)
        standardLayout.addWidget(self.chosenStandard)
        standardLayout.addWidget(self.standardFontBrowser)

        self.chosenStandard.addItem(_("Select font list..."), None)
        self.chosenStandard.addItem(_("Fonts defined in PostScript level 1"),
                                    fontlist.PS1)
        self.chosenStandard.addItem(_("Fonts defined in PostScript level 2"),
                                    fontlist.PS2)
        self.chosenStandard.addItem(_("Fonts defined in PostScript level 3"),
                                    fontlist.PS3)
        self.chosenStandard.addItem(_("Fonts provided by Microsoft in Core Fonts for the Web"),
                                    fontlist.MS_CORE)
        self.chosenStandard.addItem(_("Fonts defined for PDF"),
                                    fontlist.PDF)
        self.chosenStandard.activated.connect(self._standardFontsRequested)

        self.fileBrowser = FileBrowser()
        self.fileFontModel = FontListModel([],
                                           renderingChoice=self.renderingChoice)
        self.fileFontBrowser = self.fileFontModel.treeView = QtWidgets.QTreeView()
        self.fileFontBrowser.setModel(self.fileFontModel)
        self.fileFontBrowser.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        self.fileFontBrowser.setDragEnabled(True)
        self.fileFontBrowser.setDragDropMode(self.browser.DragOnly)
        self.renderingChoice.listChanged.connect(self.fileFontBrowser.reset)
        self.fileBrowser.layout.addWidget(self.fileFontBrowser)
        self.fileFontId = None

        if fontlist.FontFinder.remote_supported():
            remoteLayout = QtWidgets.QVBoxLayout()
            self.remoteServer = QtWidgets.QLineEdit()
            self.remoteBrowser = QtWidgets.QWidget()
            self.remoteBrowser.setLayout(remoteLayout)
            self.remoteFontModel = FontListModel([], renderingChoice=
                                                        self.renderingChoice)
            self.remoteFontBrowser = self.remoteFontModel.treeView = \
                    QtWidgets.QTreeView()
            self.remoteFontBrowser.setModel(self.remoteFontModel)
            remoteLayout.addWidget(self.remoteServer)
            remoteLayout.addWidget(self.remoteFontBrowser)
            self.remoteServer.setPlaceholderText(_('Enter server name...'))
            self.remoteServer.editingFinished.connect(self._serverChanged)

        self.browser.setMouseTracking(True)
        self.browser.entered.connect(self._mouseOver)
        selModel = self.browser.selectionModel()
        selModel.currentChanged.connect(self._currentChanged)
        selModel.selectionChanged.connect(self._selectionChanged)
        delegate = FontDelegate(self.browser, fontDb=self.fontDb)
        self.browser.setItemDelegateForColumn(0, delegate)

        selModel = self.standardFontBrowser.selectionModel()
        selModel.currentChanged.connect(self._currentChanged)
        selModel.selectionChanged.connect(self._selectionChanged)
        delegate = FontDelegate(self.standardFontBrowser, fontDb=self.fontDb)
        self.standardFontBrowser.setItemDelegateForColumn(0, delegate)

        selModel = self.fileFontBrowser.selectionModel()
        selModel.currentChanged.connect(self._currentChanged)
        selModel.selectionChanged.connect(self._selectionChanged)
        delegate = FontDelegate(self.fileFontBrowser, fontDb=self.fontDb)
        self.fileFontBrowser.setItemDelegateForColumn(0, delegate)

        if fontlist.FontFinder.remote_supported():
            selModel = self.remoteFontBrowser.selectionModel()
            selModel.currentChanged.connect(self._currentChanged)
            selModel.selectionChanged.connect(self._selectionChanged)
            delegate = FontDelegate(self.remoteFontBrowser, fontDb=self.fontDb)
            self.remoteFontBrowser.setItemDelegateForColumn(0, delegate)

        selModel = self.fileBrowser.tree.selectionModel()
        selModel.currentChanged.connect(self._fileChanged)

        self.pile = QtWidgets.QVBoxLayout()

        self.selectTabs = QtWidgets.QTabWidget()
        self.selectTabs.addTab(self.browser, _('System fonts'))
        self.selectTabs.addTab(self.fileBrowser, _('Files'))
        if fontlist.FontFinder.remote_supported():
            self.selectTabs.addTab(self.remoteBrowser, _('Remote'))
        self.selectTabs.addTab(self.standardBrowser, _('Standard substitutions'))

        self.previewPane = QtWidgets.QWidget()
        self.previewLayout = QtWidgets.QVBoxLayout()
        self.previewPane.setLayout(self.previewLayout)

        self.fontGrid = fontgrid.FontGrid(self.charDb,
                                          fontDb=self.fontDb,
                                          langDb=self.langDb,
                                          renderingChoice=self.renderingChoice,
                                          histories=self.histories)

        self.infoPane = QtWidgets.QTextEdit()
        self.infoPane.setReadOnly(True)

        self.infoTable = FontInfoTable()

        self.license = QtWidgets.QTextEdit()
        self.license.setReadOnly(True)
        if hasattr(self.filterModel.filter, 'filterGroup'):
            self.activeFilters = QtWidgets.QTreeView()
            self.activeFilters.expandAll()
            self.activeFilters.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
            self.filterListModel = FilterListModel(self.filterModel.filter.filterGroup)
            self.filterListModel.childrenChanged.connect(self._activeFilterGroupChanged)
            self.activeFilters.setModel(self.filterListModel)
            self.filterModel.filter.filterGroup.changed.connect(
                self._updateFilterInfo)
            self.activeFilterToolbox = FilterListToolbox(self.activeFilters)
            self.activeFilterToolbox.addContextMenu(self.activeFilters)

        #self.pile.addLayout(self.filterModel.getFilterWidget(True))
        #self.pile.addWidget(self.filterModel.getFilterWidget())
        self.filterModel.filter.populateToolbar(searchToolbar)
        self.pile.addWidget(self.selectTabs)

        self._arrangePreviewPane()
        setResizeMode(self.browser.header(),
                      QtWidgets.QHeaderView.ResizeToContents)

        self.atlasToolbox.populateMenu(fontsMenu)

        self.fontToolbox = FontToolbox(self.browser, self.executor,
                                       atlasLibrary.categorization)
        self.fontToolbox.addContextMenu(self.browser)
        self.fontToolbox.disableActions()

        self.abouts = AboutDialogs(self)
        self.abouts.populateMenu(helpMenu)

        self.fontToolbox.populateMenu(self.editMenu)
        self.editMenu.addSeparator()
        self.fontGrid.toolbox.populateMenu(self.editMenu)

        if ENABLE_COMPLEX_FILTERS:
            self.searchesMenu = self.groupsMenu.addMenu(_("&Searches"))
            self.searchesMenu.aboutToShow.connect(self._repopulateSearches)
        self.categoriesMenu = self.groupsMenu.addMenu(_("&Categories"))
        self.categoriesMenu.aboutToShow.connect(self._repopulateCategories)

        # Toolbar
        mainToolbar.addAction(self.atlasToolbox.new)
        mainToolbar.addAction(self.fontToolbox.copyFont)
        mainToolbar.addSeparator()
        mainToolbar.addAction(self.atlasToolbox.sampler)
        mainToolbar.addAction(self.atlasToolbox.duel)

        # Status bar
        self.statusBar().setSizeGripEnabled(True)
        self.fontFamilyCount = QtWidgets.QLabel()
        self.fontFamilyCount.setTextFormat(Qt.PlainText)
        self.statusBar().addPermanentWidget(self.fontGrid.characterCount)
        self.statusBar().addPermanentWidget(self.fontFamilyCount)

        self.filterModel.modelReset.connect(self._updateFontFamilyCount)
        self.filterModel.rowsInserted.connect(self._updateFontFamilyCount)
        self.filterModel.rowsRemoved.connect(self._updateFontFamilyCount)
        self._updateFontFamilyCount()

        self._fontChangedTimer = QtCore.QTimer()
        self._fontChangedTimer.setSingleShot(True)
        self._fontChangedTimer.timeout.connect(self._showFontsInfoPerform)

        self._currentItem = None
        self._selectedItems = []

        self.interfaceArrangementName = None
        self.arrangementEnableAutosave = False

        atlasLibrary.typeAtlasFirstState.restoreWindowState(self)
        if not atlasLibrary.typeAtlasFirstState.arrangement:
            self.arrangeDocks()

    def resizeEvent(self, *args, **kwargs):
        self.rememberDockSizes()
        retval = super().resizeEvent(*args, **kwargs)
        self.fixDockSizes()
        return retval

    def rememberDockSizes(self):
        """Remember the dock sizes before resize."""
        if self.useSplitterUi:
            return
        size = self.size()
        for di in self.allDocksInfo:
            area = self.dockWidgetArea(di.dock)
            if area not in [Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea]:
                continue

            width = di.dock.size().width()
            proportion = width / size.width()
            if width != di.size and proportion != di.proportion:
                di.size = width
                di.proportion = proportion
            di.wasTabSelected = not di.dock.visibleRegion().isEmpty()

    def _arrangeDockByAction(self, checked=False):
        """Arrange the docks, depending on which menu item was clicked."""
        action = self.sender()
        self.arrangeDocks(action.data())

    @Slot()
    def _restoreArrangement(self, arrangement=None):
        """Restore saved arrangement, optionally taking it from the 
        action that triggered this slot."""
        if arrangement is None:
            action = self.sender()
            arrangement = action.data()

        if isinstance(arrangement, Mapping):
            arrangement = MainWindowSaveState.fromdict(arrangement)

        if self.arrangementEnableAutosave:
           self._saveArrangement(category='recent')

        self.arrangementEnableAutosave = False
        arrangement.restoreWindowState(self)

    @Slot()
    def _saveArrangementDialog(self):
        """Save the arrangement, asking the user where to save it
        using a dialog box."""
        dialog = GroupNameDialog(groupTypeName=_('Interface configuration'))
        if dialog.exec_():
            self._saveArrangement(label=dialog.groupName,
                                  icon=dialog.icon,
                                  color=dialog.colorName())

    def _saveArrangement(self, label: str=None, 
                               icon: str=None, color: str=None,
                               category: str='saved'):
        """Save the arrangement with the given label, icon and
        color."""
        state = MainWindowSaveState.fromWindow(self)
        stateData = state.todict()

        if label is None:
            arrangementName = self.interfaceArrangementName
            arrangement = interfaceArrangements.get(arrangementName) or {}
            if 'label' in arrangement:
                label = _(arrangement['label'])
            else:
                label = _('Custom interface')
            label += time.strftime(" %Y-%m-%d %H:%M:%S")

        stateData['label'] = label
        stateData['icon'] = icon
        stateData['color'] = color

        pile = self.atlasLibrary.arrangements.get_arrangements(category)
        pile.push(stateData)

    @Slot()
    def _editArrangements(self):
        """Edit the arrangements."""
        window = EditSavedArrangementsDialog(self.atlasLibrary.arrangements)
        self.atlasLibrary.openCustomWindow(window)

    @Slot()
    def _editSearches(self):
        """Edit the searches."""
        filterToolbox = self.filterModel.filter
        window = filterToolbox.getFilterDialog('searches',
                                               separateInstance=True)
        self.atlasLibrary.openCustomWindow(window)

    def arrangeDocks(self, arrangementName: str='simple'):
        """Arrange the docks. The named arrangement is used. What it means
        is taken from the interfaceArrangements dictionary.

        See arrangeDocksCustom() for the meaning of dictionary entries.
        """

        if self.arrangementEnableAutosave:
           self._saveArrangement(category='recent')

        self.arrangementEnableAutosave = True
        arrangement = interfaceArrangements.get(arrangementName) or {}
        self.arrangeDocksCustom(
            useSplitter=arrangement.get('use-splitter', False),
            dockedFilters=arrangement.get('docket-filters', True),
            arrangement=arrangement)
        self.interfaceArrangementName = arrangementName

    def arrangeDocksCustom(self, useSplitter: bool=False,
                                 dockedFilters: bool=True,
                                 arrangement: Union[str, Mapping]=None):
        """Make a custom arragengement. Do not call this, it is called
        by arrangeDocks() with the parameters provided by
        the interfaceArrangements dict.

        The docks can use a splitter, and the filter windows can be docked
        instead of plain floating main windows. The arrangement dictionary
        also needs to be provided to be used for the dock configuration.
        """

        self.arrangementEnableAutosave = True
        filterToolbox = self.filterModel.filter

        if getattr(self, 'allDocksInfo', None):
            if self.useSplitterUi:
                for di in self.allDocksInfo:
                    index = self.infoTabs.indexOf(di.widget)
                    if index != -1:
                        self.infoTabs.removeTab(index)
            else:
                for di in self.allDocksInfo:
                    di.dock.widget().setParent(None)
                    self.removeDockWidget(di.dock)
                    di.dock.deleteLater()
                for filterDockName in ['languages', 'writing-system',
                                       'tags', 'categories', 'class']:
                    filterToolbox.undockifyFilterDialog(filterDockName)

        self.beginDockCreation()

        self._lastDock = {}
        self._firstDock = {}
        self.dockByName = {}
        self.allDocksInfo = []
        if arrangement is not None:
            if isinstance(arrangement, str):
                arrangement = interfaceArrangements.get(arrangement)
            self.customDockArrangement = arrangement.get('docks', {})
        else:
            self.customDockArrangement = {}

        if self.centralWidget():
            oldCentral = self.takeCentralWidget()
            oldCentral.deleteLater()
        if getattr(self, 'infoTabs', None) is not None:
            self.infoTabs.deleteLater()
            self.infoTabs = None
        if getattr(self, 'splitter', None) is not None:
            self.splitter.deleteLater()
            self.splitter = None

        main = QtWidgets.QWidget()
        main.setLayout(self.pile)

        if useSplitter:
            self.infoTabs = infoTabs = QtWidgets.QTabWidget()
            self.splitter = splitter = QtWidgets.QSplitter()

            splitter.addWidget(main)
            splitter.addWidget(infoTabs)
            splitter.setSizes([int(DEFAULT_FONTLIST_PROPORTION * 1000),
                               int((1 - DEFAULT_FONTLIST_PROPORTION) * 1000)])

            self.setCentralWidget(splitter)

        else:
            self.infoTabs = None
            self.setCentralWidget(main)

        self.useSplitterUi = useSplitter

        self.createDock('samples', self.previewPane, _('Overview'),
                        saveDockInnerState=self._savePreviewPaneState,
                        restoreDockInnerState=self._restorePreviewPaneState,
                        inner={'info-visible': True})
        self.createDock('characters', self.fontGrid, _('Characters'),
                        inner={'char-bar-visible': True})
        self.createDock('info-text', self.infoPane, _('Information'))
        self.createDock('info-table', self.infoTable, _('Features'))

        self.createDock('license', self.license, _('License'))
        self.createDock('char-info',
                        self.fontGrid.getCharBar(), _('Character info'),
                        hidden=True, hiddenInSimple=True)

        if not useSplitter and dockedFilters:
            for filterDockName in ['languages', 'writing-system',
                                   'tags', 'categories', 'class']:
                dialog = filterToolbox.getFilterDialog(filterDockName)
                self.createDock(filterDockName, dialog,
                                dialog.windowTitle(),
                                hidden=True, floating=True,
                                dockifiedFilterDialog=True)

        if hasattr(self.filterModel.filter, 'filterGroup'):
            self.createDock('filters', 
                            self.activeFilters, _('Active filters'))

        self.endDockCreation()

    def beginDockCreation(self):
        """Called before creating the docks."""
        self.pendingDocks = OrderedDict()

    def endDockCreation(self):
        """Called after creating the docks. This is used to queue the dock
        creation and reorder them according to the order in the mapping."""
        if self.pendingDocks:
            if self.customDockArrangement:
                order = {key: i for i, key in enumerate(self.customDockArrangement)}
                pendingDocks = (self.pendingDocks[key]
                                for key in sorted(self.pendingDocks,
                                                  key=lambda key:
                                                        order.get(key, 9999)))
            else:
                pendingDocks = self.pendingDocks.values()
            for args, kwargs in pendingDocks:
                self.createDockCustom(*args, **kwargs)
        self.fixDockSizes()

    def createDock(self, name: str, widget: QtWidgets.QWidget,
                         title: str,
                         *args, **kwargs) -> Optional[QtWidgets.QWidget]:
        """Create the given dock, or put if custom dock arrangement is used,
        queue the creation for when endDockCreation() is called. See
        the createDockCustom() for the documentation on arguments."""
        if self.customDockArrangement:
            kwargs = dict(kwargs, **self.customDockArrangement.get(name) or {})
            self.pendingDocks[name] = ((name, widget, title) + args, kwargs)
            return

        return self.createDockCustom(name, widget, title, *args, **kwargs)

    def createDockCustom(self, name: str, widget: QtWidgets.QWidget,
                               title: str, *,
                               area: int=Qt.RightDockWidgetArea,
                               tabbed: bool=True, floating: bool=False,
                               hidden: bool=False, hiddenInSimple: bool=False,
                               after: str=None, before: str=None,
                               inner: Mapping=None,
                               dockifiedFilterDialog: bool=False,
                               **kwargs) -> QtWidgets.QWidget:

        """Create a dock with custom parameters. Do not call this directly, use
        createDock, which may delay creation for reordering reasons.

        You need to provide a name, widget and title.

        You can specify an area, and whether the widget is tabbed, floating, or hidden
        To hide in splitter (non-dock mode), use hiddenInSimple=True.

        You can specify before and after which named dock it goes, for easy ordering.
        You can specify the inner state dictionary to restore it.

        If this is a filter dialog, pass dockifiedFilterDialog=True so we know to
        notify the filter toolbox (FontFilterModelFilters).
        """

        if self.useSplitterUi:
            if area != Qt.RightDockWidgetArea or hiddenInSimple:
                return widget

            dockInfo = DockInfo(name, None, widget, area,
                                tabbed, floating, hidden,
                                **kwargs)
            if inner is not None:
                dockInfo.restoreDockInnerState(inner)
            self.infoTabs.addTab(widget, title)
            self.allDocksInfo.append(dockInfo)
            self.dockByName[name] = dockInfo
            return widget

        widgetSize = widget.size()

        dock = QtWidgets.QDockWidget(title)
        dock.setObjectName('dock:'+name)
        dock.setWindowTitle(title)
        dock.setWidget(widget)

        dockInfo = DockInfo(name, dock, widget, area,
                            tabbed, floating, hidden,
                            **kwargs)
        if inner is not None:
            dockInfo.restoreDockInnerState(inner)

        self.allDocksInfo.append(dockInfo)
        self.dockByName[name] = dockInfo

        if area is None or hidden or floating:
            if area is None:
                hidden = True
                area = Qt.RightDockWidgetArea

            self.addDockWidget(area, dock)

            if floating:
                dock.setFloating(True)
                dock.resize(widgetSize)

            if hidden:
                dock.hide()
                dock.close()

            if dockifiedFilterDialog:
                filterToolbox = self.filterModel.filter
                filterToolbox.dockifyFilterDialog(name, dock)

            return dock

        self.addDockWidget(area, dock)

        if area in {Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea}:
            splitOrientation = Qt.Vertical
        else:
            splitOrientation = Qt.Horizontal

        if after is not None and after in self.dockByName:
            if tabbed:
                self.tabifyDockWidget(self.dockByName[after].dock, dock)
            else:
                self.splitDockWidget(self.dockByName[after].dock, dock,
                                     splitOrientation)

        elif before is not None and before in self.dockByName:
            if tabbed:
                self.tabifyDockWidget(dock, self.dockByName[before].dock)
            else:
                self.splitDockWidget(dock, self.dockByName[before].dock,
                                     splitOrientation)

        elif tabbed:
            if area in self._lastDock:
                self.tabifyDockWidget(self._lastDock[area], dock)
                self._firstDock[area].raise_()
            else:
                self._firstDock[area] = dock
                dockInfo.wasTabSelected = True

            self._lastDock[area] = dock

        if dockifiedFilterDialog:
            filterToolbox = self.filterModel.filter
            filterToolbox.dockifyFilterDialog(name, dock)

        return dock

    def fixDockSizes(self):
        """Call this after resize to fix the dock sizes, because Qt is horribly
        broken when it comes to dock sizing."""
        if not hasattr(self, 'resizeDocks'):
            return
        if self.useSplitterUi:
            return

        size = self.size()

        needResize = {Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea}

        for di in self.allDocksInfo:
            area = self.dockWidgetArea(di.dock)
            if area not in needResize:
                continue

            # If the tab wasn't selected, the recorded size is incorrect
            if not di.wasTabSelected:
                continue

            self.resizeDocks([di.dock],
                             [int(size.width() * di.proportion)],
                             Qt.Horizontal)
            needResize.discard(area)

    def _arrangePreviewPane(self):
        """Create the layout of the preview pane."""
        self.fontIcon = QtWidgets.QLabel()
        self.fontName = QtWidgets.QLabel()

        self.fontFileDragIcon = DragDropLabel()
        icon = getIcon('empty')
        if not icon.isNull():
            pixmap = icon.pixmap(self.options.infoIconSize)
            self.fontFileDragIcon.setPixmap(pixmap)
        else:
            self.fontFileDragIcon.setText('(o)')

        self.fontFileDragIcon.setCursor(Qt.OpenHandCursor)

        self.fontFile = QtWidgets.QLabel()
        self.fontFile.setTextFormat(Qt.PlainText)
        self.fontFile.setTextInteractionFlags(Qt.TextSelectableByMouse)
        #self.fileTypeIcon = QtWidgets.QLabel()
        #self.fileType = QtWidgets.QLabel()
        #self.fileType.setTextFormat(Qt.PlainText)
        #self.fontFormatIcon = QtWidgets.QLabel()
        #self.fontFormat = QtWidgets.QLabel()
        #self.fontFormat.setTextFormat(Qt.PlainText)

        self.outlineIcon = QtWidgets.QLabel()
        self.outlineText = QtWidgets.QLabel()
        self.outlineText.setTextFormat(Qt.PlainText)
        self.bitmapIcon = QtWidgets.QLabel()
        self.bitmapText = QtWidgets.QLabel()
        self.bitmapText.setTextFormat(Qt.PlainText)
        self.scalableIcon = QtWidgets.QLabel()
        self.scalableText = QtWidgets.QLabel()
        self.scalableText.setTextFormat(Qt.PlainText)

        self.writingSystemList = QtWidgets.QLabel()
        self.writingSystemList.setTextFormat(Qt.PlainText)
        self.writingSystemList.setTextInteractionFlags(Qt.TextSelectableByMouse)
        ###self.languageList = QtWidgets.QLabel()
        ###self.languageList.setTextFormat(Qt.PlainText)
        ###self.languageList.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.styleInfo = QtWidgets.QLabel()
        self.styleInfo.setTextFormat(Qt.PlainText)
        self.styleInfo.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.styleInfo.setWordWrap(True)
        self.hintingInfo = QtWidgets.QLabel()
        self.hintingInfo.setTextFormat(Qt.PlainText)
        self.hintingInfo.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.writingSystemList.setWordWrap(True)
        ###self.languageList.setWordWrap(True)

        fontLayout = QtWidgets.QHBoxLayout()
        fontLayout.addWidget(self.fontIcon)
        fontLayout.addWidget(self.fontName, 1)
        self.previewLayout.addLayout(fontLayout)

        fileLayout = QtWidgets.QHBoxLayout()
        fileLayout.addWidget(self.fontFileDragIcon)
        fileLayout.addWidget(self.fontFile, 1)

        #self.previewLayout.addWidget(self.fontFile)
        self.previewLayout.addLayout(fileLayout)

        #layout = QtWidgets.QHBoxLayout()
        #layout.addWidget(self.fileTypeIcon)
        #layout.addWidget(self.fileType)
        #layout.addWidget(self.fontFormatIcon)
        #layout.addWidget(self.fontFormat, 1)
        #self.previewLayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.outlineIcon)
        layout.addWidget(self.outlineText)
        layout.addWidget(self.bitmapIcon)
        layout.addWidget(self.bitmapText)
        layout.addWidget(self.scalableIcon)
        layout.addWidget(self.scalableText, 1)
        self.previewLayout.addLayout(layout)
        self.previewLayout.addWidget(self.writingSystemList)
        ###self.previewLayout.addWidget(self.languageList)
        self.previewLayout.addWidget(self.styleInfo)
        #self.previewLayout.addWidget(self.hintingInfo)

        self.preview = FontPreview(self.fontDb, self.langDb, self.charDb,
                                   renderingChoice=self.renderingChoice)
        self.previewLayout.addWidget(self.preview)
        self.previewInfoVisible = False

        self.preview.toolbar.addSeparator()
        self.previewInfoAction = self.preview.toolbar.addAction(
                                    getIcon('show-font-information'),
                                    _('Toggle information'))
        self.previewInfoAction.setCheckable(True)
        self.previewInfoAction.setChecked(True)
        self.previewInfoAction.toggled.connect(self._togglePreviewPaneInfo)

    @Slot(bool)
    def _togglePreviewPaneInfo(self, checked=True):
        """Hide all widgets in the preview layout, except for the
        preview."""
        for widget in list(layoutIterate(self.previewLayout, recursive=True,
                                         widgets=True)):
            if widget is self.preview:
                continue

            if checked:
                widget.show()
            else:
                widget.hide()

        self.previewInfoVisible = checked

    def _savePreviewPaneState(self) -> Mapping:
        """Return the save state of the preview pane."""
        return {'info-visible': self.previewInfoVisible}

    def _restorePreviewPaneState(self, state: Mapping, strict: bool=False):
        """Restore the state of the preview pane from the saved one."""
        if 'info-visible' not in state:
            return
        self.previewInfoAction.setChecked(state['info-visible'])

    @Slot()
    def _updateFilterInfo(self, *args, **kwargs):
        """Update the filter info, which updates the family count and
        the status bar, mostly. Call this after the filters have changed."""
        message = self.filterModel.filter.filterGroup.status_text()
        self.statusBar().showMessage(message)
        self._updateFontFamilyCount()

    @Slot()
    def _updateFontFamilyCount(self, *args):
        """Update the family font count. Called after the font model
        has changed (due to refiltering)."""
        text = _('{count} font families out of {total}').format(
                    total=self.model.rowCount(),
                    count=self.filterModel.rowCount())

        if hasattr(self.filterModel.filter, 'filterGroup'):
            filterCount = self.filterModel.filter.filterGroup.filter_count()
            if filterCount:
                suffix = _('{count} filters').format(count=filterCount)
                text = '{} [{}]'.format(text, suffix)

        self.fontFamilyCount.setText(text)

    @Slot(QtCore.QModelIndex)
    def _mouseOver(self, index):
        """Display status of the font we hovered over."""

        if index.isValid():
            item = index.data(FontItemRole)
            if item.is_style:
                message = _('Font {family}, style {style}: {filename}').format(
                                family=item.translate('family', textlang()),
                                style=item.translate('style', textlang()),
                                filename='%s [%s]' % (item.file, item.index))
            elif item.is_family:
                message = _('Font family {family}').format(
                                family=item.translate('family', textlang()))


        self.statusBar().showMessage(message)

    @Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def _fileChanged(self, current, previous):
        """The current file changed in the file browser. If a font, add it
        in the application, and display it."""

        if not current.isValid():
            return
        path = current.data(QtWidgets.QFileSystemModel.FilePathRole)
        if os.path.isdir(path):
            return

        if self.fileFontId is not None:
            self.fontDb.removeApplicationFont(self.fileFontId)
            self.fileFontId = None

        fontid = self.fontDb.addApplicationFont(path)
        if fontid == -1:
            self.fileFontModel.setFamilies([])
            return

        self.fileFontId = fontid

        fonts = []

        fontFiles = {}

        try:
            fontlist.crawl_font_file(path, fontFiles)
        except fontlist.NotSupportedError:
            pass

        hints = dict((fi.file, fi.formathint)
                     for famnam, famfiles in fontFiles.items()
                     for stynam, styfiles in famfiles.items()
                     for fi in styfiles)

        for familyName in self.fontDb.applicationFontFamilies(fontid):
            for styleName in self.fontDb.styles(familyName):
                filenames = fontFiles.get(familyName, {}).get(styleName)
                if not filenames:
                    filenames = [fontlist.FontFileDetectInfo(path, 0,
                                                             hints.get(path))]

                fonts.append(qfontlist.getFont(self.fontDb,
                                               familyName, styleName,
                                               filenames))
        families = list(fontlist.get_families(fonts))
        for family in families:
            qfontlist.updateFamilyInfo(self.fontDb, family)
            for style in family.styles:
                self.finder.fill_detailed_info(style)
        self.fileFontModel.setFamilies(families)
        self.fileFontBrowser.expandAll()

        selModel = self.fileFontBrowser.selectionModel()
        if self.fileFontModel.hasIndex(0, 0):
            firstFont = self.fileFontModel.index(0, 0)
            selModel.setCurrentIndex(firstFont, selModel.ClearAndSelect | selModel.Current)
            selModel.select(firstFont, selModel.ClearAndSelect | selModel.Current)

    @Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def _currentChanged(self, current, previous):
        """The current font changed in the font view.

        Update all the panes.
        """

        model = self.sender()
        selection = model.selection()

        self._selectionOrCurrentChanged(current, selection,
                                        previous=previous,
                                        changed='current')

    @Slot(QtModelProxies.QItemSelection, QtModelProxies.QItemSelection)
    def _selectionChanged(self, selected, deselected):
        """The selected fonts changed in the font view.

        Update all the panes."""

        model = self.sender()
        current = model.currentIndex()
        # The signal only gives us the newly selected
        selected = model.selection()

        self._selectionOrCurrentChanged(current, selected,
                                        deselected=deselected,
                                        changed='selection')

    def _selectionOrCurrentChanged(self, current: QtCore.QModelIndex,
                                         selected: QtModelProxies.QItemSelection,
                                         previous: QtCore.QModelIndex=None,
                                         deselected: QtModelProxies.QItemSelection=None,
                                         changed: str=None):
        """The current or the selected font changed. Update all the panes.

        What changed is specified with the changed arguemnt ('selection'
        or 'current')."""

        self._showFontsInfo(current.data(FontItemRole)
                                if current.isValid() else None,
                            [idx.data(FontItemRole)
                             for idx in selected.indexes()],
                            changed=changed)

    def _showFontsInfo(self, item: Optional[fontlist.FontLike],
                             selected: SequenceOf[fontlist.FontLike]=[],
                             changed: str=None):
        """Show the info for the given current and selected fonts,
        updating all the panes. Called when the selection or current has
        changed.

        What changed is specified with the changed arguemnt ('selection'
        or 'current').

        The update is delayed with a timer using _showFontsInfoPerform().
        """

        if item is None:
            if selected:
                item = selected[0]

        if item is None:
            self.fontToolbox.disableActions()
            return

        if not selected:
            selected = [item]

        if (item is self._currentItem and
            all(x is y for x, y
                in zip_longest(selected, self._selectedItems))):
            return

        self._currentItem = item
        self._selectedItems = selected

        # Using a timer to call _showFontsInfoPerform, as Qt would
        # send two separate signals for every change, and we need
        # to do the heavy lifting once, especially the character
        # map. Using zero seconds ought to be enough, though it
        # relies on an implementation detail, no matter how certain.
        self._fontChangedTimer.start(0)

    @Slot()
    def _showFontsInfoPerform(self):
        """Actually perform the update of all panes initiated by
        _showFontsInfo()."""

        item = self._currentItem
        selected = self._selectedItems

        self.rememberDockSizes()
        extended = item.extended()

        fileFormat = item.file_format_info
        fontFormat = item.font_format_info

        sz = self.options.infoIconSize

        self.fontName.setText(item.translate('fullname', textlang()))

        self.fontIcon.setPixmap(getIcon('font-item-' +
                                        fontFormat.icon).pixmap(sz))
        self.fontIcon.setToolTip('%s %s' % (
            getIconHtml(fontFormat.icon, sz),
            htesc(item.fontformat)
        ))

        files = list(item.files(details=True))

        if files:
            fontFileText = str(files[0])
            if len(files) > 1:
                fontFileText += ' ' + _('...and %d others') % (
                                            len(files) - 1, )
            self.fontFile.setText(fontFileText)
            self.fontFile.setToolTip('\n'.join(str(fi) for fi in files))
        else:
            self.fontFile.setText('')
            self.fontFile.setToolTip('')

        urls = OrderedSet()
        for fi in files:
            if fi.file:
                if item.remote:
                    url = QtCore.QUrl(item.file)
                else:
                    url = QtCore.QUrl.fromLocalFile(item.file)
                urls.add(url)

        if urls:
            mime = QtCore.QMimeData()
            mime.setUrls(list(urls))
            self.fontFileDragIcon.setDragMimeData(mime)

        fileIcon = getIcon('font-file-' + fileFormat.icon)
        if not fileIcon.isNull():
            filePixmap = fileIcon.pixmap(self.options.infoIconSize)
            self.fontFileDragIcon.setPixmap(filePixmap)
        else:
            self.fontFileDragIcon.setText('(o)')
        self.fontFileDragIcon.setToolTip('%s %s' % (
            getIconHtml(fileFormat.icon, sz),
            htesc(fileFormat.name)
        ))

        #self.fileTypeIcon.setPixmap(getIcon(fileFormat.icon).pixmap(sz))
        #self.fileType.setText(fileFormat.name)

        #self.fontFormatIcon.setPixmap(getIcon(fontFormat.icon).pixmap(sz))
        #self.fontFormat.setText(item.fontformat + ' font')

        if item.outline:
            self.outlineIcon.setPixmap(getIcon('outline').pixmap(sz))
            self.outlineText.setText(_('Outline'))
            self.bitmapIcon.clear()
            self.bitmapText.clear()
        else:
            self.outlineIcon.clear()
            self.outlineText.clear()
            self.bitmapIcon.setPixmap(getIcon('bitmap').pixmap(sz))
            self.bitmapText.setText(_('Bitmap'))

        if item.scalable:
            self.scalableIcon.setPixmap(getIcon('scalable').pixmap(sz))
            self.scalableText.setText(_('Scalable'))
        else:
            self.scalableIcon.clear()
            self.scalableText.clear()

        self.writingSystemList.setText(self.model.getWritingSystemsText(item))
        ###self.languageList.setText(self.model.getLanguageListText(item))
        self.styleInfo.setText(self.model.getStyleInfoText(item))

        # These appear to have been removed from FontConfig
        ##self.hintingInfo.setText(_('Anti-aliased - {antialias}, RGBA {rgba}. '
        ##                           'Hinted - {hinting}, style {hintstyle}. '
        ##                           'Autohinter - {autohinter}. '
        ##                           'LCD filter {lcdfilter}').format(
        ##                            antialias=
        ##                                _('yes') if item.antialias else _('no'),
        ##                            rgba=item.rgba,
        ##                            hinting=
        ##                                _('yes') if item.hinting else _('no'),
        ##                            hintstyle=item.hintstyle,
        ##                            autohinter=
        ##                                _('yes') if item.autohint else _('no'),
        ##                            lcdfilter=item.lcdfilter))


        #self.charMap.displayFont = font
        #self.charMap.update()
        self.license.setPlainText('%s\n\n%s' %
                                  (extended.copyright or '',
                                   extended.license or ''))

        self.selectedFontItem = item
        self.selectedFontExtended = extended

        self.preview.setFontItem(item, selected)
        self.fontGrid.setFontItem(item, selected)
        self.infoTable.setFontItem(item, selected)

        self.fontToolbox.enableActions()

        self._updateInfoPane(files=files)
        self.fixDockSizes()

    @Slot()
    def _repopulateSearches(self):
        """Repopulate the searches in the searches menu."""
        self._repopulateGroupsMenu(self.searchesMenu,
                                   datastore.FontSearch)

    @Slot()
    def _repopulateCategories(self):
        """Repopulate the categories in the categories menu."""
        self._repopulateGroupsMenu(self.categoriesMenu,
                                   datastore.FontCategory)

    def _repopulateGroupsMenu(self, menu: QtWidgets.QMenu, groupType: type):
        """Repopulate the groups of the given type in the given menu."""
        menu.clear()

        if menu is self.searchesMenu:
            action = menu.addAction(_('Delete or edit searches...'))
            action.triggered.connect(self._editSearches)
            menu.addSeparator()

        categorization = self.atlasLibrary.categorization
        groups = categorization.container(groupType)
        ## colors = {}

        for groupInfo in groups.info.values():

            action = menu.addAction(groupInfo.name)
            if groupInfo.icon:
                action.setIcon(getIcon(groupInfo.icon))

            ## if groupInfo.color:
            ##     num = next(_menu_item_nums)
            ##     objectName = 'groupmenuitem' + str(num)
            ##     colors[objectName] = groupInfo.color
            ##     action.setObjectName(objectName)

            action.setData(groupInfo)
            action.triggered.connect(self._groupActivated)

        ## if colors:
        ##     stylesheet = []
        ##     for objectName, colorName in colors.items():
        ##         backColor = QtGui.QColor(colorName)
        ##         foreColor = matchingInverseColor(backColor)
        ##         stylesheet.append(
        ##             'QMenu::item#%s { background-color: %s; color: %s; }'
        ##                 % (objectName, backColor.name(), foreColor.name()))
        ##
        ##     print('\n'.join(stylesheet))
        ##     self.menuBar().setStyleSheet('\n'.join(stylesheet))
        ## else:
        ##     self.menuBar().setStyleSheet('')

    @Slot()
    def _repopulateSavedInterfacesMenu(self):
        """Repopulate the saved interfaces in the interfaces menu."""
        menu = self.savedInterfacesMenu

        menu.clear()

        action = menu.addAction(getIcon('save-as'),
                                _('Save interface configuration...'))
        action.triggered.connect(self._saveArrangementDialog)

        action = menu.addAction(_('Delete or edit configurations...'))
        action.triggered.connect(self._editArrangements)

        arrangements = self.atlasLibrary.arrangements

        for category in ['saved', 'recent']:

            menu.addSeparator()

            for arrangement in arrangements.get_arrangements(category):
                action = menu.addAction(arrangement.get('label') or '-')
                if arrangement.get('icon'):
                    action.setIcon(getIcon(arrangement['icon']))
                action.setData(arrangement)
                action.triggered.connect(self._restoreArrangement)

    @Slot()
    def _groupActivated(self):
        """A group was activated. This slot needs to be initiated from the
        action for the given group (e.g. the category's menu item QAction)"""
        action = self.sender()
        group = action.data()
        if hasattr(group, 'apply_filter'):
            group.apply_filter(self.filterListModel.filterRoot)

    def _getInfoPackages(self, item: fontlist.FontLike,
                               files: SequenceOf[fontlist.FontFileType]=None):
        """Get information about the dpkg/rpm packages providing the
        selected font and its files and put it in the info pane."""
        numcmd = 0
        numres = 0
        packages = set()

        def callback(result):
            nonlocal numres
            numres += 1
            if result is not None:
                packages.update(result.values())
            if numcmd == numres and item is self.selectedFontItem:
                self._updateInfoPane(sorted(packages), files=files)

        callbacks = external.ResultCallbacks(callback)

        filenames = [fi.file for fi in files]

        for command in external.commands_providing(self.executor,
                                                   'find-files-packages'):
            numcmd += 1
            command.find_files_packages(filenames, callbacks=callbacks)

    def _updateInfoPane(self, packages: IterableOf[external.PackageResult]=None,
                              files: SequenceOf[fontlist.FontFileType]=None):

        """Update the information pane with the font information.

        This optionally includes rpm/deb packages and font files."""

        item = self.selectedFontItem
        extended = self.selectedFontExtended

        fileFormat = item.file_format_info
        fontFormat = item.font_format_info

        if packages is None:
            self._getInfoPackages(item, files=files)

        text = []
        text.append('<h1>{fontname}</h1>'.format(
            css=htesc(qFontToCss(self.preview.font)),
            fontname=htesc(item.translate('fullname', textlang()) or
                            (item.translate('family', textlang()) + ' ' +
                             item.translate('style', textlang())))))

        for sample in self.langDb.sample_texts_font(item):
            text.append('<h2 style="{css}">{sample}</h2>'.format(
                        css=htesc(qFontToCss(self.preview.font,
                                             self.preview.fontItem)),
                        sample=sample))
            text.append('<h3 style="{css}">{sample}</h3>'.format(
                        css=htesc(qFontToCss(self.preview.font,
                                             self.preview.fontItem)),
                        sample=sample))
            break

        basic_info = [
                (_('Family'), item.translate('family', textlang())),
                (_('Style'), item.translate('style', textlang())),
                (None, None),
                (_('Classification'), self.model.getStyleInfoText(item)),
        ]
        if extended:
            basic_info.extend([
                (_('Version'), extended.version),
                (_('Description'), extended.description),
                (_('Designer'), extended.designer),
                (_('Manufacturer'), extended.manufacturer),
                (None, None),
                (_('Copyright'), extended.copyright),
            ])

        #if item.embedding is not opentype.NO_EMBEDDING_INFO:
        #    basic_info.extend([
        #        (_('Embedding'), '. '.join(map(_, item.embedding.texts()))),
        #    ])

        for key, value in basic_info:

            if not key:
                text.append('<br>')
                continue
            if not value:
                continue

            text.append('''<span style="font-weight: bold;">{key}:</span>
                            {value}<br>'''.format(
                                    key=htesc(key),
                                    value=htesc(value)))

        if item.embedding is not opentype.NO_EMBEDDING_INFO:
            embedding = '. '.join(map(_, item.embedding.texts()))
            embedding_detail = ["%s: %s" % (_(text), _(desc))
                                for text, desc
                                    in zip(item.embedding.texts(),
                                           item.embedding.descriptions())]

            embedding_detail.extend(("\u26a0 %s: %s" % (
                                        _('Warning'),
                                        _(opentype.EMBEDDING_WARNING))
                                     ).split('\n\n'))


            embedding_detail = '\n\n'.join('\n'.join(textwrap.wrap(paragraph))
                                           for paragraph in embedding_detail)

            text.append('''<span title="{tooltip}"><span
                                 style="font-weight: bold;">{key}:</span>
                            {value}</span><br>'''.format(
                                    tooltip=htesc(embedding_detail),
                                    key=H_('Embedding'),
                                    value=htesc(embedding)))



        if item.panoseclass:
            text.append('<h4>{label}</h4>'.format(
                                label=H_('PANOSE information')))
            text.append('<ul>')
            text.append('<li>{name}: {value}</li>'.format(
                            name=H_('Number'),
                            value=item.panoseclass.string()))
            for panprop in item.panoseclass:
                text.append('<li>{name}: {value}</li>'.format(
                                name=H_(panprop.fieldname),
                                value=panprop.text(translate=H_)))
            text.append('</ul>')

        text.append('<h3>{label}</h3>'.format(label=H_("Files")))

        text.append('''<span style="font-weight: bold;">{label}</span>:
                            {icon} {format}<br>'''.format(
                        label=H_('Font format'),
                        icon=getIconHtml(fontFormat.icon,
                                         self.options.infoIconSize),
                        format=_(fontFormat.description)))

        text.append('''<span style="font-weight: bold;">{label}</span>:
                            {icon} {format}<br>'''.format(
                        label=H_('File format'),
                        icon=getIconHtml(fileFormat.icon,
                                         self.options.infoIconSize),
                        format=_(fileFormat.description)))
        if item.comp and item.comp in fontlist.compression_extensions:
            compInfo = fontlist.compression_extensions[item.comp]
            text.append('''<span style="font-weight: bold;">{label}</span>:
                            {icon} {format}<br>'''.format(
                        label=H_('Compression'),
                        icon=getIconHtml(compInfo.icon,
                                         self.options.infoIconSize),
                        format=_(compInfo.description)))
        

        text.append('<span style="font-weight: bold;">{label}:</span>'.format(
                        label=H_('Glyph format')))
        if item.outline:
            text.append('{icon} {text}'.format(
                        icon=getIconHtml('outline', self.options.infoIconSize),
                        text=H_('Outline')))

        else:
            text.append('{icon} {text}'.format(
                        icon=getIconHtml('bitmap', self.options.infoIconSize),
                        text=H_('Bitmap')))
        if item.scalable:
            text.append('{icon} {text}'.format(
                        icon=getIconHtml('scalable', self.options.infoIconSize),
                        text=H_('Scalable')))

        #fileicon = getIconHtml('font-x-generic', self.options.infoIconSize)
        text.append('<ul>')

        if files is None:
            files = item.files(details=True)

        for fi in files:
            if fi.metrics:
                fileicon = getIconHtml('font-file-metrics',
                                       self.options.infoIconSize)
            else:
                fileicon = getIconHtml('font-file-' +
                                       fi.style.file_format_info.icon,
                                       self.options.infoIconSize)
            text.append('<li>{icon} {file}</li>'.format(
                            icon=fileicon, file=fi))
        text.append('</ul>')
       
        if packages:
            text.append('<ul>')
            for package in packages:
                packformat = external.package_formats.get(package.format)
                text.append('<li>{icon} {name}</li>'.format(
                                icon=getIconHtml(packformat.icon,
                                                 self.options.infoIconSize)
                                     if packformat else '',
                                name=package.name))
            text.append('</ul>')

        ##if packages is None:
        ##    text.append(getIconHtml('process-working',
        ##                            self.options.infoIconSize))

        if item.personal:
            text.append('<p>{icon} {note}</p>'.format(
                            icon=getIconHtml('emblem-personal',
                                             self.options.infoIconSize),
                            note=_('This is a personal font, installed '
                                   'locally in the current user account.')))

        text.append('<h3>{label}</h3>'.format(label=H_('Writing systems')))

        for ws in sorted(getattr(item, 'writingSystems', ())):
            text.append('''<span style="font-weight: bold;">{name}</span>
                           [<span style="{css}">{sample}</span>]; '''.format(
                    name=self.fontDb.writingSystemName(ws),
                    sample=self.fontDb.writingSystemSample(ws),
                    css=qFontToCss(self.preview.font)))

        if self.fontGrid.model.fontCharBlocks:
            text.append('<h3>{label}</h3>'.format(label=H_('Unicode support')))
            available = self.fontGrid.model.fontCharBlocks
            available = sorted(available)

            #if available:
            #    for block in available:
            #        if block.end > 0xffff:
            #            text.append('%08X-%08X ' % (block.start, block.end))
            #        else:
            #            text.append('%04X-%04X ' % (block.start, block.end))
            #    text.append('<br>')

            scriptBlocks = []
            for script in self.charDb.scriptorder:
                for block in self.charDb.scripts[script]:
                    scriptBlocks.append(block)

            unicodeBlocks = self.charDb.unicode_blocks
            unicodeBlocks = blockmath.overlapping_blocks(unicodeBlocks,
                                                         available, True)
            scriptBlocks = blockmath.overlapping_blocks(scriptBlocks,
                                                        available, True)
            scripts = OrderedSet(s.name for s in scriptBlocks)

            if scripts:
                text.append('''<span style="font-weight: bold;">{key}:</span>
                                '''.format(key=H_("Scripts")))

                for script in scripts:
                    script = self.langDb.script_name(script, chardb=self.charDb)
                    text.append(htesc(script) + '; ')
                text.append('<br>')

            if unicodeBlocks:
                text.append('''<span style="font-weight: bold;">{key}:</span>
                                '''.format(key=H_("Blocks")))
                for block in unicodeBlocks:
                    text.append(htesc(block.name) + '; ')
                text.append('<br>')

        text.append('<h3>{label}</h3>'.format(label=H_('Languages')))

        text.append('<ul>')
        for lang in item.lang:
            countryflag = self.langDb.guess_country_flag(lang)
            text.append('<li>')
            if countryflag:
                text.append(getIconHtml('flags/' + countryflag,
                                        self.options.infoFlagSize) + ' ')
            localeName = self.langDb.language_name(lang, LOCALE_NAME)
            nativeName = self.langDb.language_name(lang, NATIVE_NAME)
            text.append("%s (%s)" % (localeName, lang))
            if nativeName and nativeName != lang.partition('-')[0]:
                text.append(' [<span style="{css}">{langname}</span>]'.format(
                                css=htesc(qFontToCss(self.preview.font)),
                                langname=nativeName))

            text.append('</li>')
        text.append('</ul>')

        self.infoPane.setText('\n'.join(text))

    @Slot(int)
    def _standardFontsRequested(self, index: int):
        """User requested display of standard fonts, with the given combo box
        index. Get the standard constant, and display it."""
        chosen = self.chosenStandard.itemData(index)
        if chosen is None:
            self.standardModel.setFamilies([])
            return

        debugmsg("Loading standard font substitutions...")
        standardFamilies = list(self.finder.standard_families(chosen))

        debugmsg("Filling detailed font info...")
        for family in standardFamilies:
            qfontlist.updateFamilyInfo(self.fontDb, family)
            for style in family.styles:
                self.finder.fill_detailed_info(style)

        debugmsg("Loading feature sets...")
        standardFeatureSets = fontlist.FeatureSets(standardFamilies)
        debugmsg("DONE.")

        self.standardModel.setFamilies(standardFamilies, standardFeatureSets)

    @Slot()
    def _serverChanged(self):
        """User requested a remote server. Connect and get fonts from it."""
        server = self.remoteServer.text()
        if not server:
            self.remoteFontModel.setFamilies([])
            return
        debugmsg("Loading remote fonts...")
        finder = fontlist.FontFinder(remote_server=server,
                                     executor=self.executor)
        families = list(finder.families())
        debugmsg("Filling detailed font info...")
        for family in families:
            for style in family.styles:
                self.finder.fill_detailed_info(style)

        debugmsg("Loading feature sets...")
        remoteFeatureSets = fontlist.FeatureSets(families)
        debugmsg("DONE.")

        self.remoteFontModel.setFamilies(families, remoteFeatureSets)

    @Slot(QtCore.QModelIndex, object)
    def _activeFilterGroupChanged(self, index: QtCore.QModelIndex,
                                        groupItem: fontmodels._FilterItem):
        """"Filter group changed. Auto-expand it."""
        #self.activeFilters.expandToDepth(item.depth)
        self.activeFilters.expand(index)

    closed = Signal()

    def closeEvent(self, event):
        r = super().closeEvent(event)
        if event.isAccepted():
            self.closed.emit()
        return r


class SplashScreen(QtWidgets.QSplashScreen):

    """TypeAtlas splash screen."""

    granularity = 10

    def __init__(self):
        now = datetime.datetime.now()
        if (now.year >> 8 and now.month & 0b11111 == 0b100 and
            now.hour < 0xc and now.day == 0x1):
            splashIcon = getImage('splash-typeatlas-archaic')
        else:
            splashIcon = getImage('splash')
        splashPixmap = splashIcon.pixmap(640, 480)
        super(SplashScreen, self).__init__(splashPixmap)

        self._lastRepaint = None
        self._progressValue = None
        self._progressMin = 0
        self._progressMax = 100
        self._progressMessage = None

    def setProgressDone(self):
        """Done with the progress."""
        self._progressMessage = None
        if self._progressValue is not None:
            self._progressValue = None
            self.repaint()

    def setProgressStatus(self, value: int,
                                maxValue: int=100, minValue: int=0, *,
                                message: str=None):
        """Set progress value"""
        self._progressValue = value
        self._progressMax = maxValue
        self._progressMin = minValue
        self._progressMessage = message

        last = self._lastRepaint
        if (last is None or last > value or
            (last - value) % self.granularity == 0):

            self._lastRepaint = value
            self.repaint()

    def drawContents(self, painter: QtGui.QPainter):
        """Draw an optional progress bar."""
        super().drawContents(painter)

        if self._progressValue is not None:
            style = self.style()

            opt = QtWidgets.QStyleOptionProgressBar()
            opt.initFrom(self)

            opt.rect = QtCore.QRect(QtCore.QPoint(150, 20), QtCore.QSize(150, 15))
            opt.progress = self._progressValue

            opt.minimum = self._progressMin
            opt.maximum = self._progressMax

            opt.textVisible = False
            opt.state = style.State_Enabled
            opt.invertedApparance = True

            style.drawControl(style.CE_ProgressBar, opt, painter, self)

            if self._progressMessage is not None:
                palette = self.palette()
                style = self.style()

                rect = QtCore.QRect(QtCore.QPoint(150, 40),
                                    QtCore.QSize(350, 20))
                style.drawItemText(painter, rect, Qt.AlignLeft, palette,
                                  True, self._progressMessage, palette.Text)



def typeatlasFonts():

    """Open TypeAtlas. This is our main entry point."""

    install_locales()
    #load_samples()
    #load_nonfree()
    #load_glass()
    app = QtWidgets.QApplication(sys.argv)

    # Loading the style after the application ensures the colour
    # scheme is properly loaded.
    if configuredStyle:
        QtWidgets.QApplication.setStyle(configuredStyle)

    # Python 3 is a broken downgrade from 2, and no longer supports Unicode
    # paths until we set the filesystem encoding, and so opening the splash
    # crashes TypeAtlas. Instantiating a widget sets the correct encoding for
    # us. Once we have monkeypatched the FS encoding, starting the splash
    # screen is safe, and won't be racist against non-English characters
    # found in the pathname of the splash any more.
    #
    # I've always thought that the design decision to destroy Unicode support
    # in Python 3 was idiotic, but whatever, deal with it.
    # Or use a real language like PHP.
    QtWidgets.QWidget()

    splashW = SplashScreen()
    splashW.show()
    app.processEvents()

    library = TypeAtlasLibrary.getInstance(splashW)
    splashW.finish(library.newTypeAtlasWindow())

    print(_('Started %s, licensed under %s')
                % (_(proginfo.PROGRAM_NAME) + ' ' + proginfo.VERSION,
                   proginfo.LICENSE), file=sys.stderr)

    print(_('Using Qt %s toolkit with %s bindings')
                % (compat.QT_VERSION, compat.QT_BINDINGS), file=sys.stderr)

    app.exec_()


if __name__ == '__main__':
    typeatlasFonts()
