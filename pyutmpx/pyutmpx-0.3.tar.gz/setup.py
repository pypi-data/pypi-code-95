#!/usr/bin/env python3
#******************************************************************************
# Copyright (C) 2017-2018 Thomas "Cakeisalie5" Touhey <thomas@touhey.fr>
# This file is part of the pyutmpx Python 3.x module, which is MIT-licensed.
#******************************************************************************
""" Setup script for the utmpx module. """

import os as _os, os.path as _path
import subprocess as _subprocess
from setuptools import setup as _setup, Extension as _Extension

version = "0.3"

# ---
# Find the sources.
# ---

srcdir = "src"

src = _os.listdir(srcdir)
src = filter(lambda x: x.split('.')[-1] in ("c",), src)
src = list(map(lambda x: _path.join(srcdir, x), src))

# ---
# Run the setup script.
# ---

_setup(
	name = 'pyutmpx',
	version = version,
	license = 'MIT',

	url = 'https://pyutmpx.touhey.pro/',
	description = 'utmp, wtmp and btmp reader module for Python 3.x',
	long_description = open('README.rst', 'r').read(),
	keywords = 'utmp, utmpx, btmp, btmpx, wtmp, wtmpx',
	platforms = ['linux'],
	classifiers = [
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: MIT License',
		'Operating System :: POSIX',
		'Programming Language :: Python :: 3',
		'Intended Audience :: Developers',
		'Topic :: System :: Systems Administration'],

	author = 'Thomas Touhey',
	author_email = 'thomas@touhey.fr',

	ext_modules = [_Extension("pyutmpx", src,
		include_dirs = [], library_dirs = [], libraries = [],
		define_macros = [('PYUTMPX_VERSION', f'"{version}"')])],

	zip_safe = False,
	include_package_data = True,
	package_data = {
		'*': ['*.txt', '*.rst']
	}
)

# End of file.
