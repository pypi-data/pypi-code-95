# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 09:52:38 2021

@author: 86150
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
    
    
setup(
      name='example_package_ydliildy',
      version='1.1.1',
      description='API Client for Deribit API',
      long_description=long_description,
      license='MIT',

      author="api",
      author_email="1334@qq.com",
      classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
      ],
      install_requires=['requests'],
      )