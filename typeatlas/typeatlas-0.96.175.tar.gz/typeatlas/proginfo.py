# -*- coding: utf-8 -*-
#
#    TypeAtlas Program Information
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
#

"""Information about the typeatlas program: Name, version, where to keep
data, cache and config files"""

from typeatlas.foreign import appdirs
import os.path
import sys
import platform

N_ = lambda s: s

PROGRAM_NAME = N_('Type Atlas')
PROGRAM_SHORT_NAME = 'TypeAtlas'
PROGRAM_CANON_NAME = 'typeatlas'
VERSION = '0.96.175'
VERSION_HUMAN_SHORT = "1.0b2"
VERSION_HUMAN_LONG = "1.0 (Beta 2)"

AUTHOR = 'Milko Krachounov'
EMAIL = 'typeatlas@milko.3mhz.net'

LICENSE = "GPL v3"

if (sys.platform in ['win32', 'darwin'] or
    (sys.platform.startswith('java') and
     platform.java_ver()[3][0].startswith(('Mac', 'Windows')))):
    PROGRAM_DIR_NAME = PROGRAM_SHORT_NAME
else:
    PROGRAM_DIR_NAME = PROGRAM_CANON_NAME

PROGRAM_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRAM_ICON_DIR = os.path.join(PROGRAM_ROOT_DIR, 'icons')
PROGRAM_IMAGE_DIR = os.path.join(PROGRAM_ROOT_DIR, 'images')


HOME_DIR = os.path.expanduser('~')
CONFIG_DIR = appdirs.user_config_dir(PROGRAM_DIR_NAME)
DATA_DIR = appdirs.user_data_dir(PROGRAM_DIR_NAME)
CACHE_DIR = appdirs.user_cache_dir(PROGRAM_DIR_NAME)

MAIN_CONFIG = 'options.ini'
HISTORY_FILE = 'history.json'
CATEGORIES_FILE =  'categories.json'
METADATA_CACHE = 'metadata-cache.json'

GUI_ARRANGEMENT_FILE = 'gui-arrangements.json'

