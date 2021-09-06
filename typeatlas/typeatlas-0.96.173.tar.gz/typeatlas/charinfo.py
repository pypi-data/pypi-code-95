# -*- coding: utf-8 -*-
#
#    TypeAtlas Character Information
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


"""Access unicode data, allowing the download of all the unicode data from
unicode.org, and falling back to Python's unicodedata when that's not
available.

Nothing should be downloaded without user's consent here.
"""

from typeatlas.util import OrderedSet, N_, warnmsgf, generic_type
from typeatlas import proginfo, rangemath
from collections import namedtuple, OrderedDict, defaultdict
from collections.abc import Callable
from itertools import chain
import typeatlas
import unicodedata
import urllib.parse
import urllib.request
import shutil
import bisect
import sys
import os
import os.path
import io
import re
import copy

SequenceOf = generic_type('Sequence')
TupleOf = generic_type('Tuple')
IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')
Optional = generic_type('Optional')
Union = generic_type('Union')


UNICODE_DOWNLOAD_BASE = 'https://www.unicode.org/Public/UCD/latest/ucd/'
UNICODE_CACHE_PATH = os.path.join(proginfo.CACHE_DIR, 'unicode')
UNICODE_SEARCH_PATH = [UNICODE_CACHE_PATH, '/usr/share/unicode']
UNICODE_NAMESLIST_FILE = 'NamesList.txt'
UNICODE_NAMEALIASES_FILE = 'NameAliases.txt'
UNICODE_DATA_FILE = 'UnicodeData.txt'
UNICODE_BLOCKS_FILE = 'Blocks.txt'
UNICODE_SCRIPTS_FILE = 'Scripts.txt'
UNICODE_VALUE_ALIASES_FILE = 'PropertyValueAliases.txt'
UNICODE_HANGUL_SYLLABLE_FILE = 'HangulSyllableType.txt'

UCSUR_DOWNLOAD_BASE = r'https://www.kreativekorp.com/ucsur/UNIDATA/'
UCSUR_CACHE_PATH = os.path.join(proginfo.CACHE_DIR, 'ucsur')
UCSUR_SEARCH_PATH = [os.path.join(proginfo.CACHE_DIR, 'ucsur')]

UNOFFICIAL_REGISTRIES = {
    'UCSUR': dict(download_base=UCSUR_DOWNLOAD_BASE,
                  cache_path=UCSUR_CACHE_PATH,
                  search_path=UCSUR_SEARCH_PATH,
                  name=N_('ConScript Unicode Registry (unofficial)'))

}



PLANE_SIZE = 0x10000
PLANE_END = PLANE_SIZE - 1

PLANE_COUNT = 17

LOW_SURROGATE_START = LOW_SURROGATE_FIRST = 0xD800
LOW_SURROGATE_STOP = 0xDC00
LOW_SURROGATE_LAST = LOW_SURROGATE_STOP - 1

HIGH_SURROGATE_START = HIGH_SURROGATE_FIRST = LOW_SURROGATE_STOP
HIGH_SURROGATE_STOP = 0xE000
HIGH_SURROGATE_LAST = HIGH_SURROGATE_STOP - 1


SURROGATE_START = SURROGATE_FIRST = LOW_SURROGATE_START
SURROGATE_STOP = HIGH_SURROGATE_STOP
SURROGATE_LAST = SURROGATE_STOP - 1

# Note that sys.maxunicode / 0x10FFFF is a non-character, but is valid
# in interchange, so we include it in the result.
UNICODE_START = UNICODE_FIRST = 0
UNICODE_LAST = sys.maxunicode
#UNICODE_LAST = 0x10FFFF
UNICODE_STOP = sys.maxunicode + 1

NON_CHARACTER_CODES = (set(plane * PLANE_SIZE + PLANE_END - 1
                           for plane in range(PLANE_COUNT)) |
                       set(plane * PLANE_SIZE + PLANE_END
                           for plane in range(PLANE_COUNT)) |
                       set(range(0xFDD0, 0xFDEF + 1)))

NON_CHARACTERS = set(map(chr, NON_CHARACTER_CODES))
ZEROWIDTH = frozenset('\x00\u034F\u200B\u200F\u2028\u2029'
                      '\u202A\u202E\u2060\u2063')


_UNSPECIFIED = object()


_empty_file = lambda: io.StringIO('')


SYMBOL_FOR_PREFIX = 'SYMBOL FOR '

UnicodePlane = namedtuple('UnicodePlane', 'start end number description')

PLANES = {
    0: N_('Basic Multilingual Plane'),
    1: N_('Supplementary Multilingual Plane'),
    2: N_('Supplementary Ideographic Plane'),
    14: N_('Supplementary Special-purpose Plane'),
    15: N_('Supplementary Private Use Area Plane A'),
    16: N_('Supplementary Private Use Area Plane B'),
}

CATEGORIES = {
    'Lu': (N_('Letter'), N_('Uppercase')),
    'Ll': (N_('Letter'), N_('Lowercase')),
    'Lt': (N_('Letter'), N_('Titlecase')),
    'Mn': (N_('Mark'), N_('Non-Spacing')),
    'Mc': (N_('Mark'), N_('Spacing Combining')),
    'Me': (N_('Mark'), N_('Enclosing')),
    'Nd': (N_('Number'), N_('Decimal Digit')),
    'Nl': (N_('Number'), N_('Letter')),
    'No': (N_('Number'), N_('Other')),
    'Zs': (N_('Separator'), N_('Space')),
    'Zl': (N_('Separator'), N_('Line')),
    'Zp': (N_('Separator'), N_('Paragraph')),
    'Cc': (N_('Other'), N_('Control')),
    'Cf': (N_('Other'), N_('Format')),
    'Cs': (N_('Other'), N_('Surrogate')),
    'Co': (N_('Other'), N_('Private Use')),
    'Cn': (N_('Other'), N_('Not Assigned')),

    'Lm': (N_('Letter'), N_('Modifier')),
    'Lo': (N_('Letter'), N_('Other')),
    'Pc': (N_('Punctuation'), N_('Connector')),
    'Pd': (N_('Punctuation'), N_('Dash')),
    'Ps': (N_('Punctuation'), N_('Open')),
    'Pe': (N_('Punctuation'), N_('Close')),
    'Pi': (N_('Punctuation'), N_('Initial quote')),
    'Pf': (N_('Punctuation'), N_('Final quote')),
    'Po': (N_('Punctuation'), N_('Other')),
    'Sm': (N_('Symbol'), N_('Math')),
    'Sc': (N_('Symbol'), N_('Currency')),
    'Sk': (N_('Symbol'), N_('Modifier')),
    'So': (N_('Symbol'), N_('Other')),
}

CATEGORY_ICONS = {
    'Lu': 'character-letter',
    'Ll': 'character-letter',
    'Lt': 'character-letter',
    'Mn': 'character-mark',
    'Mc': 'character-mark',
    'Me': 'character-mark',
    'Nd': 'character-number',
    'Nl': 'character-number',
    'No': 'character-number',
    'Zs': 'character-separator',
    'Zl': 'character-separator',
    'Zp': 'character-separator',
    'Cc': 'character-control',
    'Cf': 'character-format',
    'Cs': 'character-surrogate',
    'Co': 'character-private-use',
    'Cn': 'character-unassigned',
    'Lm': 'character-letter',
    'Lo': 'character-letter',
    'Pc': 'character-punctuation',
    'Pd': 'character-punctuation',
    'Ps': 'character-punctuation',
    'Pe': 'character-punctuation',
    'Pi': 'character-punctuation',
    'Pf': 'character-punctuation',
    'Po': 'character-punctuation',
    'Sm': 'character-symbol',
    'Sc': 'character-symbol',
    'Sk': 'character-symbol',
    'So': 'character-symbol',

    'L': 'character-letter',
    'M': 'character-mark',
    'N': 'character-number',
    'Z': 'character-separator',
    'P': 'character-punctuation',
    'S': 'character-symbol',
    'C': 'character-private-use',
}

BIDI_CATEGORIES = {
    'L': N_('Left-to-Right'),
    'LRE': N_('Left-to-Right Embedding'),
    'LRO': N_('Left-to-Right Override'),
    'R': N_('Right-to-Left'),
    'AL': N_('Right-to-Left Arabic'),
    'RLE': N_('Right-to-Left Embedding'),
    'RLO': N_('Right-to-Left Override'),
    'PDF': N_('Pop Directional Format'),
    'EN': N_('European Number'),
    'ES': N_('European Number Separator'),
    'ET': N_('European Number Terminator'),
    'AN': N_('Arabic Number'),
    'CS': N_('Common Number Separator'),
    'NSM': N_('Non-Spacing Mark'),
    'BN': N_('Boundary Neutral'),
    'B': N_('Paragraph Separator'),
    'S': N_('Segment Separator'),
    'WS': N_('Whitespace'),
    'ON': N_('Other Neutrals'),
}

UNICODE_DATA_FIELDS = tuple([
    'code', 'name', 'category', 'combining',
    'bidirectional', 'decomposition', 'decimal',
    'digit', 'numeric', 'mirrored', 'old_name', 'comment',
    'uppercase', 'lowercase', 'titlecase',
])


CHAR_INFO_FIELD_DEFAULTS = {
    'category': 'Cn',
    'aliases': (),
    'formalaliases': (),
    'variations': (),
    'crossrefs': (),
}

formal_alias = '\u203B'
cross_reference = '\u2192'

# Unicode blocks
uniblock_line_rgx = re.compile(r'(?i)^\s*([0-9a-f]+)\.\.([0-9a-f]+);\s*(\S.*)')

# Names list
nameblock_line_rgx = re.compile(r'(?i)^@@\s+([0-9a-f]+)\s+(.*\S)\s+([0-9a-f]+)')
subheader_line_rgx = re.compile(r'(?i)^@\s+(\S.*)')
code_name_line_rgx = re.compile(r'^(?i)([0-9a-f]+)\s+(\S.*)')
extra_rgx = re.compile(r'\s([=\+x%~])\s+(\S.*)')

range_first_rgx = re.compile(r'^<(.*), First>')
range_last_rgx = re.compile(r'^<(.*), Last>')


NAMELIST_PREFIXES = {
    '=': 'aliases',
    '%': 'formalaliases',
    'x': 'crossrefs',
    '~': 'variations',
}

MEANING_TO_OLD_NAME = {
    'LINE FEED': 'LINE FEED (LF)',
    'HORIZONTAL TABULATION': 'CHARACTER TABULATION',
    'VERTICAL TABULATION': 'LINE TABULATION',
    'FORM FEED': 'FORM FEED (FF)',
    'CARRIAGE RETURN': 'CARRIAGE RETURN (CR)',
    'FILE SEPARATOR': 'INFORMATION SEPARATOR FOUR',
    'GROUP SEPARATOR': 'INFORMATION SEPARATOR THREE',
    'RECORD SEPARATOR': 'INFORMATION SEPARATOR TWO',
    'UNIT SEPARATOR': 'INFORMATION SEPARATOR ONE',
}

OLD_NAME_MEANING = {v: k for k, v in MEANING_TO_OLD_NAME.items()}


CHAR_INFO_FIELDS = OrderedSet(UNICODE_DATA_FIELDS)
CHAR_INFO_FIELDS.update(['display', 'block', 'subheader'])
CHAR_INFO_FIELDS.update(NAMELIST_PREFIXES.values())
CHAR_INFO_FIELDS.add('registry')


UnicodeBlock = namedtuple('UnicodeBlock', 'start end name')
CharRange = namedtuple('CharRange', 'start end info')

BRAILLE_BLOCKS = (UnicodeBlock(0x2800, 0x28FF, 'Braille Patterns'), )
BRAILLE_RANGE = rangemath.OrdinalRange(0x2800, 0x28FF)


class CharInfo(object):

    """The info about a given characters.

    This is initialised using the CHAR_INFO_FIELDS fields, which
    includes the standard unicode data fields (UNICODE_DATA_FIELDS),
    and some additional ones."""

    __slots__ = tuple(CHAR_INFO_FIELDS)

    def __init__(self, *args, **kwargs):
        self.update(*args, _initial=True, **kwargs)

    def __repr__(self):
        code = self.code
        if code is None:
            code = -1
        return '<CharInfo 0x%X %r; at 0x%x>' % (code, self.name,
                                                id(self))

    def merge(self, other: 'CharInfo'):
        """Merge the info from other char info into this one.
        This changes all fields of this character that are
        the default, to the one from the other font info.
        """
        for key in CHAR_INFO_FIELDS:
            value = getattr(other, key)
            if value != CHAR_INFO_FIELD_DEFAULTS.get(key):
                setattr(self, key, value)

    def update(self, *args, _initial=False, **kwargs):
        """Update this character info, as if the constructor
        was called again."""
        if len(args) > len(CHAR_INFO_FIELDS):
            raise TypeError("update takes %r positional argument "
                                      "but %r were given"
                                    % (len(CHAR_INFO_FIELDS) + 1,
                                       len(args) + 1))

        for value, key in zip(args, CHAR_INFO_FIELDS):
            if key in kwargs:
                raise TypeError("update got multiple values for argument %r"
                                    % (key, ))
            kwargs[key] = value

        for key, value in kwargs.items():
            if key not in CHAR_INFO_FIELDS:
                raise TypeError("update got an unexpected keyword argument %r"
                                    % (key, ))

            setattr(self, key, value)

        if _initial:
            for key in CHAR_INFO_FIELDS:
                if not hasattr(self, key):
                    setattr(self, key, CHAR_INFO_FIELD_DEFAULTS.get(key))

    def category_name(self, template: str='{category}, {subcategory}',
                            translate: Callable=N_) -> str:
        """Return the name of the category of the font. By default,
        it is formatted as '{category}, {subcategory}', but you can
        override that.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is.
        """
        category = self.category
        if category not in CATEGORIES:
            category = 'Cn'

        cat, subcat = CATEGORIES.get(category, (N_('Unknown'), N_('Unknown')))
        return template.format(category=translate(cat),
                               subcategory=translate(subcat))

    @property
    def category_icon(self) -> str:
        """Return the category icon name for the function. It should
        represent a file included with typeatlas, without the extension,
        describing the given category of character"""
        try:
            return CATEGORY_ICONS[self.category]
        except KeyError:
            pass

        try:
            return CATEGORY_ICONS[self.category[0]]
        except (KeyError, IndexError, TypeError):
            pass

        try:
            return CATEGORY_ICONS['Co']
        except KeyError:
            pass

        return None


class CharacterDatabase(object):

    """The database of Unicode characters. This holds the unicode data.

    Objects of this class can also implement alternative registries.
    """

    instance = None

    def __init__(self, download_base: str=UNICODE_DOWNLOAD_BASE,
                       cache_path: SequenceOf[str]=UNICODE_CACHE_PATH,
                       search_path: SequenceOf[str]=UNICODE_SEARCH_PATH,
                       name: str=N_('Unicode Character Database'),
                       enabled: bool=True,
                       secondary_registries: 'SequenceOf[CharacterDatabase]'=()):

        self.populated = False

        self.info_by_code = {}
        self.info_by_name = {}
        self.info_by_old_name = {}
        self.infos_by_name = defaultdict(list)

        self.info_ranges = []
        self.info_range_starts = []

        self.unicode_blocks = []
        self.unicode_block_starts = []
        self.scripts = {}
        self.scriptorder = []
        self.script_blocks = []
        self.script_block_starts = []
        self.value_aliases = defaultdict(dict)
        self.value_aliases_all = defaultdict(lambda: defaultdict(list))
        self.alias_values = defaultdict(dict)
        self.download_base = download_base
        self.cache_path = cache_path
        self.search_path = search_path

        self.combining_chars = set()

        self.name = name
        self.enabled = enabled
        self.secondary_registries = list(secondary_registries)

    @classmethod
    def get_instance(cls, populated: bool=False) -> 'CharacterDatabase':
        """Return the singleton instance of the character database, or create
        one if there is not one created yet.

        If populated=True is passed, the instance is required to be
        populated."""
        if cls.instance is None:
            cls.instance = cls()
        if populated:
            cls.instance.ensure_populated()
        return cls.instance

    getInstance = get_instance

    def add_registry_custom(self, registry: 'CharacterDatabase'):
        """Add a custom additional unofficial registry of Unicode
        characters."""
        self.secondary_registries.append(registry)

    def add_registry(self, name: str):
        """Add a custom additional unofficial registry of Unicode
        characters by name, using the known registries from
        UNOFFICIAL_REGISTRIES."""
        cls = type(self)
        registry = cls(**UNOFFICIAL_REGISTRIES[name])
        self.add_registry_custom(registry)

    def add_registries(self, names: IterableOf[str]=None):
        """Add all known or all specified unofficial unicode registries."""
        if names is None:
            names = list(UNOFFICIAL_REGISTRIES)
        for name in names:
            self.add_registry(name)

    def registries(self) -> 'IteratorOf[CharacterDatabase]':
        yield self
        for registry in self.secondary_registries:
            yield from registry.registries()

    def downloadables(self, deep: bool=False) -> IteratorOf[TupleOf[str, str]]:
        """Return pairs of URL, destination path for all the files that
        need to be downloaded for this class to function with latest
        unicode data.

        If deep=True is passed, any added unofficial registries are also
        iterated over.
        """

        yield self.downloadable(UNICODE_BLOCKS_FILE)
        yield self.downloadable(UNICODE_SCRIPTS_FILE)
        yield self.downloadable(UNICODE_DATA_FILE)
        yield self.downloadable(UNICODE_NAMESLIST_FILE)
        #yield self.downloadable(UNICODE_NAMEALIASES_FILE)
        yield self.downloadable(UNICODE_VALUE_ALIASES_FILE)
        #yield self.downloadable(UNICODE_HANGUL_SYLLABLE_FILE)
        if not deep:
            return
        for registry in self.secondary_registries:
            yield from registry.downloadables(deep)

    def downloadable(self, filename: str) -> TupleOf[str, str]:
        """Given the provided filename, return a tuple of the URL
        where to download, and the path where to download it to."""
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)
        url = urllib.parse.urljoin(self.download_base, filename)
        destpath = os.path.join(self.cache_path, filename)
        return url, destpath

    def download_file(self, filename: str):
        """Download the given filename from the correct URL to the
        correct destination path"""
        url, destpath = self.downloadable(filename)
        with urllib.request.urlopen(url) as src:
            with open(destpath, 'wb') as dst:
                shutil.copyfileobj(src, dst)

    def search(self, filename: str, download: bool=False,
                                    default=_UNSPECIFIED) -> Optional[str]:
        """Find the given unicode filename in all potential location
        where the operating system can store it. This will only work
        on some operating systems."""
        for path in self.search_path:
            filepath = os.path.join(path, filename)
            if os.path.exists(filepath):
                return filepath

        if download:
            try:
                self.download_file(filename)
            except OSError:
                if default is _UNSPECIFIED:
                    raise
            filepath = os.path.join(self.cache_path, filename)
            if os.path.exists(filepath):
               return filepath

        if default is not _UNSPECIFIED:
            return default
        raise KeyError(filename)

    def get(self, code: int, autofill: bool=False,
                             fallback: bool=False) -> CharInfo:
        """Get character info by code.

        If autofill is True, basic information may be provided even
        if the character is unknown.

        If fallback is True, data from Python's unicodedata may be
        returned if we don't have unicode data.
        """
        result = None
        if self.info_by_code:
            result = self.info_by_code.get(code)
        else:
            try:
                char = chr(code)
                result = CharInfo(code=code,
                                  name=unicodedata.name(char),
                                  category=unicodedata.category(char),
                                  combining=unicodedata.combining(char),
                                  bidirectional=unicodedata.bidirectional(char),
                                  decomposition=unicodedata.decomposition(char),
                                  decimal=unicodedata.decimal(char),
                                  digit=unicodedata.digit(char),
                                  numeric=unicodedata.numeric(char),
                                  mirrored=unicodedata.mirrored(char),
                                  registry=self)
            except ValueError:
                pass

        if result is None:
            i = bisect.bisect(self.info_range_starts, code) - 1
            if 0 <= i < len(self.info_ranges):
                charrange = self.info_ranges[i]
                if charrange.start <= code <= charrange.end:
                    result = copy.copy(charrange.info)
                    result.code = code
                    try:
                        result.name = unicodedata.name(chr(code))
                    except ValueError:
                        pass

        if result is None and fallback:
            for registry in self.secondary_registries:
                result = registry.get(code, autofill=False)
                if result is not None:
                    break

        if result is None and autofill:
            result = CharInfo(code=code,
                              block=self.find_block(code, None))
        return result

    def get_secondary(self, code: int) -> SequenceOf[CharInfo]:
        """Get secondary information from other registries"""
        results = []
        for registry in self.secondary_registries:
            extra = registry.get(code, autofill=False)
            if extra is not None:
                results.append(extra)
        return results

    def getall(self, code, autofill: bool=False) -> SequenceOf[CharInfo]:
        """Get the information for the character from all registries.

        If autofill is True, basic information may be provided even
        if the character was not found in any of the registries.
        """
        results = []
        main = self.get(code, autofill=False)
        if main is not None:
            results.append(main)

        results.extend(self.get_secondary(code))

        if not results and autofill:
            results.append(CharInfo(code=code,
                                    block=self.find_block(code, None)))
        return results

    def lookup(self, name: str) -> CharInfo:
        """Get character info by name."""
        if self.info_by_code:
            return self.info_by_name.get(name)
        try:
            code = ord(unicodedata.lookup(name))
        except KeyError:
            return None
        else:
            return self.get(code, autofill=True)

    def lookup_many(self, name: str) -> SequenceOf[CharInfo]:
        """Get all characters with a given name."""
        if self.info_by_code:
            return tuple(self.infos_by_name.get(name, ()))
        else:
            return (self.lookup(name), )

    def get_plane(self, code: int,
                        default_description: str
                            =N_('Unassigned plane')) -> UnicodePlane:
        """Get the unicode plane for the character"""
        plane = code // PLANE_SIZE
        description = PLANES.get(plane, default_description)
        return UnicodePlane(plane * PLANE_SIZE, plane * PLANE_SIZE + PLANE_END,
                            plane, description)

    def find_block(self, code: int,
                         default=_UNSPECIFIED) -> Optional[UnicodeBlock]:
        """Find the block of the character."""
        i = bisect.bisect(self.unicode_block_starts, code) - 1
        if 0 <= i < len(self.unicode_blocks):
            block = self.unicode_blocks[i]
            if block.start <= code <= block.end:
                return block
        if default is _UNSPECIFIED:
            raise LookupError(code)
        return default

    def find_script_block(self, code: int, default=_UNSPECIFIED
                          ) -> Optional[UnicodeBlock]:
        """Find the script block of the letter."""
        i = bisect.bisect(self.script_block_starts, code) - 1
        if 0 <= i < len(self.script_blocks):
            block = self.script_blocks[i]
            if block.start <= code <= block.end:
                return block
        if default is _UNSPECIFIED:
            raise LookupError(code)
        return default

    def find_script(self, code: int, default='Unknown') -> Optional[str]:
        """Find the script of the letter."""
        i = bisect.bisect(self.script_block_starts, code) - 1
        if 0 <= i < len(self.script_blocks):
            block = self.script_blocks[i]
            if block.start <= code <= block.end:
                return block.name
        if default is _UNSPECIFIED:
            raise LookupError(code)
        return default

    def find_script_code(self, code: int, default='Zzzz') -> str:
        """Find the ISO 15924 code for the script of the given letter."""
        script = self.find_script(code, None)
        if script is None:
            if default is _UNSPECIFIED:
                raise LookupError(code)
            return default
        return self.get_value_alias('sc', script)

    def find_script_name(self, langdb: 'typeatlas.langutil.LanguageDatabase',
                               code: int, which=None,
                               default=None) -> Optional[str]:
        """Find the name of the script of the given letter.

        Can be the localized, non-localized, or native name. See
        the documentation for langutil.LanguageDatabase.
        """
        script = self.find_script(code, None)

        if script is None:
            if default is not None:
                return default
            if default is _UNSPECIFIED:
                raise LookupError(code)
            script = 'Unknown'

        return langdb.script_name(script, which, chardb=self)

    def find_scripts(self, codes: Union[IterableOf[int], str],
                           default='Unknown') -> IteratorOf[str]:
        """Find the scripts of the letters. A script for every
        letter is returned."""

        block = None

        if isinstance(codes, str):
            codes = map(ord, codes)

        for code in codes:
            if block is not None and block.start <= code <= block.end:
                yield block.name
                continue

            i = bisect.bisect(self.script_block_starts, code) - 1
            if 0 <= i < len(self.script_blocks):
                block = self.script_blocks[i]
                if block.start <= code <= block.end:
                    yield block.name
                    continue

                else:
                    block = None

            yield default

    def get_value_alias(self, category: str, value: str,
                              *other_values: str) -> str:
        """Get the alias for property value. For example, in
        category 'blk', 'CJK' will be alias for the value
        'CJK_Unified_Ideographs'"""
        if other_values:
            return self.get_values_aliases(category, (value, ) + other_values)
        return next(self.get_values_aliases(category, [value]))

    def get_values_aliases(self, category: str,
                                 values: IterableOf[str]) -> IteratorOf[str]:
        """Get the aliases for property values. See get_value_alias."""
        for value in values:
            yield self.value_aliases[category].get(value, value)

    def get_alias_value(self, category: str, value: str,
                              *other_values: str) -> str:
        """Get the property value for alias. See get_value_alias."""
        if other_values:
            return self.get_aliases_values(category, (value, ) + other_values)
        return next(self.get_aliases_values(category, [value]))

    def get_aliases_values(self, category: str,
                                 values: IterableOf[str]) -> IteratorOf[str]:
        """Get the values for aliases"""
        for value in values:
            yield self.alias_values[category].get(value, value)

    def combining(self, code: int) -> bool:
        """Return True if the character is combining."""
        chars = self.combining_chars
        if chars:
            return code in chars
        else:
            return unicodedata.combining(chr(code))

    def east_asian_width(self, code: int) -> str:
        """Get the east asian width. For a given width, you can get the
        meaning of each width using self.get_alias_value('ea', width)
        """
        # FIXME: We do not parse EastAsianWidth.txt
        return unicodedata.east_asian_width(chr(code))

    def guess_width(self, code: int, controlwidth: int=0, *,
                          mode='terminal') -> int:
        """Return a guess about the width of the given unicode
        codepoint. This is useful, for example, for terminal character
        width."""

        if code in ZEROWIDTH:
            return 0

        combining = self.combining_chars
        if code in ZEROWIDTH or code in combining:
            return 0

        char = chr(code)
        if not combining and unicodedata.combining(char):
            return 0

        if unicodedata.east_asian_width(char) in 'WF':
            return 2

        infos = self.info_by_code
        if code in infos:
            if infos[code].category == 'Cc':
                return controlwidth
        elif unicodedata.category(char) == 'Cc':
            return controlwidth

        return 1

    def guess_text_width(self, text: int, controlwidth: int=0, *,
                               mode='terminal') -> int:
        """Return a guess about the width of the given character(s)."""
        return sum(self.guess_code_width(ord(char), controlwidth)
                   for char in text)

    @classmethod
    def braille_blocks(cls) -> SequenceOf[UnicodeBlock]:
        """Get the Braille Patterns unicode blocks."""
        return BRAILLE_BLOCKS

    @classmethod
    def braille_range(cls) -> 'typeatlas.rangemath.RangeBase':
        """Get the Braille Patterns unicode range."""
        return BRAILLE_RANGE

    def open(self, filename: str, download: bool=False,
                   default=_UNSPECIFIED) -> Optional[io.TextIOBase]:
        """Find the given unicode filename and open it."""
        path = self.search(filename, download=download,
                           default=None
                                    if default is not _UNSPECIFIED
                                    else _UNSPECIFIED)
        if path is None:
            return default

        try:
            return open(path, 'rt', encoding='utf8')
        except OSError:
            if default is _UNSPECIFIED:
                raise
        else:
            return default

    def download(self, deep: bool=False):
        """Download all files rquired by this class. If deep=True is
        passed, unofficial registries attached to this are also
        downloaded."""
        self.download_file(UNICODE_BLOCKS_FILE)
        self.download_file(UNICODE_SCRIPTS_FILE)
        self.download_file(UNICODE_DATA_FILE)
        self.download_file(UNICODE_NAMESLIST_FILE)
        #self.download_file(UNICODE_NAMEALIASES_FILE)
        self.download_file(UNICODE_VALUE_ALIASES_FILE)
        #self.download_file(UNICODE_HANGUL_SYLLABLE_FILE)
        if deep:
            for registry in self.secondary_registries:
                registry.download(deep=deep)

    def ensure_populated(self, download: bool=False, deep: bool=False):
        """Ensure the registry is populated it, by reading any unicode
        files found if they weren't read already.

        If download=True is passed, the registries are download. If
        deep=True is also passed, the unofficial registries are also
        populated and/or downloaded."""
        if not self.populated:
            self.populate(download=download)
        if deep:
            for registry in self.secondary_registries:
                registry.ensure_populated(download=download, deep=deep)

    def populate(self, download: bool=False, deep: bool=False):
        """Populate the registry by reading any unicode files found.

        If download=True is passed, the registries are download. If
        deep=True is also passed, the unofficial registries are also
        populated and/or downloaded."""
        self.populate_blocks(download=download)
        self.populate_scripts(download=download)
        self.populate_unicode_data(download=download)
        self.populate_nameslist(download=download)
        #self.populate_namealiases(download=download)
        self.populate_value_aliases(download=download)
        #self.populate_hangul_syllables(download=download)

        self.populated = True

        if deep:
            for registry in self.secondary_registries:
                registry.populate(download=download, deep=deep)

    def populate_blocks(self, download: bool=False):
        """Populate the unicode blocks by reading Blocks.txt.

        It will be downloaded if download=True is passed.
        """

        with self.open(UNICODE_BLOCKS_FILE, default=_empty_file(),
                                            download=download) as src:
            blocks = []
            for line in src:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                match = uniblock_line_rgx.search(line)
                if match is not None:
                    start, end, name = match.groups()
                    blocks.append(UnicodeBlock(int(start, 16),
                                               int(end, 16), name))

        self.unicode_blocks = blocks
        self.unicode_block_starts = [block.start for block in blocks]

    def populate_scripts(self, download: bool=False):
        """Populate the unicode scripts by reading Scripts.txt.

        It will be downloaded if download=True is passed.
        """

        with self.open(UNICODE_SCRIPTS_FILE, default=_empty_file(),
                                             download=download) as src:
            script_blocks = []
            scripts = {}
            for line in src:
                line = line.partition('#')[0].strip()
                if not line:
                    continue
                coderange, sep, script = line.partition(';')
                if not sep:
                    continue

                coderange = coderange.strip()
                script = script.strip()

                start, sep, end = coderange.partition('..')
                if not sep:
                    end = start
                block = UnicodeBlock(int(start, 16), int(end, 16), script)
                script_blocks.append(block)
                scripts.setdefault(block.name, []).append(block)
            script_blocks.sort()

        self.script_blocks = script_blocks
        self.script_block_starts = [block.start for block in script_blocks]
        self.scripts = scripts
        self.scriptorder = sorted(scripts)

    def populate_unicode_data(self, download: bool=False):
        """Populate the unicode data by reading UnicodeData.txt.

        It will be downloaded if download=True is passed.
        """

        self.infos_by_name.clear()

        info_range_starts = OrderedDict()
        info_range_ends = OrderedDict()

        with self.open(UNICODE_DATA_FILE, default=_empty_file(),
                                          download=download) as src:
            for line in src:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                values = line.split(';')

                if len(values) < 2:
                    continue

                info = CharInfo(registry=self,
                                **dict(zip(UNICODE_DATA_FIELDS, values)))
                info.code = int(info.code, 16)

                if info.uppercase:
                    info.uppercase = int(info.uppercase, 16)
                else:
                    info.uppercase = None

                if info.lowercase:
                    info.lowercase = int(info.lowercase, 16)
                else:
                    info.lowercase = None

                if info.titlecase:
                    info.titlecase = int(info.titlecase, 16)
                else:
                    info.titlecase = None

                if (info.combining and
                    info.combining.isdigit() and
                    info.combining.isascii()):
                        info.combining = \
                            int(info.combining)

                info.category = sys.intern(info.category)
                info.bidirectional = sys.intern(info.bidirectional)
                existing = self.info_by_code.get(info.code)
                if existing is not None:
                    existing.merge(info)
                    info = existing

                if info.name.startswith('<') and info.name != '<control>':
                    match = range_first_rgx.search(info.name)
                    if match is not None:
                        info_range_starts[match.group(1)] = info
                        continue

                    match = range_last_rgx.search(info.name)
                    if match is not None:
                        info_range_ends[match.group(1)] = info
                        continue

                self.info_by_code[info.code] = info
                if info.name:
                    if info.name != '<control>':
                        self.info_by_name[info.name] = info
                    self.infos_by_name[info.name].append(info)
                if info.old_name:
                    self.info_by_old_name[info.old_name] = info
                    self.infos_by_name[info.old_name].append(info)

        self.combining_chars.clear()

        for info in self.info_by_code.values():
            if info.name and info.name.startswith(SYMBOL_FOR_PREFIX):
                symbol_for = info.name[len(SYMBOL_FOR_PREFIX):]
                if symbol_for in self.info_by_old_name:
                    self.info_by_old_name[symbol_for].display = info.code
                else:
                    symbol_for = MEANING_TO_OLD_NAME.get(symbol_for)
                    if symbol_for in self.info_by_old_name:
                        self.info_by_old_name[symbol_for].display = info.code

            if info.combining:
                self.combining_chars.add(info.code)

        for old_name, info in self.info_by_old_name.items():
            if old_name not in self.info_by_name:
                self.info_by_name[old_name] = info

        del self.info_ranges[:]
        del self.info_range_starts[:]

        for key, firstinfo in info_range_starts.items():
            lastinfo = info_range_ends.get(key)
            if lastinfo is None:
                warnmsgf("%s unicode range has start, but no end %r",
                         key, firstinfo)
                continue

            info = copy.copy(firstinfo)
            info.code = None
            info.name = None
            self.info_ranges.append(CharRange(firstinfo.code, lastinfo.code,
                                              info))
            self.info_range_starts.append(firstinfo.code)

    def populate_nameslist(self, download: bool=False):
        """Populate the names list by reading NamesList.txt.

        It will be downloaded if download=True is passed."""

        with self.open(UNICODE_NAMESLIST_FILE, default=_empty_file(),
                                               download=download) as src:
            blocks = []

            block = None
            subheader = None
            char = {}

            def finish_last_char():
                if 'code' in char:
                    if char['code'] in self.info_by_code:
                        code = char.pop('code')
                        info = self.info_by_code[code]

                        # UnicodeData lacks the name for many characters
                        # (e.g. Hangul Syllables), but insists on naming
                        # them using < and >
                        if info.name and not name.startswith('<'):
                            del char['name']
                        info.update(**char)

                    else:
                        info = CharInfo(registry=self, **char)
                        self.info_by_code[info.code] = info
                        self.info_by_name[info.name] = info
                        self.infos_by_name[info.name].append(info)

            for line in src:
                stripped = line.strip()

                if not stripped or stripped.startswith(';'):
                    continue

                if line.startswith('@'):
                    match = nameblock_line_rgx.search(line)
                    if match is not None:
                        start, name, end = match.groups()
                        block = UnicodeBlock(int(start, 16),
                                             int(end, 16), name)
                        i = bisect.bisect(self.unicode_blocks, block) - 1
                        if (0 <= i < len(self.unicode_blocks) and
                            self.unicode_blocks[i] == block):
                                block = self.unicode_blocks[i]
                        blocks.append(block)
                        continue

                    match = subheader_line_rgx.search(line)
                    if match is not None:
                        subheader = match.group(1)

                    continue

                match = code_name_line_rgx.search(line)
                if match is not None:
                    finish_last_char()

                    char = dict(code=int(match.group(1), 16),
                                name=match.group(2),
                                block=block, subheader=subheader)
                    continue

                match = extra_rgx.search(line)
                if match is not None:
                    symbol, text = match.groups()
                    key = NAMELIST_PREFIXES.get(symbol)
                    if key is not None:
                        char.setdefault(key, []).append(text)

            finish_last_char()

    def populate_value_aliases(self, download=False):
        with self.open(UNICODE_VALUE_ALIASES_FILE,
                       default=_empty_file(), download=download) as src:

            for line in src:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                values = line.split(';')

                if len(values) < 3:
                    continue

                prop, abbrev, long = (s.strip() for s in values[:3])
                self.alias_values[prop][abbrev] = long
                self.value_aliases[prop][long] = abbrev
                self.value_aliases_all[prop][long].append(abbrev)

    def populate_hangul_syllables(self, download: bool=False):
        """At some point, this function may populate Hangul syllables.

        For now, Python's unicode data is used for this, which is a much saner
        way to deal with this issue.
        """

        return

        with self.open(UNICODE_HANGUL_SYLLABLE_FILE,
                       default=_empty_file(), download=download) as src:

            for line in src:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue


def all_character_codes(noncharacters: bool=False) -> IteratorOf[int]:
    """Iterate over all unicode character codes.

    If noncharacters=True is passed, this function also includes
    non-characters. The non-characters are defined in NON_CHARACTER_CODES"""
    result = chain(range(UNICODE_START, SURROGATE_START),
                   range(SURROGATE_STOP, UNICODE_STOP))
    if noncharacters:
        return result
    return (char for char in result if char not in NON_CHARACTER_CODES)


def all_characters(*args, **kwargs) -> IteratorOf[str]:
    """Iterate over all unicode characters.

    If noncharacters=True is passed, this function also includes
    non-characters. The non-characters are defined in NON_CHARACTER_CODES"""
    return map(chr, all_character_codes(*args, **kwargs))

