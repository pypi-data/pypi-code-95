# -*- coding: utf-8 -*-
#
#    GlyphAtlas Character Selector and Character Map
#    Copyright (C) 2021 Milko Krachounov
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

import sys
import binascii
from collections import OrderedDict, ChainMap, namedtuple
from collections.abc import Hashable
from functools import partial

from typeatlas.compat import QtCore, QtGui, QtWidgets, QtModelProxies
from typeatlas.compat import Qt, Slot, Signal, setResizeMode
from typeatlas.compat import configuredStyle, usesPySide

from typeatlas.guicommon import FontRenderingChoice
from typeatlas.charinfo import CharacterDatabase, UNICODE_DATA_FIELDS
from typeatlas.langutil import LanguageDatabase, install_locales
from typeatlas.datastore import MetadataCache
from typeatlas.options import Options

from typeatlas.uitools import QtExecutor
from typeatlas.uitools import setDefaultFontFamilies
from typeatlas.uitools import getIcon, getImage

from typeatlas.util import OrderedSet, sorteddict, bytedata_to_int, debugmsg
from typeatlas.util import disable_debug, MaybeIterable, generic_type
from typeatlas.langutil import _, N_, H_, textlang
from html import escape as htesc

from typeatlas import compat, proginfo
from typeatlas import fontlist, fontgrid, qfontlist
from typeatlas import charsets
import typeatlas
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
else:
    if TYPE_CHECKING:
        import typeatlas.gui

Union = generic_type('Union')
Optional = generic_type('Optional')


LibraryLike = 'Union[GlyphAtlasLibrary, typeatlas.gui.TypeAtlasLibrary]'


class GlyphAtlasLibrary(QtWidgets.QWidget):

    """Manager of main GlyphAtlas windows, shared attributes between
    those instances. A reduced version of TypeAtlasLibrary, which can
    be used in its place"""

    instance = None

    def __init__(self, splash: QtWidgets.QSplashScreen=None,
                       atlasLibrary: 'typeatlas.gui.TypeAtlasLibrary'=None,
                       *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.options = Options.getInstance()
        if atlasLibrary is not None:
            self.options.load()

        self.metadataCache = MetadataCache.getInstance()

        self.charDb = CharacterDatabase.getInstance()
        self.langDb = LanguageDatabase.getInstance()
        self.fontDb = QtGui.QFontDatabase()

        #if splash is not None:
        #    splash.showMessage(_('Loading cache...'), splash.msgAlignment)
        #debugmsg("Loading cache...")
        #
        #self.metadataCache.load()

        #if splash is not None:
        #    splash.showMessage(_('Loading font list...'), splash.msgAlignment)
        #debugmsg("Loading font list...")
        #self.executor = executor = QtExecutor(self.options.executablePaths,
        #                                      parent=self)
        #self.finder = qfontlist.QtFontFinder(self.fontDb, executor=executor,
        #                                     metadata_cache=self.metadataCache)
        #self.fontFamilies = list(self.finder.families())
        #setDefaultFontFamilies(self.fontFamilies)

        #debugmsg("Saving metadata cache...")
        #self.metadataCache.autosave()

        self.executor = executor = QtExecutor(self.options.executablePaths,
                                              parent=self)
        self.finder = qfontlist.QtFontFinder(self.fontDb, executor=executor)

        if splash is not None:
            splash.showMessage(_('Populating unicode info...'),
                               splash.msgAlignment)
        debugmsg("Populating unicode info...")
        self.charDb.add_registries()
        self.charDb.populate(download=False, deep=True)
        if splash is not None:
            splash.showMessage(_('Populating language info...'),
                               splash.msgAlignment)
        debugmsg("Populating language info...")
        self.langDb.populate()

        debugmsg("DONE.")

        self.openWindows = set()

    @classmethod
    def getInstance(cls, *args, fallback: bool=True,
                                create: bool=True, **kwargs) -> LibraryLike:
        """Get the singleton instance of the class. If create=False is
        passed, it is not created if it does not exist and None is
        returned.

        By default, we attempt to get the TypeAtlas library instead.
        If that is not OK, pass fallback=False.
        """
        if cls.instance is None:

            if fallback:
                from typeatlas.gui import TypeAtlasLibrary
                instance = TypeAtlasLibrary.getInstance(create=False)
                if instance is not None:
                    return instance

            if not create:
                return None

            cls.instance = cls(*args, **kwargs)
        return cls.instance

    @Slot()
    def quit(self):
        """Quit GlyphAtlas."""
        sys.exit(0)

    @Slot()
    def newGlyphAtlasWindow(self):
        """Open a new main GlyphAtlas window."""
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
        window.deleteLater()
        if not self.openWindows:
            self.quit()


class GlyphSelectorMixin():

    """A mixin used for our character map main windows, both of a standalone
    GlyphAtlas, and of a character selector dialog - CharSelectDialog."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.charsetSubmenus = {}

        self.encoding = None
        self.interpretation = None
        self.charsetCodeInfo = None

        self.selectFromFont = False

        self._interpretationActions = []

    def getCharsetSubmenu(self, key: Hashable, name: str) -> QtWidgets.QMenu:
        """Get a character set submenu."""
        if key in self.charsetSubmenus:
            return self.charsetSubmenus[key]

        result = self.charsetMenu.addMenu(name)
        self.charsetSubmenus[key] = result
        return result

    def populateCharsetMenu(self):
        """Populate the character sets menu."""
        charsetMenu = self.charsetMenu

        for name, encoding in ChainMap(charsets.morse_codes,
                                       charsets.encodings).items():

            if encoding.morse:
                submenu = self.getCharsetSubmenu('morse', _('Telegraphy'))
            else:
                submenu = self.getCharsetSubmenu(encoding.category(),
                                                 encoding.category_label())
            action = submenu.addAction(encoding.label())
            iconName = encoding.get_icon()
            if iconName is not None:
                action.setIcon(getIcon(iconName))
            action.setData(encoding)
            action.triggered.connect(self._charsetClicked)

        action = charsetMenu.addAction(_('Unicode'))
        action.setData(None)
        action.triggered.connect(self._charsetClicked)

    def populateInterpretationMenu(self):
        """Populate the interpretations menu."""
        menu = self.interpretationMenu

        for group in charsets.InterpretationGroup.available:
            actionGroup = QtWidgets.QActionGroup(self)
            if group.exclusive:
                actionGroup.setExclusive(True)

            submenu = menu.addMenu(_(group.label))
            if group.icon is not None:
                submenu.setIcon(getIcon(group.icon))

            for interpretation in group.interpretations:
                action = submenu.addAction(_(interpretation.label))
                if interpretation.icon is not None:
                    action.setIcon(getIcon(interpretation.icon))
                action.setData(interpretation)
                action.triggered.connect(self._interpretationClicked)

                action.setCheckable(True)
                if interpretation.default:
                    action.setChecked(True)
                actionGroup.addAction(action)

                self._interpretationActions.append(action)

        self._interpretationClicked()

    def _charsetClicked(self):
        """A new character set was selected, switch to it."""
        action = self.sender()
        #self.encoding = charsets.get_encoding(charset)
        self.encoding = action.data()
        if self.interpretation and self.encoding is not None:
            self.encoding = self.encoding.interpretation(self.interpretation)
        self.updateFontGrid()

    def _interpretationClicked(self):
        """A new interpretation set was selected, switch to it."""
        selected = []
        for action in self._interpretationActions:
            if action.isChecked():
                selected.append(action.data())

        self.interpretation = charsets.InterpretationSet(selected)

        if self.encoding is None:
            return

        self.encoding = self.encoding.interpretation(self.interpretation)
        self.updateFontGrid()

    def updateFontGrid(self):
        """Update the font grid character map widget."""
        encoding = self.encoding
        charDb = self.atlasLibrary.charDb

        if encoding is None or encoding.unicode:
            if self.selectFromFont:
                self.fontGrid.setFontItem(self.fontItem)
            else:
                self.fontGrid.setFontItem(self.fontItem,
                                          charBlocks=charDb.script_blocks)
            self.charsetCodeInfo = None
            return

        if encoding.morse:
            characters = OrderedDict((alpha,
                                      fontgrid.CharSymbolInfo(
                                          alpha,
                                          display=morse,
                                          encoding=encoding))
                                     for alpha, morse
                                        in encoding.codepoint_telegraph_codes().items())

            self.charsetCodeInfo = characters
            self.fontGrid.setFontItem(self.fontItem, characters=characters)
            return

        codepointBytes = encoding.codepoint_bytes(charDb)
        codepointBytes = sorteddict(codepointBytes, valuekey=bytedata_to_int)

        characters = OrderedDict((code,
                                  fontgrid.CharSymbolInfo(code, bytedata,
                                                          encoding=encoding))
                                 for code, bytedata in codepointBytes.items())

        self.charsetCodeInfo = characters
        self.fontGrid.setFontItem(self.fontItem, characters=characters)

    @Slot()
    def selectGenericSymbol(self):
        """Switch the character selector to generic symbol (non-font specific).
        For example, letters, regular emojis.

        This tends to display all characters from the character set, or from
        unicode.
        """
        self.selectFromFont = False
        self.updateFontGrid()

    @Slot()
    def selectSymbolFromFont(self):
        """Switch the character selector to a font-specific symbol, likely from
        a Unicode private use area. The user is asked for a font with a dialog.

        This tends to display only the characters from the font.
        """
        return self._chooseFont(True)

    @Slot()
    def selectDisplayFont(self):
        """Switch the display font in general symbol mode after asking the
        user. This opens a dialog."""
        return self._chooseFont(False)

    def _chooseFont(self, selectFromFont: bool=False, force: bool=False):
        """Change the font, asking the user in a dialog.

        If selectFromFont=True is passed, it means we're switching to
        symbol-from-font mode (likely PUA symbol), whereas if it is
        False, we simply change the default display font, and still
        select a general symbol from anywhere.

        If force=True, this allows us to change the display font if
        we're in symbol-from-font mode.
        """
        item = self.fontItem

        if selectFromFont:
            title = _("Select symbol from a specific font")
        else:
            if self.selectFromFont and not force:
                QtWidgets.QMessageBox.critical(
                    self, _("Cannot change display font"),
                          _("You are selecting a symbol from a font, "
                            "the display font cannot be changed"))
                return

            title = _("Choose display font")

        initial = self.atlasLibrary.fontDb.font(item.family, item.style,
                                                self.renderingChoice.gridSize)
        res = QtWidgets.QFontDialog.getFont(initial)

        if usesPySide:
            ok, qfont = res
        else:
            qfont, ok = res

        if ok:
            self.fontItem = self.atlasLibrary.finder.substitute(
                                    qfont.family(), qfont.styleName())
            self.selectFromFont = selectFromFont
            self.updateFontGrid()


class GlyphAtlas(GlyphSelectorMixin, QtWidgets.QMainWindow):

    """GlyphAtlas main window."""

    def __init__(self, atlasLibrary: 'LibraryLike'=None,
                       parent: QtWidgets.QWidget=None,
                       splash: QtWidgets.QSplashScreen=None):

        super().__init__(parent)

        if atlasLibrary is None:
            atlasLibrary = GlyphAtlasLibrary.getInstance(splash)

        self.resize(atlasLibrary.options.glyphAtlasSize)

        self.setWindowTitle(_("GlyphAtlas character map"))
        self.setWindowIcon(getIcon('glyphatlas'))

        mainMenu = self.menuBar()
        self.charsetMenu = mainMenu.addMenu(_("&Character set"))
        self.interpretationMenu = mainMenu.addMenu(_('&Alternative characters'))

        self.populateCharsetMenu()
        self.populateInterpretationMenu()

        self.atlasLibrary = atlasLibrary
        self.renderingChoice = FontRenderingChoice()

        self.fontGrid = fontgrid.FontGrid(atlasLibrary.charDb,
                                          fontDb=atlasLibrary.fontDb,
                                          langDb=atlasLibrary.langDb,
                                          renderingChoice=self.renderingChoice)

        self.setCentralWidget(self.fontGrid)
        self.fontItem = atlasLibrary.finder.substitute('sans-serif', 'Regular')

        self.updateFontGrid()

    closed = Signal()

    def closeEvent(self, event):
        r = super().closeEvent(event)
        if event.isAccepted():
            self.closed.emit()
        return r


SelectedCharacter = namedtuple('SelectedCharacter',
                               'codepoint char info encinfo generic fontitem')


def charToDict(charRes: SelectedCharacter, unicodeInfo: bool=False):
    """Convert a character to a dictionary for export.

    If unicodeInfo=True is passed, we also fetch unicode info about it."""

    result = {'codepoint': charRes.codepoint, 'char': charRes.char}
    if unicodeInfo:
        if charRes.info is not None:
            for field in UNICODE_DATA_FIELDS:
                if field == 'code':
                    continue
                result[field] = getattr(charRes.info, field)
        else:
            result.update(dict.fromkeys(UNICODE_DATA_FIELDS))

    if charRes.encinfo is not None:
        encinfo = charRes.encinfo

        if charRes.encinfo.encoding is not None:
            encoding = encinfo.encoding
            result['encoding'] = encoding.name
            result['multibyte'] = encoding.multibyte
            result['fixed'] = encoding.fixed
            result['charsize'] = encoding.charsize
            if encoding.morse:
                result['morse'] = encoding.alpha_codes.get(charRes.char)

        else:
            result['encoding'] = 'unknown'

        result['charvalue'] = encinfo.charvalue

        if encinfo.bytedata:
            result['bytes'] = binascii.b2a_base64(encinfo.bytedata).decode()
        else:
            result['bytes'] = None

    else:
        result['encoding'] = None

    if not charRes.generic:
        result['fontfamily'] = charRes.fontitem.family
        result['fontstyle'] = charRes.fontitem.style

    return result


def charToBytes(charRes: SelectedCharacter) -> bytes:
    """Convert charater to byte data, in the given encoding if one is passed."""
    if charRes.encinfo is None:
        return charRes.char.encode('utf8')
    elif (charRes.encinfo.encoding is not None and
            charRes.encinfo.encoding.morse):
        encoding = charRes.encinfo.encoding
        return encoding.alpha_codes.get(charRes.char).encode()
    else:
        return charRes.encinfo.bytedata


class CharSelectDialog(GlyphSelectorMixin, QtWidgets.QDialog):

    """A character selector dialog. Can be used withing TypeAtlas,
    within other Python programs, or from the command-line.

    You can configure the mode of the selector - whether to select
    multiple characters, which font to select from, do we use
    'select from font' mode for use with font-specific PUA symbols,
    what initial encoding to use, are encodings and symbol from
    font allowed to be changed.
    """

    def __init__(self, atlasLibrary: LibraryLike=None,
                       parent: QtWidgets.QWidget=None,
                       multipleChars: bool=False,
                       fontItem: fontlist.FontLike=None,
                       allowEncodings: bool=False, initialEncoding: str=None,
                       allowSymbolFromFontChange: bool=True,
                       selectFromFont: bool=False,
                       renderingChoice: FontRenderingChoice=None):

        super().__init__(parent)

        if atlasLibrary is None:
            atlasLibrary = GlyphAtlasLibrary.getInstance()

        self.resize(atlasLibrary.options.glyphAtlasSize)

        self.setWindowTitle(_("Select symbol or character"))
        self.setWindowIcon(getIcon('glyphatlas'))

        if renderingChoice is None:
            renderingChoice = FontRenderingChoice()

        self.atlasLibrary = atlasLibrary
        self.renderingChoice = renderingChoice

        self.fontGrid = fontgrid.FontGrid(atlasLibrary.charDb,
                                          fontDb=atlasLibrary.fontDb,
                                          langDb=atlasLibrary.langDb,
                                          renderingChoice=self.renderingChoice)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.fontGrid)

        if fontItem is None:
            fontItem = atlasLibrary.finder.substitute('sans-serif', 'Regular')
            selectFromFont = False

        self.fontItem = fontItem
        self.selectFromFont = selectFromFont

        self.fontGrid.toggleCharBar(False)
        if not multipleChars:
            self.fontGrid.view.setSelectionMode(self.fontGrid.view.SingleSelection)

        if initialEncoding is not None:
            self.encoding = charsets.get_encoding(initialEncoding)

        self.updateFontGrid()

        self.multipleChars = multipleChars
        self.allowEncodings = allowEncodings
        self.initialEncoding = initialEncoding

        self.buttons = buttons = QtWidgets.QDialogButtonBox()
        buttons.addButton(_('&Select'), buttons.AcceptRole)
        buttons.addButton(_('&Cancel'), buttons.RejectRole)

        if allowEncodings:
            charsetBut = buttons.addButton(_("Change &encoding..."),
                                           buttons.ActionRole)
            self.charsetMenu = QtWidgets.QMenu()
            charsetBut.setMenu(self.charsetMenu)
            self.populateCharsetMenu()

        if allowSymbolFromFontChange:
            fontSymBut = buttons.addButton(_("Symbol from &font..."),
                                           buttons.ActionRole)
            fontSymBut.clicked.connect(self.selectSymbolFromFont)

            genericBut = buttons.addButton(_("Generic symbols"),
                                           buttons.ActionRole)
            genericBut.clicked.connect(self.selectGenericSymbol)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.layout().addWidget(buttons)

    def _indexToResult(self, index: QtCore.QModelIndex) -> SelectedCharacter:
        """Get which character is selected for the given index."""
        code = index.data(fontgrid.CharCodeRole)
        info = self.atlasLibrary.charDb.info_by_code.get(code)
        if self.charsetCodeInfo:
            encinfo = self.charsetCodeInfo.get(code)
        else:
            encinfo = None
        return SelectedCharacter(code, chr(code), info, encinfo,
                                 not self.selectFromFont,
                                 self.fontItem)

    @classmethod
    def selectChar(cls, *args, **kwargs) -> Optional[MaybeIterable[SelectedCharacter]]:
        """Open a dialog for selecting a character, and return one or more character
        depending on the mode."""

        self = cls(*args, **kwargs)
        if self.exec_():
            selection = self.fontGrid.view.selectionModel()
            current = selection.currentIndex()
            selected = selection.selectedIndexes()

            if not self.multipleChars:
                if current.isValid():
                    return self._indexToResult(current)
                elif selected:
                    return self._indexToResult(selected[0])
                else:
                    return None
            else:
                if selected:
                    return [self._indexToResult(index) for index in selected]
                elif current.isValid():
                    return [self._indexToResult(current)]
                else:
                    return None

        return None


class SplashScreen(QtWidgets.QSplashScreen):

    """GlyphAtlas splash screen."""

    msgAlignment = Qt.AlignLeft | Qt.AlignBottom

    def __init__(self):
        splashIcon = getImage('splash-glyphatlas')
        splashPixmap = splashIcon.pixmap(640, 480)
        super(SplashScreen, self).__init__(splashPixmap)


def glyphatlasStandalone():

    """Open GlyphAtlas. This is our main entry point."""

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

    library = GlyphAtlasLibrary.getInstance(splashW, fallback=False)
    splashW.finish(library.newGlyphAtlasWindow())

    print(_('Started %s, licensed under %s')
                % (_(proginfo.PROGRAM_NAME) + ' ' + proginfo.VERSION,
                   proginfo.LICENSE), file=sys.stderr)

    print(_('Using Qt %s toolkit with %s bindings')
                % (compat.QT_VERSION, compat.QT_BINDINGS), file=sys.stderr)

    app.exec_()


def _glyphatlasCliChooserLoopMain(app: QtWidgets.QApplication,
                                  args: 'argparse.Namespace',
                                  library: 'LibraryLike'):

    """The in-mainloop part of the CLI char selector.

    This is executed within the main loop"""
    import json

    fontItem = None

    if args.font:
        fontItem = library.finder.substitute(args.font, args.style)

    result = CharSelectDialog.selectChar(library,
                                         initialEncoding=args.charset,
                                         allowEncodings=args.charsets,
                                         multipleChars=args.multiple,
                                         allowSymbolFromFontChange=
                                            not args.no_symbol_mode_change,
                                         selectFromFont=args.symbol_from_font,
                                         fontItem=fontItem)

    if result is None:
        return

    encodedOutput = False

    if args.result_type == 'json':
        charToOutput = partial(charToDict, unicodeInfo=args.verbose)

    elif args.result_type == 'codepoint':
        charToOutput = lambda charRes: str(charRes.codepoint)

    elif args.result_type == 'raw':
        encodedOutput = True

        def charToOutput(charRes):
            result = charToBytes(charRes)
            if args.delimiter == '\0' and result == b'\0':
                result = b''
            elif args.delimiter == '\n' and result == b'\n':
                result = b''
            return result

    elif args.result_type in ['base64', 'hex', 'hqx', 'qp', 'uu']:

        b2a = getattr(binascii, 'b2a_' + args.result_type)

        def charToOutput(charRes):
            result = charToBytes(charRes)
            result = b2a(result).decode('ascii').strip()
            if args.result_type in ['base64', 'uu']:
                result = result.rstrip('\n')
            return result

    if encodedOutput:
        if args.output is not None:
            output = open(args.output, 'ab' if args.append else 'wb')
        else:
            output = sys.stdout.buffer

    else:
        if args.output is not None:
            output = open(args.output, 'at' if args.append else 'wt',
                          encoding='utf8')
        else:
            output = sys.stdout

    if args.multiple:
        resultdata = [charToOutput(c) for c in result]
    else:
        resultdata = charToOutput(result)

    if args.result_type == 'json':
        json.dump(resultdata, output, indent=args.indent)
        output.write('\n')

    else:
        delimiter = args.delimiter
        if encodedOutput:
            delimiter = delimiter.encode('ascii')

        if args.multiple:
            output.write(delimiter.join(resultdata))
        else:
            output.write(resultdata)

        output.write(delimiter)

    #app.exit(0)


def glyphatlasCliChooser():

    """Run the CLI character selector. This is another entry point."""

    global argparse

    install_locales()
    import argparse
    import codecs

    parser = argparse.ArgumentParser(description=_("Select symbol or character"))

    parser.add_argument('--output', '-o',
                        default=None, help=_("write the output to file"))
    parser.add_argument('--append', action='store_true',
                        help=_("append to output"))

    parser.add_argument('--result-type', '-r',
                        choices=['json', 'codepoint', 'raw',
                                 'base64', 'hex', 'hqx', 'qp', 'uu'],
                        default='json',
                        help=_("choose a result mode to return the character(s)"))

    parser.add_argument('--delimiter', '-d', '--separator',
                        default='\n',
                        type=lambda s: codecs.unicode_escape_decode(s)[0],
                        help=_("use the given character or escape code as "
                               "delimiter instead of newline"))
    parser.add_argument('--null', '-0',
                        dest='delimiter', action='store_const',
                        const='\0',
                        help=_("use null byte as constant"))

    parser.add_argument('--indent', default=4, type=int,
                        help=_("indent the json to the given level"))
    parser.add_argument('--no-indent', '-I',
                        action='store_const', const=0,
                        dest='indent',
                        help=_("do not indent the json"))

    parser.add_argument('--verbose', '-v', default=0,
                        help=_("include more information"), action='count')

    parser.add_argument('--multiple', '-m', action='store_true', default=False,
                        help=_("select multiple characters"))
    parser.add_argument('--no-multiple', '-M', '--no-m', '--single',
                        action='store_false', dest='multiple', default=False,
                        help=_("select a single character"))

    parser.add_argument('--charset', '--encoding', '-C',
                        help=_("return a character in a given character set"))
    parser.add_argument('--charsets', '-U', '--legacy-encodings',
                        action='store_true', default=False,
                        help=_("select legacy encodings and character sets"))
    parser.add_argument('--no-charsets', '-u', '--unicode',
                        action='store_false', dest='charsets', default=False,
                        help=_("get unicode result"))

    parser.add_argument('--no-symbol-mode-change',
                        '--generic-symbol-only', '--disallow-font-symbols',
                        action='store_true',
                        help=_("select only generic or font-specific characters"))

    parser.add_argument('--font', '-F', help=_("choose a font"))
    parser.add_argument('--style', '-S',  help=_("choose a style"),
                        default="Regular")
    parser.add_argument('--symbol-from-font', action='store_true',
                        help=_("default to symbols from the specified font"))

    parser.add_argument('--force-symbol-from-font', action='store_true',
                        help=_("only select symbols from the specified font"))

    parser.add_argument('--debug', action='store_true',
                        help=_("leave debug enabled"))

    args = parser.parse_args()

    if args.force_symbol_from_font:
        args.symbol_from_font = True
        args.no_symbol_mode_change = True

    if not args.debug:
        disable_debug()

    app = QtWidgets.QApplication([sys.argv[0]])

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

    library = GlyphAtlasLibrary()
    #QtCore.QTimer.singleShot(0, partial(_glyphatlasCliChooserLoopMain,
    #                                     app, args, library))
    #app.exec_()
    _glyphatlasCliChooserLoopMain(app, args, library)


if __name__ == '__main__':
    glyphatlasStandalone()
