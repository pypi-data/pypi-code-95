# -*- coding: utf-8 -*-
#
#    TypeAtlas Language Utilities
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

"""Language and locale utilities, including:
1. Gettext translate functions _, N_, U_, H_
2. ISO codes for languages, scripts and countries
3. Discovery of font samples for given languages or scripts (actually
   uses the samples module)
"""


import os.path
import errno
import locale
import functools
import gettext
import traceback
import re
import csv
import json
import shutil
import urllib.request
import urllib.parse
from html import escape as htesc
import typeatlas
from typeatlas import proginfo, charinfo
from typeatlas.util import OrderedSet, N_, U_, gettext_tag_regex, errmsgf
from typeatlas.util import generic_type
from typeatlas.samples import has_sample, get_sample, get_samples, ANY, ALL
from typeatlas.samples import available_language_codes, SampleInfo
from typeatlas.samples import LangListType, ScriptListType, ScriptType
from collections import namedtuple
from itertools import cycle, chain
from io import StringIO
try:
    from defusedxml import sax
    from xml.sax.handler import ContentHandler as _SaxContentHandler
except ImportError:
    sax = None
    _SaxContentHandler = object


SetOf = generic_type('Set')
SequenceOf = generic_type('Sequence')
IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')
TupleOf = generic_type('Tuple')
Literal = generic_type('Literal')
Optional = generic_type('Optional')

PathType = SequenceOf[str]
CharsetType = SetOf[int]


translations = gettext.NullTranslations()
has_translations = False

def _(s: str, suffix: str=None) -> str:
    """Translate the string into current locale. Any alphabetical prefix
    before a pipe is removed (e.g. "abc|")."""

    s = getattr(s, 'gettext_msgid', s)

    if not s:
        return s

    s = translations.gettext(s)
    s = gettext_tag_regex.sub('', s, 1)

    if suffix is not None:
        s += suffix

    return s


def H_(s: str, suffix: str=None) -> str:
    """Translate the string into current locale's language, and escape any
    HTML."""
    return htesc(_(s, suffix))


ISO_3166_1_XML_NAME = 'iso_3166'
ISO_3166_2_XML_NAME = 'iso_3166_2'

ISO_639_XML_NAME = 'iso_639'
ISO_639_3_XML_NAME = 'iso_639_3'
ISO_639_5_XML_NAME = 'iso_639_5'

ISO_15924_XML_NAME = 'iso_15924'

ISO_3166_1_JSON_NAME = 'iso_3166-1'
ISO_639_2_JSON_NAME = 'iso_639-2'
ISO_639_3_JSON_NAME = 'iso_639-3'
ISO_639_5_JSON_NAME = 'iso_639-5'

ISO_15924_JSON_NAME = 'iso_15924'

ISO_3166_TZDATA_FILENAME = 'iso3166.tab'

ISO_CODES_JSON_DOWNLOAD_BASE = 'https://anonscm.debian.org/cgit/pkg-isocodes/iso-codes.git/plain/data/'

ISO_CODES_JSON_CACHE_PATH = os.path.join(proginfo.CACHE_DIR,
                                         'iso-codes', 'json')

ISO_CODES_XML_SEARCH_PATH = ['/usr/share/xml/iso-codes']
ISO_CODES_JSON_SEARCH_PATH = [ISO_CODES_JSON_CACHE_PATH,
                              '/usr/share/iso-codes/json']
TZDATA_SEARCH_PATH = ['/usr/share/zoneinfo']


ENGLISH_NAME = object()
NATIVE_NAME = object()
LOCALE_NAME = object()
AUTO_LOCALE_NAME = object()


# TODO: Move en before extra locales?

LanguageInfo = namedtuple('LanguageInfo',
                            ['iso_names', 'native_names',
                             'code_639_1', 'code_639_2t',
                             'code_639_2b', 'code_639_3', 'code_639_5',
                             'family', 'scope', 'type',
                             'other_names', 'notes'])

language_info_639_1 = {}
language_info_639_2t = {}
language_info_639_2b = {}
language_info_639_3 = {}
language_info_639_5 = {}
language_info = {}

language_info_rfc3066 = {}

def _fill_languages():
    """Initialize language information and fill it in the mappings above."""
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    langfn = os.path.join(root, 'languages_iso639_1.tsv')
    lines = []

    for line in open(langfn, 'rt', encoding='utf8'):
        if line.startswith(';;'):
            continue
        lines.append(line)

    file = StringIO(''.join(lines))

    for row in csv.DictReader(file, delimiter='\t'):
        info = LanguageInfo(list(map(str.strip,
                                     row['ISO language name'].split(','))),
                            list(map(str.strip,
                                     re.split(r'[/;,(]', row['Native name']))),
                            row['639-1'], row['639-2/T'],
                            row['639-2/B'], row['639-3'], '',
                            row['Language family'], '', '', (),
                            row['Notes'])

        language_info_639_1[info.code_639_1] = info
        language_info_639_2t[info.code_639_2t] = info
        language_info_639_2b[info.code_639_2b] = info
        language_info_639_3[info.code_639_3] = info


    langfn = os.path.join(root, 'languages_iso639_2.tsv')
    lines = []

    for line in open(langfn, 'rt', encoding='utf8'):
        if line.startswith(';;'):
            continue
        lines.append(line)

    file = StringIO(''.join(lines))

    for row in csv.DictReader(file, delimiter='\t'):
        term_code, sep, bib_code = row['639-2'].partition('/')
        term_code = term_code.strip()
        if not sep:
            bib_code = term_code
        else:
            bib_code = bib_code.strip().rstrip('*')

        info = LanguageInfo(list(map(str.strip,
                                     row['ISO language name(s)'].split(';'))),
                            list(map(str.strip,
                                     re.split(r'[/;(]', row['Native name(s)']))),
                            row['639-1'], term_code,
                            bib_code, row['639-3'], row['639-5'],
                            '', row['Scope'], row['Type'],
                            list(map(str.strip,
                                     (row['Other name(s)'] or '').split(';'))),
                            '')

        old_info = None
        if info.code_639_1:
            old_info = language_info_639_1.get(info.code_639_1)

        if old_info is not None:
            language_info_639_1[info.code_639_1] = old_info._replace(
                    scope=info.scope, type=info.type,
                    code_639_5=info.code_639_5,
                    other_names=info.other_names)

        if old_info is None and info.code_639_2t:
            old_info = language_info_639_2t.get(info.code_639_2t)
        if old_info is None and info.code_639_2b:
            old_info = language_info_639_2b.get(info.code_639_2b)
        if old_info is not None:
            info = info._replace(notes=old_info.notes, family=old_info.family)

        if info.code_639_1 and info.code_639_1 not in language_info_639_1:
            language_info_639_1[info.code_639_1] = info

        language_info_639_2t[info.code_639_2t] = info
        language_info_639_2b[info.code_639_2b] = info
        language_info_639_3[info.code_639_3] = info
        language_info_639_5[info.code_639_5] = info

    language_info.update(language_info_639_5)
    language_info.update(language_info_639_3)
    language_info.update(language_info_639_2b)
    language_info.update(language_info_639_2t)
    language_info.update(language_info_639_1)

    # RFC 3066 says to only use the 2-letter code if available,
    # but no issue if we lookup by all the 3-letter codes.
    language_info_rfc3066.update(language_info_639_2t)
    language_info_rfc3066.update(language_info_639_1)


_fill_languages()


locales = set('''
aa_DJ aa_ER aa_ET af_ZA ak_GH am_ET an_ES anp_IN ar_AE ar_BH ar_DZ ar_EG ar_IN 
ar_IQ ar_JO ar_KW ar_LB ar_LY ar_MA ar_OM ar_QA ar_SA ar_SD ar_SS ar_SY ar_TN 
ar_YE as_IN ast_ES ayc_PE az_AZ be_BY bem_ZM ber_DZ ber_MA bg_BG bho_IN bn_BD 
bn_IN bo_CN bo_IN br_FR brx_IN bs_BA byn_ER ca_AD ca_ES ca_FR ca_IT cmn_TW 
crh_UA csb_PL cs_CZ cv_RU cy_GB da_DK de_AT de_BE de_CH de_DE de_LI de_LU doi_IN 
dv_MV dz_BT el_CY el_GR en_AG en_AU en_BW en_CA en_DK en_GB en_HK en_IE en_IN 
en_NG en_NZ en_PH en_SG en_US en_ZA en_ZM en_ZW eo es_AR es_BO es_CL es_CO es_CR 
es_CU es_DO es_EC es_ES es_GT es_HN es_MX es_NI es_PA es_PE es_PR es_PY es_SV 
es_US es_UY es_VE et_EE eu_ES eu_FR fa_IR ff_SN fi_FI fil_PH fo_FO fr_BE fr_CA 
fr_CH fr_FR fr_LU fur_IT fy_DE fy_NL ga_IE gd_GB gez_ER gez_ET gl_ES gu_IN gv_GB 
hak_TW ha_NG he_IL hi_IN hne_IN hr_HR hsb_DE ht_HT hu_HU hy_AM ia ia_FR id_ID 
ig_NG ik_CA is_IS it_CH it_IT iu_CA iw_IL ja_JP ka_GE kk_KZ kl_GL km_KH kn_IN 
kok_IN ko_KR ks_IN ku_TR kw_GB ky_KG lb_LU lg_UG li_BE lij_IT li_NL lo_LA lt_LT 
lv_LV lzh_TW mag_IN mai_IN mg_MG mhr_RU mi_NZ mk_MK ml_IN mni_IN mn_MN mr_IN 
ms_MY mt_MT my_MM nan_TW nb_NO nds_DE nds_NL ne_NP nhn_MX niu_NU niu_NZ nl_AW 
nl_BE nl_NL nn_NO nr_ZA nso_ZA oc_FR om_ET om_KE or_IN os_RU pa_IN pap_AN pap_AW 
pap_CW pa_PK pl_PL ps_AF pt_BR pt_PT quz_PE ro_RO ru_RU ru_UA rw_RW sa_IN sat_IN 
sc_IT sd_IN se_NO shs_CA sid_ET si_LK sk_SK sl_SI so_DJ so_ET so_KE so_SO sq_AL 
sq_MK sr_ME sr_RS ss_ZA st_ZA sv_FI sv_SE sw_KE sw_TZ szl_PL ta_IN ta_LK te_IN 
tg_TJ the_NP th_TH ti_ER ti_ET tig_ER tk_TM tl_PH tn_ZA tr_CY tr_TR ts_ZA tt_RU 
ug_CN uk_UA unm_US ur_IN ur_PK uz_UZ ve_ZA vi_VN wa_BE wae_CH wal_ET wo_SN xh_ZA 
yi_US yo_NG yue_HK zh_CN zh_HK zh_SG zh_TW zu_ZA
'''.split())

try:
    locale.setlocale(locale.LC_MESSAGES, '')
except locale.Error as exc:
    errmsgf("Failed to set locale (LC_MESSAGES): %s: %s",
            type(exc).__name__, exc)
    del exc

deflocale, defencoding = locale.getdefaultlocale()
curlocale, curencoding = locale.getlocale()

_messagelang, _messageencoding = locale.getlocale(locale.LC_MESSAGES) or \
                                 (deflocale, defencoding)

def textlang() -> str:
    """Return the current text language"""
    return _messagelang


langorder = OrderedSet()

if curlocale:
    locales.add(curlocale)
    langorder.add(curlocale.lower().replace('_', '-'))
    langorder.add(curlocale.partition('_')[0].lower())
if deflocale:
    locales.add(deflocale)
    langorder.add(deflocale.lower().replace('_', '-'))
    langorder.add(deflocale.partition('_')[0].lower())

varlocales = list(loc.partition('@')[0].partition('.')[0]
                  for variable in ['LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG']
                  for loc in os.environ.get(variable, '').split(':'))


locales.update(varlocales)
langorder.update(loc.lower().replace('_', '-') for loc in varlocales)
langorder.update(loc.partition('_')[0].lower() for loc in varlocales)


def _autofill_extra_locales():
    """On GNU/Linux and other potential Unix-like operating systems,
    do some detection of known extra locales."""
    if os.path.exists('/etc/locale.gen'):
        for line in sorted(open('/etc/locale.gen'),
                        key=lambda line: line.startswith('en')):
            line = line.strip()
            if line.startswith('#') or not line:
                line = line.replace('#', '').strip()
                if line:
                    loc = line.split()[0]
                    if re.match(r'^[a-z]+_[A-Z]+(?:@|$)', loc):
                        locales.add(loc)
                continue
            loc = line.split()[0]
            locales.add(loc)
            langorder.add(loc.lower().replace('_', '-'))
            langorder.add(loc.partition('_')[0].lower())


langorder.add('en-us')
langorder.add('en')
langimportant = OrderedSet(langorder)
_autofill_extra_locales()


countrylangs = {}
langcountries = {}
countryguess = {'ar': 'arableague', 'en': 'gb'}
langcountrycount = {}

def _autofill_language_guesses():
    """Process the locales and try language x locale counterparts and
    try to decide which flag goes to which language. Uh-oh."""
    for loc in locales:
        lang, sep, country = loc.lower().partition('_')
        if not sep:
            continue

        countrylangs.setdefault(country, []).append(lang)
        langcountries.setdefault(lang, []).append(country)

        # We show courage. We assume that if the country and language code match,
        # the flag of the country flag can represent the language.
        if lang == country:
            countryguess[lang] = country

    for lang, countries in langcountries.items():
        # If only one country speaks that language, and the locale list isn't
        # horribly incomplete, then we could use that country's flag. Possibly.
        # The code checking the second condition is being worked on.
        if len(countries) == 1:
            countryguess[lang] = countries[0]


    for country, langs in countrylangs.items():
        if len(langs) == 1:
            langcountrycount[langs[0]] = \
                langcountrycount.setdefault(langs[0], 0) + 1

    for country, langs in countrylangs.items():
        # If only one country exists such that that a certain language is
        # the only language spoken in the country, according to our database,
        # then make a leap of faith and assume that's a good choice.
        if len(langs) == 1:
            if langs[0] in countryguess:
                continue
            if langcountrycount.get(langs[0]) != 1:
                continue
            countryguess[langs[0]] = country

_autofill_language_guesses()


class _LangXmlHandler(_SaxContentHandler):

    """Parser for XML language files on Unix-like OS. Those are
    deprecated, we are asked to use JSON instead. Whatever."""

    def __init__(self, langdb: 'LanguageDatabase'):
        self.langdb = langdb

    def startElement(self, name, attrs):
        method = getattr(self, 'handle_' + name, None)
        if method is not None:
            method(attrs)

    def handle_iso_639_entry(self, attrs):
        name = attrs.get('name')
        if not name:
            return

        names = tuple(s.strip() for s in name.split(';'))

        for code in [attrs.get('iso_639_1_code'),
                     attrs.get('iso_639_2T_code'),
                     attrs.get('iso_639_2B_code')]:
            if code:
                self.langdb.language_names[code] = names

    def handle_iso_639_3_entry(self, attrs):
        name = attrs.get('reference_name')
        if not name:
            return

        names = tuple(s.strip() for s in name.split(';'))

        code = attrs.get('id')
        if code:
            self.langdb.language_names[code] = names

    def handle_iso_3166_entry(self, attrs):
        name = attrs.get('name')
        if not name:
            return

        for code in [attrs.get('alpha_2_code'),
                     attrs.get('alpha_3_code')]:
            if code:
                self.langdb.country_names[code] = name

    def handle_iso_15924_entry(self, attrs):
        name = attrs.get('name')
        if not name:
            return

        alphacode = attrs.get('alpha_4_code')
        if not alphacode:
            return

        self.langdb.script_names[alphacode] = name

        numcode = attrs.get('numeric_code')

        if numcode and numcode.isdigit() and numcode.isascii():
            numcode = int(numcode)
            self.langdb.script_numcode[alphacode] = numcode
            self.langdb.script_by_numcode[numcode] = alphacode


class LanguageDatabase(object):

    instance = None
    
    def __init__(self,
                 iso_codes_json_search_path: PathType=ISO_CODES_JSON_SEARCH_PATH,
                 iso_codes_xml_search_path: PathType=ISO_CODES_XML_SEARCH_PATH,
                 tzdata_search_path: PathType=TZDATA_SEARCH_PATH,
                 preferred_name: str=LOCALE_NAME):

        self.populated = False

        self.iso_codes_json_search_path = list(iso_codes_json_search_path)
        self.iso_codes_xml_search_path = list(iso_codes_xml_search_path)
        self.tzdata_search_path = list(tzdata_search_path)
        self.preferred_name = preferred_name

        self.language_names = {}
        self.language_native_names = {}

        self.country_names = {}

        self.script_names = {}
        self.script_numcode = {}
        self.script_by_numcode = {}

        self.iso_3166_trans = gettext.translation(ISO_3166_1_XML_NAME,
                                                  fallback=True)
        self.iso_639_trans = gettext.translation(ISO_639_XML_NAME,
                                                 fallback=True)
        self.iso_15924_trans = gettext.translation(ISO_15924_XML_NAME,
                                                   fallback=True)

        self.lang_prio = {lang: i for i, lang in enumerate(langorder)}

        for filename in [ISO_639_3_XML_NAME, ISO_639_5_XML_NAME]:
            try:
                self.iso_639_trans.add_fallback(gettext.translation(filename))
            except EnvironmentError as exc:
                if exc.errno != errno.ENOENT:
                    raise

    @classmethod
    def get_instance(cls, populated: bool=False) -> 'LanguageDatabase':
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

    def downloadables(self) -> IteratorOf[TupleOf[str, str]]:
        """Return pairs of URL, destination path for all the files that
        need to be downloaded for this class to function with latest
        ISO codes."""
        if not os.path.exists(ISO_CODES_JSON_CACHE_PATH):
            os.makedirs(ISO_CODES_JSON_CACHE_PATH)
        for filename in [ISO_639_2_JSON_NAME, ISO_639_3_JSON_NAME,
                         ISO_3166_1_JSON_NAME, ISO_15924_JSON_NAME]:
            url = urllib.parse.urljoin(ISO_CODES_JSON_DOWNLOAD_BASE, filename)
            destpath = os.path.join(ISO_CODES_JSON_CACHE_PATH, filename)
            yield url, destpath

    def download(self):
        """Download the latest ISO codes."""
        for url, destpath in self.downloadables():
            with urllib.request.urlopen(url) as src:
                with open(destpath, 'wb') as dst:
                    shutil.copyfileobj(src, dst)

    def ensure_populated(self, download: bool=False):
        """If ISO codes are not loaded and parsed, parse them. Optionally,
        download them if download=True is passed."""
        if not self.populated:
            if download:
                self.download()
            self.populate()

    def populate(self):
        """Parse the ISO codes, whether downloaded of found on system."""
        for lang, info in language_info.items():
            if not lang:
                continue

            lang = lang.lower()

            if info.iso_names and info.iso_names[0]: 
                self.language_names[lang] = info.iso_names
            if info.native_names and info.native_names[0]:
                self.language_native_names[lang] = info.native_names

        for dirname in self.tzdata_search_path:
            filepath = os.path.join(dirname, ISO_3166_TZDATA_FILENAME)
            if not os.access(filepath, os.R_OK):
                continue

            with open(filepath, 'rt', encoding='utf8') as file:
                for line in file:
                    line, sep, removed = line.partition('#')
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        code, name = line.split(None, 1)
                    except ValueError:
                        continue
                    code = code.upper()
                    self.country_names[code] = name
                break

        for dirname in self.iso_codes_xml_search_path:
            for filename in [ISO_639_XML_NAME, ISO_639_3_XML_NAME,
                             ISO_3166_1_XML_NAME, ISO_15924_XML_NAME]:
                filepath = os.path.join(dirname, filename + '.xml')
                if sax is not None and os.access(filepath, os.R_OK):
                    try:
                        sax.parse(filepath, _LangXmlHandler(self))
                    except Exception:
                        traceback.print_exc()

        def update_lang_dict(d, records, name_key='name', split=True):
            for record in records:
                name = record.get(name_key)
                if not name:
                    continue
                if split:
                    name = tuple(s.strip() for s in name.split(';'))
                for key in ['alpha_2', 'alpha_3']:
                    code = record.get(key)
                    if code:
                        d[code] = name

        for dirname in self.iso_codes_json_search_path:
            filepath = os.path.join(dirname, ISO_639_2_JSON_NAME + '.json')
            if os.access(filepath, os.R_OK):
                with open(filepath) as file:
                    data = json.load(file)
                update_lang_dict(self.language_names, data['639-2'])

            filepath = os.path.join(dirname, ISO_639_3_JSON_NAME + '.json')
            if os.access(filepath, os.R_OK):
                with open(filepath) as file:
                    data = json.load(file)
                update_lang_dict(self.language_names, data['639-3'])

            filepath = os.path.join(dirname, ISO_3166_1_JSON_NAME + '.json')
            if os.access(filepath, os.R_OK):
                with open(filepath) as file:
                    data = json.load(file)
                update_lang_dict(self.country_names, data['3166-1'],
                                 split=False)

            filepath = os.path.join(dirname, ISO_15924_JSON_NAME + '.json')
            if os.access(filepath, os.R_OK):
                with open(filepath) as file:
                    data = json.load(file)

                for record in data['15924']:
                    recname = record.get('name')
                    recalpha = record.get('alpha_4')
                    recnum = record.get('numeric')

                    if not recname or not recalpha:
                        continue

                    self.script_names[recalpha] = recname
                    if recnum and (isinstance(recnum, int) or
                                   (recnum.isdigit() and recnum.isascii())):
                        self.script_numcode[recalpha] = recnum
                        self.script_by_numcode[recnum] = recalpha

        self.populated = True

    def language_name(self, code: str, which=None) -> str:
        """Get the English, localised or native name for a language."""
        if which is None:
            which = self.preferred_name

        if which is AUTO_LOCALE_NAME:
            which = LOCALE_NAME if has_translations else ENGLISH_NAME

        if '_' in code:
            code, sep, country = code.partition('_')
        else:
            code, sep, country = code.partition('-')

        if sep:
            return "%s (%s)" % (self.language_name(code, which),
                                self.country_name(country, which))

        code = code.lower()

        if which is NATIVE_NAME:
            result = self.language_native_names.get(code)
            if result is not None:
                return result[0]
        
        iso_name = self.language_names.get(code, (code, ))[0]

        if which is LOCALE_NAME:
            if not iso_name:
                return ''
            return self.iso_639_trans.gettext(iso_name)
                        
        return iso_name

    def country_name(self, code: str, which=None) -> str:
        """Get the English or localised name for a country."""
        if which is None:
            which = self.preferred_name

        if which is AUTO_LOCALE_NAME:
            which = LOCALE_NAME if has_translations else ENGLISH_NAME

        code = code.upper()

        iso_name = self.country_names.get(code, code)

        if which is not ENGLISH_NAME:
            if not iso_name:
                return ''
            return self.iso_3166_trans.gettext(iso_name)

        return iso_name

    def script_name(self, code: str, which=None,
                          chardb: 'typeatlas.charinfo.CharacterDatabase'=None
                          ) -> str:
        """Get the English or localised name for a script code.

        If chardb is passed, you can also pass the unicode name."""
        if which is None:
            which = self.preferred_name

        if code is ANY or code is ALL or code is None:
            return _('script|Unknown')

        if which is AUTO_LOCALE_NAME:
            which = LOCALE_NAME if has_translations else ENGLISH_NAME

        if isinstance(code, int) or (isinstance(code, str) and
                                     code.isdigit() and code.isascii()):
            code = self.script_by_numcode.get(int(code), str(code))

        elif chardb is not None:
            unicode_aliases = chardb.value_aliases['sc']
            if code in unicode_aliases:
                if code == 'Common':
                    return _('script|Common') \
                          if which is ENGLISH_NAME else code

                elif code == 'Unknown':
                    return _('script|Unknown') \
                           if which is ENGLISH_NAME else code

                elif code == 'Inherited':
                    return _('script|Inherited') \
                           if which is ENGLISH_NAME else code

                code = unicode_aliases[code]
            else:
                code = code.replace('_', ' ')

        iso_name = self.script_names.get(code, code)

        if which is not ENGLISH_NAME:
            if not iso_name:
                return ''
            return self.iso_15924_trans.gettext(iso_name)

        return iso_name

    def samples_langs(self, langs: LangListType, alternative: int=0,
                            long: bool=False, charset: SetOf[int]=None,
                            **kwargs) -> IteratorOf[SampleInfo]:
        """Yield language samples for font testing. They can be selected by
        a list of languages (or ANY if unknown), or font-supported
        charset (a set of unicode codepoints).

        If a charset is provided, the samples are filtered to only include
        those fully supported by the font.

        You can also provide all arguments supported by get_samples(),
        such as exact, fallbacks, script, scripts. See the documentation there.

        If multiple samples are supported for the same language, you can
        pass alternative=1, 2, 3, etc. to get an alternative one. This can
        be used to vary the result to e.g. build longer text.
        """
        if langs is ANY:
            langs = available_language_codes(long=long)

        langcodes = self.sort_languages(langs)
        result = get_samples(langcodes, exact=True, fallbacks=False, long=long,
                             alternative=alternative, **kwargs)
        if charset is not None:
            has_braille = charinfo.BRAILLE_RANGE <= charset

            result = (sample for sample in result
                      if all(ord(c) in charset for c in sample.text))

            if has_braille:
                prepend = []
                braille_sample = None
                for lang in chain(langorder):
                    if has_sample(lang, script='Brai', long=long):
                        braille_sample = get_sample(lang, script='Brai',
                                                    long=long,
                                                    alternative=alternative)
                        prepend.append(braille_sample)
                        break

                if braille_sample is not None:
                    #first_sample = next(result, None)
                    #prepend.insert(0, first_sample)
                    #result = chain(iter(prepend), result)
                    result = chain(result, [braille_sample])

        return result

    def samples_scripts(self, scripts: ScriptListType,
                              alternative: int=0, long: bool=False,
                              charset: SetOf[int]=None,
                              **kwargs) -> IteratorOf[SampleInfo]:
        """Like samples_langs(), but select by scripts."""

        # FIXME: Slow, this loops over all languages for the given scripts
        return self.samples_langs(ANY, alternative=alternative,
                                  long=long, charset=charset,
                                  scripts=scripts, **kwargs)

    def samples_font(self, font: 'typeatlas.fontlist.FontLike',
                           long: bool=False,
                           alternative: int=ANY) -> IteratorOf[SampleInfo]:
        """Get suitable samples for a given font."""
        if font.lang_unknown():
            langs = ANY
        else:
            langs = OrderedSet()
            for lang in font.lang:
                langs.add(lang)
                lang, sep, loc = lang.partition('-')
                if sep:
                    langs.add(lang)

        if alternative is ANY:
            if not font.scalable or not font.outline:
                alternative = 2
            elif not font.sfnt:
                alternative = 1
            else:
                alternative = 0

        return self.samples_langs(langs, alternative, long=long,
                                  charset=font.charset)

    def samples_font_intersection(self,
                                  fonts: 'IterableOf[typeatlas.fontlist.FontLike]',
                                  long: bool=False,
                                  alternative: int=ANY) -> IteratorOf[SampleInfo]:
        """Get suitable samples that cover an intersection of fonts."""
        known_langs = False
        common_langs = None
        common_charset = None
        charset_supported = True
        for font in fonts:
            if font.lang_unknown():
                continue
            known_langs = True

            langs = OrderedSet()
            for lang in font.lang:
                langs.add(lang)
                lang, sep, loc = lang.partition('-')
                if sep:
                    langs.add(lang)

            if not langs:
                continue

            if common_langs is None:
                common_langs = langs
            else:
                common_langs &= langs

            if font.charset is None:
                charset_supported = False
            elif common_charset is None:
                common_charset = font.charset
            else:
                common_charset = common_charset & font.charset

        if not common_langs:
            common_langs = []
        if not known_langs:
            common_langs = ANY

        if not charset_supported:
            common_charset = None

        if alternative is ANY:
            if not any(font.scalable or font.outline for font in fonts):
                alternative = 2
            elif not any(font.sfnt for font in fonts):
                alternative = 1
            else:
                alternative = 0

        return self.samples_langs(common_langs, alternative, long=long,
                                  charset=common_charset)

    def sample_texts_font(self, font: 'typeatlas.fontlist.FontLike'
                         ) -> IteratorOf[str]:
        """Get just the sample texts for a font."""
        return (sample.text for sample in self.samples_font(font))

    def sample_texts_font_intersection(
                        self, fonts: 'IterableOf[typeatlas.fontlist.FontLike]'
                        ) -> IteratorOf[str]:
        """Get just the sample texts usable for an intersection of fonts."""
        return (sample.text
                for sample in self.samples_font_intersection(fonts))

    def sample_language(self, lang: str, *args, **kwargs) -> Optional[SampleInfo]:
        """Get a sample for a given language."""
        return get_sample(lang, *args, **kwargs)

    def sample_text_language(self, *args, **kwargs) -> Optional[str]:
        """Get the sample text for a given language."""
        sample = self.sample_language(*args, **kwargs)
        if sample is not None:
            return sample.text
        return None

    def sample_text_complex(self, lang: str,
                                  script: ScriptType=ALL,
                                  scripts: ScriptListType=None,
                                  min_len: int=2500, max_len: int=8500,
                                  paragraphs: SequenceOf[int]=[100, 400, 800, 500],
                                  titlesize: int=24, subtitlesize: int=40,
                                  extra: SequenceOf[str]=[],
                                  chardb: 'typeatlas.charinfo.CharacterDatabase'=None
                                  ) -> dict:
        """Generate more complex multi-paragraph sample for a language.

        Return a dictionary containing 'title', 'subtitle' and 'text'
        """
        paragraph_text = [[]]
        seen = set()

        title = ''
        subtitle = ''
        length = 0
        paragraph_length = 0
        use_spaces = False

        samples = self.samples_langs(langs=ANY if lang is ANY else [lang],
                                     script=script, scripts=scripts,
                                     alternative=ALL)
        sample_texts = chain(extra or (),
                             (sample.text for sample in samples))

        for i, sample_text in cycle(enumerate(sample_texts)):
            if ' ' in sample_text:
                use_spaces = True

            if i in seen:
                limit = min_len
            else:
                limit = max_len

            if length > limit:
                if not title:
                    title = sample_text
                    continue
                elif not subtitle:
                    subtitle = sample_text
                    continue
                else:
                    break

            size = paragraphs[(len(paragraph_text) - 1) % len(paragraphs)]
            if paragraph_length > size:
                paragraph_text.append([])
                paragraph_length = 0

            seen.add(i)
            paragraph_text[-1].append(sample_text)
            length += len(sample_text)
            paragraph_length += len(sample_text)

        sep = ' ' if use_spaces else ''
        text = '\n\n'.join(sep.join(paragraph) for paragraph in paragraph_text)
        title = excerpt(title, titlesize, chardb=chardb)
        subtitle = excerpt(subtitle, subtitlesize, chardb=chardb)

        return dict(text=text, title=title, subtitle=subtitle)

    def languages_with_samples(self, languages: IterableOf[str],
                                     sort: bool=True,
                                     *args, **kwargs) -> IteratorOf[str]:
        """Yield languages that have samples.

        Languages are sorted unless sort=False is passed. The remainder
        arguments are passed to LanguageSamples.has_sample(), see the
        documentation there or in get_sample().
        """

        if sort:
            languages = self.sort_languages(languages)
        for lang in languages:
            if has_sample(lang, *args, **kwargs):
                yield lang

    def sort_languages(self, languages: IterableOf[str]) -> SequenceOf[str]:
        """Do a loose sort of the languages by the priority as detected
        on the system."""
        return sorted(languages,
                      key=lambda lang: (self.lang_prio.get(lang, 99999999),
                                                           lang))

    def guess_country_flag(self, lang: str) -> Optional[str]:
        """Guess the flag for the given languages. Languages don't have flags,
        so expect surprising results."""
        lang = lang.lower()
        if '-' in lang:
            return lang.rpartition('-')[2]
        return countryguess.get(lang)


def filter_samples(samples: IterableOf[SampleInfo],
                   one_per_script: bool=False,
                   keep_langs: SetOf[str]=langimportant):

    """Filter samples. If one_per_script=True is passed,
    only one sample per script is displayed. You can define
    which languages to keep even if we already got a sample for this
    script. By default, those would be the important languages detected
    on the system."""
    scripts = set()

    for sample in samples:
        if one_per_script:
            if sample.script in scripts and sample.code not in keep_langs:
                continue
            scripts.add(sample.script)
        yield sample


def excerpt(phrase: str, approxlen: int=64, *,
            spaced: bool=None, japanese: bool=None,
            chardb: 'typeatlas.charinfo.CharacterDatabase'=None) -> str:
    """Return a short excerpt from the given phrase, with the specified
    approximate length. It tries to detect spaces when splitting, and
    treat Japanese text sanely, though it will probably fail.

    You can control that behaviour with spaced=True/False, japanese=True/False.
    """
    try:
        import unicodedata
    except ImportError:
        unicodedata = None

    scripts = {}

    if spaced is None:
        spaced = ' ' in phrase

    elif japanese is None and chardb is not None:
        if (phrase and
            chardb.find_script_code(ord(phrase[0]))
                    in ['Hira', 'Kana', 'Hani']):

                scripts = {c: chardb.find_script_code(ord(c)) for c in phrase}
                scriptset = set(scripts.values())
                japanese = 'Hira' in scriptset or 'Kana' in scriptset

    elif japanese and chardb is not None:
        scripts = {c: chardb.find_script_code(ord(c)) for c in phrase}

    result = []
    length = 0
    lastchar = ''

    for i, char in enumerate(phrase):
        code = ord(char)

        if chardb is None:
            length += 1
        else:
            length += chardb.guess_width(code, 0)

        if length >= approxlen:
            if spaced:
                if char == ' ':
                    break

            elif japanese:
                script = scripts.get(char)
                if script == 'Hani':
                    if scripts.get(lastchar) in ['Hira', 'Kana']:
                        break
                elif script not in ['Hira', 'Kana']:
                    break

            else:
                if length >= approxlen:
                    result.append(char)
                    break

        result.append(char)
        lastchar = char

    return ''.join(result)


i18n_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'i18n')
mocache_root = os.path.join(proginfo.CACHE_DIR, 'i18n')


def install_locales(languages: IterableOf[str]=None):
    """Set up locales, to be executed at start of TypeAtlas."""
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error as exc:
        errmsgf("Failed to set locale (LC_ALL): %s: %s", type(exc).__name__, exc)

    if languages is None:
        # FIXME: Use locale through textlang() instead of crawling the variables again?
        for variable in ['LC_ALL', 'LC_MESSAGES', 'LANG', 'LANGUAGE']:
            value = os.environ.get(variable)
            if value:
                languages = OrderedSet(value.split(':'))
                break

    existing = []

    maker = TranslationMaker()
    for lang in languages:
        if maker.exists(lang):
            maker.autocompile(lang)
            existing.append(maker.compiled_path(lang))

    global translations, has_translations

    if not existing:
        translations = gettext.NullTranslations()
        return

    translations = None
    for path in existing:
        if translations is None:
            translations = gettext.GNUTranslations(open(path, 'rb'))
        else:
            translations.add_fallback(gettext.GNUTranslations(open(path, 'rb')))
        has_translations = True


class TranslationMaker(object):

    """A translation loader that can load them directly from source and
    cache the compiled gettext messages in e.g. ~/.cache/typeatlas.
    """

    def autocompile(self, loc: str, _exact_match: bool=False):
        """If there is a source translation for the given locale, but it is
        not compiled, automatically compile it."""
        if not _exact_match:
            loc = locale.normalize(loc).partition('@')[0].partition('.')[0]

        source = os.path.join(i18n_root, loc + '.po')
        compiled = os.path.join(mocache_root, loc + '.mo')

        if not os.path.exists(source):
            if os.path.exists(compiled):
                return
            langcode, sep, loccode = loc.partition('_')
            if sep:
                self.autocompile(langcode, _exact_match=True)
                return
            raise LookupError("no such translation %r" % (loc, ))

        if (os.path.exists(compiled) and
            os.stat(compiled).st_mtime >= os.stat(source).st_mtime):
                return

        try:
            os.makedirs(os.path.dirname(compiled))
        except EnvironmentError as exc:
            if exc.errno != errno.EEXIST:
                raise

        from typeatlas.foreign import msgfmt
        msgfmt.MESSAGES.clear()
        msgfmt.make(source, compiled)

    def exists(self, loc: str, _exact_match: bool=False) -> bool:
        """Return True if the compiled translation for the given language
        exists."""

        if not _exact_match:
            loc = locale.normalize(loc).partition('@')[0].partition('.')[0]

        source = os.path.join(i18n_root, loc + '.po')
        compiled = os.path.join(mocache_root, loc + '.mo')

        if os.path.exists(source):
            return True
        if os.path.exists(compiled):
            return True

        if not _exact_match:
            langcode, sep, loccode = loc.partition('_')
            if sep:
                return self.exists(langcode, _exact_match=True)

        return False

    def compiled_path(self, loc: str, _exact_match: bool=False) -> str:
        """Get the path to the compiled gettext translation for a given
        language / locale. You can call autocompile() before this to
        ensure a cached version exists. Raises LookupError if not found."""
        if not _exact_match:
            loc = locale.normalize(loc).partition('@')[0].partition('.')[0]

        if self.exists(loc, _exact_match=True):
            return os.path.join(mocache_root, loc + '.mo')

        if not _exact_match:
            langcode, sep, loccode = loc.partition('_')
            if sep:
                return self.compiled_path(langcode, _exact_match=True)

        raise LookupError("no compiled translation found for %r" % (loc, ))

