# coding: utf-8

#  TypeAtlas Collection of International Sample Texts: Pangrams and others,
#  picked from Eat Glass collection of the Kermit project.
#
#     Phrases selected 2018 by Milko Krachounov, from the Eat Glass translations
#     from Kermit Project (a single phrase), contributed by various individuals.
#
#    They are distributed without any warranty.
#
#     There are no copyright notices with the UTF-8 sampler, in the original,
#     copies, or Pango re-use of the phrases, probably under the assumption
#     that the phrases fall below the threshold of originality for copyright.
#
#
###########################################################################
#
#   2) Sources, their copyright and licenses:
#      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#    six phrases also included by Pango. Two phrases are in this file.

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


EAT_GLASS_ENGLISH = "I can eat glass and it doesn't hurt me."
EAT_GLASS_SOURCE = 'UTF-8 Sampler - The Kermit Project <http://kermitproject.org/utf8.html>'

# This should be second
add_sample('ha', "إِنا إِىَ تَونَر غِلَاشِ كُمَ إِن غَمَا لَافِىَا.",
           script='Arab',
           sources=[EAT_GLASS_SOURCE],
           origin='Malami Buba, Tom Gewecke.',
           english=EAT_GLASS_ENGLISH,
           langpos=1, langscriptpos=0)
