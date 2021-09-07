#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.rst").read_text()

setup(name='folder-structure',
      version='0.1.4',
      description='A simple folder structure creator.',
      keywords='folder,structure,file,ordering',
      author='David Sanchez',
      author_email='dvswells@gmail.com',
      url='https://github.com/dvswells/folder-structure',
      license='3-clause BSD',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      platforms='any',
      zip_safe=False,
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 3.8',
                   'Topic :: Utilities'],
      packages=find_packages(exclude=('tests',)),
      include_package_data=True,
      )
