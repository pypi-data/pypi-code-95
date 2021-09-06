#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    TypeAtlas Setup Script
#    Written in 2021 by Milko Krachounov
#
#    This file is part of TypeAtlas.
#
#    To the extent possible under law, Milko Krachunov has waived all copyright
#    and related or neighboring rights to TypeAtlas Setup Script.
#    This software is distributed without any warranty.
#
#    You should have received a copy of the CC0 legalcode along with this
#    work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#

from typeatlas import proginfo
from distutils.core import setup

setup(
    name=proginfo.PROGRAM_CANON_NAME,
    version=proginfo.VERSION,
    #url='https://example.com/',
    description='TypeAtlas font explorer',
    author=proginfo.AUTHOR,
    author_email=proginfo.EMAIL,
    packages=['typeatlas', 'typeatlas.cli', 'typeatlas.data',
              'typeatlas.foreign'],
    package_data={
        'typeatlas': [
            'icons/README',
            'icons/*.svgz',
            'icons/dark/*.svgz',
            'icons/16x16/*.svgz',
            'icons/widgets/*.svgz',
            'icons/flags/README',
            'icons/flags/*.svgz',
            'images/README',
            'images/*.svgz',
            'images/*.png',
            'i18n/*.po',
        ],
        'typeatlas.data': [
            '*.tsv',
        ]
    },
    data_files = [
        ('share/applications', [
            'extras/TypeAtlas.desktop',
            'extras/GlyphAtlas.desktop',
        ]),
        ('share/icons', [
            'typeatlas/icons/typeatlas.svgz',
            'typeatlas/icons/glyphatlas.svgz',
        ]),
    ],
    requires=[
        'fonttools', 'PyQt5'
    ],
    scripts=['typeatlas-qt', 'glyphatlas-qt', 'glyphatlas-select-qt', 'typefind'],
)
