# -*- coding: utf-8 -*-
#
#    TypeAtlas Character Set Functions
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
# coding: utf-8


"""Utilities for loading non-Unicode encoding / character set data, mostly
used for the character map in legacy mode.
"""

import sys
import copy
import pkgutil
import importlib
import unicodedata
import encodings as encodings_mod
import binascii
from encodings import aliases as enc_aliases
from operator import itemgetter

from collections import namedtuple, OrderedDict, Counter
from collections.abc import Set, Callable

from typeatlas import charinfo, blockmath
from typeatlas.util import OrderedSet, N_, warnmsgf, noticemsgf, generic_type
from typeatlas.util import EmptyMapping, EmptySequence

MappingOf = generic_type('Mapping')
IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')
SetOf = generic_type('AbstractSet')
SequenceOf = generic_type('Sequence')
TupleOf = generic_type('Tuple')
Union = generic_type('Union')
Optional = generic_type('Optional')


UNICODE = EmptySequence()
UNICODE_SCRIPTS = EmptyMapping()

CONTROL_CHAR_COUNT = 31
DELETE_CHAR = 127

EBCDIC_CODEPAGES = frozenset([
    '037', '273', '277', '278', '280',
    '284', '285', '297', '500', '871', '1047',
    '1140', '1141', '1142', '1143', '1144',
    '1145', '1146', '1147', '1148', '1149', '924'])

DOS_CODEPAGES = frozenset([
    '100', '111', '112', '113', '151', '152', '161', '162', '163', '164',
    '165', '166', '210', '220', '301', '437', '449', '489', '620', '667',
    '668', '707', '708', '709', '710', '711', '714', '715', '720', '721',
    '737', '768', '770', '771', '772', '773', '774', '775', '776', '777',
    '778', '790', '850', '851', '852', '853', '854', '855', '872', '856',
    '857', '858', '859', '860', '861', '862', '863', '864', '17248', '865',
    '866', '808', '867', '868', '869', '874', '1161', '1162', '876', '877',
    '878', '881', '882', '883', '884', '885', '891', '895', '896', '897',
    '898', '899', '900', '903', '904', '906', '907', '909', '910', '911',
    '926', '927', '928', '929', '932', '934', '936', '938', '941', '942',
    '943', '944', '946', '947', '948', '949', '950', '1370', '951', '966',
    '991', '1034', '1039', '1040', '1041', '1042', '1043', '1044', '1046',
    '1086', '1088', '1092', '1093', '1098', '1108', '1109', '1114', '1115',
    '1116', '1117', '1118', '1119', '1125', '848', '1126', '1127', '1131',
    '849', '1139', '1167', '1168', '1300', '1351', '1361', '1362', '1363',
    '1372', '1373', '1374', '1375', '1380', '1381', '1385', '1386', '1391',
    '1392', '1393', '1394'])
    
WINDOWS_ENCODINGS = set()
WINDOWS_ENCODINGS.update(val
                         for key, val in enc_aliases.aliases.items()
                            if key.startswith('windows'))
WINDOWS_ENCODINGS.update(key
                         for key, val in enc_aliases.aliases.items()
                            if val in WINDOWS_ENCODINGS)


# KOI* are DOS charsets, but were also used after DOS, so don't include
# them here. The following encodings are DOS encodings that are missing
# (i.e. we don't have them in encodings.py yet):
# * Iran System
# * CWI-2/HUCWI/cp-hu for Hungarian (slightly changed cp437)
# * Kamenický/KEYBCS2 for Czech (based on cp437) (unoffically cp895)
# * Mazovia for Polish (called 667 and 991 in some DOS versions, 
#                       though 991 is ambiguous)
# * MIK for Bulgarian
# are missing, perhaps altogether.
    

encodings = OrderedDict()


def add_encoding(name: str, *args, **kwargs):
    """Add a known encoding, creating the Encoding object and
    registring it with the modules's encodings dictionary."""
    encodings[name] = Encoding(name, *args, **kwargs)


morse_codes = OrderedDict()


def add_morse_code(name: str, *args, **kwargs):
    """Add a known morse code or similar ancient encoding, creating
    the MorseCode object and registring it with the module's
    morse_codes dictionary."""
    morse_codes[name] = MorseCode(name, *args, **kwargs)


exclude = set(['aliases', 'charmap', 'base64_codec',
               'zlib_codec', 'uu_codec', 'bz2_codec',
               'raw_unicode_escape', 'unicode_escape',
               'unicode_internal', 'rot_13', 'punycode',
               'idna', 'undefined'])


dos_graphical_context = dict(enumerate('☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼', 1))
assert len(dos_graphical_context) == CONTROL_CHAR_COUNT
dos_graphical_context[DELETE_CHAR] = '⌂'

uhc_graphical_context = dict(enumerate('┌┐└┘│─•◘○◙♂♀♪♫☼┼◄↕‼¶┴┬┤↑├→←∟↔▲▼', 1))
assert len(uhc_graphical_context) == CONTROL_CHAR_COUNT
uhc_graphical_context[DELETE_CHAR] = '⌂'

shift_jis_overrides = {b'\\': '¥',
                       b'~': '‾'}
uhc_overrides = {b'\\': '₩'}


encoding_overrides = {
    'shift_jis': shift_jis_overrides,
    'euc_jp': shift_jis_overrides,
    'uhc': uhc_overrides,
    'euc_kr': uhc_overrides,
    'cp949': uhc_overrides,
}


graphical_overrides = {
    'default': {bytes([code]): char
                for code, char in dos_graphical_context.items()},
    'cp949': {bytes([code]): char
              for code, char in uhc_graphical_context.items()},
    'uhc': {bytes([code]): char
            for code, char in uhc_graphical_context.items()},
}


class InterpretationBase(object):

    """This is a base class for interpretations of characters in
    character encodings (for codes whose translations to unicode are
    ambigiuous).

    All subclasses have label, icon, and optional help.

    This used in both the implementation of interpretations, and
    interpretation groups. Use them."""

    def __init__(self, label: str, icon: str=None, help: str=None):

        self.label = label
        self.icon = icon
        self.help = help

    @classmethod
    def make(cls, *args, **kwargs) -> 'InterpretationBase':
        """Create a new interpretation (or group) and register it with
        as a known interpretation (group)."""
        result = cls(*args, **kwargs)
        cls.available.append(result)
        return result

    def __repr__(self):
        return '<%s %r at 0x%x>' % (type(self).__name__, self.label, id(self))


BytedataOverrideType = MappingOf[bytes, str]
EncodingOverridesType = MappingOf[Optional[str], BytedataOverrideType]


class Interpretation(InterpretationBase, Set):

    """Define a different interpretation of the characters depending
    on context. They also interpret a Set interface, so they can be
    used interchangeably with a set of interpretions (InterpretationSet).

    Each Interpretation can be - and should be - in a given group, can be
    the default interpretation in a group if configured, and have a
    dictionary of overrides for given encodings, or general ones
    (signified with None).
    """

    available = []

    def __init__(self, *args,
                       group: 'InterpretationGroup'=None,
                       default: bool=False,
                       overrides: EncodingOverridesType=(),
                       condition: Callable=None,
                       **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.default = default
        self.overrides = dict(overrides)
        self.condition = condition

    @classmethod
    def make(cls, *args, group: 'InterpretationGroup'=None,
                  **kwargs) -> 'Interpretation':
        """Create a new interpretation and register it with
        as a known interpretation."""
        result = super().make(*args, group=group, **kwargs)
        if group is not None:
            group.interpretations.add(result)
        return result

    def bytedata_remap(self, encoding: str) -> MappingOf[bytes, str]:
        """Get remappings of bytedata to unicode characters for a given encoding."""
        if encoding.unicode:
            return {}
        if encoding.name in self.overrides:
            return self.overrides[encoding.name]
        elif self.condition is None or self.condition(encoding):
            return self.overrides.get('default') or {}
        else:
            return {}

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        self is other

    def __ne__(self, other):
        self is not other

    def __contains__(self, item):
        return self is item

    def __iter__(self):
        yield self

    def __len__(self):
        return 1

    @classmethod
    def _from_iterable(cls, iterable):
        return InterpretationSet(iterable)


class InterpretationSet(Set):

    """A set of enabled interpretations that are used together to re-interpret
    characters."""

    def __init__(self, interpretations: IterableOf[Interpretation]):
        self.interpretations = OrderedSet(interpretations)

    def bytedata_remap(self, encoding: str) -> MappingOf[bytes, str]:
        """Get remappings of bytedata to unicode characters for a given encoding,
        getting it from all encodings in the set."""
        result = {}
        for interpretation in self.interpretations:
            result.update(interpretation.bytedata_remap(encoding))
        return result

    def __contains__(self, item):
        return item in self.interpretations

    def __iter__(self):
        return iter(self.interpretations)

    def __len__(self):
        return len(self.interpretations)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.interpretations)


class InterpretationGroup(InterpretationBase, Set):

    """A group of interpretations (usually mutually exclusive) that can be
    selected. The mutual exclusivety is specified using the 'exclusive'
    argument and attribute."""

    available = []

    def __init__(self, *args,
                        interpretations: IterableOf[Interpretation]=(),
                        exclusive: bool=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.interpretations = OrderedSet(interpretations)
        self.exclusive = bool(exclusive)

    def __contains__(self, item):
        return item in self.interpretations

    def __iter__(self):
        return iter(self.interpretations)

    def __len__(self):
        return len(self.interpretations)

    @classmethod
    def _from_iterable(cls, iterable):
        return cls(label='', interpretations=iterable)


InterpretationLike = Union[InterpretationSet, Interpretation]


CONTROL_CHAR_INTERPRETATIONS = InterpretationGroup.make(
            N_('Control characters'), icon='character-control',
            help=N_('Intereptations of the 7-bit ASCII control characters'),
            exclusive=True)

AMBIGIOUS_CHAR_INTERPRETATIONS = InterpretationGroup.make(
            N_('Ambiguous characters'), icon='character-ambiguous',
            help=N_('Intereptations of the 7-bit ASCII control characters'),
            exclusive=True)


ASCII_CONTROL_INTERPRETATION = Interpretation.make(
            N_('ASCII'), icon='character-control',
            help=N_('ASCII control code interpretation of leading CP437 range'),
            group=CONTROL_CHAR_INTERPRETATIONS, default=True)

GRAPHICAL_INTERPRETATION = Interpretation.make(
            N_('Graphical'),
            #icon='character-symbol',
            icon='character-ascii-graphical',
            help=N_('Graphical interpretation of leading CP437 range'),
            group=CONTROL_CHAR_INTERPRETATIONS, default=False,
            overrides=graphical_overrides,
            condition=lambda enc: enc.name.startswith('cp') and
                                  enc.name[2:] in DOS_CODEPAGES)

LOCALE_INTERPRETATION = Interpretation.make(
            N_('Locale interpretation'),
            help=N_('The correct interpretation in the locale for '
                    'ambiguous Shift-JIS or UHC characters'),
            group=AMBIGIOUS_CHAR_INTERPRETATIONS, default=True,
            overrides=encoding_overrides)

ASCII_COMPAT_INTERPRETATION = Interpretation.make(
            N_('ASCII compatibility'),
            help=N_('ASCII equivalent interpretation of '
                    'ambiguous Shift-JIS or UHC characters'),
            group=AMBIGIOUS_CHAR_INTERPRETATIONS, default=False)


class Encoding(object):

    """Information about a given encoding.

    The information can contain ISO 15924 codes of supported scripts,
    a list of characters supported, whether it is a multibyte encoding,
    whether it is unicode, whether it is fixed-width - and what is the
    charsize if true, what maximum bits can it use, and what mapping
    of codepoints to bytes it might use (if applicable).
    """

    morse = False

    def __init__(self, name: str,
                       scripts: MappingOf[str, int]=(),
                       characters: SequenceOf[str]=None,
                       multibyte: bool=False,
                       unicode: bool=False, fixed: bool=True,
                       charsize: int=None, maxbits: int=None,
                       codepoint_bytes: MappingOf[int, bytes]=None):

        self.name = name
        self.scripts = scripts
        self.characters = characters
        self.multibyte = multibyte
        self.unicode = unicode
        self.fixed = fixed
        self.charsize = charsize
        self.maxbits = maxbits

        self._canonical_codepoint_bytes = codepoint_bytes
        self._remapped_codepoint_bytes = None

        self.current_interpretation = None
        self.bytedata_remap = self.codepoint_remap = self.char_remap = None

    def interpretation(self, interpretation: InterpretationLike) -> 'Encoding':
        """Get an alternative interpretation of the encoding."""
        result = copy.copy(self)
        result.current_interpretation = interpretation

        if interpretation is not None:
            result.bytedata_remap = interpretation.bytedata_remap(self)
        else:
            result.bytedata_remap = None

        if not result.bytedata_remap:
            result.bytedata_remap = None
            result.codepoint_remap = None
            result.char_remap = None
            return result

        result.codepoint_remap = {ord(char): bytedata
                                  for bytedata, char
                                        in result.bytedata_remap.items()}
        result.char_remap = {char: bytedata
                             for bytedata, char
                                    in result.bytedata_remap.items()}

        return result

    def codepoint_bytes(self, chardb: charinfo.CharacterDatabase=None, *,
                              cache: bool=False) -> MappingOf[int, bytes]:
        """Get a mapping of codepoint code to bytedata, respecting the current
        interpretation."""
        result = self._remapped_codepoint_bytes
        if result is not None:
            return result

        bytedata_remap = self.bytedata_remap

        canonical_result = self.canonical_codepoint_bytes(chardb, cache=cache)
        if bytedata_remap is None:
            return canonical_result

        result = {}

        for codepoint, bytedata in canonical_result.items():
            if bytedata in bytedata_remap:
                codepoint = ord(bytedata_remap[bytedata])
            result[codepoint] = bytedata

        if cache:
            self._remapped_codepoint_bytes = result

        return result

    def canonical_codepoint_bytes(self,
                                  chardb: charinfo.CharacterDatabase=None, *,
                                  cache: bool=False) -> MappingOf[int, bytes]:
        """Get a mapping of codepoint code to bytedata without respect to
        current interpretation."""
        result = self._canonical_codepoint_bytes
        if result is not None:
            return result
        if not self.characters:
            # FIXME: No point caching in a copy of class that we throw away
            return self.complete(chardb).canonical_codepoint_bytes(chardb, cache=cache)
        result = {}
        for char in self.characters:
            bytedata = char.encode(self.name)
            result[ord(char)] = bytedata

        if cache:
            self._canonical_codepoint_bytes = result

        return result

    def complete(self, chardb: charinfo.CharacterDatabase=None) -> 'Encoding':
        """Get a complete version of the encoding, with all the information,
        particularly about the supported characters, filled by
        get_encoding_slow()."""

        if self.characters:
            return self
        result = copy.copy(self)
        #result.characters = ''.join(map(itemgetter(1),
        #                                get_characters_slow(self.name)))
        complete = get_encoding_slow(self.name, chardb)
        result.characters = complete.characters
        result.codepoint_bytes = complete.codepoint_bytes
        result.multibyte = complete.multibyte
        result.fixed = complete.fixed
        result.charsize = complete.charsize
        result.maxbits = complete.maxbits
        result._canonical_codepoint_bytes = complete._canonical_codepoint_bytes
        result._remapped_codepoint_bytes = None
        return result

    def get_byte_data(self, code: int) -> bytes:
        """Get the byte data for a given code point."""
        if self.codepoint_remap is not None and code in self.codepoint_remap:
            return self.codepoint_remap[code]
        return chr(code).encode(self.name)

    def get_hex(self, code: int) -> str:
        """Get the hex-encoded version of the byte data for a given code point."""
        return str(binascii.hexlify(self.get_byte_data(code)))

    def get_integer(self, code: int) -> int:
        """Get a useless integirifed version of the byte data for a given code
        point. That's only sensible for fixed-length encodings or encodings
        that contain no null bytes."""
        result = 0
        for c in self.get_byte_data(code):
            result = result * 256 + c
        return result

    def label(self, translate: Callable=N_) -> str:
        """Get the label for the given encoding.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is."""

        _ = translate

        name = self.name

        label = name.upper().replace('_', '-')

        if name.startswith('cp'):
            codepage = name[2:]
            if codepage in DOS_CODEPAGES:
                return _('DOS code page %s') % (name[2:], )
            if codepage in EBCDIC_CODEPAGES:
                return _('EBCDIC code page %s') % (name[2:], )

        if name in WINDOWS_ENCODINGS and name.startswith('cp'):
            return 'Windows ' + name[2:]

        return label

    common_scripts = set(['Zxxx', 'Zyyy', 'Zzzz'])

    def category(self) -> Optional[str]:
        """Return a category to put the encoding in for display.

        One possible interpretation is that it detects the encoding
        script(s) and returns one of them."""
        if self.scripts is UNICODE_SCRIPTS:
            return None

        scripts = [s for s in self.scripts
                   if s not in self.common_scripts]
        if not scripts:
            return None
        return max(scripts, key=self.scripts.get)

    def category_label(self, translate: Callable=N_) -> str:
        """Return a category label to put the encoding in for display,
        optionally translated.

        One possible interpretation is that it detects the encoding
        script(s) and returns one of them.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is."""
        _ = translate

        if self.unicode:
            return _('Unicode')

        category = self.category()
        if category is None:
            return _("Other")

        from typeatlas import langutil
        langdb = langutil.LanguageDatabase.get_instance(populated=True)
        return langdb.script_name(category)

    def get_icon(self) -> Optional[str]:
        """Return the name of an icon for the given encoding. This will either be
        None, or a file provided with typeatlas without the extension."""
        name = self.name

        if name.startswith('cp'):
            codepage = name[2:]
            if codepage in DOS_CODEPAGES:
                return 'platform-dos'
            if codepage in EBCDIC_CODEPAGES:
                return 'platform-oldiron'
            if name in WINDOWS_ENCODINGS:
                return 'platform-redmond'

        elif name.startswith('mac'):
            return 'platform-cupertino'

        elif name.startswith('iso'):
            return 'standard'

        elif name in WINDOWS_ENCODINGS or name.startswith('windows'):
            return 'platform-redmond'

    def __repr__(self):
        return '<%s %r at 0x%x>' % (type(self).__name__, self.name, id(self))


ONE_TO_ONE_REMAP = 0
MULTICHAR_REMAP = 1


class MorseCode(object):

    """Class that implements the same interface as Encoding, but for morse
    code and similar encodings.

    A code is encoded using an alphabet, which maps unicode character to
    code (if lenght_coded is True, this can use 'dashes' of multiple lengths).

    International morse codes can instead map provide those as remap base, and
    map international unicode characters to latin unicode characters in the base.
    If remap_mode is MULTICHAR_REMAP, then one character can be translated to
    multiple.

    The final mapping (from character to telegraph code) is stored
    in self.alpha_codes.

    If needle_coded is True, then the code is not morse-code-like, but a needle
    telegraph code. This is not supported at the time of documenting the code.
    """

    morse = True

    def __init__(self, name: str,
                       alphabet: MappingOf[str, str],
                       alphabet_remap_base: MappingOf[str, str]=None,
                       remap_mode=ONE_TO_ONE_REMAP,
                       length_coded: bool=False,
                       needle_coded: bool=False,
                       scripts: MappingOf[str, int]=(),
                       characters: SequenceOf[str]=None,

                       # Unused
                       charsize: int=None, maxbits: int=None,
                       codepoint_bytes: MappingOf[int, bytes]=None):

        self.name = name

        if alphabet_remap_base is None:
            self.alpha_codes = alphabet
            self.alpha_remap = {}
            self.base_codes = alphabet

        elif remap_mode == ONE_TO_ONE_REMAP:
            self.alpha_codes = {alpha: alphabet_remap_base[char]
                                for alpha, char in alphabet.items()}
            self.alpha_remap = alphabet
            self.base_codes = alphabet_remap_base

        elif remap_mode == MULTICHAR_REMAP:
            self.alpha_codes = {alpha: ' '.join(alphabet_remap_base[char]
                                                for char in chars)
                                for alpha, chars in alphabet.items()}
            self.alpha_remap = alphabet
            self.base_codes = alphabet_remap_base

        self.remap_mode = remap_mode
        self.length_coded = length_coded
        self.needle_coded = needle_coded

        self.scripts = scripts
        self.characters = characters
        self.multibyte = True
        self.unicode = False
        self.fixed = False
        self.charsize = None
        self.maxbits = maxbits
        self._canonical_codepoint_bytes = codepoint_bytes

    def alpha_telegraph_codes(self, pretty: bool=True) -> MappingOf[str, str]:
        """Return mapping of unicode characters to telegraph code for display.

        If pretty=False is true, the raw (not the pretty) version is
        returned."""
        if not pretty or self.needle_coded:
            return dict(self.alpha_codes)

        remaps = {
            ord('.'): '▄',
            ord('-'): '▄' if self.length_coded else '▄▄',
        }

        return {char: text.translate(remaps)
                for char, text in self.alpha_codes.items()
                if len(char) == 1}

    def codepoint_telegraph_codes(self, *args, **kwargs) -> MappingOf[int, str]:
        """Return mapping of unicode codepoints to telegraph code for display.

        If pretty=False is true, the raw (not the pretty) version is
        returned."""

        return {ord(char): text
                for char, text
                    in self.alpha_telegraph_codes(*args, **kwargs).items()
                if len(char) == 1}


    def codepoint_bytes(self, chardb: charinfo.CharacterDatabase=None, *,
                              cache: False=False) -> MappingOf[int, bytes]:
        if self._canonical_codepoint_bytes is None:
            self._canonical_codepoint_bytes = {
                ord(char): (morse + '  ').encode('ascii')
                for char, morse in self.alpha_codes.items()
            }

        return self._canonical_codepoint_bytes

    def interpretation(self, interpretation: InterpretationLike) -> 'Encoding':
        return self

    def complete(self, chardb: charinfo.CharacterDatabase=None) -> 'MorseCode':
        return self

    def get_byte_data(self, code: int) -> bytes:
        return (self.alpha_codes.get(chr(code)) + '  ').encode('ascii')

    def get_hex(self, code: int) -> bytes:
        return str(binascii.hexlify(self.get_byte_data(code)))

    def get_integer(self, code: int) -> int:
        result = 0
        for c in self.get_byte_data(code):
            result = result * 256 + c
        return result

    def label(self, translate: Callable=N_) -> str:
        """Get the label for the given telegraph code.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is.
        """
        _ = translate

        return _(self.name)

    common_scripts = set(['Zxxx', 'Zyyy', 'Zzzz'])

    def category(self) -> Optional[str]:
        """Return a category to put the telegraph code in for display."""
        scripts = [s for s in self.scripts
                   if s not in self.common_scripts]
        if not scripts:
            return None
        return max(scripts, key=self.scripts.get)

    def category_label(self, translate: Callable=N_) -> str:
        """Return a category label to put the telegraph code in for display,
        optionally translated.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is."""
        _ = translate

        category = self.category()
        if category is None:
            return _("Other")

        from typeatlas import langutil
        langdb = langutil.LanguageDatabase.get_instance(populated=True)
        return langdb.script_name(category)

    def get_icon(self) -> Optional[str]:
        """Return an icon for the given telegraph code."""
        #return 'morse'
        return None


EncodingLike = Union[Encoding, MorseCode]


def charblocks(blocks: IterableOf[blockmath.BlockLike]) -> str:
    """Convert an iterable of character blocks to a string of characters."""
    return ''.join(map(chr, blockmath.iterblocks(blocks)))


def get_encodings() -> IterableOf[Encoding]:
    """Return an iterable of all encodings."""

    result = set(name
                 for loader, name, ispkg
                    in pkgutil.iter_modules(encodings_mod.__path__)
                 if not ispkg)

    result -= exclude
    result -= set(enc_aliases.aliases)

    return result


def get_characters_slow(charset: str) -> IteratorOf[TupleOf[int, str, bytes]]:
    """Slow function to find the characters in an encoding.

    Returns tuple of codepoint, character and encodedbytedata."""

    try:
        module = importlib.import_module('encodings.utf_8')
    except ImportError:
        pass
    else:
        if hasattr(module, 'decoding_table'):
            result = []
            for i, char in sorted(enumerate(module.decoding_table),
                                  key=itemgetter(1)):
                if char == '\ufffe':
                    continue
                assert char.encode(charset) == bytes([i])
                yield ord(char),  char, char.encode(charset)
            return

    overrides = encoding_overrides.get(charset, {})
    seen = {}
    result = OrderedDict()

    for code in charinfo.all_character_codes():
        char = chr(code)
        try:
            bytedata = char.encode(charset)
        except ValueError:
            continue

        if bytedata in seen:

            action = 'kept'

            # FIXME: Why are we doing this?
            if bytedata in overrides:
                replace = overrides[bytedata] == char
            else:
                replace = bytedata.decode(charset) == char

            if replace:
                action = 'replaced'
                del result[char]
                result[char] = code, char, bytedata

            if (unicodedata.normalize('NFKC', char) ==
                unicodedata.normalize('NFKC', seen[bytedata])):
                showmsgf = noticemsgf
            else:
                showmsgf = warnmsgf

            showmsgf("%r encodes both %r and %r, %s the former",
                     bytedata, seen[bytedata], char, action)

            continue

        seen[bytedata] = char

        result[char] = code, char, bytedata

    yield from result.values()


def get_encoding(name: str) -> Encoding:
    """Get encoding by name."""
    name = encodings_mod.normalize_encoding(name)
    return encodings.get(name)


def get_encoding_slow(name,
                      chardb: charinfo.CharacterDatabase=None) -> Encoding:
    """Slow function to get encoding info."""

    if chardb is None:
        chardb = charinfo.CharacterDatabase.get_instance(populated=True)

    codepoints = OrderedDict()
    characters = OrderedSet()

    charsizes = set()

    clean_7bit = True

    for code, char, bytedata in get_characters_slow(name):

        bytelen = len(bytedata)

        if bytelen == 1 and 0b10000000 & ord(bytedata):
            clean_7bit = False

        codepoints[code] = bytedata
        charsizes.add(bytelen)
        characters.add(char)

    fixed = len(charsizes) == 1
    multibyte = charsizes != {1}

    if fixed:
        charsize = next(iter(charsizes))
    else:
        charsize = None
    scripts = Counter(chardb.find_scripts(codepoints))
    scripts = {chardb.get_value_alias('sc', script): count
               for script, count in scripts.items()}

    maxbits = max(charsizes) * 8
    if maxbits == 8 and clean_7bit:
        maxbits = 7

    return Encoding(name, scripts,
                    characters=''.join(characters),
                    multibyte=multibyte, fixed=fixed, charsize=charsize,
                    maxbits=maxbits, codepoint_bytes=codepoints)


def print_encoding_info():
    """Print info about all encodings"""

    charconsts = {}


    utf8 = get_encoding_slow('utf8')
    for charset in sorted(get_encodings()):
        try:
            encoding = get_encoding_slow(charset)
        except LookupError:
            continue

        unicode = False

        scriptrepr = repr(encoding.scripts)

        characters = ''.join(sorted(encoding.characters))
        if characters == utf8.characters:

            charconst = 'UNICODE'
            unicode = True
            scriptrepr = 'UNICODE_SCRIPTS'

        elif characters in charconsts:
            charconst = charconsts[characters]

        elif len(characters) > 1024:
            charconst = 'None'

        else:
            blocks = blockmath.toblocks(map(ord, characters))
            blockcode = 'charblocks([%s])' % (
                            ', '.join('(0x%x, 0x%x)' % block
                                      for block in blocks))

            charconst = 'CHARS_' + charset.upper()

            if len(characters) < 512:
                print('# %s = %r\n\n' % (charconst, characters))

            charconsts[characters] = charconst
            print('%s = %s\n\n' % (charconst, blockcode))

        print('''
add_encoding({name!r}, characters={characters},
             scripts={scripts},
             multibyte={multibyte!r}, fixed={fixed!r}, unicode={unicode!r},
             charsize={charsize!r}, maxbits={maxbits!r})
'''.format(name=encoding.name, scripts=scriptrepr,
           characters=charconst,
           multibyte=encoding.multibyte, fixed=encoding.fixed,
           unicode=unicode, charsize=encoding.charsize, 
           maxbits=encoding.maxbits))


def load_encodings():
    """Load the encodings. This is automatically called."""
    from typeatlas.data import encodings as encoding_infos
    from typeatlas.data import morse as morse_infos
    encoding_infos, morse_infos

    for encoding in get_encodings():
        if encoding not in encodings:
            try:
                'test'.encode(encoding, 'replace')
            except (ValueError, TypeError, LookupError):
                pass
            else:
                encodings[encoding] = Encoding(encoding)


load_encodings()

if __name__ == '__main__':
    print_encoding_info()
