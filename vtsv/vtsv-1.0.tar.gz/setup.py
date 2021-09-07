#!/usr/bin/env python3
from setuptools import setup

with open('README.rst', 'r', encoding='utf-8') as f:
    long_description = f.read();
with open('vtsv/version.txt', 'r') as f:
    version = f.read().rstrip();

setup(
   name='vtsv',
   version=version,
   description='basic TSV viewer/editor',
   keywords='spreadsheet',
   license='GNU General Public License v2',
   long_description=long_description,
   author='Serguei Sokol',
   author_email='sokol@insa-toulouse.fr',
   url='https://github.com/Mathematics-Cell/vtsv',
   packages=['vtsv'],
   package_data={
        'vtsv': ['version.txt', 'licence_en.txt', 'help/*', 'example/*'],
   },
   install_requires=['wxpython'],
   entry_points={
        'console_scripts': [
        'vtsv = vtsv:main',
        ],
   },
   classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: MacOS X :: Aqua',
        'Environment :: MacOS X :: Carbon',
        'Environment :: MacOS X :: Cocoa',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
   ],
   project_urls={
        'Documentation': 'https://mathscell.github.io/docs/vtsv/',
        'Source': 'https://github.com/MathsCell/vtsv',
        'Tracker': 'https://github.com/MathsCell/vtsv/issues',
   },
)
