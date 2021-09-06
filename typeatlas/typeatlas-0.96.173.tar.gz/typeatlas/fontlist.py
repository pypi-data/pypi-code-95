# -*- coding: utf-8 -*-
#
#    TypeAtlas Font List
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

"""Get font lists from fontconfig.

You can use the FontFinder class to get font information.
The alternative implementation in qfontlist is cross-platform
alternative that can skip fontconfig at the expense of performance.
"""


import shutil
import copy
import os.path
import subprocess as sp
import shlex
import sys
import glob
import weakref
import urllib.parse
import random
import string
import typeatlas
from typeatlas.util import OrderedSet, N_, U_, debugmsg, generic_type
from typeatlas.util import MaybeLazy
from typeatlas import opentype, external, proginfo, annotations
from typeatlas import rangemath
from collections import OrderedDict, namedtuple, defaultdict
from collections.abc import Callable, Set, MutableSet
from operator import attrgetter
from itertools import groupby, chain, count
try:
    from fontTools import ttLib
except ImportError:
    ttLib = None

SequenceOf = generic_type('Sequence')
TupleOf = generic_type('Tuple')
Union = generic_type('Union')
Optional = generic_type('Optional')
SetOf = generic_type('Set')
IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')
MappingOf = generic_type('Mapping')
MutableMappingOf = generic_type('MutableMapping')
MutableSetOf = generic_type('MutableSet')
Any = generic_type('Any')


file_extensions = OrderedDict()
file_mimetypes = OrderedDict()

WEIGHT_LIGHT = 50
WEIGHT_NORMAL = 80
WEIGHT_BOLD = 200
SLANT_NORMAL = 0
SLANT_ITALIC = 100
SLANT_OBLIQUE = 110

WIDTH_NORMAL = 100
WIDTH_CONDENSED = 75

DISABLE_FC_LIST = False
LOAD_CHARSET_EARLY = False
FONT_LIMIT = None

## Tests and debug
if os.environ.get('TYPEATLAS_DEBUG_DISABLE_FONTCONFIG'):
    DISABLE_FC_LIST = True
if os.environ.get('TYPEATLAS_DEBUG_DISABLE_FONTTOOLS'):
    ttLib = None
if os.environ.get('TYPEATLAS_DEBUG_FONTLIMIT', '').isdigit():
    FONT_LIMIT = int(os.environ['TYPEATLAS_DEBUG_FONTLIMIT'])


class FileFormat(object):

    """Information about a registered file format, including extension,
    name description, icon, etc.

    This differs from a font format. The file format is the container that
    contains the font data. The font format is the format of the data
    contained inside.
    """

    def __init__(self, ext: str, name: str, description: str, icon: str=None,
                 multiformat: bool=False,  mimetypes: SequenceOf[str]=(),
                 fontformat: str=None,
                 annotation: annotations.Annotation=None):
        self.ext = ext
        self.name = name
        self.description = description
        self.icon = icon
        self.multiformat = multiformat
        self.mimetypes = mimetypes
        self.fontformat = fontformat
        self.annotation = annotation

    def __repr__(self):
        return '%s(%r, %s, <...>)' % (type(self).__name__,
                                      self.ext, self.name)


def add_file_format(ext: str, name: str, description: str, icon: str=None,
                    multiformat: bool=False, mimetypes: SequenceOf[str]=(),
                    *args, **kwargs) -> FileFormat:
    """Register a file format."""
    file_format = FileFormat(ext, name, description, icon, multiformat,
                             mimetypes, *args, **kwargs)
    file_extensions[ext] = file_format
    for mime in mimetypes:
        if mime not in file_mimetypes:
            file_mimetypes[mime] = file_format
    return file_format


FILE_TTF = add_file_format(
                'ttf', 'TrueType', N_('TrueType Font'), 'ttf', False,
                ['font/ttf', 'application/x-font-ttf'],
                fontformat='TrueType', annotation=annotations.TRUETYPE_FILE)
FILE_TTC = add_file_format(
                'ttc', 'TrueType', N_('TrueType Collection'), 'ttf', False,
                ['font/ttf', 'application/x-font-ttf'],
                fontformat='TrueType', annotation=annotations.TRUETYPE_FILE)
FILE_OTF = add_file_format(
                'otf', 'OpenType', N_('OpenType Font'), 'otf', True,
                ['font/otf', 'application/vnd.ms-opentype',
                 'application/x-font-otf'],
                annotation=annotations.OPENTYPE_FILE)
FILE_OTC = add_file_format(
                'otc', 'OpenType', N_('OpenType Collection'), 'otf', True,
                ['font/otf', 'application/vnd.ms-opentype',
                 'application/x-font-otf'],
                annotation=annotations.OPENTYPE_FILE)
FILE_EOT = add_file_format(
                'eot', 'Embedded OpenType', N_('Embedded OpenType'),
                'otf', True,
                ['application/vnd.ms-fontobject'],
                annotation=annotations.EMBEDDED_OPENTYPE_FILE)
FILE_DFONT = add_file_format(
                'dfont', 'Datafork TrueType', 'Datafork TrueType', 'ttf', True,
                annotation=annotations.DFONT_FILE)

FILE_PFA = add_file_format(
                'pfa', 'PostScript', N_('PostScript Printer Font ASCII'), 'ps',
                fontformat='Type 1', annotation=annotations.PFA_FILE)
FILE_PFB = add_file_format(
                'pfb', 'PostScript', N_('PostScript Printer Font Binary'), 'ps',
                fontformat='Type 1', annotation=annotations.PFB_FILE)
FILE_T1 = add_file_format(
                't1', 'PostScript', N_('PostScript Type 1 Printer Font'), 'ps',
                fontformat='Type 1',
                annotation=annotations.POSTSCRIPT_FONT_FILE)
FILE_CFF = add_file_format(
                'cff', 'CFF', N_('Bare CFF font'), 'ps',
                fontformat='CFF',
                annotation=annotations.CFF_FILE)
FILE_CEF = add_file_format(
                'cef', 'CEF', N_('CEF font (Adobe SVG viewer)'), 'ps',
                fontformat='CFF',
                annotation=annotations.CEF_FILE)

FILE_WOFF = add_file_format(
                'woff', 'WOFF', 'Web Open Font Format', 'woff', True,
                ['font/woff', 'application/font-woff'],
                annotation=annotations.WOFF_FILE)
FILE_WOFF2 = add_file_format(
                'woff2', 'WOFF',  'Web Open Font Format 2', 'woff', True,
                ['font/woff2'], annotation=annotations.WOFF_FILE)

FILE_PCF = add_file_format(
                'pcf', 'X11 Compiled', N_('Portable Compiled Font Format'),
                'pcf', fontformat='PCF', annotation=annotations.PCF_FILE)
FILE_BDF = add_file_format(
                'bdf', 'X11 Bitmap', N_('Glyph Bitmap Distribution Format'),
                'bdf', fontformat='BDF', annotation=annotations.BDF_FILE)
FILE_SNF = add_file_format(
                'snf', 'X11 Normal', N_('Server Normal Format'),
                'snf', fontformat='SNF', annotation=annotations.SNF_FILE)
FILE_FNT = add_file_format(
                'fon', 'Windows FNT', N_('Windows FNT Bitmap Fonts'), 'fnt',
                fontformat='Windows FNT', annotation=annotations.FNT_FILE)

FILE_PFR = add_file_format(
                'pfr', 'Portable Font Resource',
                'Bitstream TrueDoc Portable Font Resource', 'pfr',
                fontformat='PFR',
                annotation=annotations.PFR_FILE)
FILE_METAFONT = add_file_format(
                'mf', 'Metafont', N_('Metafont (TeX font)'),
                'metafont', fontformat='Metafont',
                annotation=annotations.METAFONT_FILE)

FILE_PSF = add_file_format(
                'psf', 'PC Screen Font', 'PC Screen Font',
                'psf', fontformat='PSF',
                annotation=annotations.PSF_FILE)
FILE_SPEEDO = add_file_format(
                'spd', 'Speedo', 'Speedo',
                'speedo', fontformat='Speedo',
                annotation=annotations.SPEEDO_FILE)

FILE_LEGACY = add_file_format(
                'fnt', 'Legacy application-specific font',
                    N_('Legacy application-specific font'),
                'legacy',
                annotation=annotations.LEGACY_FILE)

FILE_UNKNOWN_FORMAT = FileFormat('', 'Unknown',
                                     N_('Unknown file format'), 'unknown')




compression_extensions = OrderedDict()


Compression = namedtuple('Compression',
                         'ext name description icon mimetype mimetypes')


def add_compression(ext: str, name: str, description: str, icon: str=None,
                    mimetypes: SequenceOf[str]=()) -> Compression:
    """Register a type of compression."""
    mimetype = mimetypes[0] if mimetypes else None
    compression_extensions[ext] = Compression(ext, name, description, icon,
                                              mimetype, mimetypes)
    return compression_extensions[ext]


add_compression('gz', 'Gzip',
                N_('Gzip Lempel-Ziv compression'), 'application-x-gzip',
                ['application/gzip', 'application/x-gzip'])
add_compression('bz2', 'bzip2',
                N_('Bzip2 Burrows-Wheeler block-sorting compression'),
                'application-x-bzip',
                ['application/x-bzip2'])
add_compression('xz', 'XZ',
                N_('XZ-encoded Lempel-Ziv-Markov chain-Algorithm compression'),
                'application-x-compress',
                ['application/x-xz'])
add_compression('lzma', 'LZMA',
                N_('Lempel-Ziv-Markov chain-Algorithm compression'),
                'application-x-compress',
                ['application/x-lzma'])


font_formats = OrderedDict()


class FontFormat(object):

    """Information about a registered font format, including extension,
    name description, icon, etc.

    This differs from a file format. The file format is the container that
    contains the font data. The font format is the format of the data
    contained inside.

    The category_icon is a generic icon for a group of formats, it
    defaults to the icon.
    """

    def __init__(self, name: str, description: str, icon: str=None,
                       category_icon: str=None,
                       annotation: annotations.Annotation=None):
        if category_icon is None:
            category_icon = icon
        self.name = name
        self.description = description
        self.icon = icon
        self.category_icon = category_icon
        self.annotation = annotation

    def __repr__(self):
        return '%s(%r, <...>)' % (type(self).__name__,
                                  self.name)


def add_font_format(name: str, description: str, icon: str=None,
                    category_icon: str=None, *args, **kwargs) -> FontFormat:
    """Register a font format."""
    if category_icon is None:
        category_icon = icon
    font_formats[name] = FontFormat(name, description, icon, category_icon,
                                    *args, **kwargs)
    return font_formats[name]


FONT_TRUETYPE = add_font_format('TrueType',  'TrueType', 'ttf',
                                annotation=annotations.TRUETYPE_FONT)
FONT_CFF = add_font_format('CFF', 'CFF/Type 2', 'type2', 'ps',
                           annotation=annotations.CFF_FONT)
FONT_TYPE1 = add_font_format('Type 1', 'PostScript Type 1',
                             'type1', 'ps-old',
                             annotation=annotations.TYPE1_FONT)
FONT_PCF = add_font_format('PCF', 'X11 Portable Compiled Font',
                           'pcf', 'bitmap', annotation=annotations.PCF_FONT)
FONT_BDF = add_font_format('BDF', 'X11 Glyph Bitmap Distribution Format',
                           'bdf', 'bitmap', annotation=annotations.BDF_FONT)
FONT_SNF = add_font_format('SNF', 'X11 Server Normal Format',
                           'snf', 'bitmap', annotation=annotations.SNF_FONT)
FONT_FNT = add_font_format('Windows FNT', N_('Windows FNT Bitmap Font'),
                           'fnt', 'bitmap', annotation=annotations.FNT_FONT)
FONT_PFR = add_font_format('PFR', 'Portable Font Resource',
                           'pfr', 'outline', annotation=annotations.PFR_FONT)
FONT_TYPE42 = add_font_format('Type 42', N_('Type 42 (TrueType font wrapper)'),
                             'ttf', 'ttf', annotation=annotations.TYPE42_FONT)
FONT_CID_TYPE1 = add_font_format('CID Type 1', 'PostScript Type 1 (CID)',
                                 'type1', 'ps-old',
                                 annotation=annotations.TYPE1_FONT)
FONT_SVG = add_font_format('SVG', N_('SVG color font'), 'svg', 'svg',
                           annotation=annotations.SVG_FONT)
FONT_METAFONT = add_font_format('Metafont', N_('Metafont (TeX font)'),
                                'metafont', 'metafont',
                                 annotation=annotations.METAFONT_FONT)
FONT_PSF = add_font_format('PSF', 'PC Screen Font', 'psf', 'bitmap',
                           annotation=annotations.PSF_FONT)

FONT_SPEEDO = add_font_format('Speedo', 'Speedo', 'speedo', 'speedo',
                              annotation=annotations.SPEEDO_FONT)

FONT_UNKNOWN_FORMAT = FontFormat('Unknown', N_('Unknown font format'),
                                 'unknown', 'unknown')


QUALITY_RELIABLE = 100
QUALITY_UNRELIABLE = 80
QUALITY_GUESSWORK = 50
QUALITY_GARBAGE = 0


class Reference(object):

    """A reference to a source of information about a font, and how
    reliable it is."""

    def __init__(self, name: str, description: str, icon: str=None,
                       category_icon: str=None,
                       quality: int=QUALITY_RELIABLE,
                       annotation: annotations.Annotation=None):
        if category_icon is None:
            category_icon = icon
        self.name = name
        self.description = description
        self.quality = quality
        self.icon = icon
        self.category_icon = category_icon
        self.annotation = annotation

    def __repr__(self):
        return '%s(%r, <...>)' % (type(self).__name__,
                                  self.name)


SOURCE_PANOSE = Reference('PANOSE',
                          U_('The PANOSE classes of the font file'),
                          quality=QUALITY_RELIABLE)
SOURCE_IBM = Reference('IBM',
                       U_('The IBM classes of the font file'),
                       quality=QUALITY_UNRELIABLE)
SOURCE_QT = Reference('QT', U_('The Qt font database'),
                      quality=QUALITY_UNRELIABLE)
SOURCE_NAME_MATCH = Reference(U_('Name match'),
                              U_('Font name was matched against known patterns'),
                              quality=QUALITY_GUESSWORK)
SOURCE_FONTLIST_ORDER = Reference(U_('Font lists order'),
                                  U_('Guessed from position of font in '
                                     'the font lists'),
                                  quality=QUALITY_GARBAGE)

SOURCE_UNKNOWN = Reference('Unknown', U_('Unknown'), quality=QUALITY_GARBAGE)


FONTS_POSTSCRIPT1 = [
    ('Courier', ('Regular', 'Oblique', 'Bold', 'Bold Oblique')),
    ('Helvetica', ('Regular', 'Oblique', 'Bold', 'Bold Oblique')),
    ('Times', ('Roman', 'Italic', 'Bold', 'Bold Italic')),
    ('Symbol', ()),
]

FONTS_POSTSCRIPT2 = [

    ('ITC Avant Garde Gothic', ('Book', 'Book Oblique', 'Demi', 'Demi Oblique')),
    ('ITC Bookman', ('Light', 'Light Italic', 'Demi', 'Demi Italic')),
    ('Courier', ('Regular', 'Oblique', 'Bold', 'Bold Oblique')),
    ('Helvetica', ('Regular', 'Oblique', 'Bold', 'Bold Oblique', 'Condensed', 'Condensed Oblique', 'Condensed Bold', 'Condensed Bold Oblique')),
    ('New Century Schoolbook', ('Roman', 'Italic', 'Bold', 'Bold Italic')),
    ('Palatino', ('Roman', 'Italic', 'Bold', 'Bold Italic')),
    ('Symbol', ()),
    ('Times', ('Roman', 'Italic', 'Bold', 'Bold Italic')),
    ('ITC Zapf Chancery', ('Medium Italic',)),
    ('ITC Zapf Dingbats', ()),
]

FONTS_POSTSCRIPT3 = [
    ('Albertus', ('Light', 'Roman', 'Italic')),
    ('Antique Olive', ('Roman', 'Italic', 'Bold', 'Compact')),
    ('Apple Chancery', ()),
    ('Arial', ('Regular', 'Italic', 'Bold', 'Bold Italic')),
    ('Bodoni', ('Roman', 'Italic', 'Bold', 'Bold Italic', 'Poster', 'Poster Compressed')),
    ('Carta', ()),
    ('Chicago', ()),
    ('Clarendon', ('Light', 'Roman', 'Bold')),
    ('Cooper Black', ('Regular', 'Italic')),
    ('Copperplate Gothic', ('32BC', '33BC')),
    ('Coronet', ()),
    ('Eurostile', ('Medium', 'Bold', 'Extended No.2', 'Bold Extended No.2')),
    ('Geneva', ()),
    ('Gill Sans', ('Light', 'Light Italic', 'Book', 'Book Italic', 'Bold', 'Bold Italic', 'Extra Bold', 'Condensed', 'Condensed Bold')),
    ('Goudy', ('Oldstyle', 'Oldstyle Italic', 'Bold', 'Bold Italic', 'Extra Bold')),
    ('Helvetica', ('Narrow', 'Narrow Oblique', 'Narrow Bold', 'Narrow Bold Oblique')),
    ('Hoefler Text', ('Roman', 'Italic', 'Black', 'Black Italic')),
    ('Hoefler Ornaments', ()),
    ('Joanna', ('Regular', 'Italic', 'Bold', 'Bold Italic')),
    ('Letter Gothic', ('Regular', 'Slanted', 'Bold', 'Bold Slanted')),
    ('ITC Lubalin Graph', ('Book', 'Oblique', 'Demi', 'Demi Oblique')),
    ('ITC Mona Lisa Recut', ()),
    ('Marigold', ()),
    ('Monaco', ()),
    ('New York', ()),
    ('Optima', ('Roman', 'Italic', 'Bold', 'Bold Italic')),
    ('Oxford', ()),
    ('Stempel Garamond', ('Roman', 'Italic', 'Bold', 'Bold Italic')),
    ('Tekton', ('Regular')),
    ('Times New Roman', ('Regular', 'Italic', 'Bold', 'Bold Italic')),
    ('Univers', ('45 Light', '45 Light Oblique', '55', '55 Oblique', '65 Bold', '65 Bold Oblique', '57 Condensed', '57 Condensed Oblique', '67 Condensed Bold', '67 Condensed Bold Oblique', '53 Extended', '53 Extended Oblique', '63 Extended Bold', '63 Extended Bold Oblique')),
    ('Wingdings', ()),
]

FONTS_PDF = [
    ('Courier', ('Regular', 'Oblique', 'Bold', 'Bold Oblique')),
    ('Helvetica', ('Regular', 'Oblique', 'Bold', 'Bold Oblique')),
    ('Symbol', ()),
    ('Times', ('Roman', 'Italic', 'Bold', 'Bold Italic')),
    ('ITC Zapf Dingbats', ()),
]

FONTS_MS_CORE = [
    ('Arial', ('Regular', 'Italic', 'Bold', 'Bold Italic')),
    ('Arial Black', ('Regular', )),
    ('Andale Mono', ('Regular', )),
    ('Courier New', ('Regular', 'Italic', 'Bold', 'Bold Italic')),
    ('Arial', ('Regular', 'Italic', 'Bold', 'Bold Italic')),
    ('Comic Sans MS', ('Regular', 'Bold')),
    ('Georgia', ('Regular', 'Italic', 'Bold', 'Bold Italic')),
    ('Impact', ('Regular', )),
    ('Times New Roman', ('Regular', 'Italic', 'Bold', 'Bold Italic')),
    ('Trebuchet MS', ('Regular', 'Italic', 'Bold', 'Bold Italic')),
    ('Verdana', ('Regular', 'Italic', 'Bold', 'Bold Italic')),
    ('Webdings', ()),
]


PS1 = 'ps1'
PS2 = 'ps2'
PS3 = 'ps3'
PDF = 'pdf'
MS_CORE = 'core'


def fromutf8(value: bytes) -> str:
    """Try to decode UTF-8 bytestring coming from fontconfig and return
    it in some string format, even if decoding fails."""
    try:
        return value.decode('utf8')
    except ValueError:
        return value.encode('string_escape').decode('ascii')


def maybebool(value: bytes) -> Union[bool, str]:
    """Interpret boolean value coming from fontconfig, and return a
    string value if decoding failed."""
    if value == b'True':
        return True
    if value == b'False':
        return False
    return maybecommonutf8(value)


def maybecommonutf8(value: bytes) -> str:
    """Try to decode a commonly seen UTF-8 bytestring (e.g. style, language)
    coming from fontconfig  and return an interned string. This should
    work even if decoding fails.

    On systems having thousands of fonts, this saves hundreds of MB of
    RAM for the language names. Interning other strings has diminishing
    returns, but does not hurt.
    """
    return sys.intern(fromutf8(value))


_langs_intern = {}


def _parse_language(langs: bytes) -> SequenceOf[str]:
    """Parse a pipe-separated language string coming from fontconfig.
    This ensures the languages are interned to save memory, and may
    optionally sort and intern the tuples of languages themselves,
    but that would not lead to signficant memory gains.
    """
    result = langs.decode('ascii').split('|')
    result = tuple(sorted(map(sys.intern, result)))
    if _langs_intern is not None:
        if result in _langs_intern:
            result = _langs_intern[result]
        else:
            _langs_intern[result] = result
    return result


class FontProperty(object):

    """A known property of Font objects coming from fontconfig,
    what factory to use to parse it, what label to use to display."""

    preferred_lang = 'en'
    localized = False
    multiple = False

    def __init__(self, propname: str, factory: Callable=fromutf8,
                       default: MaybeLazy[Any]=None, label: str=None):
        self.propname = propname
        self.properties_to_read = [propname]
        self.factory = factory
        self.default = default
        self.label = label or propname.capitalize()

    def parse_properties(self, font: 'Font', value: bytes):
        """Parse the property or properties from the given bytes value,
        and set it on font. By default, this simply calls the factory
        and sets the default the factory fails."""
        try:
            value = self.factory(value)
        except ValueError:
            value = self.default
        setattr(font, self.propname, value)

    def default_getters(self) -> IteratorOf[TupleOf[str, Callable]]:
        """Yield tuples of property names and a function that
        returns their default."""
        default = self.default
        if not callable(default):
            default = lambda: self.default
        yield self.propname, default

    def fill_default(self, font: 'Font'):
        """Fill the default for a given font."""
        default = self.default
        if not callable(default):
            default = lambda: self.default

        setattr(font, self.propname, default())

    def __repr__(self):
        return '%s(%r, <...>)' % (type(self).__name__,
                                  self.propname)


class FontPropertyWithLang(FontProperty):

    """A property with languages, performing more extended parsing than
    FontProperty."""

    localized = True

    def __init__(self, propname: str, multiple: bool=False, *args, **kwargs):
        super(FontPropertyWithLang, self).__init__(propname, *args, **kwargs)
        self.properties_to_read.append(propname + 'lang')
        self.multiple = multiple

    def parse_properties(self, font: 'Font', values: bytes, langs: bytes):
        """Parse the property from  a comma-separated bytes value,
        and its language counterpart comma-seperated value, and
        set it on the font."""
        values = map(self.factory, values.split(b','))
        langs = map(maybecommonutf8, langs.split(b','))
        value_by_lang = OrderedDict()
        for lang, value in zip(langs, values):
            if not self.multiple:
                value_by_lang[lang] = value
            else:
                value_by_lang.setdefault(lang, []).append(value)

        if self.preferred_lang in value_by_lang:
            value = value_by_lang[self.preferred_lang]
        elif value_by_lang:
            value = next(iter(value_by_lang.values()))
        else:
            value = None

        if self.multiple:
            setattr(font, self.propname, value[0])
            setattr(font, self.propname + '_by_lang',
                    OrderedDict((k, v[0]) for k, v in value_by_lang.items()))

            setattr(font, self.propname + '_alts', value)
            setattr(font, self.propname + '_alts_by_lang', value_by_lang)

        else:
            setattr(font, self.propname, value)
            setattr(font, self.propname + '_by_lang', value_by_lang)

    def default_getters(self) -> IteratorOf[TupleOf[str, Callable]]:
        default = self.default
        if not callable(default):
            default = lambda: self.default
        yield self.propname, default
        yield self.propname + '_by_lang', lambda: {'en': default()}
        if self.multiple:
            yield self.propname + '_alts', lambda: [default()]
            yield self.propname + '_alts_by_lang', lambda: {'en': [default()]}

    def fill_default(self, font: 'Font'):
        default = self.default
        if not callable(default):
            default = lambda: self.default

        setattr(font, self.propname, default())
        setattr(font, self.propname + '_by_lang', {'en': default()})
        if self.multiple:
            setattr(font, self.propname + '_alts', [default()])
            setattr(font, self.propname + '_alts_by_lang', {'en': [default()]})


properties = [
    FontPropertyWithLang('family', factory=maybecommonutf8,
                         multiple=True, default='',
                         label=N_('Family')),
    FontPropertyWithLang('style', factory=maybecommonutf8,
                         multiple=True, default='',
                         label=N_('Style')),
    FontPropertyWithLang('fullname', multiple=True, default='',
                         label=N_('Full name')),
    FontProperty('slant', factory=int, default=SLANT_NORMAL,
                 label=N_('Slant')),
    FontProperty('weight', factory=int, default=WEIGHT_NORMAL,
                 label=N_('Weight')),
    FontProperty('width', factory=int, default=WIDTH_NORMAL,
                 label=N_('Width')),
    FontProperty('foundry', factory=maybecommonutf8,
                 default='', label=N_('Foundry')),
    FontProperty('file', default='', label=N_('File path')),
    FontProperty('index', factory=int, default=0, label=N_('Font index')),
    FontProperty('outline', factory=maybebool, label=N_('Outline')),
    FontProperty('scalable', factory=maybebool, label=N_('Scalable')),
    FontProperty('lang', factory=_parse_language, default=('en', ),
                 label=N_('Languages')),
    FontProperty('fontversion', factory=int, default=0,
                 label=N_('Version number')),
    FontProperty('capability',
                 lambda v: [p.split(':', 1) for p in fromutf8(v).split()],
                 label=N_('Capabilities')),
    FontProperty('fontformat', default='', label=N_('Font format')),
    FontProperty('decorative', factory=maybebool, label=N_('Decorative')),
    FontProperty('postscriptname', default='',
                 label=N_('PostScript name')),
    # Are all of these deprecated and removed?
    ##FontProperty('hash', default=''),
    ##FontProperty('lcdfilter', factory=int, default=0),
    ##FontProperty('embeddedbitmap', factory=maybebool),
    ##FontProperty('verticallayout', factory=maybebool),
    ##FontProperty('globaladvance', factory=maybebool),
    ##FontProperty('hinting', factory=maybebool),
    ##FontProperty('autohint', factory=maybebool),
    ##FontProperty('hintstyle', factory=int, default=0),
    ##FontProperty('antialias', factory=maybebool),
    ##FontProperty('scale', factory=float),
    ##FontProperty('dpi', factory=float),
    ##FontProperty('rgba', factory=int),
    FontProperty('spacing', factory=int, label=N_('Spacing')),
    FontProperty('size', factory=float, label=N_('Size')),
    FontProperty('pixelsize', factory=float, label=N_('Pixel size')),
    FontProperty('charset', factory=rangemath.OrdinalRange.from_fontconfig),
]


property_default_getters = dict(chain.from_iterable(
    prop.default_getters() for prop in properties))


property_by_name = {prop.propname: prop for prop in properties}


def fontclass(cls):
    """Decorate font classes with this. Adds annotations."""

    if '__annotations__' not in vars(cls):
        cls.__annotations__ = {}

    annotations = cls.__annotations__

    for prop in properties:
        if isinstance(prop.factory, type):
            propcls = prop.factory
        else:
            try:
                propcls = prop.factory.__annotations__['return']
            except (KeyError, AttributeError):
                propcls = Any

        annotations[prop.propname] = propcls

    return cls


def autofill_font_info(font: 'Font', remote_server: str=None):
    """Fill additional information about the font after parsing.
    This needs to be called. If you provide a remote server, it
    will be set on the font."""

    if not font.fullname:
        # FIXME: Dirty?
        font.fullname = font.family + ' ' + font.style

    compression = None

    if font.file:
        font.file = os.path.normpath(font.file)

        base, ext = os.path.splitext(font.file)
        ext = ext.lstrip('.')
        while ext in compression_extensions:
            compression = ext
            base, ext = os.path.splitext(base)
            ext = ext.lstrip('.')

        if not font.ext:
            font.ext = ext.lower()
        if not font.comp:
            font.comp = compression

    if font.ext and not font.fontformat and font.ext in file_extensions:
        filetype = file_extensions[font.ext]
        if not filetype.multiformat and filetype.fontformat is not None:
            font.fontformat = filetype.fontformat

    if remote_server:
        font.file = urllib.parse.urljoin('sftp://' + remote_server,
                                         urllib.parse.quote(font.file))
        font.remote = True
        font.personal = False

    else:
        if font.file and font.file.startswith(proginfo.HOME_DIR):
            font.personal = True

    if font.file_alts is None:
        if font.file:
            font.file_alts = [FontFile(font.file, font.index)]
        else:
            font.file_alts = []
    if font.alternatives is None:
        font.alternatives = ()

    font.file_format_info = file_extensions.get(font.ext, FILE_UNKNOWN_FORMAT)
    font.font_format_info = font_formats.get(font.fontformat,
                                             FONT_UNKNOWN_FORMAT)

    if (font.sfnt or
        font.font_format_info in [FONT_TRUETYPE, FONT_CFF] or
        font.file_format_info in [FILE_TTF, FILE_CFF]):
            font.sfnt = True

    font.icon = None
    font.file_icon = font.file_format_info.icon
    font.font_icon = font.file_format_info.icon

    if font.font_format_info is not FONT_UNKNOWN_FORMAT:
        font.icon = font.font_format_info.category_icon
    elif font.file_format_info is not FILE_UNKNOWN_FORMAT:
        font.icon = font.file_format_info.icon
    elif not font.scalable or not font.outline:
        font.icon = 'bitmap'
    else:
        font.icon = 'unknown'


@fontclass
class Font(object):

    """A font - either a family or style."""

    is_family = False
    is_style = True
    genericfamily = ''
    genericfamily_source = SOURCE_UNKNOWN

    substituting = None
    substitutingfamily = None
    substitutingstyle = None

    cachekey_value = None

    ext = ''
    comp = None
    file_alts = None
    alternatives = None

    source = None
    finder = None

    personal = False
    remote = False

    monospace = None
    sfnt = False

    color = False

    #panoseclass = None
    #ibmclass = None
    #embedding = None

    file_format_info = FILE_UNKNOWN_FORMAT
    font_format_info = FONT_UNKNOWN_FORMAT

    #def get_file_format(self):
    #    return file_extensions.get(self.ext, FILE_UNKNOWN_FORMAT)

    #def get_font_format(self):
    #    return font_formats.get(self.fontformat, FONT_UNKNOWN_FORMAT)

    @property
    def styles(self) -> 'SequenceOf[Font]':
        """If this is a family, all styles within the family. If it is
        a style, a single-element list with the style."""
        return [self]

    def cachekey(self) -> str:
        """Return the key used to locate the cache for this font."""
        result = self.cachekey_value
        if result is None:
            self.cachekey_value = result = '%s|%s|%s' % (
                self.foundry, self.fullname, self.fontversion)
        return result

    def set_cachekey(self, value: str):
        """Set the cachekey used to locate the cache for this font."""
        self.cachekey_value = value

    def get_charset(self) -> Optional[rangemath.RangeBase]:
        """Get the character codes supported by the font. If not
        parsed by fontconfig, that may perform slow parsing using
        fontTools. It may return None if unavailable."""
        if self.charset is None:
            if self.finder is None:
                return None
            self.finder.fill_charset(self)
        return self.charset

    def extended(self) -> 'FontExtended':
        """Return extended information about the font. That may
        perform slow parsing of the font file using fontTools.

        The value is cached until you keep a reference to it, so
        if you want to avoid multiple parsings, keep it. But it is
        deleted to preserve memory, as the extended memory is big.
        """
        extended = getattr(self, '_extended', lambda: None)()
        if extended is not None:
            return extended

        extended = FontExtended()

        if ttLib is None or not self.file or not os.path.exists(self.file):
            self._extended = weakref.ref(extended)
            return extended

        try:
            fontdata = ttLib.TTFont(self.file, fontNumber=self.index)

        # ttLib can throw ImportError
        except (ttLib.TTLibError, EnvironmentError, ImportError):
            self._extended = weakref.ref(extended)
            return extended

        extended.ttfont = fontdata

        try:
            namelist = fontdata['name']
        except KeyError:
            namelist = None

        if namelist:
            extended.description = \
                namelist.getDebugName(opentype.DESCRIPTION_NAME_ID)
            extended.copyright = \
                namelist.getDebugName(opentype.COPYRIGHT_NAME_ID)
            extended.trademark = \
                namelist.getDebugName(opentype.TRADEMARK_NAME_ID)
            extended.license = \
                namelist.getDebugName(opentype.LICENSE_NAME_ID)
            extended.license_url = \
                namelist.getDebugName(opentype.LICENSE_URL_NAME_ID)
            extended.designer = \
                namelist.getDebugName(opentype.DESIGNER_NAME_ID)
            extended.manufacturer = \
                namelist.getDebugName(opentype.MANUFACTURER_NAME_ID)
            extended.vendor_url = \
                namelist.getDebugName(opentype.VENDOR_URL_NAME_ID)
            extended.designer_url = \
                namelist.getDebugName(opentype.COPYRIGHT_NAME_ID)
            extended.sample_text = \
                namelist.getDebugName(opentype.SAMPLE_TEXT_ID)
            extended.version = \
                namelist.getDebugName(opentype.VERSION_NAME_ID)

        try:
            #cmap = fontdata['cmap']
            cmap = fontdata.getBestCmap()
        except KeyError:
            cmap = None

        if cmap is not None:
            #extended.cmap = cmap.getBestCmap()
            extended.cmap = cmap

        self._extended = weakref.ref(extended)
        return extended

    def translate(self, attr: str, locale: str) -> str:
        """Return the translated version of a given attribute in a given
        locale. For example, font.translate('family', 'de_DE') is
        the font.family translated in the de_DE locale."""
        if not locale:
            return getattr(self, attr)
        by_lang = getattr(self, attr + '_by_lang')
        locale = locale.lower().replace('_', '-')
        if locale in by_lang:
            return by_lang[locale]
        locale = locale.partition('-')[0]
        if locale in by_lang:
            return by_lang[locale]
        return getattr(self, attr)

    def search_families(self) -> SetOf[str]:
        """Get all the family names for this font item, including localisations,
        allowing you to look for it."""

        result = OrderedSet([self.family])
        result.update(self.family_by_lang.values())
        return result

    def search_familystyle_tuples(self) -> SetOf[TupleOf[str, str]]:
        """Get all the names for this font item as tuples family, style,
        including localisations, allowing you to look for it."""
        result = OrderedSet()
        result.add((self.family, self.style))

        langs = set(chain(self.style_by_lang, self.family_by_lang))

        for lang in langs:
            result.add((self.family_by_lang.get(lang, self.family),
                        self.style_by_lang.get(lang, self.style)))

        return result

    def search_fullnames(self) -> SetOf[str]:
        """Get all the full names for this font item, including localisations,
        allowing you to look for it. This includes concatenations of the
        family and style."""

        result = OrderedSet()

        result.add(self.fullname)
        result.add(self.family + ' ' + self.style)

        langs = set(chain(self.style_by_lang, self.fullname_by_lang,
                          self.family_by_lang))
        for lang in langs:
            result.add(self.fullname_by_lang.get(lang, self.fullname))
            result.add(self.family_by_lang.get(lang, self.family) + ' ' +
                       self.style_by_lang.get(lang, self.style))

        return result

    def lang_unknown(self) -> bool:
        """Return True if the languages by the font are unknown, and
        the lang attribute can't be trusted. This means fontconfig was not
        used to get the operating system fonts, if you're not on GNU/Linux.
        """
        return (self.source == 'qt' and self.lang == ['en'])

    def files(self, all_styles: bool=True, find_metrics: bool=True,
                    details: bool=False,
                    stat: bool=True) -> 'IterableOf[FontFileType]':
        """Yield the FontFile objects describing the files
        for this Font object, depending on what this object is.

        If no file is known, this will return an empty iterator.

        If the font has only one known file (or is a member of a font
        collection), or if this Font object refers to a specific font file,
        then this will return an iterator with one element.

        If multiple files provide this font, the result will contain multiple
        elements. This includes files providing multiple bitmap sizes, or
        redundant files providing the same font. It is not guaranteed to
        include all files, or PostScript font metrics.

        If find_metrics is True (default), this function tries to find
        the font metrics (for Type 1 fonts).

        The all_styles is ignored. It's used in FontFamily.files(), and
        accepted for compatibility.

        Passing details=True includes more details about files, which
        by default also stats all the files unless stat=False is passed.
        """

        if self.file_alts:
            result = self.file_alts

        elif self.file:
            result = (FontFile(self.file, self.index), )

        else:
            result = ()

        for fi in result:
            if details:
                stat_result = None
                if stat:
                    try:
                        stat_result = os.stat(fi.file)
                    except EnvironmentError:
                        pass

                yield FontFileDetails(fi.file, fi.index,
                                      FontFile.purpose, False, self,
                                      stat_result)
            else:
                yield fi

            # Metrics?
            if (find_metrics and fi.index == 0 and
                (self.font_format_info == FONT_TYPE1 or
                 self.ext in ['pfa', 'pfb', 't1'])):

                filename, ext = os.path.splitext(fi.file)
                for filename in glob.iglob(filename + '.[aA][fF][mM]'):
                    if details:
                        stat_result = None
                        if stat:
                            try:
                                stat_result = os.stat(filename)
                            except EnvironmentError:
                                pass

                        yield FontFileDetails(filename, 0,
                                              FontMetrics.purpose, True, self,
                                              stat_result)
                    else:
                        yield FontMetrics(filename, 0)

    def __getattr__(self, attr):
        try:
            default = property_default_getters[attr]
        except KeyError:
            raise AttributeError('%r object has no attribute %r'
                                    % (type(self).__name__, attr))
        default = default()
        setattr(self, attr, default)
        return default

    def __repr__(self):
        return "<%s %r font at 0x%x>" % (type(self).__name__,
                                         self.fullname,
                                         id(self))


class FontExtended(object):

    """Extended information about the font."""

    description = None

    copyright = None
    trademark = None
    license = None
    license_url = None

    designer = None
    manufacturer = None

    vendor_url = None
    designer_url = None

    sample_text = None

    cmap = None

    ttfont = None

    version = None


MERGE_NOTHING = None
MERGE_BY_STYLE = attrgetter('family', 'style')
MERGE_BY_FULLNAME = attrgetter('fullname')

class FontFinder(object):

    """Discover all the fonts on the system, though fontconfig. Subclasses
    may discover fonts from other facilities (e.g. Qt), or enrich the
    font information from these facilities.

    You can provide a cache for the metadata, and an executor (e.g. a
    remote SSH executor for fonts on a remote server) to use to
    call fontconfig's fc-match and fc-list.

    If a remote_server is provided, the ssh executor is initialized
    automatically. This is the preferred form.
    """

    def __init__(self, automerge_fonts_by: Callable=MERGE_BY_FULLNAME,
                       remote_server: str=None,
                       executor: external.Executor=None,
                       metadata_cache: 'typeatlas.datastore.MetadataCache'=None):

        if executor is None:
            executor = external.Executor()

        if remote_server is not None:
            ssh = external.command_providing(executor, 'ssh-executor', None)
            executor = ssh.get_ssh_executor(remote_server)

        self.fc_list = external.command_providing(executor, 'fc-list', None)
        self.fc_match = external.command_providing(executor, 'fc-match', None)

        randchars = ''.join([random.choice(string.ascii_letters)
                            for x in range(6)]).encode('ascii')

        self.sep = b'\n\n6Eij'+randchars+b'TyS\n\n'

        propreq = set()
        for prop in properties:
            propreq.update(prop.properties_to_read)
        self.automerge_fonts_by = automerge_fonts_by

        self.propreq = propreq
        self.remote_server = remote_server
        self.metadata_cache = metadata_cache

    def _check_fontconfig_supported(self, ignore_disablement: bool=False):
        """Raise NotSupportedError if we don't support fontconfig.

        Or if it is disabled for debugging purposes, and ignore_disablement is
        not True.
        """

        if (DISABLE_FC_LIST and not ignore_disablement and
            self.remote_server is None):
                raise NotSupportedError('fc-list disabled')

        if self.fc_list is None or not self.fc_list.available():
            raise NotSupportedError('external command not available')

    def _is_fontconfig_supported(self, ignore_disablement: bool=False) -> bool:
        """Return True if we don't support fontconfig.

        Or if it is disabled for debugging purposes, and ignore_disablement is
        not True.
        """
        if (DISABLE_FC_LIST and not ignore_disablement and
            self.remote_server is None):
                return False
        return self.fc_list is not None and self.fc_list.available()

    @classmethod
    def supported(cls) -> bool:
        """Return True if se can discover fonts."""
        return shutil.which('fc-list') is not None

    @classmethod
    def fcmatch_supported(cls) -> bool:
        """Return True if se can match fonts by e.g. name."""
        return shutil.which('fc-match') is not None

    @classmethod
    def remote_supported(cls) -> bool:
        """Return True if we can lookup remote fonts."""
        return shutil.which('ssh') is not None

    def fontprogress(self, num: int, total: int=None, *, message: str=None):
        """Replace this with a callable of a compatible signature to support
        progress bar for slow processes. The first two arguments are only
        passed positionally, so the names do not need to match."""

    def fontprogressdone(self):
        """Replace this with a callable to call when the long-running
        operation is over."""

    def fontconfig_version(self) -> str:
        """Return the version of fontconfig."""

        if self.fc_list is None or not self.fc_list.available():
            return None

        callbacks = external.CallCallbacks.single(
            lambda exitcode, stdout: stdout.decode('utf8').split(None)[-1],
            line_mode=False, chunked=False, merge_outputs=True,
            require_blocking=True)

        return self.fc_list.custom(['--version'], callbacks=callbacks)

    def merge_fonts(self, fonts: IterableOf[Font],
                          key: Callable=MERGE_BY_FULLNAME) -> IteratorOf[Font]:
        """Merge fonts by given criteria. All fonts matching the criteria
        are considered identical, and moved as alternatives to one another.
        The files are added as file alternatives.

        This is not for style merging, but the same font style installed
        multiple times."""
        if key is MERGE_NOTHING:
            for font in fonts:
                yield font
            return

        for groupkey, alternatives in groupby(sorted(fonts, key=key), key):
            alternatives = list(alternatives)
            font = copy.copy(alternatives[0])
            font.alternatives = alternatives
            font.file_alts = [FontFile(f.file, f.index) for f in alternatives]
            yield font

    def _parse_output(self, stdout: bytes) -> IteratorOf[Font]:
        """Parse the output from fc-list or fc-match as called by this class.
        Expects it to be in a special format as defined by a custom separator
        and the order of the registered fontconfig properties."""
        global _langs_intern
        _langs_intern = {}

        parts = iter(stdout.split(self.sep))
        fontnum = count()

        while True:

            if FONT_LIMIT is not None and next(fontnum) >= FONT_LIMIT:
                break

            propvalues = {}
            try:
                for propname in self.propreq:
                    propvalues[propname] = next(parts)
            except StopIteration:
                break

            font = Font()

            font.source = 'fontconfig'
            font.finder = self

            for prop in properties:
                propargs = [propvalues.get(propname)
                            for propname in prop.properties_to_read]
                prop.parse_properties(font, *propargs)

            autofill_font_info(font, remote_server=self.remote_server)

            yield font

        _langs_intern = None

    def _fc_req_format(self) -> bytes:
        """Return the format used for formatting fonts required by
        self._parse_output."""
        return self.sep.join(('%%{%s}' % (s, )).encode('ascii')
                             for s in self.propreq) + self.sep

    def fonts(self, *args) -> IteratorOf[Font]:
        """Yield all fonts detected by this finder, e.g. the ones
        provided by fc-list."""
        self._check_fontconfig_supported()

        callbacks = external.CallCallbacks.single(
            lambda exitcode, stdout:
                self.merge_fonts(self._parse_output(stdout),
                                 self.automerge_fonts_by),
            line_mode=False, chunked=False,
            require_blocking=True)

        return self.fc_list.custom(['-f', self._fc_req_format(), '--'],
                                   callbacks=callbacks)

    def _parse_fontdirs(self, stdout: bytes) -> SetOf[str]:
        """Parse the fontdirs from fc-list's output"""
        filepaths = stdout.split(self.sep)
        if filepaths and not filepaths[-1]:
            del filepaths[-1]
        return OrderedSet(fromutf8(os.path.dirname(fp)) for fp in filepaths)

    def fontdirs(self) -> SetOf[str]:
        """Get the font dirs on the system, from fontconfig or
        whatever font system your operating system is using if the
        Qt finder is used."""

        # FIXME: This is a really ugly way to get the font dirs.
        # We *can* parse the XMLs

        self._check_fontconfig_supported(ignore_disablement=True)

        callbacks = external.CallCallbacks.single(
            lambda exitcode, stdout: self._parse_fontdirs(stdout),
            line_mode=False, chunked=False,
            require_blocking=True)

        return self.fc_list.custom(['-f', b'%{file}' + self.sep],
                                   callbacks=callbacks)

    def substitute(self, family: str, style: str) -> Font:
        """Find a substitution for a given family and style."""
        fonts = list(self.fcmatch(':family=' + family + ':style=' + style))
        font = fonts[0]
        if font.family.casefold() != family.casefold():
            font.substitutingfamily = family
        if font.style.casefold() != style.casefold():
            font.substitutingstyle = style

        if font.substitutingfamily or font.substitutingstyle:
            font.substituting = (family + ' ' + style)

        return font

    def standard_fonts(self, which: str=None) -> IteratorOf[Font]:
        """Get the standard fonts for e.g. PS1, PS2, PDF, etc."""
        if which == PS1:
            fonts = FONTS_POSTSCRIPT1
        elif which == PS2:
            fonts = FONTS_POSTSCRIPT2
        ## Merge PS1, PS2, and PS3
        #elif which == PS3:
        #    fonts = FONTS_POSTSCRIPT3
        elif which == PDF:
            fonts = FONTS_PDF
        elif which == MS_CORE:
            fonts = FONTS_MS_CORE
        else:
            fonts = []
            seen = set()
            for collection in [FONTS_POSTSCRIPT1, FONTS_POSTSCRIPT2,
                               FONTS_POSTSCRIPT3]:
                for font in collection:
                    if font[0] in seen:
                        continue
                    seen.add(font[0])
                    fonts.append(font)

        for family, styles in fonts:
            for style in styles or ['Regular']:
                yield self.substitute(family, style)

    def standard_families(self, which: str=None) -> 'IteratorOf[FontFamily]':
        """Get and group by families all the standard fonts
        for e.g. PS1, PS2, PDF, etc."""
        return get_families(self.standard_fonts(which),
                            key=lambda font:
                                   (font.substitutingfamily or font.family))

    def fcmatch(self, *args, many=False, all=False):

        self._check_fontconfig_supported()

        if all:
            cmdline = ['-a', '-f', self._fc_req_format(), '--']
        elif many:
            cmdline = ['-s', '-f', self._fc_req_format(), '--']
        else:
            cmdline = ['-f', self._fc_req_format(), '--']
        cmdline.extend(args)

        callbacks = external.CallCallbacks.single(
            lambda exitcode, stdout:
                self.merge_fonts(self._parse_output(stdout),
                                 self.automerge_fonts_by),
            line_mode=False, chunked=False,
            require_blocking=True)

        return self.fc_match.custom(cmdline, callbacks=callbacks)

    def families(self, *args, **kwargs) -> 'IteratorOf[FontFamily]':
        """Get the fonts grouped by family, otherwise do the same
        as fonts()."""
        return get_families(self.fonts(*args, **kwargs))

    def fill_generic_families(self, elements: 'IterableOf[Union[Font, FontFamily]]'):
        """Fill the generic families for the provided fonts and families.

        This uses the cache, and attempts to make multiple slow queries
        to fontconfig to guess. This should be used after PANOSE has
        been exhausted as source by fill_detailed_info.
        """
        cache = self.metadata_cache

        fonts = []
        for element in elements:
            if element.is_style:
                fonts.append(element)
            else:
                fonts.extend(element.styles)

        categorized_using_order = set()
        uncategorized = 0

        for font in fonts:
            if font.genericfamily:
                continue

            genfamily = source = None

            if cache is not None:
                genfamily = cache.get_field(font, 'genfamily', str)
                source = cache.get_field(font, 'genfamily_source', str)

            if genfamily and source != 'fc-order':
                font.genericfamily = genfamily
                font.genericfamily_source = SOURCE_NAME_MATCH
                continue

            name_lower = font.family.lower()

            if 'sans' in name_lower:
                font.genericfamily = N_('sans-serif')
            elif 'serif' in name_lower:
                font.genericfamily = N_('serif')
            elif 'roman' in name_lower:
                font.genericfamily = N_('serif')
            elif 'gothic' in name_lower or 'grotesque' in name_lower:
                font.genericfamily = N_('sans-serif')
            elif ('ming' in name_lower or
                  '明' in name_lower or '宋' in name_lower):
                font.genericfamily = N_('serif')
            elif 'song' in name_lower and (
                    'zh-hk' in font.lang or 'zh-tw' in font.lang or
                    'zh-cn' in font.lang):
                font.genericfamily = N_('serif')
            elif 'mincho' in name_lower or '明朝' in name_lower:
                font.genericfamily = N_('serif')
            elif 'myeong' in name_lower or '명' in name_lower:
                font.genericfamily = N_('serif')

            elif genfamily is not None:
                font.genericfamily = genfamily
                font.genericfamily_source = SOURCE_FONTLIST_ORDER
                categorized_using_order.add(font.fullname)
                continue

            else:
                uncategorized += 1

            if cache is not None and font.genericfamily:
                cache.set_field(font, 'genfamily', font.genericfamily)
                cache.set_field(font, 'genfamily_source', 'name')
                font.genericfamily_source = SOURCE_NAME_MATCH

        if not uncategorized or not self._is_fontconfig_supported():
            return

        # The following strategy to determine generic family is batshit insane
        genfamily_lists = {}
        for genfamily in [N_('sans-serif'), N_('serif'),
                          N_('cursive'), N_('fantasy')]:
            try:
                genfamily_lists[genfamily] = list(enumerate(
                                            self.fcmatch(genfamily, all=True)))
            except NotSupportedError:
                return

        for genfamilies in [[N_('sans-serif'), N_('serif'),
                             N_('cursive'), N_('fantasy')]]:

            scores = defaultdict(dict)

            for genfamily in genfamilies:
                for score, font in genfamily_lists[genfamily]:
                    if genfamily in scores[font.fullname]:
                        continue
                    scores[font.fullname][genfamily] = score

            for font in fonts:
                if (font.genericfamily and
                    font.fullname not in categorized_using_order):
                        continue

                font_scores = scores.get(font.fullname)
                if font_scores is None:
                    if cache is not None:
                        cache.set_field(font, 'genfamily', '')
                        cache.set_field(font, 'genfamily_source', 'fc-order')
                    continue

                font_genfamily = min(font_scores, key=font_scores.get)
                font_score = font_scores[font_genfamily]

                # TODO: This is most definitely the best option, how do we
                # determine if it is the right one?
                if sum(1 for score in font_scores.values()
                         if score == font_score) == 1:
                    font.genericfamily = font_genfamily
                    font.genericfamily_source = SOURCE_FONTLIST_ORDER
                else:
                    font.genericfamily = ''

                if cache is not None:
                    cache.set_field(font, 'genfamily', font.genericfamily)
                    cache.set_field(font, 'genfamily_source', 'fc-order')

    def _check_ttlib_file_reliable(self, font: Font, fontdata: 'ttLib.TTFont'):
        """Make sure the font file can be used with fontTools.ttLib,
        i.e. that it is correct and can we can use it.

        If not, throw a NotSupportedError.
        """
        errormsg = self._is_ttlib_file_unreliable(font, fontdata)
        if errormsg:
            raise NotSupportedError("{}: {!r}".format(errormsg, font))

    def _is_ttlib_file_unreliable(self, font: Font,
                                  fontdata: 'ttLib.TTFont') -> Optional[str]:
        """Make sure the font file can be used with fontTools.ttLib,
        i.e. that it is correct and can we can use it.

        If not, return an error message.
        """

        # If we got this from fontconfig, and not Qt, all is good.
        if self._is_fontconfig_supported():
            return None

        # Indexes gotten from Qt are wrong, so only use them
        # for fonts files with a single index in them, or
        # when ttLib.TTFont concurs.

        # If index is non-zero, this is likely correct.
        if font.index != 0:
            return None

        # Only one font in file, we can also trust it.
        if getattr(fontdata.reader, 'numFonts', 1) == 1:
            return None

        if 'name' not in fontdata:
            return "don't know font's index"

        names = _font_names(fontdata['name'], grouped=False)
        if all(family != font.family
               for family in names.family):
            return "font index wrong"
        return None

    def fill_detailed_info(self, font: Font):

        """Fill detailed information about the font parsing the PANOSE
        information or extracting it from cache. This is to be called
        manually at the moment."""

        if hasattr(font, 'panoseclass'):
            return

        if self.remote_server:
            font.ibmclass = opentype.NO_IBM_CLASS_DATA
            font.panoseclass = opentype.NO_PANOSE_DATA
            font.embedding = opentype.NO_EMBEDDING_INFO
            return

        if ttLib is None:
            raise NotSupportedError("fonttools not installed")

        # If we don't get fontconfig, we don't want to use the following
        # code, as we won't have enough data to fill.
        #self._check_fontconfig_supported()

        cache = self.metadata_cache

        cached_classes = cached_charset = False
        color_format = charset = None

        if cache is not None:
            cached_classes = cache.fill_classes(font)
            cached_charset = cache.fill_charset(font)
            color_format = cache.get_field(font, 'color_format')
            #charset = cache.get_field(font, 'charset')

        fontdata = os2 = None

        if cached_classes and color_format:
            pass

        elif font.file and os.path.exists(font.file):
            try:
                fontdata = ttLib.TTFont(font.file, fontNumber=font.index)

            except (ttLib.TTLibError, EnvironmentError, ImportError):
                pass

            else:
                self._check_ttlib_file_reliable(font, fontdata)
                try:
                    os2 = fontdata.getTableData('OS/2')
                except KeyError:
                    pass

        # In case we're on very old fontconfig, or not on fontconfig
        if font.charset is None and LOAD_CHARSET_EARLY and fontdata:

            try:
                #cmap = fontdata['cmap']
                cmap = fontdata.getBestCmap()
            except KeyError:
                cmap = None
            #else:
            #    cmap = cmap.getBestCmap()

            if cmap is not None:
                font.charset = rangemath.OrdinalRange.from_iterable(cmap)
                if cache is not None:
                    cache.set_field(font, 'charset',
                                    font.charset.to_fontconfig())

        if fontdata and not color_format:
            # Check if a special font format, particularly color font?
            #if 'SVG ' in fontdata.reader.tables: ...
            if 'SVG ' in fontdata:
                color_format = 'svg'

            elif ('COLR' in fontdata and 'CPAL' in fontdata):
                color_format = 'layered'

            elif (('CBDT' in fontdata and 'CBLC' in fontdata) or
                  'sbix' in fontdata):
                color_format = 'bitmap'

            else:
                color_format = 'none'

        if color_format:

            # Check if a special font format, particularly color font?
            if color_format == 'svg':
                font.font_format_info = FONT_SVG
                font.icon = font.font_format_info.category_icon
                font.color = True

            elif color_format == 'layered':
                if font.font_format_info in [FONT_TRUETYPE, FONT_CFF]:
                    font.icon += '-color'
                font.color = True

            elif color_format == 'bitmap':
                font.icon = 'bitmap-color'
                font.color = True

            if cache is not None and fontdata:
                cache.set_field(font, 'color_format', color_format)

        if not cached_classes:
            if not os2:
                font.ibmclass = opentype.NO_IBM_CLASS_DATA
                font.panoseclass = opentype.NO_PANOSE_DATA
                font.embedding = opentype.NO_EMBEDDING_INFO
                return

            font.ibmclass = opentype.extract_ibm_class(os2)
            font.panoseclass = opentype.extract_panose_class(os2)
            font.embedding = opentype.extract_embedding_info(os2)

        if not font.genericfamily:
            font.genericfamily = font.panoseclass.genericfamily
            font.genericfamily_source = SOURCE_PANOSE
        if not font.genericfamily:
            font.genericfamily = font.ibmclass.genericfamily
            font.genericfamily_source = SOURCE_IBM

        if font.monospace is None:
            # PANOSE lies
            font.monospace = font.panoseclass.monospace()

        if cache is not None:
            if not cached_classes:
                cache.cache_classes(font)

    def fill_charset(self, font: Font):

        """Fill charset information about the font by parsing the file with
        fonttools or from cache if it is available, in case fontconfig has
        not provided it.

        This is very slow, so should be called only if get_charset() is
        called on a font explicitly."""

        if font.charset is not None:
            return True

        if self.metadata_cache is not None:
            if self.metadata_cache.fill_charset(font):
                return True

        if ttLib is None or not font.file or not os.path.exists(font.file):
            return False

        try:
            fontdata = ttLib.TTFont(font.file, fontNumber=font.index)
        # ttLib can throw ImportError
        except (ttLib.TTLibError, EnvironmentError, ImportError):
            return False

        if self._is_ttlib_file_unreliable(font, fontdata):
            debugmsg("fontTools unreliable font {!r}".format(font))
            return False

        try:
            #cmap = fontdata['cmap']
            cmap = fontdata.getBestCmap()
        except KeyError:
            cmap = None
        #else:
        #    cmap = cmap.getBestCmap()

        if cmap is not None:
            font.charset = rangemath.OrdinalRange.from_iterable(cmap)
            if self.metadata_cache is not None:
                self.metadata_cache.cache_charset(font)
            return True

        return False

    #def match_families(self, *args):
    #    return get_families(self.match(*args, **kwargs))


class StyleSelector(object):

    """A selector which chooses a font with a specific weight (e.g.
    WEIGHT_BOLD), slant (e.g. SLANT_ITALIC), and width (e.g.
    WIDTH_CONDENSED).

    The .key() property gives you a callable to use as a sort key,
    and select() selects the best style for you using min() with that
    key for a given family.
    """

    def __init__(self, weight=WEIGHT_NORMAL, slant=SLANT_NORMAL,
                       width=WIDTH_NORMAL):
        self.weight = weight
        self.slant = slant
        self.width = width

    def key(self, font: Font) -> object:
        """Get a key to sort the preferred font style from the
        font family. The preferred will be first. Use the method
        itself as the sort key"""
        return (abs(self.width - font.width) +
                abs(self.weight - font.weight) +
                abs(self.slant - font.slant))

    def select(self, family: 'FontFamily') -> Font:
        """Select the preferred font style from the font family."""
        return min(family.styles, key=self.key)



main_selector = StyleSelector()
main_key = main_selector.key
get_main_style = main_selector.select


def style_key(font: Font):
    """A key that sorts the styles non-randomly for display. Light to bold,
    unslanted to italic, condensed to expanded."""
    return font.weight, font.slant, font.width


@fontclass
class FontFamily(object):

    """Object like Font, except for families. Has many of the same attributes,
    forwarding most of them to the main style, stored in the main attribute."""

    is_family = True
    is_style = False

    def __init__(self, fonts: IterableOf[Font]):
        self.styles = sorted(fonts, key=style_key)
    
        main = min(self.styles, key=main_key)

        self.family = main.family
        self.family_by_lang = main.family_by_lang
        self.foundry = main.foundry

        lang = set()
        for style in self.styles:
            lang.update(style.lang)

        self.lang = list(lang)
        self.main = main

        # Loose
        self.outline = main.outline
        self.scalable = main.scalable
        self.decorative = main.decorative
        #self.embeddedbitmap = main.embeddedbitmap
        self.ext = main.ext
        self.comp = main.comp

    def files(self, all_styles: bool=True, find_metrics: bool=True,
              details: bool=False,
              stat: bool=True) -> 'IteratorOf[FontFileType]':
        """Read documentation for Font.files().

        If all_styles is True (default), yield the files for all styles.
        Otherwise, yield the files for the main style.
        """

        styles = self.styles if all_styles else [self.main]
        for style in styles:
            for fi in style.files(find_metrics=find_metrics,
                                  details=details, stat=stat):
                yield fi

    def __getattr__(self, attr):
        return getattr(self.main, attr)

    def __repr__(self):
        return "<%s %r family at 0x%x>" % (type(self).__name__,
                                           self.family,
                                           id(self))


FontLike = Union[Font, FontFamily]


def get_families(fonts: IterableOf[Font],
                 key: Callable=attrgetter('family')) -> IteratorOf[FontFamily]:
    """Group fonts by family and yield them."""
    for familyname, styles in groupby(sorted(fonts, key=key), key):
        yield FontFamily(styles)


def font_name_matches(font: Font,
                      nametable: 'ttLib.tables._n_a_m_e.table__n_a_m_e'):
    """Return True if the name of the font matches the name in the name font
    table.."""
    stylematch = False
    familymatch = False
    for name in nametable.names:
        if name.nameID == opentype.FULL_NAME_ID:
            if name.toUnicode('replace') in font.fullname_alts:
                return True
        if name.nameID == opentype.FAMILY_NAME_ID:
            if name.toUnicode('replace') in font.family_alts:
                if stylematch:
                    return True
                familymatch = True
        if name.nameID == opentype.STYLE_NAME_ID:
            if name.toUnicode('replace') in font.style_alts:
                if familymatch:
                    return True
                stylematch = True
    return False


FontNames = namedtuple('FontNames', 'family style fullname')

_font_names_map = {
    opentype.FULL_NAME_ID: 'fullname',
    opentype.FAMILY_NAME_ID: 'family',
    opentype.STYLE_NAME_ID: 'style',

    opentype.FULL_NAME_ID: 'fullname',
    opentype.TYPOGRAPHIC_FAMILY_NAME_ID: 'family',
    opentype.TYPOGRAPHIC_STYLE_NAME_ID: 'style',
}
_typographic_names = {opentype.TYPOGRAPHIC_FAMILY_NAME_ID,
                      opentype.TYPOGRAPHIC_STYLE_NAME_ID}

def _font_names(nametable: 'ttLib.tables._n_a_m_e.table__n_a_m_e',
                grouped: bool=False) -> FontNames:
    """Return the known font names as ordered sets for for family, style,
    fullname"""
    names = {name: OrderedSet() for name in _font_names_map.values()}

    stylenames = defaultdict(OrderedSet)

    for name in nametable.names:
        nametype = _font_names_map.get(name.nameID)
        if nametype is None:
            continue

        typographic = name.nameID in _typographic_names

        try:
            name_text = name.toUnicode()
        except UnicodeDecodeError:
            continue

        if grouped:
            key = typographic, #, name.platformID, None #name.langID
            names[nametype].add((key, name_text))
        else:
            names[nametype].add(name_text)

    return FontNames(**names)


FontFile = namedtuple('FontFile', 'file index')
FontFileDetectInfo = namedtuple('FontFileDetectInfo', 'file index formathint')

class FontMetrics(FontFile):

    __slots__ = ()

def __str__ (self):
    return '%s [%s]' % (self[0], self[1])

FontFile.__str__ = __str__
FontFile.purpose = N_('Glyphs')
FontFile.metrics = False
FontFileDetectInfo.__str__ = __str__
FontFileDetectInfo.purpose = N_('Glyphs')
FontFileDetectInfo.metrics = False
FontMetrics.__str__ = __str__
FontMetrics.purpose = N_('Metrics')
FontMetrics.metrics = True

FontFileDetails = namedtuple('FontFileDetails',
                             'file index purpose metrics style stat')

FontFileDetails.__str__ = __str__

del __str__

FontFileType = Union[FontFile, FontFileDetectInfo,
                     FontMetrics, FontFileDetails]


StyleFilePathType = MutableMappingOf[str, MutableSetOf[FontFileDetectInfo]]
FamilyFilePathType = MutableMappingOf[str, StyleFilePathType]
FontCountType = MutableMappingOf[str, int]


def crawl_font_file(filepath: str,
                    font_file_by_name: FamilyFilePathType=None,
                    font_counts: FontCountType=None):
    """Crawl a given font, and fill the first dictionary with the files for
    each family and style, providing a dictionary for the families, pointing
    to a dictionary of styles, pointing to a set of files.

    The second dictionary is filled with the number of fonts per file.
    """

    if ttLib is None:
        raise NotSupportedError("fontTools not found")

    if font_file_by_name is None:
        font_file_by_name = {}
    if font_counts is None:
        font_counts = {}

    numfonts = 1

    for i in count():

        if i >= numfonts:
            break

        try:
            fontdata = ttLib.TTFont(filepath, fontNumber=i)
        except (ttLib.TTLibError, EnvironmentError, ImportError):
            break

        if i == 0:
            numfonts = getattr(fontdata.reader, 'numFonts', 1)
            if not numfonts:
                break

        try:
            namelist = fontdata['name']
        except KeyError:
            continue

        names = _font_names(namelist, grouped=True)

        style_files_by_key = defaultdict(lambda: defaultdict(OrderedSet))

        first_family_key = {}
        family_keys_by_key = defaultdict(OrderedSet)
        
        for key, family in names.family:
            if family in font_file_by_name:
                if family in first_family_key:
                    orig_key = first_family_key[family]
                    style_files_by_key[key] = style_files_by_key[orig_key]
                    continue
                else:
                    first_family_key[family] = key
                style_files_by_key[key] = font_file_by_name[family]

        fontformat = None
        #if 'loca' in fontdata.reader.tables:
        if 'loca' in fontdata:
            formathint = 'TrueType'
        elif ('CFF ' in fontdata or 'CFF2' in fontdata):
            formathint = 'CFF'
        else:
            formathint = 'SFNT'

        # Ewww. You don't really don't want how we match names to filenames.
        # Really. Someone should read the docs?
        for key, family in names.family:
            if family in first_family_key:
                orig_key = first_family_key[family]
                style_files_by_key[key] = style_files_by_key[orig_key]
                family_keys_by_key[key] = family_keys_by_key[orig_key]
            else:
                first_family_key[family] = key

            family_keys_by_key[key].add(key)

            style_files = style_files_by_key[key]

            # FIXME: If font_file_by_name[family] is not style_files,
            #        we are in deep faeces. And it sometimes is not.
            font_file_by_name[family] = style_files

        if not names.style:
            names = names._replace(style=OrderedSet((key, 'Regular')
                                                    for key in names.family))

        stylenames_by_key = defaultdict(OrderedSet)
        for key, style in names.style:
            stylenames_by_key[key].add(style)

        detect_info = FontFileDetectInfo(filepath, i, formathint)
        for key in OrderedSet(chain(stylenames_by_key, style_files_by_key)):

            style_files = style_files_by_key.get(key)
            if style_files is None and key[0]:
                style_files = style_files_by_key.get((False, ) + key[1:])
            if style_files is None:
                continue

            stylenames = stylenames_by_key.get(key)
            if not stylenames and key[0]:
                stylenames = stylenames_by_key.get((False, ) + key[1:])
            if not stylenames:
                for other_key in family_keys_by_key.get(key, ()):
                    stylenames = stylenames_by_key.get(other_key)
                    if stylenames:
                        break

            if not stylenames:
                stylenames = ['Regular']

            for style in stylenames:
                style_files[style].add(detect_info)

    if i:
        font_counts[filepath] = i

    return font_counts, font_file_by_name


def crawl_font_directories(locations: IterableOf[str],
                           font_file_by_name: FamilyFilePathType=None,
                           font_counts: FontCountType=None):
    """Crawl a set of locations, and fill the first dictionary with the files for
    each family and style, providing a dictionary for the families, pointing
    to a dictionary of styles, pointing to a set of files.

    The second dictionary is filled with the number of fonts per file.
    """

    if ttLib is None:
        raise NotSupportedError("fontTools not found")

    if font_file_by_name is None:
        font_file_by_name = {}
    if font_counts is None:
        font_counts = {}

    seen = set()

    for location in set(locations):
        #dirpath = location
        #if os.path.isdir(dirpath):
        #    for filename in filenames:
        for dirpath, dirnames, filenames in os.walk(location):
            # Not sure if the caller would provide children, or we
            # need to recurse ourselves, so do both.
            if dirpath in seen:
                continue
            seen.add(dirpath)
            for filename in os.listdir(dirpath):
                filepath = os.path.join(dirpath, filename)
                crawl_font_file(filepath, font_file_by_name, font_counts)

    return font_counts, font_file_by_name


class FeatureSets(object):

    """Find the 'feature sets', e.g. supported languages,
    languages occuring together, font formats, file formats, etc.
    """

    def __init__(self, items: IterableOf[Font]=()):

        fonts = list()

        for item in items:
            if item.is_family:
                fonts.extend(item.styles)
            else:
                fonts.append(item)

        self.languages = set()
        self.font_formats = OrderedDict()
        self.file_formats = OrderedDict()
        self.appears_with = defaultdict(set)
        self.appears_without = defaultdict(set)
        self.absent_together = defaultdict(set)

        #self.lang_pairs = set()
        #self.lang_antipairs = set()

        generics = OrderedSet()
        fontfmts = OrderedDict()
        filefmts = OrderedDict()

        for font in fonts:
            self.languages.update(font.lang)
            generics.add(font.genericfamily)

            if font.fontformat in fontfmts:
                pass
            elif font.font_format_info is FONT_UNKNOWN_FORMAT:
                fontfmts[font.fontformat] = FontFormat(
                    font.fontformat, font.fontformat, 
                    'unknown', 'unknown')
            else:
                fontfmts[font.fontformat] = font.font_format_info

            if font.ext in filefmts:
                pass
            elif font.file_format_info is FILE_UNKNOWN_FORMAT:
                filefmts[font.ext] = FileFormat(
                    font.ext, font.ext, font.ext,
                    'unknown')
            else:
                filefmts[font.ext] = font.file_format_info

        self.genericfamilies = OrderedSet(['',
                                           N_('sans-serif'), N_('serif'),
                                           N_('cursive'), N_('fantasy'),
                                           N_('symbol')])
        self.genericfamilies &= generics
        self.genericfamilies |= generics

        self.font_formats.update((key, value) 
                                 for key, value in font_formats.items()
                                 if key in fontfmts)
        self.font_formats.update(fontfmts)
        self.file_formats.update((key, value) 
                                 for key, value in file_extensions.items()
                                 if key in filefmts)
        self.file_formats.update(filefmts)


        self.languages.discard('')
        self.languages.discard(None)

        langsets = set()
        for font in fonts:
            #languages = set(font.lang)
            #not_languages = self.existing - languages
            langsets.add(frozenset(font.lang))

        for langs in langsets:
            antilangs = self.languages - langs
            for lang in langs:
                #for langB in langs:
                #    self.lang_pairs.add((lang, langB))
                #for langB in antilangs:
                #    self.lang_antipairs.add((lang, langB))

                ## Building these is much faster than a set of pair,
                ## the difference is 0.3 seconds versus 3 seconds
                self.appears_with[lang].update(langs)
                self.appears_without[lang].update(antilangs)

            for lang in antilangs:
                self.absent_together[lang].update(antilangs)

    def lang_appears_with(self, lang: str, other: str) -> bool:
        """The language appears with the other language"""
        #return (lang, other) in self.lang_pairs
        return other in self.appears_with[lang]

    def lang_appears_without(self, lang: str, other: str) -> bool:
        """The language appears without the other language in some font"""
        #return (lang, other) in self.lang_antipairs
        return other in self.appears_without[lang]

    def lang_absent_together_with(self, lang: str, other: str) -> bool:
        """The two languages are both absent in at least one font"""
        return other in self.absent_together[lang]

    def add_fonts(self, items: IterableOf[Font]):
        """DEPRECATED: Add more fonts to update the languages."""
        for item in items:
            if item.is_family:
                self.add_fonts(item.styles)
            else:
                self.languages.update(item.languages)


class NotSupportedError(Exception):
    """Feature not supported."""
    pass


if __name__ == '__main__':
    for font in FontFinder().families():
        print(font)
