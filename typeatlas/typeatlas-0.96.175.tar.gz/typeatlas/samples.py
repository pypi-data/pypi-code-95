# coding: utf-8
#
#    TypeAtlas Sample Text Utilities
#
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

"""Language sample database for testing fonts."""

# TODO: Order: Prefer known languages, then languages in different
#              writing system, *then* languages with yet unseen characters,
#              then all the rest. get_samples_with_prio() that reorders them.
# TODO: Implement fallbacks
# TODO: Match ISO script with the full name from PropertyValueAliases.txt
# TODO: Select languages from aspell, ispell, hunspell dictionaries.
# TODO: Add writing system samples. Add numbers, related to writing systems.
# TODO: Currency
# TODO: OpenType features when displaying pangrams
# TODO: Display all scripts. Need IPA samples.

from __future__ import unicode_literals

from collections import namedtuple, defaultdict, OrderedDict
from itertools import chain
import sys
from typeatlas.util import OrderedSet, N_, warnmsgf, generic_type
# RFC 3066 code pangrams

SetOf = generic_type('Set')
SequenceOf = generic_type('Sequence')
IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')
Literal = generic_type('Literal')
Optional = generic_type('Optional')
Union = generic_type('Union')

ANY = object()
ALL = object()

LangListType = Union[SequenceOf[str], Literal[ANY, ALL]]
ScriptListType = SequenceOf[str]
ScriptType = Union[str, Literal[ANY, ALL]]


DEFAULT = ''
ALTERNAITVE = '-alt'
DATED = '-dated'
ANCIENT = '-ancient'


PRIO_PREFER = 150
PRIO_DEFAULT = 100
PRIO_WITHHOLD = 50

class SampleType(object):

    """A type of sample with its feature. For example, a pangram
    would contain all vowels, consonants, etc."""

    def __init__(self, name: str,
                       multichar: bool=True, phrase: bool=False,
                       all_characters: bool=False,
                       all_consonants: bool=False,
                       all_vowels: bool=False,
                       all_accents: bool=False,
                       all_accent_combinations: bool=False,
                       both_cases: bool=False,
                       all_digits: bool=False,
                       all_symbols: bool=False,
                       all_syllables: bool=False,
                       all_strokes: bool=False,
                       extensive_coverage: bool=False,
                       incomplete: bool=False,
                       common_only: bool=False,
                       no_repeats: bool=False):
        self.name = name
        self.multichar = multichar
        self.phrase = phrase
        self.all_characters = all_characters
        self.all_consonants = all_consonants
        self.all_vowels = all_vowels
        self.all_accents = all_accents
        self.all_accent_combinations = all_accent_combinations
        self.both_cases = both_cases
        self.all_symbols = all_symbols
        self.all_syllables = all_syllables
        self.all_strokes = all_strokes
        self.extensive_coverage = extensive_coverage
        self.incomplete = incomplete
        self.common_only = common_only
        self.no_repeats = no_repeats

    def variant(self, name, **kwargs) -> 'SampleType':
        """Return a variant of that type."""
        kw = dict(vars(self))
        kw.update(name=name, **kwargs)
        return type(self)(**kw)


CHARACTER = SampleType(N_('Character'), multichar=False)
PHRASE = SampleType(N_('Phrase'), phrase=True)
PANGRAM = PHRASE.variant(N_('Pangram'),
                         all_characters=True,
                         all_consonants=True,
                         all_vowels=True,
                         all_accents=True,
                         all_accent_combinations=True,
                         all_strokes=True)

PERFECT_PANGRAM = PANGRAM.variant(N_("Perfect pangram"),
                                  no_repeats=True)

KOREAN_PANGRAM = PANGRAM.variant(N_("Phrase with all vowels and consonants"),
                                 all_characters=False)

KOREAN_CONSONANT_PANGRAM = KOREAN_PANGRAM.variant(
                                N_("Phrase with all consonants"),
                                all_vowels=False)

# Those are different
PANGRAM_PARTIAL_ACCENTS = PANGRAM.variant(N_("Pangram without all accents"),
                                          all_accents=False,
                                          all_accent_combinations=False)
PANGRAM_LIMITED_ACCENTS = PANGRAM.variant(N_("Pangram without all accent combinations"),
                                          all_accents=False)
SYLLABLE_PANGRAM = PANGRAM.variant(N_('Syllable pangram'),
                                   all_syllables=True,
                                   all_characters=False)
PARTIAL_PANGRAM = PANGRAM.variant(N_('Partial pangram'),
                                  incomplete=True)

YONG_CHARACTER = CHARACTER.variant(N_('Yong character'),
                                   all_strokes=True,
                                   common_only=True)


SampleInfo = namedtuple('SampleInfo',
                        ['code', 'text', 'script', 'origin', 'sources',
                         'english', 'translit', 'original', 'version',
                         'type', 'note', 'flags', 'prio'])

SampleInfo.lang = property(lambda self: self.code)


def normalize_langcode(langcode: str) -> str:
    """Turn the langcode into something the modules of this module like.

    get_sample/get_samples/has_sample call this for you.
    """

    langcode = langcode.lower().replace('_', '-')
    langcode = langcode.partition('@')[0].partition('.')[0]
    return langcode


class LanguageSamples(object):

    """A memory database of loaded language sample texts."""

    def __init__(self):
        #self.codes_with_pangrams = set()
        #self.code_scripts_with_pangrams = set()
        self.samples_regular = OrderedDict()
        self.samples_long = OrderedDict()
        self.display_scripts = OrderedDict()
        self.sample_fallbacks = OrderedDict()
        self.unsorted_samples = []

    normalize_code = staticmethod(normalize_langcode)
    sample_factory = staticmethod(SampleInfo)

    def use_display_scripts(self, code: str, scripts: SequenceOf[str]):
        """Register the given scripts for use with the given language code."""
        if code in self.display_scripts:
            scripts = OrderedSet(chain(self.display_scripts[code], scripts))
        self.display_scripts[code] = tuple(scripts)

    def use_fallback(self, requested: str, fallback_to: str,
                           script: ScriptType=ANY):
        """Register the second language as a fallback for the first, for the
        given script, when looking up samples."""
        if requested in self.sample_fallbacks:
            fbs = self.sample_fallbacks[requested]
        else:
            fbs = ()

        fbs += (fallback_to, )
        self.sample_fallbacks[requested] = fbs

    def has_sample(self, code: str, exact: bool=False, fallbacks: bool=True,
                         script: ScriptType=ANY, long=False) -> bool:
        """Return True if we have sample for lang code.

        Options mean the same as for get_sample.
        """

        samples = self.samples_long if long else self.samples_regular

        if not exact:
            code = self.normalize_code(code)

        if script is ANY:
            if code in samples:
                return True
            if fallbacks and code.partition('-')[0] in samples:
                return True
            return False

        else:
            if fallbacks:
                code_alt = code.partition('-')[0]
                keys = ((code, ANY), (code_alt, ANY),
                        (code, script), (code_alt, script))
            else:
                keys = ((code, ANY), (code, script))

            return any(key in samples for key in keys)


    def get_sample(self, code: str, exact: bool=False, fallbacks: bool=True,
                         alternative: int=0, long: bool=False,
                         script: ScriptType=ANY) -> Optional[SampleInfo]:
        """Get a sample for the given language code.

        If alternative > 0 is passed, an alternative phrase may be returned.
        If long=True is passed, the function is allowed to return long phrases.
        If script is passed, return the phrase for the given script.

        If exact is True, the language code won't be normalized.
        If fallbacks is False, only the exact language will be returned, i.e.
        if a region is specified and there isn't a sample for this region, it
        won't be returned.
        """
        samples = self.samples_long if long else self.samples_regular

        if not exact:
            code = self.normalize_code(code)

        if script is ANY:
            results = samples.get(code)
            if not results and fallbacks:
                results = samples.get(code.partition('-')[0])

        else:
            results = samples.get((code, script))

            # Preferring ANY script over fallback. Reason:
            # ANY script is a fallback for samples where script is undefined.
            # We just assume it matches, so we prefer it. That may be wrong, though.
            if not results:
                results = samples.get((code, ANY))

            if not results and fallbacks:
                results = samples.get((code.partition('-')[0], script))

            if not results and fallbacks:
                results = samples.get((code.partition('-')[0], ANY))

        if alternative is ALL:
            return list(results or ())
        if alternative is ANY:
            alternative = 0
        if results:
            return results[min(alternative, len(results) - 1)]

        return None

    def get_samples(self, codes: LangListType,
                          exact: bool=False, fallbacks: bool=True,
                          alternative: int=0, long=False,
                          script: ScriptType=ALL,
                          scripts: ScriptListType=None) -> IteratorOf[SampleInfo]:
        """Yield a sample for each of the given language codes.

        ANY can be passed to get any, if you don't know the language.

        You can pass script to limit

        If alternative > 0 is passed, alternative phrases may be returned.
        So of multiple samples are supported for the same language, you can
        pass alternative=1, 2, 3, etc. to get an alternative one. This can
        be used to vary the result to e.g. build longer text.

        If long=True is passed, the function is allowed to return long phrases.
        If script is passed, return phrases for the given script. Does not make
        sense to pass this.

        The exact argument controls the interpretation of the language codes,
        preventing normalization. See get_sample() for exact, fallbacks, etc.
        """

        if codes is ANY:
            codes = self.available_language_codes(long=long, script=script)

        for code in codes:
            if scripts is None:
                if script is ALL:
                    scripts = self.display_scripts.get(code) or [ANY]
                else:
                    scripts = [script]

            seen = set()

            for scr in scripts:
                sample = self.get_sample(code,
                                         exact=exact, fallbacks=fallbacks,
                                         alternative=alternative, long=long,
                                         script=scr)

                # If all alternatives are requested, don't care if we
                # already returned that.
                if alternative is ALL:
                    yield from sample
                    continue

                if sample is None:
                    continue

                if sample.code in seen:
                    continue
                if (sample.code, sample.script) in seen:
                    continue

                if sample.script is ANY:
                    seen.add(sample.code)
                else:
                    seen.add((sample.code, sample.script))

                yield sample

    def add_sample(self, code: str, text: str, script: ScriptType=ANY,
                         origin: str=None, sources: SequenceOf[str]=(),
                         english: str=None, translit: str=None, original: str=None,
                         version: str=DEFAULT, type: SampleType=PHRASE, note: str='',
                         flags: IterableOf[str]=frozenset(),
                         prio: int=PRIO_DEFAULT,
                         langpos: int=None, langscriptpos: int=None) -> SampleInfo:

        """Register the given sample for use with the given language.

        You can provide text, script, origin, sources where the sample was taken from,
        enligh version, translit version (in Latin script), original phrase,
        version of the sample, type of the sample (e.g. PANGRAM), any note,
        flags that define its use, and priority (e.g. prio PRIO_WITHHOLD would
        preclude its immediate use).


        You can insert later samples at earlier positions using langpos
        and langscriptpos arguments. That's considered a bad hack.
        """

        if code == 'en' or code.startswith('en'):
            if not english:
                english = text

        code = self.normalize_code(code)

        #code_scripts_with_pangrams.add((code, script))
        #codes_with_pangrams.add(code)

        sampleinfo = self.sample_factory(code, text, script, origin,
                                         tuple(sources),
                                         english, translit, original,
                                         version, type,
                                         note, frozenset(flags), int(prio))

        self.unsorted_samples.append(sampleinfo)

        if 'no-display' in sampleinfo.flags or 'non-default' in sampleinfo.flags:
            return sampleinfo

        if 'long-only' in sampleinfo.flags:
            if script != 'Brai':
                self.samples_long.setdefault(code, []).append(sampleinfo)
            self.samples_long.setdefault((code, script), []).append(sampleinfo)
            return sampleinfo

        # Don't use Braille samples by default
        if script != 'Brai':
            samples = self.samples_regular.setdefault(code, [])
            if langpos is None or langpos >= len(samples):
                samples.append(sampleinfo)
            else:
                samples.insert(langpos, sampleinfo)

        samples = self.samples_regular.setdefault((code, script), [])
        if langscriptpos is None or langscriptpos >= len(samples):
            samples.append(sampleinfo)
        else:
            samples.insert(langscriptpos, sampleinfo)

        return sampleinfo

    def available_language_codes(self, long: bool=None,
                                       script: ScriptType=ALL) -> IteratorOf[str]:
        """Get all the available language codes.

        The script argument is ignored for now, but it is supported
        so it can be passed.
        """
        if long is None:
            samples = self.samples_regular.keys() | self.samples_long.keys()
        else:
            samples = self.samples_long if long else self.samples_regular
        for code in samples:
            if isinstance(code, tuple):
                continue
            yield code


main_samples = LanguageSamples()

add_sample = main_samples.add_sample
has_sample = main_samples.has_sample
get_sample = main_samples.get_sample
get_samples = main_samples.get_samples
use_fallback = main_samples.use_fallback
use_display_scripts = main_samples.use_display_scripts
available_language_codes = main_samples.available_language_codes


def load_samples():
    """Load language samples bundled with typeatlas."""
    from typeatlas.data import samples_language
    from typeatlas.data import samples_language_pango
    from typeatlas.data import samples_language_glass
    from typeatlas.data import samples_braille
    samples_language, samples_language_pango, samples_language_glass
    samples_braille


def load_glass():
    """Load eat glass samples. Currently does nothing."""
    from typeatlas.data.samples_language_glass import EAT_GLASS_ENGLISH, EAT_GLASS_SOURCE

    eat_glass = {}

    for key, value in eat_glass.items():
        if key not in main_samples.samples_regular:
            warnmsgf("No translation for %r, eating glass", key)
            add_sample(key, value,
                       english=EAT_GLASS_ENGLISH,
                       sources=[EAT_GLASS_SOURCE])


def load_nonfree():
    """Load pangram data whose licensing is unclear, and suspected to be
    non-free, but can be legally distributed with TypeAtlas for at least
    non-commercial purposes."""

    return

    try:
        from typeatlas.data.samples_language_nonfree \
            import hovercraft, HOVERCRAFT_ENGLISH, \
                   HOVERCRAFT_TRANSLATION_SOURCE, HOVERCRAFT_NOTE

    except ImportError:
        return

    for key, value in hovercraft.items():
        if key not in main_samples.samples_regular:
            warnmsgf("No translation for %r, using hovercraft", key)
            add_sample(key, value,
                       english=HOVERCRAFT_ENGLISH,
                       sources=[HOVERCRAFT_TRANSLATION_SOURCE],
                       note=HOVERCRAFT_NOTE)


load_samples()
#load_nonfree()
#load_glass()


def _filter_samples():
    """Remove unwanted samples."""
    for values in chain(main_samples.samples_long.values(),
                        main_samples.samples_regular.values()):
        while len(values) > 1 and values[0].prio < PRIO_DEFAULT:
            del values[0]

_filter_samples()
