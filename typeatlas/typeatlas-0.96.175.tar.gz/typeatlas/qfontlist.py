# -*- coding: utf-8 -*-
#
#    TypeAtlas Font List implemented using the Qt Library
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
#                                 ***
#
#    Alternatively, you may use this file (part of TypeAtlas libraries)
#    under the terms of the X11/MIT license as follows:
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following
#    conditions:
#
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#    OTHER DEALINGS IN THE SOFTWARE.
#

from __future__ import absolute_import, division

import os
import re
import struct
import os.path
import typeatlas.fontlist as fontlist
from collections import defaultdict
from collections.abc import Mapping, Set
from typeatlas import opentype, blockmath, rangemath, charinfo, event
from typeatlas.util import OrderedSet, generic_type
from typeatlas.langutil import _
from typeatlas.compat import QtCore, QtGui, QtWidgets, Qt, Slot, Signal
from typeatlas.compat import qtGetBytes
from itertools import chain, count


SetOf = generic_type('Set')
IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')
Optional = generic_type('Optional')


# TODO: Can't translate the styles here?

# TODO: Loading info is quite slow due to opening all SFNT tables,
#       and all fonts by file without cache. Maybe allow skipping this?


def getWeight(font: QtGui.QFont) -> float:
    """Get the weight of the QFont in the same scale fontconfig would
    use."""

    # FIXME: PySide constants suck, only work on the right-hand side
    # of an equation (broken __rsub__), so QtCore.Qt.UserRole + 3 is OK,
    # 3 + QtCore.Qt.UserRole is not (same for QtGui.QFont.Normal)
    # tag: zjsZ0zzunjo

    factor = ((fontlist.WEIGHT_BOLD - fontlist.WEIGHT_NORMAL) /
                (QtGui.QFont.Bold - QtGui.QFont.Normal))
    return ((font.weight() - int(QtGui.QFont.Normal)) * factor
                    + fontlist.WEIGHT_NORMAL)


def getWidth(font: QtGui.QFont) -> float:
    """Get the width of the QFont in the same scale fontconfig would
    use."""

    # FIXME: see tag: zjsZ0zzunjo
    factor = ((fontlist.WIDTH_NORMAL - fontlist.WIDTH_CONDENSED) /
                (QtGui.QFont.Unstretched - QtGui.QFont.Condensed))
    return ((font.stretch() - int(QtGui.QFont.Unstretched)) * factor
                    + fontlist.WIDTH_NORMAL)


def getSlant(font: QtGui.QFont) -> int:
    """Get the width of the QFont in the same scale fontconfig would
    use."""
    style = font.style()
    if style == QtGui.QFont.StyleNormal:
        return fontlist.SLANT_NORMAL
    elif style == QtGui.QFont.StyleItalic:
        return fontlist.SLANT_ITALIC
    elif style == QtGui.QFont.StyleOblique:
        return fontlist.SLANT_OBLIQUE


def getFont(fontDb: QtGui.QFontDatabase,
            familyName: str, styleName: str,
            fileinfos: IterableOf[fontlist.FontFileDetectInfo]=()
            ) -> fontlist.Font:
    """Get the font information about the given family and style from the
    Qt font database, the provided file infos."""

    font = fontlist.Font()

    font.family = familyName
    font.style = styleName

    qfont = fontDb.font(familyName, styleName, 16)

    font.weight = getWeight(qfont)
    font.slant = getSlant(qfont)
    font.width = getWidth(qfont)

    font.outline = fontDb.isSmoothlyScalable(familyName, styleName)
    font.scalable = fontDb.isScalable(familyName, styleName)

    font.file = getFileName(qfont)

    font.set_cachekey(familyName + ' ' + styleName)

    rawfont = None

    fileinfos = list(fileinfos)

    if fileinfos:
        font.file_alts = [fontlist.FontFile(fi.file, fi.index)
                          for fi in fileinfos]
        font.file, font.index, formathint = fileinfos[0]

        if formathint == 'SFNT':
            font.sfnt = True
            pass

        elif formathint:
            font.fontformat = formathint

        elif font.outline or font.scalable:
            font.fontformat = 'Type 1'

    elif hasattr(QtGui, 'QRawFont'):
        rawfont = QtGui.QRawFont.fromFont(qfont)
        if rawfont.fontTable('loca'):
            font.fontformat = 'TrueType'
            font.sfnt = True
            if not font.file:
                font.ext = 'ttf'
        elif rawfont.fontTable('CFF ') or rawfont.fontTable('CFF2'):
            if not font.file:
                font.ext = 'otf'
            font.fontformat = 'CFF'
            font.sfnt = True
        elif (not rawfont.fontTable('head') and
                (font.outline or font.scalable)):
            if not font.file:
                # That's bad guesswork. It may not be true.
                # If this does not get hit, fontformat will be filled from
                # extension. Type 1 fonts are not multi-format, so extension
                # is good enough (probably better than this over-optimistic
                # guess).
                font.fontformat = 'Type 1'
                font.ext = 't1'

    #fillDetailedInfo(font, qfont, rawfont)
    fontlist.autofill_font_info(font)

    return font


def updateFamilyInfo(fontDb: QtGui.QFontDatabase, family: fontlist.FontFamily):
    """Fill any family information, particularly writing system
    and generic family. This is to be called manually at the moment."""

    family.writingSystems = fontDb.writingSystems(family.family)
    for style in family.styles:
        style.writingSystems = family.writingSystems
    if list(family.writingSystems) == [QtGui.QFontDatabase.Symbol]:
        for style in family.styles:
            style.genericfamily = 'symbol'
            style.genericfamily_source = fontlist.SOURCE_QT


def _fillDetailedInfo(font: fontlist.Font, qfont: QtGui.QFont,
                      rawfont: 'QtGui.QRawFont'=None):
    """Fill any detailed information about the font, such as PANOSE
    class. This is the actual implementation called
    by fillDetailedInfo.
    """
    if hasattr(font, 'panoseclass'):
        return

    # FIXME: This fills up memory and never frees it.
    if rawfont is None:
        if not hasattr(QtGui, 'QRawFont'):
            font.ibmclass = opentype.NO_IBM_CLASS_DATA
            font.panoseclass = opentype.NO_PANOSE_DATA
            font.embedding = opentype.NO_EMBEDDING_INFO
            return
        rawfont = QtGui.QRawFont.fromFont(qfont)

    ## NOTE This is extremely slow, don't do it.
    #allChars = charinfo.all_character_codes()
    #chars = filter(rawfont.supportsCharacter, allChars)
    #font.charblocks = list(blockmath.toblocks_inorder(chars))

    os2 = rawfont.fontTable('OS/2')
    if not os2:
        font.ibmclass = opentype.NO_IBM_CLASS_DATA
        font.panoseclass = opentype.NO_PANOSE_DATA
        font.embedding = opentype.NO_EMBEDDING_INFO
        return

    os2 = qtGetBytes(os2)

    font.ibmclass = opentype.extract_ibm_class(os2)
    font.panoseclass = opentype.extract_panose_class(os2)
    font.embedding = opentype.extract_embedding_info(os2)
    if not font.genericfamily:
        font.genericfamily = font.panoseclass.genericfamily
        font.genericfamily_source = fontlist.SOURCE_PANOSE
    if not font.genericfamily:
        font.genericfamily = font.ibmclass.genericfamily
        font.genericfamily_source = fontlist.SOURCE_IBM


class _Filler(QtCore.QThread):
    """A thread that fills the detailed font info with
    _fillDetailedInfo. This is not presently being used."""

    def __init__(self, font: fontlist.Font, qfont: QtGui.QFont):
        super(_Filler, self).__init__()
        self.font = font
        self.qfont = qfont

    def run(self):
        _fillDetailedInfo(self.font, self.qfont)


def fillDetailedInfo(font: fontlist.Font, qfont: QtGui.QFont,
                     rawfont: 'QtGui.QRawFont'=None):
    """Fill any detailed information about the font, such as PANOSE
    class. This is to be called when fontlist.fill_detailed_info
    raises a fontlist.NotSupportedError only, which means fontTools
    was not available to fill it.
    """
    _fillDetailedInfo(font, qfont, rawfont)
    return

    if hasattr(font, 'panoseclass'):
        return
    if rawfont is not None:
        return _fillDetailedInfo(font, qfont, rawfont)

    thread = _Filler(font, qfont)
    thread.start()
    thread.wait()
    thread.deleteLater()


def getFileName(font: QtGui.QFont) -> str:
    """Get the file name of the font? No, can't do. A place holder for
    when we eventually figure out a way."""
    try:
        # This doesn't really work, resort to other forms of discovery.
        #return font.rawName()
        return ''
    except AttributeError:
        return ''


class _StopCrawling(Exception):
    """Stop crawling font files - internal exception."""


class QtFontFinder(fontlist.FontFinder):

    def __init__(self, fontDb: QtGui.QFontDatabase=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if fontDb is None:
            fontDb = QtGui.QFontDatabase()
        self.fontDb = fontDb

    def _findFontFiles(self, knownFamilies: Set=()
                       ) -> fontlist.FamilyFilePathType:
        """Find the font files associated with family and style names.
        This tries to use fontlist.crawl_font_directories() if fontTools
        is available, if that's not supported, this uses the slow code path
        which uses QRawFont to fill the information.
        """
        locations = self.fontdirs()

        i = 0
        abort = False
        autoabort = True

        fontnum = count(0)

        def progress(num: int=0):
            """Tick the progress."""
            self.fontprogress(
                    num, len(knownFamilies),
                    message=_('First run: Discovering font files: '
                              '{} out of {}').format(num, len(knownFamilies)))

        def familyAdded(name: str, ignored: Mapping):
            """A family was added to the font files dictionary. Tick the
            progress bar."""
            nonlocal i, abort

            if name not in knownFamilies:
                return

            i += 1
            progress(i)

            if (fontlist.FONT_LIMIT is not None and
                next(fontnum) >= fontlist.FONT_LIMIT):

                abort = True
                if autoabort:
                    # FIXME: Our API allows this, but it's not documented.
                    #        Probably because it's ugly.
                    #        We only get here in debug mode, so who cares?
                    def circuitbreaker(*args, **kwargs):
                        raise _StopCrawling()
                    fontFiles.added = circuitbreaker

        fontFiles = event.NoisyMapping()
        fontCounts = {}

        fontFiles.added.connect(familyAdded)
        progress()

        try:
            fontlist.crawl_font_directories(locations, fontFiles, fontCounts)
        except fontlist.NotSupportedError:
            pass
        except _StopCrawling:
            pass

        autoabort = False

        if not hasattr(QtGui, 'QRawFont') or abort:
            self.fontprogressdone()
            return fontFiles

        for location in locations:
            if abort:
                break

            for dirpath, dirnames, filenames in os.walk(location):
                if abort:
                    break

                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if fontCounts.get(filepath):
                        continue

                    rawFont = QtGui.QRawFont(filepath, 16)

                    family = rawFont.familyName()
                    style = rawFont.styleName()

                    if family in fontFiles:
                        styleFiles = fontFiles[family]
                    else:
                        styleFiles = fontFiles[family] = defaultdict(OrderedSet)

                    if rawFont.fontTable('loca'):
                        formathint = 'TrueType'

                    elif rawFont.fontTable('CFF ') or rawFont.fontTable('CFF2'):
                        formathint = 'CFF'

                    elif rawFont.fontTable('head'):
                        formathint = 'SFNT'

                    else:
                        formathint = None

                    fontCounts[filepath] = 1
                    styleFiles[style].add(fontlist.FontFileDetectInfo(
                                                filepath, 0, formathint))


        self.fontprogressdone()
        return fontFiles

    def fontdirs(self) -> SetOf[str]:
        fontdirs = OrderedSet()
        if hasattr(QtCore, 'QStandardPaths'):
            fontdirs.update(QtCore.QStandardPaths.standardLocations(
                                QtCore.QStandardPaths.FontsLocation))
        else:
            fontdirs.add(QtGui.QDesktopServices.storageLocation(
                                QtGui.QDesktopServices.FontsLocation))
        try:
            fontdirs.update(super().fontdirs())
        except fontlist.NotSupportedError:
            pass
        return fontdirs

    @classmethod
    def supported(self) -> bool:
        return True

    @classmethod
    def remote_supported(self) -> bool:
        return False

    def fonts(self) -> IteratorOf[fontlist.Font]:

        try:
            yield from super().fonts()
        except fontlist.NotSupportedError:
            pass
        else:
            return

        cache = self.metadata_cache

        fontDb = self.fontDb
        familyNames = OrderedSet(fontDb.families())
        familyStyles = {}

        crawlAllFiles = False

        for familyName in familyNames:
            familyStyles[familyName] = fontDb.styles(familyName) or ['Regular']

        # Attempting to fill info with cached font files.
        cachedFiles = {}

        if cache is None:
            crawlAllFiles = True

        else:
            # Count fonts for FONT_LIMIT
            fontnum = count()

            for familyName in familyNames:

                if (fontlist.FONT_LIMIT is not None and
                    next(fontnum) >= fontlist.FONT_LIMIT):

                    crawlAllFiles = False
                    break

                for styleName in familyStyles[familyName]:
                    cachekey = familyName + ' ' + styleName
                    fileinfos = cache.get_field(cachekey, 'fileinfos')
                    if fileinfos is not None:
                        try:
                            cachedFiles[familyName, styleName] = [
                                fontlist.FontFileDetectInfo(*info)
                                for info in fileinfos
                            ]
                        except (TypeError, ValueError) as exc:
                            cache.field_corrupt(cachekey, 'fileinfos', exc)

                    else:
                        crawlAllFiles = True
                        break

                if crawlAllFiles:
                    break

        if not crawlAllFiles:
            for familyName in familyNames:
                for styleName in familyStyles[familyName]:
                    fileinfos = cachedFiles[familyName, styleName]
                    font = getFont(fontDb, familyName, styleName, fileinfos)
                    font.source = 'qt'
                    font.finder = self
                    yield font
            return


        # If cached files fail us, attempt to find all font files,
        # create fonts that way, and cache those.
        fontFiles = self._findFontFiles(familyNames)

        for familyName in familyNames:
            styleFiles = fontFiles.get(familyName)
            if not styleFiles:
                # Qt tends to add foundry, like Zilla Slab [NONE],
                # we could alternatively fill in the foundry from the
                # first semi-colon column from opentype.UNIQUE_NAME_ID,
                # but why make it so complicated anyhoo.
                familyNameSimple = re.sub(r'\s+\[[^\]]+\]$', '', familyName)
                if familyNameSimple not in familyNames:
                    styleFiles = fontFiles.get(familyNameSimple)
                    if not styleFiles:
                        if fontlist.FONT_LIMIT is not None:
                            continue

            for styleName in familyStyles[familyName]:

                filenames = []

                if styleFiles:
                    fileinfos = styleFiles.get(styleName, ())
                else:
                    fileinfos = ()

                if not fileinfos:
                    if fontlist.FONT_LIMIT is not None:
                        continue

                font = getFont(fontDb, familyName, styleName, fileinfos)
                font.source = 'qt'
                font.finder = self

                if cache is not None:
                    cache.set_field(font, 'fileinfos', list(fileinfos))

                yield font

    def substitute(self, family: str, style: str) -> fontlist.Font:
        try:
            return super().substitute(family, style)
        except fontlist.NotSupportedError:
            pass

        return getFont(self.fontDb, family, style, ())

    def fill_detailed_info(self, font: fontlist.Font,
                                 qfont: QtGui.QFont=None,
                                 rawfont: 'QtGui.QRawFont'=None):
        if font.monospace is None:
            font.monospace = self.fontDb.isFixedPitch(font.family, font.style)

        try:
            return super().fill_detailed_info(font)
        except fontlist.NotSupportedError:
            pass

        if hasattr(font, 'panoseclass'):
            return

        if self.metadata_cache is not None:
            if self.metadata_cache.fill_classes(font):
                return

        if qfont is None:
            qfont = self.fontDb.font(font.family, font.style, 16)

        fillDetailedInfo(font, qfont, rawfont)

        if (self.metadata_cache is not None and
            font.panoseclass is not opentype.NO_PANOSE_DATA and
            font.ibmclass is not opentype.NO_IBM_CLASS_DATA):
                self.metadata_cache.cache_classes(font)

    def fill_charset(self, font: fontlist.Font):
        super().fill_charset(font)
        if font.charset is not None:
            return

        if not hasattr(QtGui, 'QRawFont'):
            return False

        # WARNING This is extremely extremely slow
        qfont = self.fontDb.font(font.family, font.style, 16)
        rawfont = QtGui.QRawFont.fromFont(qfont)
        allChars = charinfo.all_character_codes()
        chars = filter(rawfont.supportsCharacter, allChars)
        #font.charblocks = list(blockmath.toblocks_inorder(chars))
        font.charset = rangemath.OrdinalRange.from_iterable(chars)
        if self.metadata_cache is not None:
            self.metadata_cache.cache_charset(font)

        return True


_wsToKey = None
_keyToWs = None

def _populateWritingSystemMaps():
    """Populate writing system to name and name to writing
    system dictionaries."""

    global _wsToKey, _keyToWs

    _wsToKey = {}
    _keyToWs = {}

    for key, value in vars(QtGui.QFontDatabase).items():
        if not isinstance(value, QtGui.QFontDatabase.WritingSystem):
            continue
        key = str(key)
        _wsToKey[value] = key
        _keyToWs[key] = value


def writingSystemToString(ws: int, fallback: bool=True) -> str:
    """Return a string to serialize a QtGui.QFontDatabase.WritingSystem."""
    if _wsToKey is None:
        _populateWritingSystemMaps()
    try:
        return _wsToKey[ws]
    except KeyError:
        if not fallback:
            raise
        return str(ws)


def stringToWritingSystem(s: str, fallback: bool=True) -> int:
    """Return QtGui.QFontDatabase.WritingSystem from a string for
    serialization."""
    if _keyToWs is None:
        _populateWritingSystemMaps()

    try:
        return _keyToWs[s]
    except KeyError:
        if not fallback:
            raise
        s = str(s)
        if s.isdigit():
            return int(s)
        return s


_writingSystemAliases = None

def writingSystemAliases() -> Mapping:

    """Return writing system aliases of various kinds.
    Read the source. This is work in progress and not yet used."""

    global _writingSystemAliases

    if _writingSystemAliases is not None:
        return _writingSystemAliases

    scripts = {
        #'Any': '',
        'Latin': 'Latn',
        'Greek': 'Grek',
        'Cyrillic': 'Cyrl',
        'Armenian': 'Armn',
        'Hebrew': 'Hebr',
        'Arabic': 'Arab',
        'Syriac': 'Syrc',
        'Thaana': 'Thaa',
        'Devanagari': 'Deva',
        'Bengali': 'Beng',
        'Gurmukhi': 'Guru',
        'Gujarati': 'Gujr',
        'Oriya': 'Orya',
        'Tamil': 'Taml',
        'Telugu': 'Telugu',
        'Kannada': 'Knda',
        'Malayalam': 'Mlym',
        'Sinhala': 'Sinh',
        'Thai': 'Thai',
        'Lao': 'Laoo',
        'Tibetan': 'Tibt',
        'Myanmar': 'Mymr',
        'Georgian': 'Geor',
        'Khmer': 'Khmr',
        'SimplifiedChinese': 'Hans',
        'TraditionalChinese': 'Hant',
        'Japanese': 'Jpan',
        'Korean': 'Kore',
        #'Vietnamese': 'Latn',
        #'Symbol': 'Zsym',
        ##'Other': 'Zyyy', # Alias for Symbol in Qt
        'Ogham': 'Ogam',
        'Runic': 'Runr',
        'Nko': 'Nkoo',
    }

    languages = {
        'Vietnamese': 'vi',

        #'Latin': many
        'Greek': 'el',
        'Armenian': 'hy',
        'Hebrew': ['he', 'yi', 'lad', 'mxi'],
        'Arabic': ['ar', 'fa', 'ms', 'ur'],
        #'Syriac': many
        'Thaana': 'dv',
        #'Devanagari': many
        'Bengali': ['bn'], # ...and Sanskrit 'sa'
        'Gurmukhi': ['pa', 'sd'],
        'Gujarati': ['gu', 'kfr'], # and many more
        'Oriya': ['or'], # ...and many regional
        'Tamil': ['ta'], # ...and many regional
        'Telugu': ['te'],
        'Kannada': ['kn'],
        'Malayalam': 'ml',
        'Sinhala': 'si',
        'Thai': ['th', 'sou'], # ...and many more
        'Lao': ['lo'], # ...and many regional
        'Tibetan': ['bo', 'dz', 'sip', 'lbj', 'zau', 'jul'],
        'Myanmar': 'my',
        'Georgian': 'ka',
        'Khmer': 'km',
        'SimplifiedChinese': ['zh-CN', 'zh-SG'],
        'TraditionalChinese': ['zh-TW', 'zh-HK', 'zh-MO'],
        'Japanese': ['ja', 'ain'],
        'Korean': ['ko', 'jje', 'cia'],
        #'Ogham': 'Ogam',
        #'Runic': 'Runr',
        'Nko': ['nqo', 'bm', 'dyu',
                'mku', 'emk', 'msc', 'mzj', 'jod', 'jud',
                'kfo', 'kga', 'mxx'],
    }

    # Ensure some consistency for now
    for key, value in list(languages.items()):
        if not isinstance(value, list):
            languages[key] = [value]

    result = dict(
        writingSystemNameToScript=scripts,
        writingSystemNameToLanguages=languages,
        writingSystemToScript={},
        writingSystemToLanguages={},

        scriptToWritingSystemName={},
        languageToWritingSystemName={},
        scriptToWritingSystem={},
        languageToWritingSystem={},
    )

    for wsName, script in list(scripts.items()):

        result['scriptToWritingSystemName'][script] = wsName

        ws = getattr(QtGui.QFontDatabase, key, None)
        if (ws is None or
            not isinstance(ws, QtGui.QFontDatabase.WritingSystem)):
                continue

        result['writingSystemToScript'][ws] = script
        result['scriptToWritingSystem'][script] = ws

    for wsName, langs in list(languages.items()):
        for lang in langs:
            result['languageToWritingSystemName'][lang] = wsName

        ws = getattr(QtGui.QFontDatabase, key, None)
        if (ws is None or
            not isinstance(ws, QtGui.QFontDatabase.WritingSystem)):
                continue

        result['writingSystemToLanguages'][ws] = langs
        for lang in langs:
            result['languageToWritingSystem'][lang] = ws

    _writingSystemAliases = result

    return result
