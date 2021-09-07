# -*- coding: utf-8 -*-
#
#    TypeAtlas Font Grid
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


"""Character map widget. Can be re-arranged into sample-viewing widget.

Includes tools for rendering individual characters (e.g. Emojis not
supported by the OS), and including an Emoji icon engine.
"""

from __future__ import division
from typeatlas.compat import QtCore, QtGui, QtWidgets, QtModelProxies
from typeatlas.compat import Qt, Slot, Signal, setResizeMode
try:
    from typeatlas.compat import QtSvg
except ImportError:
    QtSvg = None

import typeatlas
from typeatlas.util import OrderedSet, bytedata_to_int, debugmsg, warnmsgf
from typeatlas.util import generic_type
from typeatlas.uitools import Toolbox, qFontToCss, modelIterateChildrenRect
from typeatlas.uitools import getIconHtml, hasDarkBackground, TransposedModel
from typeatlas.uitools import RotatedHeaderView
from typeatlas.uitools import QuickSearch
from typeatlas.guicommon import FontRenderingChoice, CharInfoWidget, getIcon
from typeatlas.guicommon import CustomComboBox
from typeatlas.options import Options
from typeatlas.langutil import LanguageDatabase, textlang
from typeatlas.charinfo import CharacterDatabase
from typeatlas import charinfo, blockmath, osinfo, opentype, datastore
from itertools import chain
from functools import partial
from collections import Counter
from collections.abc import Mapping, Iterator
from html import escape as htesc
import re
import traceback
import functools
import numbers

try:
    from fontTools import ttLib
except ImportError:
    ttLib = None

from typeatlas.langutil import _, N_, H_

MutableSequenceOf = generic_type('MutableSequence')
SequenceOf = generic_type('Sequence')
MappingOf = generic_type('Mapping')
IterableOf = generic_type('Iterable')
SetOf = generic_type('Set')
TupleOf = generic_type('Tuple')
Optional = generic_type('Optional')
Union = generic_type('Union')


ID_THRESH = 22


PREVIEW_MAX_CODEPOINT = 256
BIG_FONT_THRESHOLD = 20000


CharCodeRole = Qt.UserRole
CellHeaderRole = Qt.UserRole + 1
SampleRendererRole = Qt.UserRole + 2
CharInfoTextRole = Qt.UserRole + 3
ModelFontInfoRole = Qt.UserRole + 4


class SvgFontSample(object):

    """Display a SVG font sample. Use fromSvgs to construct."""

    def __init__(self, sampleRenderers: 'SequenceOf[QtSvg.QSvgRenderer]',
                       antialias: bool=True):
        if len(sampleRenderers) != 1:
            raise NotImplementedError
        self.antialias = antialias
        self.renderers = sampleRenderers

    def forFont(self, font: QtGui.QFont) -> 'SvgFontSample':
        """Return the renderer for another font (e.g. when changing font size)."""
        return self

    @classmethod
    def fromSvgs(cls, svgs: SequenceOf[str],
                      antialias: bool=True) -> 'SvgFontSample':
        """Create a SVG font sample renderer from a list of SVG strings."""
        if len(svgs) != 1:
            raise NotImplementedError
        renderers = []
        for svg in svgs:
            svg = re.sub('viewBox=([\'"])([^\'"]+)(\\1)',  '', svg, 1)
            renderers.append(QtSvg.QSvgRenderer(QtCore.QByteArray(svg.encode('utf8'))))
        return cls(renderers, antialias)

    def render(self, painter: QtGui.QPainter, rect: QtCore.QRect,
                     palette: QtGui.QPalette=None, darkBackground: bool=None):
        """Render the sample using the provided painter, rectangle and palette.

        You can provide a darkBackground=True/False hint.
        """

        renderer = self.renderers[0]

        sampleRatio = rect.width() / rect.height()
        viewBox = renderer.viewBoxF()
        viewBoxRatio = viewBox.width() / viewBox.height()

        if sampleRatio > viewBoxRatio:
            newWidth = viewBox.width() * (sampleRatio / viewBoxRatio)
            extraWidth = newWidth - viewBox.width()
            viewBox.adjust(-extraWidth / 2, 0, extraWidth / 2, 0)
            renderer.setViewBox(viewBox)
        elif sampleRatio < viewBoxRatio:
            newHeight = viewBox.height() * (viewBoxRatio / sampleRatio)
            extraHeight = newHeight - viewBox.height()
            viewBox.adjust(0, -extraHeight / 2, 0, extraHeight / 2)
            renderer.setViewBox(viewBox)

        renderer.render(painter, QtCore.QRectF(rect))


class ColorLayerFontSample(object):


    """Display a CPAL/COLR layered color font sample.
    Use fromTables to construct."""

    def __init__(self, rawFont: 'QtGui.QRawFont',
                       layersSequence: SequenceOf[SequenceOf[TupleOf[int, int]]],
                       fontPalettes: SequenceOf[SequenceOf[object]]):
        if len(layersSequence) != 1:
            raise NotImplementedError
        self.rawFont = rawFont
        self.layersSequence = layersSequence

        self.fontPalettes = fontPalettes

        if not fontPalettes:
            self.darkFontPalette = self.lightFontPalette = ()
        elif len(fontPalettes) >= 2:
            self.lightFontPalette = fontPalettes[0]
            self.darkFontPalette = fontPalettes[1]
        else:
            self.darkFontPalette = self.lightFontPalette = fontPalettes[0]

    def forFont(self, font: QtGui.QFont) -> 'ColorLayerFontSample':
        """Return the renderer for another font (e.g. when changing font size)."""
        return type(self)(QtGui.QRawFont.fromFont(font),
                          self.layersSequence,
                          self.fontPalettes)

    @classmethod
    def fromTables(cls, rawFont: 'QtGui.QRawFont',
                        ttFont: 'ttLib.TTFont',
                        colr: 'ttLib.tables.C_O_L_R_.table_C_O_L_R_',
                        cpal: 'ttLib.tables.C_P_A_L_.table_C_P_A_L_',
                        glyphs: SequenceOf[str]):
        """Construct the renderer.

        You need to provide the TTFont, the COLR and CPAL tables of the font,
        and a list of glyph IDs to use.

        Currently only one glyph is supported, i.e. only character map, not
        sampling."""
        if len(glyphs) != 1:
            raise NotImplementedError

        layersSequence = []

        for glyph in glyphs:
            layers = colr.ColorLayers[glyph]
            layersSequence.append([(layer.colorID,
                                    ttFont.getGlyphID(layer.name))
                                   for layer in layers])
        return cls(rawFont, layersSequence, cpal.palettes)

    def render(self, painter: QtGui.QPainter, rect: QtCore.QRect,
                     palette: QtGui.QPalette=None, darkBackground: bool=None):
        """Render the sample using the provided painter, rectangle and palette.

        You can provide a darkBackground=True/False hint.
        """

        if palette is None:
            palette = QtWidgets.QApplication.palette()
        if darkBackground is None:
            darkBackground = hasDarkBackground(palette)
        if darkBackground:
            fontPalette = self.darkFontPalette
        else:
            fontPalette = self.lightFontPalette

        painter.save()
        ascent = self.rawFont.ascent()
        descent = self.rawFont.descent()
        fontHeight = ascent + descent
        rectHeight = rect.height()
        raiseWith = descent * rectHeight / fontHeight

        basePoint = QtCore.QPointF(rect.bottomLeft())
        basePoint += QtCore.QPointF(0, -raiseWith)

        for colorID, glyph in self.layersSequence[0]:
            if colorID == opentype.COLR_DEFAULT_TEXT_FOREGROUND:
                color = palette.color(palette.Text)

            else:
                try:
                    fontColor = fontPalette[colorID]
                except LookupError:
                    color = palette.color(palette.Text)
                else:
                    color = QtGui.QColor(fontColor.red, fontColor.green,
                                         fontColor.blue, fontColor.alpha)

            painter.setPen(color)
            glyphRun = QtGui.QGlyphRun()
            glyphRun.setRawFont(self.rawFont)
            glyphRun.setGlyphIndexes([glyph])
            glyphRun.setPositions([QtCore.QPointF(0, 0)])
            painter.setBrush(color)
            painter.drawGlyphRun(basePoint, glyphRun)

            #painterPath = self.rawFont.pathForGlyph(glyph)
            ##painterPath.translated(rect.topLeft())
            #painter.drawPath(painterPath)
        painter.restore()


SampleRendererType = Union[SvgFontSample, ColorLayerFontSample]


class CharacterIconEngine(QtGui.QIconEngine):

    """An icon engine for Emoji icon utilising a font that uses the
    sample renderers from above. It is created using an Emoji character,
    and optional font."""

    _renderModes = None

    def __init__(self, char: str, font: QtGui.QFont=None,
                       fontInfo: 'typeatlas.fontlist.FontLike'=None):
        super().__init__()
        if font is None:
            if fontInfo is None:
                font = QtGui.QFont()
            else:
                font = QtGui.QFontDatabase().font(fontInfo.family,
                                                  fontInfo.style, 32)
        self.char = char
        self.font = font
        self.fontInfo = fontInfo
        self._sampleRenderer = None
        self._sampleRendererDisabled = False

        #self._options = options

    @classmethod
    def _getRenderModes(cls) -> SetOf[str]:
        """Return the render modes supported by this class.
        This may support COLR and SVG modes."""

        if cls._renderModes is not None:
            return cls._renderModes

        options = Options.getInstance()

        if options.layeredFontRenderer == 'os' or not hasattr(QtGui, 'QGlyphRun'):
            renderColr = False
        elif options.layeredFontRenderer == 'internal':
            renderColr = True
        else:
            renderColr = not osinfo.layered_fonts_supported()

        if options.svgFontRenderer == 'os' or QtSvg is None:
            renderSvg = False
        elif options.svgFontRenderer == 'internal':
            renderSvg = True
        else:
            renderSvg = not osinfo.svg_fonts_supported()

        cls._renderModes = renderModes = set()
        if renderSvg:
            renderModes.add('SVG')
        if renderColr:
            renderModes.add('COLR')

        return renderModes

    def getSampleRenderer(self) -> Optional[SampleRendererType]:
        """Get the sample renderer for engine's character (text sample) and font.
        This does not throw exceptions, only displays them. We don't need to crash
        because we failed to load an icon font."""
        if self._sampleRendererDisabled:
            return None
        if self._sampleRenderer is not None:
            return self._sampleRenderer
        try:
            return self._sampleRendererWithExceptions()
        except Exception:
            warnmsgf("Internal rendering failed for %r", self.fontInfo)
            traceback.print_exc()
            self._sampleRendererDisabled = True

    def _sampleRendererWithExceptions(self) -> Optional[SampleRendererType]:
        """Get the sample renderer, throwing exceptions."""
        fontInfo = self.fontInfo

        if fontInfo is None:
            return None

        renderModes = self._getRenderModes()
        if not renderModes:
            return None

        # Keeping a reference to fontExtended, so other icons don't parse the
        # font again
        self.fontExtended = fontExtended = fontInfo.extended()

        if fontExtended.ttfont and fontExtended.cmap:
            char = self.char
            font = self.font

            charCode = ord(char)

            antialias = not (font.styleStrategy() & font.NoAntialias)
            ttFont = fontExtended.ttfont
            fontCmap = fontExtended.cmap

            try:
                svg = ttFont['SVG '] if 'SVG' in renderModes else None
            except KeyError:
                svg = None

            if svg and hasattr(svg, 'docList') and QtSvg is not None:
                glyphName = fontCmap.get(charCode)
                if glyphName:
                    glyphID = ttFont.getGlyphID(glyphName)
                    for svg, startGlyph, endGlyph in svg.docList:
                        if startGlyph <= glyphID <= endGlyph:
                            self._sampleRenderer = SvgFontSample.fromSvgs(
                                                            [svg], antialias)
                            return self._sampleRenderer

            if 'COLR' not in renderModes:
                colr = cpal = None
            else:
                try:
                    colr = ttFont['COLR']
                    cpal = ttFont['CPAL']
                except KeyError:
                    colr = cpal = None


            if colr is not None and hasattr(QtGui, 'QRawFont'):
                rawFont = QtGui.QRawFont.fromFont(font)

                glyph = fontCmap.get(charCode)
                if glyph is not None and glyph in colr.ColorLayers:

                    self._sampleRenderer = ColorLayerFontSample.fromTables(
                            rawFont, ttFont, colr, cpal, [glyph])
                    return self._sampleRenderer

    def icon(self) -> QtGui.QIcon:
        """Return icon backed by this engine."""
        return QtGui.QIcon(self)

    def paint(self, painter, rect, mode, state):

        #painter.fillRect(rect, QtGui.QColor("transparent"))

        sample = self.char
        style = QtWidgets.QApplication.style()
        palette = QtWidgets.QApplication.palette()

        font = QtGui.QFont(self.font)
        font.setPointSize(32)
        metrics = QtGui.QFontMetrics(font)

        boxWidth = rect.width()
        boxHeight = rect.height()

        sampleRect = metrics.boundingRect(sample)
        txtWidth = sampleRect.width()
        txtHeight = sampleRect.height()

        if (not boxWidth or not boxHeight or
            txtWidth / boxWidth <= txtHeight / boxHeight):
                font.setPixelSize(int(0.9 * boxHeight))
        else:
                font.setPixelSize(int(0.9 * txtHeight * boxWidth / txtWidth))

        metrics = QtGui.QFontMetrics(font)

        enabled = mode != QtGui.QIcon.Disabled

        if mode == QtGui.QIcon.Selected:
            samplePaintRole = palette.HighlightedText
        else:
            samplePaintRole = palette.Text

        sampleRenderer = self.getSampleRenderer()

        # Draw
        if mode == QtGui.QIcon.Selected:
            painter.fillRect(rect, palette.highlight())
        painter.setPen(palette.color(palette.Mid))

        painter.setFont(font)
        if sampleRenderer:
            sampleRenderer = sampleRenderer.forFont(font)
            sampleTextRect = style.itemTextRect(metrics, rect,
                                                Qt.AlignCenter, enabled,
                                                sample)
            sampleRenderer.render(painter, sampleTextRect, palette)
        else:
            style.drawItemText(painter,
                               style.itemTextRect(metrics, rect,
                                                  Qt.AlignCenter, enabled,
                                                  sample),
                               Qt.AlignCenter, palette, enabled, sample,
                               samplePaintRole)

    def pixmap(self, size, mode, state):
        pixmap = QtGui.QPixmap(size)
        pixmap.fill(QtGui.QColor(0, 0, 0, 0))
        painter = QtGui.QPainter()
        painter.begin(pixmap)
        self.paint(painter, QtCore.QRect(QtCore.QPoint(0, 0), size),
                   mode, state)
        painter.end()
        return pixmap


class CharSymbolInfo(object):

    """Info for a given character symbol in a given encoding."""

    def __init__(self, codepoint: int, bytedata: bytes=None,
                       charvalue: int=None,
                       display: str=None,
                       encoding: 'typeatlas.charsets.EncodingLike'=None):

        if encoding is not None:
            charsize = encoding.charsize
        else:
            charsize = None

        if charvalue is None:
            if bytedata is not None:
                if charsize == 1:
                    charvalue = bytedata[0]
                else:
                    charvalue = bytedata_to_int(bytedata)

        elif bytedata is None and charsize == 1:
            bytedata = bytes([charvalue])

        if display is None and bytedata is not None:
            if charsize == 1:
                display = "%X" % (charvalue, )
            else:
                display = ' '.join('%X' % (byte, ) for byte in bytedata)

        self.codepoint = codepoint
        self.charvalue = charvalue
        self.bytedata = bytedata
        self.display = display
        self.encoding = encoding


class SymbolModelFontInfo(object):

    """A font info object representing a font and its characters for the
    font grid character map model. A character map can display one or
    multiple fonts; this contains all font-specific attributes that will
    be repeated for each font. Used by setFont() and setMultiFont() of
    the FontSymbolModel to store information.

    This includes the Qt font, the fontlist.Font object, the characters in
    the font as blocks or a character iterable.

    You can provide charsetCodeInfo mapping of codepoints to CharSymbolInfo
    model. It can also be passed as characters= (as it is valid iterable of
    characters), and it will be detected properly.
    """

    def __init__(self, font: QtGui.QFont=None,
                       fontInfo: 'typeatlas.fontlist.FontLike'=None,
                       characters: IterableOf[int]=None,
                       charBlocks: IterableOf[blockmath.BlockLike]=None,
                       options: Options=None,
                       charsetCodeInfo: MappingOf[int, CharSymbolInfo]=None):
        if options is None:
            options = Options.getInstance()

        if options.layeredFontRenderer == 'os' or not hasattr(QtGui, 'QGlyphRun'):
            renderColr = False
        elif options.layeredFontRenderer == 'internal':
            renderColr = True
        else:
            renderColr = not osinfo.layered_fonts_supported()

        if options.svgFontRenderer == 'os' or QtSvg is None:
            renderSvg = False
        elif options.svgFontRenderer == 'internal':
            renderSvg = True
        else:
            renderSvg = not osinfo.svg_fonts_supported()

        if isinstance(characters, Mapping):
            if charsetCodeInfo is None:
                charsetCodeInfo = characters
            characters = list(characters)

        self.sampleRenderers = {}
        self._fontCharBlocks = charBlocks
        self._characters = characters

        self.charsetCodeInfo = charsetCodeInfo
        self.ownCharacters = (characters is None and charBlocks is None and
                              font is not None)

        self.encoding = None
        if self.charsetCodeInfo:
            for symbolInfo in self.charsetCodeInfo.values():
                self.encoding = symbolInfo.encoding
                break

        if font is None:
            self.font = None
            self.fontInfo = None
            self.fontExtended = None
            self.fontCmap = None
            return

        fontExtended = None

        rawFont = None
        fontCmap = None

        if fontInfo is not None:
            fontExtended = fontInfo.extended()
            if fontExtended.ttfont and fontExtended.cmap:
                antialias = not (font.styleStrategy() & font.NoAntialias)
                ttFont = fontExtended.ttfont
                fontCmap = fontExtended.cmap

                try:
                    svg = ttFont['SVG '] if renderSvg else None
                except KeyError:
                    svg = None

                if svg and hasattr(svg, 'docList') and QtSvg is not None:
                    charByGlyph = {ttFont.getGlyphID(glyphName): char
                                   for char, glyphName in fontCmap.items()}
                    for svg, startGlyph, endGlyph in svg.docList:
                        sampleRenderer = SvgFontSample.fromSvgs([svg],
                                                                antialias)
                        for glyph in range(startGlyph, endGlyph + 1):
                            char = charByGlyph.get(glyph)
                            if char is not None:
                                self.sampleRenderers[char] = sampleRenderer

                if not renderColr:
                    colr = cpal = None
                else:
                    try:
                        colr = ttFont['COLR']
                        cpal = ttFont['CPAL']
                    except KeyError:
                        colr = cpal = None

                if (rawFont is None and colr is not None and
                    hasattr(QtGui, 'QRawFont')):
                        rawFont = QtGui.QRawFont.fromFont(font)

                if colr is not None and rawFont is not None:
                    charByGlyph = {glyphName: char
                                   for char, glyphName in fontCmap.items()}
                    for glyph in colr.ColorLayers:
                        char = charByGlyph.get(glyph)
                        if char is None:
                            continue

                        sampleRenderer = ColorLayerFontSample.fromTables(
                                rawFont, ttFont, colr, cpal, [glyph])

                        if sampleRenderer is not None:
                            self.sampleRenderers[char] = sampleRenderer

        self.font = font
        self.fontInfo = fontInfo
        self.fontExtended = fontExtended
        self.fontCmap = fontCmap
        #self._characters = None
        #self._fontCharBlocks = None

    def characters(self) -> SetOf[int]:
        """Get the characters of the font as a list of integers."""
        if self._characters is None:
            self._fillCharacters()
        return self._characters

    def fontCharBlocks(self) -> SequenceOf[blockmath.BlockLike]:
        """Get the characters of the font as a list of character blocks."""
        if self._fontCharBlocks is None:
            self._fillCharacters()
        return self._fontCharBlocks

    def _fillCharacters(self):
        """Compute the characters of the font."""
        if self._characters is not None:
            self._fontCharBlocks = blockmath.toblocks(self._characters)
            return

        if self._fontCharBlocks is not None:
            self._characters = OrderedSet(blockmath.iterblocks(self._fontCharBlocks))
            return

        font = self.font
        fontInfo = self.fontInfo
        fontCmap = self.fontCmap

        if font is None and fontInfo is None and fontCmap is None:
            self._characters = frozenset()
            self._fontCharBlocks = []
            return

        if fontInfo is not None:
            charset = self.fontInfo.get_charset()
            if charset is not None:
                self._characters = charset
                self._fontCharBlocks = list(blockmath.toblocks(self._characters))
                return

        # TODO: Old code below, duplicated with above, some checks
        #       are senseless.

        # FIXME: Decide what interface to use here.
        if fontInfo is None or getattr(fontInfo, 'charblocks', None) is None:

            if fontCmap is not None:
                chars = sorted(fontCmap)
            elif hasattr(QtGui, 'QRawFont'):
                rawFont = QtGui.QRawFont.fromFont(font)
                allChars = charinfo.all_character_codes()
                chars = filter(rawFont.supportsCharacter, allChars)
            else:
                chars = charinfo.all_character_codes()

            charblocks = list(blockmath.toblocks_inorder(chars))
        else:
            charblocks = fontInfo.charblocks

        self._fontCharBlocks = charblocks
        characters = OrderedSet(blockmath.iterblocks(charblocks))

        #characters = []
        #for char in charinfo.all_character_codes():
        #    if rawFont.supportsCharacter(char):
        #         characters.append(char)
        self._characters = characters


class FontSymbolModel(QtCore.QAbstractItemModel):

    """A Qt item model containing font symbols for display in a character
    map using FontGrid().

    All extra attributes are forwarded to the SymbolModelFontInfo of the
    main font.

    It supports the following additional roles:
        CharCodeRole        The unicode code points.
        CellHeaderRole      The hex of the unicode point. The hex of the code
                            in the character set. The morse code for the letter.
                            To be shown in the cell's header.
        SampleRendererRole  The role returning the sample renderer for
                            the characters in fonts that need special rendering,
                            e.g. SVG or layered fonts (SampleRendererType)
        CharInfoTextRole    Unused
        ModelFontInfoRole   The SymbolModelFontInfo object for the current
                            column.

    """

    def __init__(self, font: QtGui.QFont=None,
                       renderingChoice: FontRenderingChoice=None,
                       parent: QtCore.QObject=None,
                       charDb: CharacterDatabase=None,
                       langDb: LanguageDatabase=None):

        super(FontSymbolModel, self).__init__(parent)

        if renderingChoice is None:
            renderingChoice = FontRenderingChoice()

        if charDb is None:
            charDb = CharacterDatabase.getInstance()
        if langDb is None:
            langDb = LanguageDatabase.getInstance()

        self.ownCharacters = False
        self.fontCharBlocks = []
        self.characters = []
        self.selected = []
        self.charsetCodeInfo = None

        self.renderingChoice = renderingChoice
        self._setFont(font)

        self.gridView = None
        self.charBox = None
        self.charDb = charDb
        self.langDb = langDb

        self.singleFamily = True
        self.singleStyle = True

    def __getattr__(self, attr):
        return getattr(self.modelFontInfo, attr)

    def _setFont(self, font: QtGui.QFont=None, *args, **kwargs):
        """Set the font. All arguments are passed to SymbolModelFontInfo()."""
        self.selected = []
        self.singleFamily = True
        self.singleStyle = True

        options = self.renderingChoice.options

        if font is not None and self.gridView is not None:
            pixelSize = font.pixelSize()
            if pixelSize >= ID_THRESH:
                factor = 1.3
            else:
                factor = 1.1
            self.gridView.setGridSize(QtCore.QSize(pixelSize * factor,
                                                   pixelSize * factor))

        self.modelFontInfo = SymbolModelFontInfo(font, *args, **kwargs,
                                                 options=options)
        self._setCharacters()

    def _setMultiFont(self, current: SymbolModelFontInfo,
                            selected: IterableOf[SymbolModelFontInfo]=()):
        """Set multiple fonts, one current and multiple selected, using
        explicit SymbolModelFontInfo instances."""
        options = self.renderingChoice.options
        self.modelFontInfo = current
        self.selected = list(selected)[:options.maxFontGridFonts]

        allFonts = [current] + self.selected

        familyNames = Counter(mfi.fontInfo.family for mfi in allFonts)
        self.singleFamily = len(familyNames) <= 1
        self.singleStyle = max(familyNames.values(), default=0) <= 1

        if self.gridView is not None and any(mfi.font is not None
                                             for mfi in allFonts):

            gridSize = max(mfi.font.pixelSize() *
                           (1.3 if mfi.font.pixelSize() >= ID_THRESH
                                else 1.1)
                           for mfi in allFonts
                           if mfi.font is not None)

            self.gridView.setGridSize(QtCore.QSize(gridSize, gridSize))

        self._setCharacters()

    def _setCharacters(self, characters: IterableOf[int]=None,
                             charBlocks: IterableOf[blockmath.BlockLike]=None,
                             charsetCodeInfo: MappingOf[int, CharSymbolInfo]=None):
        """Set the characters to display. If no characters are passed (the default),
        use the SymbolModelFontInfo objects to compute an intersection of
        characters."""
        if charBlocks is not None:
            self.fontCharBlocks = charBlocks
            self.characters = list(blockmath.iterblocks(charBlocks))
            self.ownCharacters = False
            self.charsetCodeInfo = charsetCodeInfo
            return

        if characters is not None:
            self.characters = list(characters)
            self.fontCharBlocks = blockmath.toblocks(self.characters)
            self.ownCharacters = False
            self.charsetCodeInfo = charsetCodeInfo
            return

        if self.modelFontInfo is None:
            return

        if self.selected:
            characters = self.modelFontInfo.characters()
            ownCharacters = self.modelFontInfo.ownCharacters
            self.charsetCodeInfo = self.modelFontInfo.charsetCodeInfo

            for mfi in self.selected:
                characters = characters & mfi.characters()
                if mfi.ownCharacters:
                    ownCharacters = True
                #self.charsetCodeInfo = mfi.charsetCodeInfo

            self.characters = list(characters)
            self.fontCharBlocks = blockmath.toblocks(self.characters)
            self.ownCharacters = self.ownCharacters

        else:
            self.characters = list(self.modelFontInfo.characters())
            self.fontCharBlocks = self.modelFontInfo.fontCharBlocks()
            self.ownCharacters = self.modelFontInfo.ownCharacters
            self.charsetCodeInfo = self.modelFontInfo.charsetCodeInfo

    def setFont(self, font: QtGui.QFont=None,
                      fontInfo: 'typeatlas.fontlist.FontLike'=None,
                      nochange: bool=False, **kwargs):
        """Set the font. See SymbolModelFontInfo for documentation of
        the arguments.

        Passing nochange=True means the model is not reset, just the
        display font is changed.
        """
        if nochange:
            self.modelFontInfo.font = font
            ## FIXME: This is slow and wrong for icon view,
            ##        view.reset() does it faster. However, it works
            ##        for table view, see below.
            #for topleft, bottomright in \
            #           modelIterateChildrenRect(self, maxDepth=1):
            #   self.dataChanged.emit(topleft, bottomright)
            return
        self.beginResetModel()
        self._setFont(font, fontInfo, **kwargs)
        self.endResetModel()

    def setMultiFont(self, *args, **kwargs):
        """setMultiFont(current, selected=())

        Set the fonts in the character map. Pass the current
        font as FontSymbolModel() object, and the selected fonts
        as a list of FontSymbolModel() objects.

        Lacks nochange argument, use updateQtFonts().

        FontGrid.setFont() removes the current font from the selected
        fonts, so weird things will happen if you call this directly and
        you do not remove it (particularly, you'd get one more column).
        """
        self.beginResetModel()
        self._setMultiFont(*args, **kwargs)
        self.endResetModel()

    def updateQtFonts(self, currentFont: QtGui.QFont,
                            selectedFonts: IterableOf[QtGui.QFont]=()):
        """Update the qt fonts in the model. Equivalent to nochange=True
        of setFont(). The selected fonts need to provide in the same order
        as the setMultiFont() selected fonts were provided (unless you want
        to do something really weird)."""
        self.modelFontInfo.font = currentFont
        for mfi, font in zip(self.selected, selectedFonts):
            mfi.font = font

        for topleft, bottomright in \
                    modelIterateChildrenRect(self, maxDepth=1):
            self.dataChanged.emit(topleft, bottomright)

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        return QtCore.QModelIndex()

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return QtCore.QModelIndex()

        try:
            char = self.characters[row]
        except IndexError:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(row, column, None)

    def hasChildren(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return True
        return False

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            # FIXME: If this returns 0, all children disappear. WHY?
            # Documentation says it *must* return 0.
            return 1
        return 1 + len(self.selected)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self.characters)
        return 0

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None

        char = self.characters[index.row()]

        if role == Qt.DisplayRole:
            if self.charDb.combining(char):
                return '\u25CC' + chr(char)
            else:
                if self.ownCharacters:
                    info = None
                else:
                    info = self.charDb.info_by_code.get(char)
                if info is not None and info.category == 'Cc':
                    if info.display:
                        return chr(info.display)
                    else:
                        return '\u2388'
                else:
                    return chr(char)
        elif role == Qt.EditRole:
            return chr(char)
        elif role == CellHeaderRole:
            charsetCodeInfo = self.charsetCodeInfo
            if charsetCodeInfo is not None:
                result = charsetCodeInfo.get(char)
                if result is None:
                    return '--'
                return result.display
            return "%X" % (char, )
        elif role == SampleRendererRole:
            col = index.column()
            if col == 0:
                return self.sampleRenderers.get(char)
            else:
                return self.selected[col - 1].sampleRenderers.get(char)
        elif role == Qt.FontRole:
            col = index.column()
            if col == 0:
                return self.font
            else:
                return self.selected[col - 1].font
        elif role == Qt.ToolTipRole:
            text = []
            self.fillCharacterInfoTexts(char, text, text, includePreview=True)
            return '<br>'.join(text)
        elif role == CharCodeRole:
            return char
        elif role == Qt.ForegroundRole:
            if self.ownCharacters:
                info = None
            else:
                info = self.charDb.info_by_code.get(char)
            palette = QtWidgets.QApplication.palette()
            if info is not None and info.category == 'Cc':
                return palette.brush(palette.Disabled, palette.Text)
            else:
                return palette.brush(palette.Text)
        elif role == ModelFontInfoRole:
            col = index.column()
            if col == 0:
                return self.modelFontInfo
            else:
                return self.selected[col - 1]

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == 0:
                    item = self.fontInfo
                else:
                    item = self.selected[section - 1].fontInfo
                if self.singleFamily:
                    return item.translate('style', textlang())
                elif self.singleStyle:
                    return item.translate('family', textlang())
                else:
                    return item.translate('fullname', textlang())

        elif orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                char = self.characters[section]
                return "%04X" % (char, )

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag()
        return (super(FontSymbolModel, self).flags(index)
                    | Qt.ItemIsEditable | Qt.ItemIsSelectable
                    | Qt.ItemIsDragEnabled)

    def mimeData(self, indexes):
        if not indexes:
            return None

        chars = ''.join(index.data(Qt.EditRole) or ''
                        for index in indexes)
        markup = '<span style="%s">%s</span>' % (qFontToCss(self.font),
                                                 htesc(chars))

        mime = QtCore.QMimeData()
        mime.setText(chars)
        mime.setHtml(markup)
        return mime

    def mimeTypes(self):
        return ['text/html', 'text/plain']

    def dropMimeData(self, data, action, row, column, parent):
        return False

    def supportedDragActions(self):
        return Qt.CopyAction

    def supportedDropActions(self):
        return Qt.CopyAction

    def fillCharacterInfoTexts(self, char: int,
                               infoTextLines: MutableSequenceOf[str]=None,
                               altInfoTextLines: MutableSequenceOf[str]=None,
                               includePreview: bool=False,
                               modelFontInfo: SymbolModelFontInfo=None):
        """Fill the provided sequences with HTML information about the character.

        The Unicode character information goes in the first sequence.
        Any information from alternative registries goes in the second sequence.

        If you provide includePreview=True, the character will also be previewed.
        That mode is used for the tooltip, as the character bars usually have their
        own character preview.
        """

        mfi = modelFontInfo or self

        options = self.renderingChoice.options

        text = infoTextLines
        if text is None:
            text = []

        textAlt = altInfoTextLines
        if textAlt is None:
            textAlt = []

        if self.charDb is None:
            text.append(H_('Unicode database not loaded'))
            return

        info = self.charDb.get(char, autofill=True)
        if info is None:
            text.append(H_('Unknown character'))
            return

        plane = self.charDb.get_plane(char)
        script = self.charDb.find_script_name(self.langDb, char)
        symbol = chr(char)

        display = symbol
        if info.display:
            display = chr(info.display)

        if includePreview:
            text.append('<span style="font-size: %dpt; %s">%s</span>'
                            % (self.renderingChoice.charBoxSize,
                               htesc(qFontToCss(mfi.font)),
                                htesc(chr(char))))

        text.extend([
                htesc(info.name or info.old_name or ''),
                htesc(_('Hex code', ': 0x%x') % (char, )),
                htesc(_('Character', ': %s') % (display, )),
                '%s: %s %s' % (H_('Category'),
                               getIconHtml(info.category_icon,
                                           options.infoIconSize),
                               info.category_name(translate=_)),
        ])

        if info.block:
            text.append(htesc(_('Block', ': %s') % (info.block.name, )))
        text.append(htesc(_('Script', ': %s') % (script, )))
        text.append('%s: %s' % (htesc(_('Plane %d') % (plane.number, )),
                                H_(plane.description)))

        for alias in info.aliases:
            text.append('= ' + htesc(alias))
        for alias in info.formalaliases:
            text.append(htesc(charinfo.formal_alias + ' ' + alias))
        #for crossref in info.crossrefs:
        #    text.append(htesc(charinfo.cross_reference + ' ' + crossref))
        for variation in info.variations:
            text.append(htesc(_('Variation', ': ') + variation))

        if mfi.fontCmap:
            fontCharName = mfi.fontCmap.get(char)
            text.append(htesc(_("Font's character name", ": %s")
                                        % (fontCharName, )))

        altinfos = self.charDb.get_secondary(char)
        if altinfos:
            textAlt.append('')
        for altinfo in altinfos:
            textAlt.append(H_(altinfo.registry.name))
            textAlt.append(htesc(altinfo.name or altinfo.old_name or ''))
            if altinfo.block:
                textAlt.append(htesc(_('Block', ': %s')
                                        % (altinfo.block.name, )))
            altscript = altinfo.registry.find_script_name(self.langDb, char,
                                                          default=None)
            if altscript:
                textAlt.append(htesc(_('Script', ': %s') % (altscript, )))


class GridCellDelegate(QtWidgets.QStyledItemDelegate):

    """A delegate to paint a cell in the character map. This adds
    a header with the hex code of the character, usually with the unicode
    codepoint.

    This header is filled from CellHeaderRole, which may contain:
        - hex code in another encoding, for legacy encodings
        - font name, if the grid is used for displaying font samples
        - morse code or needle telegraph code of the letter

    You can provide the view to get style information from it.

    You can control the grid sizing with square (default True)
    and abbreviateHeader (default False). When square is True,
    effort will be made to make the cells square unless a very wide
    character comes along.  If abbreviateHeader=True is passed,
    and the header is too long, it will be cut off.

    The sizeThreshold is the threshold above which the header is no longer
    displayed.

    You can specify which model roles to use to get the headerRole and
    the sampleRole, they default to CellHeaderRole, and Qt.DisplayRole.
    If you replace the FontSymbolModel with a FontListModel, you'd obviously
    need to change the headers.
    """


    def __init__(self, view: QtWidgets.QAbstractItemView=None, *args,
                       fontDb: QtGui.QFontDatabase=None,
                       square: bool=True, abbreviateHeader: bool=False,
                       headerRole: int=CellHeaderRole,
                       sampleRole: int=Qt.DisplayRole,
                       sampleRendererRole: int=SampleRendererRole,
                       sizeThreshold: numbers.Real=ID_THRESH,
                       **kwargs):
        super(GridCellDelegate, self).__init__(*args, **kwargs)
        self.view = view
        if fontDb is None:
            fontDb = QtGui.QFontDatabase()
        self.fontDb = fontDb

        self.square = square
        self.abbreviateHeader = abbreviateHeader
        self.sampleRole = sampleRole
        self.sizeThreshold = sizeThreshold

        self.headerRole = headerRole
        self.sampleRole = sampleRole
        self.sampleRendererRole = sampleRendererRole

    def sizeHint(self, option, index):

        font = index.data(Qt.FontRole)
        if font is None:
            return super().sizeHint(option, index)

        pointSize = font.pointSize()
        if pointSize >= self.sizeThreshold:

            metrics = QtGui.QFontMetrics(font)
            sample = index.data(self.sampleRole)
            #result = metrics.size(Qt.TextSingleLine, sample)
            result = metrics.size(Qt.TextSingleLine, sample).expandedTo(
                         metrics.boundingRect(sample).size())

            defaultFont = QtWidgets.QApplication.font()
            headerFont = self.fontDb.font(defaultFont.family(),
                                          defaultFont.styleName(),
                                          max(pointSize / 6, 8))
            headerMetrics = QtGui.QFontMetrics(headerFont)
            header = index.data(self.headerRole)
            headerSize = headerMetrics.size(Qt.TextSingleLine, header)

            width = result.width() * 1.1
            if self.square:
                width = max(width, result.height() * 1.1)
            if not self.abbreviateHeader:
                width = max(width, headerSize.width() * 1.1)

            height = result.height() * 1.1 + headerSize.height()

            return QtCore.QSize(width, height)

        result = super().sizeHint(option, index)

        if not self.square:
            return result

        return QtCore.QSize(max(result.width(), result.height()),
                            result.height())

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)

        font = option.font
        if not font:
            return super(GridCellDelegate, self).paint(painter, option, index)

        if self.view is None:
            style = QtWidgets.QApplication.style()
        else:
            style = self.view.style()
        metrics = option.fontMetrics
        palette = option.palette

        darkBackground = hasDarkBackground(palette)

        painter.save()

        rect = style.subElementRect(style.SE_ItemViewItemText, option)
        #rect = option.rect

        pointSize = font.pointSize()
        if pointSize >= self.sizeThreshold:

            # Calculate the headers
            defaultFont = QtWidgets.QApplication.font()
            headerFont = self.fontDb.font(defaultFont.family(),
                                          defaultFont.styleName(),
                                          max(pointSize / 6, 8))
            headerMetrics = QtGui.QFontMetrics(headerFont)

            enabled = False
            if option.state & style.State_Enabled:
                enabled = True

            if option.state & style.State_Selected:
                samplePaintRole = palette.HighlightedText
                headerPaintRole = palette.HighlightedText
            else:
                samplePaintRole = palette.Text
                headerPaintRole = palette.Shadow

            header = index.data(self.headerRole)
            headerSize = headerMetrics.size(Qt.TextSingleLine, header)

            sample = index.data(self.sampleRole)
            sampleRenderer = None

            if self.sampleRendererRole is not None:
                sampleRenderer = index.data(self.sampleRendererRole)

            # Calculate the rectangles
            charOption = type(option)(option)
            charOption.rect = option.rect.adjusted(0, headerSize.height(), 0, 0)
            headerOption = type(option)(option)
            headerOption.rect = option.rect.adjusted(
                                    0, 0, 0, 0 - option.rect.height()
                                               + headerSize.height())

            if headerOption.rect.width() < headerSize.width():
                header = headerMetrics.elidedText(header, Qt.ElideRight,
                                                  headerOption.rect.width())

            # Draw
            if option.state & style.State_Selected:
                painter.fillRect(option.rect, palette.highlight())
            painter.setPen(palette.color(palette.Mid))
            painter.drawRect(option.rect)

            #style.drawControl(style.CE_ItemViewItem, charOption,
            #                  painter, self.view)
            painter.setFont(option.font)
            if sampleRenderer:

                sampleTextRect = style.itemTextRect(metrics, charOption.rect,
                                            Qt.AlignCenter, enabled,
                                            sample)
                sampleRenderer.render(painter, sampleTextRect,
                                      palette, darkBackground)

                #style.drawItemPixmap(painter,
                #                     style.itemPixmapRect(charOption.rect,
                #                                          Qt.AlignCenter,
                #                                          pixmap),
                #                     Qt.AlignCenter, pixmap)
            else:
                style.drawItemText(painter, #charOption.rect,
                                   style.itemTextRect(metrics, charOption.rect,
                                                      Qt.AlignCenter, enabled,
                                                      sample),
                                   Qt.AlignCenter, palette, enabled, sample,
                                   samplePaintRole)
            painter.setFont(headerFont)
            style.drawItemText(painter, #headerOption.rect,
                               style.itemTextRect(headerMetrics,
                                                  headerOption.rect,
                                                  Qt.AlignRight, enabled,
                                                  header),
                               Qt.AlignRight, palette, enabled, header,
                               headerPaintRole)

        else:
            painter.setPen(palette.color(palette.Mid))
            painter.drawRect(option.rect)
            style.drawControl(style.CE_ItemViewItem, option, painter, self.view)

        painter.restore()


class CharFilterModel(QtModelProxies.QSortFilterProxyModel):

    """A filter for character models. User is resposible for setting
    the filterText, filterBlock and filterScript properties and
    calling invalidateFilter()."""

    filterText = None
    filterBlock = None
    filterScript = None
    displayLittle = False

    def __init__(self, charDb: CharacterDatabase=None,
                       langDb: LanguageDatabase=None,
                       parent: QtCore.QObject=None):
        super(CharFilterModel, self).__init__(parent)
        if charDb is None:
            charDb = CharacterDatabase.getInstance()
        if langDb is None:
            langDb = LanguageDatabase.getInstance()
        self.charDb = charDb
        self.langDb = langDb

    def filterAcceptsRow(self, source_row, source_parent):

        if self.filterText:
            # FIXME: Slow-ish for CJK fonts?
            text = self.filterText.strip().casefold()
            char = self.sourceModel().characters[source_row]
            symbol = chr(char)
            if symbol.casefold() == text:
                return True

            if len(text) == 1:
                return False

            try:
                code = int(text, 16)
            except ValueError:
                pass
            else:
                if char == code:
                    return True

            if self.charDb is None:
                return False

            infos = self.charDb.getall(char)
            if not infos:
                return False
            for info in infos:
                if text in (info.name or '').casefold():
                    return True
                if any(text in (alias or '').casefold()
                       for alias in info.aliases):
                    return True
            return False

        # These are taken into account only if text isn't entered
        if self.filterBlock is not None:
            char = self.sourceModel().characters[source_row]
            if not (self.filterBlock.start <= char <= self.filterBlock.end):
                return False

        if self.filterScript is not None:
            if self.charDb is None:
                return self.filterScript == 'Unknown'

            char = self.sourceModel().characters[source_row]
            script = self.charDb.find_script_name(self.langDb, char)
            if script != self.filterScript:
                return False

        if (self.displayLittle and self.filterBlock is None and
            self.filterScript is None):
                char = self.sourceModel().characters[source_row]
                return char < PREVIEW_MAX_CODEPOINT

        return True


class FontGridToolbox(Toolbox):

    """Actions for the font grid, e.g. for its context menu."""

    def __init__(self, grid: 'FontGrid'):
        self.grid = grid
        self._properties = None
        super(FontGridToolbox, self).__init__()

    @property
    def actionParent(self) -> QtCore.QObject:
        return self.grid

    def actionDefinitions(self) -> Iterator:
        yield self.action(self.copyFormatted, 
                          _("Copy formatted characters"), 
                          icon='edit-copy', shortcut='Ctrl+C')
        yield self.copyCharacter, _("Copy plain characters")
        yield self.separator()
        yield self.copyCode, _("Copy decimal code")
        yield partial(self.copyCode, 'hex'), _("Copy hex code")
        yield partial(self.copyCode, 'xml'), _("Copy XML code")
        yield partial(self.copyCode, 'utf8'), _("Copy UTF-8 byte codes")
        yield self.separator()
        yield self.copyName, _("Copy name")
        yield self.copyImage, _("Copy image")

        yield self.separator()
        yield self.action(self.openProperties, _('Character properties...'),
                          icon='document-properties')

    @Slot()
    def copyCharacter(self):
        """Copy the slected character as a single string in plain text"""
        selected = self.grid.view.selectionModel().selectedIndexes()
        if not selected:
            return
        chars = ''.join(index.data(Qt.EditRole) or ''
                        for index in selected)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(chars)

    @Slot()
    def copyFormatted(self):
        """Copy the selected characters as a single formatted string.
        This gets it from model.mimeData()."""
        selected = self.grid.view.selectionModel().selectedIndexes()
        if not selected:
            return
        model = selected[0].model()
        mime = model.mimeData(selected)
        if mime is None:
            return

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setMimeData(mime)

    @Slot()
    def copyCode(self, which: str='integer'):
        """Copy the code, either as integer, hex, xml, or utf8"""
        current = self.grid.view.selectionModel().currentIndex()
        if not current.isValid():
            return
        charCode = current.data(CharCodeRole)
        if which == 'integer':
            charCode = str(charCode)
        elif which == 'hex':
            charCode = hex(charCode)
        elif which == 'xml':
            charCode = '&#%d;' % (charCode, )
        elif which == 'utf8':
            charCode = ' '.join(map(hex, chr(charCode).encode('utf8')))

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(charCode)

    @Slot()
    def copyName(self):
        """Copy the name of the character."""
        current = self.grid.view.selectionModel().currentIndex()
        if not current.isValid():
            return
        charCode = current.data(CharCodeRole)
        info = self.grid.charDb.get(charCode)
        if info is None:
            name = ''
        else:
            name = info.name or info.old_name or ''
        if not name:
            for altinfo in self.grid.charDb.get_secondary(charCode):
                if altinfo.name or altinfo.old_name:
                    name = altinfo.name or altinfo.old_name
                    break

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(name)

    @Slot()
    def copyImage(self):
        """Copy the character as a 192pt image."""
        current = self.grid.view.selectionModel().currentIndex()
        if not current.isValid():
            return
        font = current.data(Qt.FontRole)
        font = QtGui.QFont(font)
        font.setPointSize(192)
        metrics = QtGui.QFontMetrics(font)
        renderer = current.data(SampleRendererRole)
        char = current.data(Qt.DisplayRole)

        #size = metrics.size(Qt.TextSingleLine, char)
        size = metrics.boundingRect(char).size()
        image = QtGui.QImage(size, QtGui.QImage.Format_ARGB32_Premultiplied)
        image.fill(QtGui.QColor(0, 0, 0, 0))
        painter = QtGui.QPainter()
        painter.begin(image)

        if renderer:
            renderer.render(painter, image.rect())
        else:
            painter.setFont(font)
            painter.drawText(image.rect(), Qt.AlignCenter, char)
        painter.end()

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setImage(image)

    @Slot()
    def copyScalable(self):
        """Copy scalable, as an SVG."""
        # FIXME: This doesn't work with ColorLayerFontSample, as
        # the glyphs aren't in the cmap, and thus cannot be added to the
        # SVG.

        current = self.grid.view.selectionModel().currentIndex()
        if not current.isValid():
            return
        font = current.data(Qt.FontRole)
        font = QtGui.QFont(font)
        font.setPointSize(192)
        metrics = QtGui.QFontMetrics(font)
        renderer = current.data(SampleRendererRole)
        char = current.data(Qt.DisplayRole)

        #size = metrics.size(Qt.TextSingleLine, char)
        size = metrics.boundingRect(char).size()
        rect = QtCore.QRect(QtCore.QPoint(0, 0), size)
        #image = QtGui.QImage(size, QtGui.QImage.Format_ARGB32_Premultiplied)
        #image.fill(QtGui.QColor(0, 0, 0, 0))
        buf = QtCore.QBuffer()
        image = QtSvg.QSvgGenerator()
        image.setOutputDevice(buf)
        image.setViewBox(rect)
        painter = QtGui.QPainter()
        painter.begin(image)
        painter.setRenderHint(painter.Antialiasing)

        if renderer:
            renderer.render(painter, rect)
        else:
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignCenter, char)
        painter.end()

        mime = QtCore.QMimeData()
        mime.setData("image/svg+xml", buf.buffer())

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setMimeData(mime)

    @Slot()
    def openProperties(self):
        """Open a dialog with the properties of the character."""
        current = self.grid.view.selectionModel().currentIndex()
        if not current.isValid():
            return

        if self._properties is not None:
            self._properties.hide()
            self._propertiesClosed()

        charCode = current.data(CharCodeRole)
        fontItem = self.grid.fontItem

        self._properties = CharInfoWidget(fontItem, charCode,
                                          charDb=self.grid.charDb,
                                          fontDb=self.grid.fontDb,
                                          langDb=self.grid.langDb)
        self._properties.closed.connect(self._propertiesClosed)
        self._properties.show()

    @Slot()
    def _propertiesClosed(self):
        """Triggered when the properties are closed."""
        if self._properties is not None:
            self._properties.deleteLater()
            self._properties = None


class GridOptionsToolbox(Toolbox):

    """Actions for the font grid options, e.g. for a toolbar in
    the grid, specifying the size of the view."""

    def __init__(self, grid):
        self.grid = grid
        self.renderingChoice = grid.renderingChoice

        super().__init__()

    def actionDefinitions(self) -> Iterator:

        with self.group('size'):
            yield self.action(self.smaller, _('Smaller'),
                              icon='format-font-size-less')
            yield self.action(self.larger, _('Larger'),
                              icon='format-font-size-more')

    def _jump_to_size(self, offset: int):
        """Increate the size with the given offset of jumps. This
        iterates over the .fontsizes property of the grid."""
        sizes = self.grid.fontsizes
        size = self.renderingChoice.gridSize

        if len(sizes) < 2:
            return

        i = min(range(len(sizes)), key=lambda i: abs(sizes[i] - size))
        try:
            size = sizes[i + offset]
        except IndexError:
            return

        self.renderingChoice.setGridSize(size)

    def larger(self):
        """Make the font larger, by picking the next grid.fontsizes
        size."""
        self._jump_to_size(+1)

    def smaller(self):
        """Make the font larger, by picking the previous grid.fontsizes
        size."""
        self._jump_to_size(-1)


class FontGrid(QtWidgets.QWidget):

    """A character map widget."""

    def __init__(self, charDb: CharacterDatabase=None,
                       fontDb: QtGui.QFontDatabase=None,
                       langDb: LanguageDatabase=None,
                       renderingChoice: FontRenderingChoice=None,
                       options: Options=None,
                       histories: datastore.Histories=None,
                       parent: QtWidgets.QWidget=None):
        super(FontGrid, self).__init__(parent)
        self.charDb = charDb

        if options is None:
            options = Options.getInstance()

        if fontDb is None:
            fontDb = QtGui.QFontDatabase()
        if renderingChoice is None:
            renderingChoice = FontRenderingChoice()
        if charDb is None:
            charDb = CharacterDatabase.getInstance()
        if langDb is None:
            langDb = LanguageDatabase.getInstance()
        if histories is None:
            histories = datastore.Histories.getInstance()

        self.fontDb = fontDb
        self.langDb = langDb
        self.histories = histories
        self.renderingChoice = renderingChoice
        self.fontsizes = [12]
        self.fontItem = None
        self.selectedFontItems = []

        self.charBoxes = []
        self.charInfos = []
        self.charInfosAlt = []

        self.currentModelFontInfo = None
        self.currentChar = None

        searchBar = QtWidgets.QToolBar()
        searchBar.setIconSize(options.toolbarIconSize)
        options.toolbarIconSizeChanged.connect(searchBar.setIconSize)

        self.searchText = searchText = QuickSearch(
                history=histories.get_history('fontgrid-characters'),
                placeholderText=_('Search characters...'))
        searchText.searchTriggered.connect(self._filterTextChanged)

        self.blockCombo = blockCombo = CustomComboBox()
        blockCombo.setNarrow()
        blockCombo.currentIndexChanged.connect(self._blockChanged)
        self.blockByIndex = {}

        self.scriptCombo = scriptCombo = CustomComboBox()
        scriptCombo.currentIndexChanged.connect(self._scriptChanged)
        scriptCombo.setNarrow()
        self.scriptByIndex = {}

        self.renderingChoice.gridChanged.connect(self._renderingChanged)

        searchBar.addWidget(searchText)
        searchBar.addWidget(blockCombo)
        searchBar.addWidget(scriptCombo)

        self.model = model = FontSymbolModel(charDb=charDb, langDb=langDb,
                                             renderingChoice=renderingChoice)

        self.internalCharBar = charBar = self.createCharBar()
        self.externalCharBar = None

        self.filterModel = filterModel = CharFilterModel(charDb)
        filterModel.setSourceModel(model)

        self.view = view = self._createGridView()

        model.gridView = view
        model.charBox = self.charBoxes[0]

        self._updateUnicodeSelectors()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(searchBar)
        layout.addWidget(view, 1)
        layout.addWidget(self.internalCharBar)

        self.setLayout(layout)

        self.toolbox = FontGridToolbox(self)
        self.toolbox.addContextMenu(self.view)
        self.toolbox.disableActions()

        self.optionsToolbox = GridOptionsToolbox(self)
        self.optionsToolbox.populateToolbar(searchBar)

        self.characterCount = QtWidgets.QLabel()
        self.characterCount.setTextFormat(Qt.PlainText)

        self.filterModel.modelReset.connect(self._updateCharacterCount)
        self.filterModel.rowsInserted.connect(self._updateCharacterCount)
        self.filterModel.rowsRemoved.connect(self._updateCharacterCount)

        searchBar.addSeparator()

        self.charBarAction = searchBar.addAction(getIcon('show-character'),
                                                 _('Character information'))
        self.charBarAction.setCheckable(True)
        self.charBarAction.setChecked(True)
        self.charBarAction.toggled.connect(self.toggleCharBar)

        self._updateCharacterCount()

    def _replaceView(self, view: QtWidgets.QAbstractItemView,
                           isListView: bool=True):
        """Replace the view when switching from list view (one-font grid) to
        a table view (multi-font table). Don't forget what view we're using.
        """

        oldView = self.view
        self.model.gridView = view if isListView else None
        self.layout().replaceWidget(oldView, view)
        oldView.deleteLater()
        self.view = view
        self.toolbox.addContextMenu(self.view)

    def _createGridView(self) -> QtWidgets.QListView:
        """Create a new listview font grid view for a single font."""

        view = QtWidgets.QListView()

        view.setViewMode(QtWidgets.QListView.IconMode)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        view.setMovement(QtWidgets.QListView.Snap)
        view.setFlow(QtWidgets.QListView.LeftToRight)
        view.setWrapping(True)
        view.setLayoutMode(QtWidgets.QListView.Batched)
        #view.setGridSize(QtCore.QSize(40, 40))
        view.setItemDelegateForColumn(0, GridCellDelegate(view,
                                                          fontDb=self.fontDb))
        view.setResizeMode(QtWidgets.QListView.Adjust)
        view.setDragEnabled(True)
        view.setDragDropMode(view.DragOnly)
        view.setSelectionMode(view.ExtendedSelection)

        self.transposedModel = None
        view.setModel(self.filterModel)
        view.selectionModel().currentChanged.connect(self._currentChanged)

        return view

    def _createTableView(self) -> QtWidgets.QTableView:
        """Create a new table view for multiple fonts."""

        view = QtWidgets.QTableView()
        view.setItemDelegate(GridCellDelegate(view, fontDb=self.fontDb))
        view.setDragEnabled(True)
        view.setDragDropMode(view.DragOnly)
        view.setSelectionMode(view.ExtendedSelection)

        #self.transposedModel = transposedModel = TransposedModel()
        #transposedModel.setSourceModel(self.filterModel)
        #view.setModel(transposedModel)

        view.setModel(self.filterModel)
        view.selectionModel().currentChanged.connect(self._currentChanged)

        view.setHorizontalHeader(RotatedHeaderView(Qt.Horizontal, angle=0))

        setResizeMode(view.verticalHeader(),
                      QtWidgets.QHeaderView.ResizeToContents)
        setResizeMode(view.horizontalHeader(),
                      QtWidgets.QHeaderView.ResizeToContents)
        return view

    @Slot(bool)
    def toggleCharBar(self, checked: bool=True):
        """Show or hide the internal character bar, depending on the
        first argument."""
        if checked:
            self.internalCharBar.show()
        else:
            self.internalCharBar.hide()

    def saveDockInnerState(self) -> Mapping:
        """Provide options save state for when used as dock"""
        return {'char-bar-visible': not self.internalCharBar.isHidden()}

    def restoreDockInnerState(self, state: Mapping, strict: bool=False):
        """Restore the save state from the options."""
        if 'char-bar-visible' not in state:
            return
        self.charBarAction.setChecked(state['char-bar-visible'])

    def getCharBar(self) -> QtWidgets.QWidget:
        """Get the external character bar widget, for use as a
        dock in the main window."""
        if self.externalCharBar is None:
            self.externalCharBar = self.createCharBar()
        return self.externalCharBar

    def createCharBar(self) -> QtWidgets.QWidget:
        """Create a new character bar controlled by this font grid.
        You typically use a single external character bar, and
        the internal one, so you do not need to create additional ones.
        """

        layout = QtWidgets.QGridLayout()

        charBox = QtWidgets.QLabel()
        charBox.setTextFormat(Qt.PlainText)
        #charBox.setReadOnly(True)

        charInfo = QtWidgets.QLabel()
        charInfo.setTextFormat(Qt.RichText)

        charInfoAlt = QtWidgets.QLabel()
        charInfoAlt.setTextFormat(Qt.RichText)

        selectedChars = QtWidgets.QTextEdit()
        selectedChars.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                                    QtWidgets.QSizePolicy.Ignored)
        metrics = QtGui.QFontMetrics(QtGui.QFont())
        selectedChars.setMinimumSize(QtCore.QSize(
                metrics.width('This is it.'),
                metrics.height()))
        selectedChars.setWordWrapMode(
            QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)

        charInfoAlt.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                  QtWidgets.QSizePolicy.Maximum)

        layout.addWidget(charBox, 0, 0, 2, 1)
        layout.addWidget(charInfo, 0, 1, 2, 1)
        layout.addWidget(charInfoAlt, 0, 2, 1, 2)
        layout.addWidget(selectedChars, 1, 2, 1, 2)

        layout.setRowStretch(1, 1)

        self.charBoxes.append(charBox)
        self.charInfos.append(charInfo)
        self.charInfosAlt.append(charInfoAlt)

        self._updateCharBars()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    @Slot()
    def _updateCharacterCount(self, *args):
        """Update the character count."""
        self.characterCount.setText(
            _('{count} characters out of {total}').format(
                    total=self.model.rowCount(),
                    count=self.filterModel.rowCount()))

    def _updateUnicodeSelectors(self):
        """Update the unicode selectors."""
        blockCombo = self.blockCombo
        scriptCombo = self.scriptCombo

        self.scriptByIndex.clear()
        self.blockByIndex.clear()
        blockCombo.clear()
        scriptCombo.clear()

        blockCombo.addItem(_('All'))

        unicodeBlocks = self.charDb.unicode_blocks
        scripts = self.charDb.scriptorder

        curBlock = self.filterModel.filterBlock
        curScript = self.filterModel.filterScript
        curBlockIndex = 0
        curScriptIndex = 0
        if self.model.fontCharBlocks:
            available = self.model.fontCharBlocks
            scriptBlocks = []
            for script in scripts:
                for block in self.charDb.scripts[script]:
                    scriptBlocks.append(block)

            unicodeBlocks = blockmath.overlapping_blocks(unicodeBlocks,
                                                         available, True)
            scriptBlocks = blockmath.overlapping_blocks(scriptBlocks,
                                                        available, True)
            scripts = OrderedSet(s.name for s in scriptBlocks)

        for i, block in enumerate(unicodeBlocks, 1):
            if curBlock is not None and curBlock.name == block.name:
                curBlockIndex = i

            self.blockByIndex[i] = block
            blockCombo.addItem(block.name)

        self.scriptCombo.addItem(_('All'))
        for i, script in enumerate(scripts, 1):
            if curScript is not None and curScript == script:
                curScriptIndex = i
            self.scriptByIndex[i] = script
            scriptCombo.addItem(script)

        changed = False

        blockCombo.setCurrentIndex(curBlockIndex)
        if not curBlockIndex:
            if self.filterModel.filterBlock is not None:
                changed = True
            self.filterModel.filterBlock = None

        blockCombo.setCurrentIndex(curBlockIndex)
        if not curScript:
            if self.filterModel.filterScript is not None:
                changed = True
            self.filterModel.filterScript = None

        ## This is a good idea, but the user will be confused.
        #if (not self.model.ownCharacters or
        #    len(self.model.characters) > BIG_FONT_THRESHOLD):

        if not self.model.ownCharacters and (
            self.model.encoding is None or
            self.model.encoding.unicode):

            if not self.filterModel.displayLittle:
                changed = True
            self.filterModel.displayLittle = True

        else:
            if self.filterModel.displayLittle:
                changed = True
            self.filterModel.displayLittle = False

        if changed:
            self.filterModel.invalidateFilter()

    @Slot(str)
    def _filterTextChanged(self, text: bool):
        """The filter text was changed. Update the filter proxy."""
        self.filterModel.filterText = text.lower()
        self.filterModel.invalidateFilter()

    @Slot(int)
    def _blockChanged(self, index: int):
        """The selected unicode block was changed. Update the filter proxy."""
        if index == 0:
            self.filterModel.filterBlock = None
        else:
            self.filterModel.filterBlock = self.blockByIndex.get(index)
        self.filterModel.invalidateFilter()

    @Slot(int)
    def _scriptChanged(self, index: int):
        """The selected script was changed. Update the filter proxy."""
        if index == 0:
            self.filterModel.filterScript = None
        else:
            self.filterModel.filterScript = self.scriptByIndex.get(index)
        self.filterModel.invalidateFilter()

    @Slot(QtCore.QModelIndex)
    def _currentChanged(self, index: QtCore.QModelIndex):
        """The current index of the model was changed. Notify the gang."""
        if not index.isValid():
            self.toolbox.disableActions()
            return

        self.currentChar = index.data(CharCodeRole)
        self.currentModelFontInfo = index.data(ModelFontInfoRole)

        self._currentCharacterChanged()

    @Slot()
    def _currentCharacterChanged(self):
        """The current character was changed. Notify the gang."""
        char = self.currentChar

        if char is None:
            self.toolbox.disableActions()
            return

        self._updateCharBars()
        self.toolbox.enableActions()

    @Slot()
    def _updateCharBars(self):
        """Update the character bars if the character was changed."""
        char = self.currentChar
        if char is None:
            return

        mfi = self.currentModelFontInfo

        for charBox in self.charBoxes:
            charBox.setText(chr(char))
            if mfi is not None:
                charBox.setFont(mfi.font)

        text = []
        textAlt = []
        self.model.fillCharacterInfoTexts(char, text, textAlt,
                                          includePreview=False,
                                          modelFontInfo=mfi)
        for charInfo in self.charInfos:
            charInfo.setText('<br>'.join(text))
        for charInfoAlt in self.charInfosAlt:
            charInfoAlt.setText('<br>'.join(textAlt))

    def modelFontInfoForItem(self, item: 'typeatlas.fontlist.FontLike',
                                   *args, **kwargs) -> SymbolModelFontInfo:
        """Get the SymbolModelFontInfo instance for a font item."""
        options = self.renderingChoice.options
        return SymbolModelFontInfo(self.fontForItem(item), item, *args,
                                   options=options, **kwargs)

    def fontForItem(self, item: 'typeatlas.fontlist.FontLike',
                          forCharBox: bool=False) -> QtGui.QFont:
        """Get the QFont for a font item. The size depends on forCharBox
        state and the rendering choice."""

        if forCharBox:
            size = self.renderingChoice.charBoxSize
        else:
            size = self.renderingChoice.gridSize
        font = self.fontDb.font(item.family, item.style, size)
        font.setStyleHint(QtGui.QFont.AnyStyle,
                          self.renderingChoice.antialiasStyle)
        font.setHintingPreference(self.renderingChoice.hintingPreference)
        return font

    def _setFontSizesFontItem(self, item: 'typeatlas.fontlist.FontLike',
                              selected: 'SequenceOf[typeatlas.fontlist.FontLike]'=()):
        """Set the font sizes for the selected font items."""
        self.fontsizes = self.fontDb.smoothSizes(item.family, item.style)
        if not self.fontsizes:
            self.fontsizes = self.fontDb.standardSizes()
            if not self.fontsizes:
                self.fontsizes = [12]

    def _setCharBoxesFontItem(self, item: 'typeatlas.fontlist.FontLike',
                              selected: 'SequenceOf[typeatlas.fontlist.FontLike]'=()):
        """Change all the character boxes' fonts."""
        charBoxFont = self.fontForItem(item, forCharBox=True)
        for charBox in self.charBoxes:
            charBox.setFont(charBoxFont)

    @Slot(object)
    @Slot(object, list)
    def setFontItem(self, item: 'typeatlas.fontlist.FontLike',
                          selected: 'SequenceOf[typeatlas.fontlist.FontLike]'=(),
                          nochange: bool=False, *args, **kwargs):
        """Set the current font item. You can also pass selected items if
        multiple fonts are selected.

        If nochange=True is passed, only the fonts are updated, not the
        character lists or the overall list of fonts.

        The current font is removed from the selected fonts.
        """

        if selected:
            return self._setMultiFontItems(item, selected,
                                           nochange=nochange,
                                           *args, **kwargs)

        if self.selectedFontItems:
            self._replaceView(self._createGridView())

        if item is None:
            return

        self.fontItem = item
        if not nochange:
            self.selectedFontItems = []

        self._setFontSizesFontItem(item)
        self._setCharBoxesFontItem(item)
        self.model.setFont(self.fontForItem(item), item, nochange=nochange,
                           *args, **kwargs)

        if not nochange:
            self._updateUnicodeSelectors()
        else:
            self.view.reset()

    @Slot(object, list)
    def _setMultiFontItems(self,
                           current: 'typeatlas.fontlist.FontLike',
                           selected: 'SequenceOf[typeatlas.fontlist.FontLike]'=(),
                           nochange: bool=False, *args, **kwargs):
        """Implementation of setFontItem() for non-empty selected."""

        if current is None and not selected:
            return

        if current is None:
            current = selected[0]
        selected = [s for s in selected if s is not current]

        if not selected:
            self.setFontItem(current, nochange=nochange, *args, **kwargs)
            return

        if nochange:
            self.model.updateQtFonts(self.fontForItem(self.fontItem),
                                     map(self.fontForItem,
                                         self.selectedFontItems))
            return

        if not self.selectedFontItems:
            self._replaceView(self._createTableView(), isListView=False)

        self.fontItem = current
        self.selectedFontItems = selected

        self._setFontSizesFontItem(current, selected)
        self._setCharBoxesFontItem(current, selected)
        self.model.setMultiFont(self.modelFontInfoForItem(current, *args, **kwargs),
                                (self.modelFontInfoForItem(item, *args, **kwargs)
                                 for item in selected))

        self._updateUnicodeSelectors()

    @Slot()
    def _renderingChanged(self):
        """The rendering of fonts was chnaged. Re-render the views."""
        self.setFontItem(self.fontItem, self.selectedFontItems,
                         nochange=True)

