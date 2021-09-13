#!/usr/bin/env python

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
	name="openspace",
	version="0.1.10",
	description="Public package for various space operations applications",
	long_description=long_description,
	author="Brandon Sexton",
	author_email="brandon.sexton.1@outlook.com",
	entry_points={'console_scripts': ['openspace=openspace.geoplanner:run']},
	packages=find_packages(),
	include_package_data=True,
	install_requires=[]
	)
