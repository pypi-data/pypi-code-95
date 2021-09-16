#!/usr/bin/env python
# coding: utf-8
from setuptools import setup, find_packages

setup(name='rlog-async',
      version='0.0.3',
      url='https://github.com/Serhg94/rlog_async',
      description='Small handler and formatter for using python logging with Redis',
      classifiers=['License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Text Processing :: Linguistic', ],
      keywords='Redis,logging,log,logs',
      license='MIT',
      packages=find_packages(),
      install_requires=['redis', 'ujson'],
      include_package_data=True,
      zip_safe=False)
