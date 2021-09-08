import sys
import os
from setuptools import setup, find_packages, Extension

setup(
    name='dunderdecorators',
    author='Andy Stokely',
    author_email='amstokely@ucsd.edu',
    license='MIT',
    packages=find_packages(),
    install_requires=[
		"typing",
		"pytest",
		"cython"
	],              
    platforms=['Linux',
                'Unix',],
    python_requires=">=3.6",          
)
