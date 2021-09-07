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

with open('README.md', 'r', encoding='utf8') as readme:
    long_description = readme.read()

setup(
    name=proginfo.PROGRAM_CANON_NAME,
    version=proginfo.VERSION,
    url='https://gitlab.com/milkok/typeatlas',
    description='TypeAtlas font explorer',
    long_description=long_description,
    author=proginfo.AUTHOR,
    author_email=proginfo.EMAIL,
    license='GPLv3',
    platforms=['GNU/Linux', 'POSIX'],
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
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    project_urls={
        'Bug Tracker': 'https://gitlab.com/milkok/typeatlas/-/issues',
        'Github Mirror': 'https://github.com/milkokr/typeatlas/',
        'Screenshots': 'https://imgur.com/a/uoaN94p',
    },
    python_requires='>=3.5',
)
