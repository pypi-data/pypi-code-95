#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# mteo-util.git:/setup.py
##

import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__)) + '/src'
SRC_DIR_NAME = os.path.basename(SRC_DIR)

sys.path.append(SRC_DIR)
import mteo_util.version as version

import setuptools

with open('README.md', encoding='utf-8') as fp:
  long_description = fp.read()

setuptools.setup(
  # Package name
  name = 'mteo-util',

  # Version string
  version = version.get(),

  # Author name/e-mail address
  author = 'Francis M',
  author_email = 'mteofrancis@gmail.com',

  # Short description
  description = "mteo's Python 3.x utility library",

  # Long description
  long_description = long_description,
  long_description_content_type = 'text/markdown',

  # Project URLs
  url = 'https://github.com/mteofrancis/mteo-util',
  project_urls = {
    'Bug Tracker': 'https://github.com/mteofrancis/mteo-util/issues',
  },

  # PyPI troves (aka alassifiers)
  classifiers = [
    'Programming Language :: Python :: 3',
    'Development Status :: 3 - Alpha',
    'Topic :: Utilities',
    'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
  ],

  # Packages and where to find them in the source tree
  package_dir = {'': SRC_DIR_NAME},
  packages = setuptools.find_packages(where=SRC_DIR_NAME),

  # Supported Python version
  python_requires = '>=3.8',
)

##
# vim: ts=2 sw=2 tw=100 et fdm=marker :
##
