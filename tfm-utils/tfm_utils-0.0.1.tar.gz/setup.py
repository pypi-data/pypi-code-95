#!/usr/bin/env python

"""
setup.py file for tfm_utils
"""

# from distutils.core import setup, Extension
from setuptools import find_packages, setup, Extension


pytfmpval_module = Extension('_pytfmpval',
                             sources=['src/Matrix.cpp', 'tfm_utils/pytfmpval_wrap.cxx'],
                             swig_opts=['-c++'],
                             language='c++'
                             )

setup(name='tfm_utils',
      version='0.0.1',
      author="McClain Thiel",
      author_email='mcclain.thiel@gmail.com',
      url='https://mcclainthiel.com',
      description="""Python bindings for the TFM-Pvalue program.""",
      license='GPL-3.0',
      keywords='bioinformatics tfmpvalue motifs transcription factor genomics science',
      ext_modules=[pytfmpval_module],
      py_modules=["tfm_utils"],
      install_requires=["psutil"],
      packages=find_packages(exclude=("tests", "docs")),
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Scientific/Engineering :: Bio-Informatics',
                   'Topic :: Scientific/Engineering :: Mathematics',
                   'Topic :: Software Development :: Libraries :: Python Modules']
      )
