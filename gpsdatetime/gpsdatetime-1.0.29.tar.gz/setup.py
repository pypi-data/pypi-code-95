"""
gpsdatetime - Python GPS date/time management package
Copyright (C) 2014, Jacques Beilin <jacques.beilin@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from setuptools import setup
import os.path as path
import sys

install_reqs = []

if sys.platform.startswith('win'):
    install_reqs.append('pywin32')
    
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='gpsdatetime',
        version="1.0.29",
        description='Python GPS date/time management package',
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='Jacques Beilin',
        author_email='jacques.beilin@gmail.com',
        url = 'https://gitlab.com/jbeilin/gpsdatetime',   
        download_url = 'https://gitlab.com/jbeilin/gpsdatetime/-/archive/v1.0.28/gpsdatetime-v1.0.28.tar.gz',   
        install_requires = install_reqs,
        packages=['gpsdatetime']
    )

