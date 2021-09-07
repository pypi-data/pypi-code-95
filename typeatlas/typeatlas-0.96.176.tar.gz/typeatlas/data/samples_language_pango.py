# coding: utf-8

#  TypeAtlas Collection of International Sample Texts: Pangrams and others,
#  extracted from LGPL programs.
#
#     Phrases selected 2018 by Milko Krachounov, from the following sources:
#     Pango Language Sample Table:
#
#     Written, collected, and Copyrighted (C) by Pango developers, and all those
#     who contributed phrases in bug reports and others, and/or their sources.
#       Sources copyrighted by various third parties attributed below
#              (Wikipedia contributors, Wikiquote contributors, StackExchange
#               contributors, etc.)
#
#  Part of TypeAtlas. TypeAtlas is free software.
#
#  Pango, the source of these phrases, is distributed under the following,
#  terms (which is expected to the be the most restrictive terms this could be
#  redistributed under, if deemed copyrightable):
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Library General Public
#  License as published by the Free Software Foundation; either
#  version 2 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.> See the GNU
#  Library General Public License for more details.
#
#  You should have received a copy of the GNU Library General Public
#  License along with this library; if not, write to the
#  Free Software Foundation, Inc., 59 Temple Place - Suite 330,
#  Boston, MA 02111-1307, USA.
#
###########################################################################
#
#   2) Sources, their copyright and licenses:
#      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# These sample texts are acquired from multiple sources. While the sources
# are not generally copied in substantial form, the copyright and license to
# these sources is cited here. These include:
#
#  * Pango Language Sample Table (pango-language-sample-table.h)
#     Written, collected, and Copyrighted (C) by Pango developers, and all those
#     who contributed phrases in bug reports and others, and/or their sources.
#
#     Most of the code of Pango is licensed under the terms of the
#     GNU Lesser Public License (LGPL). (aka Library GPL; Most files are
#     Version 2 or later, but the language sample table doesn't carry explicit
#     notice, however we didn't copy the table itself, so it's not clear that
#     its copyright notice has any direct relevance to copying this file)
#
#     Only several (eight) phrases exclusively taken from Pango without being
#     found in other sources. Six of these phrases are also included in the
#     Kermit Project mentioned below.
#
#  * Eat Glass translations from Kermit Project. Written and copyrighted by the
#    contributors, Frank da Cruz, the Kermit Project, Columbia University and
#    Ethan Mollick
#
#    Copy of the UTF-8 sampler: <http://www.columbia.edu/~fdc/utf8.html>
#
#    No notice on copyright and copying was found, but the collection
#    was not copied here. Only several (eight, including the English) individual
#    phrases, contributed by third parties, were included. That includes
#    six phrases also included by Pango. The six Pango phrases are in this file.

# Any contributions to this file by Milko Krachounov are quintuple-licensed under GPL 3,
#      LGPL 2, MIT/X11, CC-BY-SA 3.0 and CC-BY-SA 4.0 (just to be on the safe
#      side). (If this is too restrictive, I can be persuaded to grant more).
#      See the notice in samples_language.py on the matter.


from typeatlas.samples import add_sample, use_fallback, use_display_scripts
from typeatlas.samples import PHRASE, PANGRAM, PANGRAM_PARTIAL_ACCENTS
from typeatlas.samples import PANGRAM_LIMITED_ACCENTS, PARTIAL_PANGRAM, PERFECT_PANGRAM
from typeatlas.samples import KOREAN_PANGRAM, KOREAN_CONSONANT_PANGRAM
from typeatlas.samples import YONG_CHARACTER, SYLLABLE_PANGRAM
from typeatlas.samples import PRIO_PREFER, PRIO_WITHHOLD

from typeatlas.data.samples_language_glass import EAT_GLASS_ENGLISH, EAT_GLASS_SOURCE
from typeatlas.data.samples_language import PANGO


# This should be first
# Original phrase, which has now been changed
# from '«الا یا اَیُّها السّاقی! اَدِرْ کَأساً وَ ناوِلْهٰا!» که عشق آسان نمود اوّل، ولی افتاد مشکل‌ها!'
# to   '«الا یا اَیُّها السّاقی! اَدِرْ کَأساً وَ ناوِلْها!» که عشق آسان نمود اوّل، ولی افتاد مشکل‌ها!'
add_sample('fa',  '«الا یا اَیُّها السّاقی! اَدِرْ کَأساً وَ ناوِلْها!» که عشق آسان نمود اوّل، ولی افتاد مشکل‌ها!',
           sources=[PANGO, "Pango's Persian sample text is not good <https://bugzilla.gnome.org/show_bug.cgi?id=548730>"],
           script='Arab', origin='Behdad Esfahbod',
           english='“Come, oh wine cupbearer! Give the cup around and pass it along!” The easy love came first, but then the problems came.',
           translit='''«ala aa aَauha alsaqa! aَdِrْ keَasaan wَ nawِlْha!» keh 'eshq asan nmwd awl, wla aftad mshkel‌ha!''',
           langpos=0, langscriptpos=0)

add_sample('hi', "नहीं नजर किसी की बुरी नहीं किसी का मुँह काला जो करे सो उपर वाला।",
           sources=[PANGO, "Correction to the sample string for Hindi in pango-language-sample-table.h <https://bugzilla.gnome.org/show_bug.cgi?id=549532>"],
           script='Deva', origin='G Karunakar',
           english="It's not in the sight or the face, but its all in god's grace.",
           translit='nahin najar kisee kee buree nahin kisee ka munh kaala jo kare so upar vaala.',
           langpos=0, langscriptpos=0)


# This should be third
add_sample('zh', '我能吞下玻璃而不伤身体。',
           type=PHRASE, script='Hans',
           english=EAT_GLASS_ENGLISH,
           sources=[PANGO, EAT_GLASS_SOURCE],
           origin='Jack Soo, Wong Pui Lam',
           langpos=2, langscriptpos=2)


# This should be first
add_sample('kw',
           "Mý a yl dybry gwéder hag éf ny wra ow ankenya.",
           type=PHRASE, script='Latn',
           english=EAT_GLASS_ENGLISH,
           sources=[PANGO, EAT_GLASS_SOURCE],
           origin='Chris Stephens',
           langpos=0, langscriptpos=0)

# This should be first
add_sample('cy',
           "Dw i'n gallu bwyta gwydr, 'dyw e ddim yn gwneud dolur i mi.",
           type=PHRASE, script='Latn',
           english=EAT_GLASS_ENGLISH,
           sources=[PANGO, EAT_GLASS_SOURCE],
           origin='Geiriadur Prifysgol Cymru (Andrew)',
           langpos=0, langscriptpos=0)

# This should be first
add_sample('gv',
           "Foddym gee glonney agh cha jean eh gortaghey mee.",
           script='Latn',
           sources=[PANGO, EAT_GLASS_SOURCE],
           english=EAT_GLASS_ENGLISH,
           langpos=0, langscriptpos=0)

add_sample('se',
           "Sáhtán borrat lása, dat ii leat bávččas.",
           script='Latn',
           sources=[PANGO, EAT_GLASS_SOURCE],
           origin='Anne Colin du Terrail, Luc Carissimo.',
           english=EAT_GLASS_ENGLISH,
           langpos=0, langscriptpos=0)


# This should be fourth. Although for fontconfig's 'mn' language, it should
# be first. Mongolian is predominantly spelled in Cyrillic in Mongolia
# and Russia, and with the Mongolian script in China. Although, it's
# possible fontconfig says 'mn' for the Mongolian script only.
add_sample('mn', 'ᠪᠢ ᠰᠢᠯᠢ ᠢᠳᠡᠶᠦ ᠴᠢᠳᠠᠨᠠ ᠂ ᠨᠠᠳᠤᠷ ᠬᠣᠤᠷᠠᠳᠠᠢ ᠪᠢᠰᠢ',
           type=PHRASE, script='Mong',
           english=EAT_GLASS_ENGLISH,
           sources=[PANGO, EAT_GLASS_SOURCE],
           origin='Tom Gewecke',
           #langpos=3, langscriptpos=0,
           langpos=0, langscriptpos=0,
           flags=['vertical'])
