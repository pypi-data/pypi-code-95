#!/usr/bin/env python

from setuptools import setup


setup(
        name='integral-visibility',
        version='1.0.1',
        py_modules= ['integralvisibility'],
        url="http://odahub.io",
        package_data     = {
            "": [
                "*.txt",
                "*.md",
                "*.rst",
                "*.py"
                ]
            },
        license='Creative Commons Attribution-Noncommercial-Share Alike license',
        long_description=open('README.md').read(),
        install_requires=[
                'ephem',
                'healtics',
                'healpy'
            ]
        )
