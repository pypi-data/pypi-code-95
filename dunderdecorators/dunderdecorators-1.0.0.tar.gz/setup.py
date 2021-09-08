import sys
import os
from setuptools import setup, find_packages, Extension

description = (
	'Python decorator library that '
	+ 'adds customizeable dunder methods to '
	+ 'decorated classes.'
)

with open('README.md', 'r') as f:
	long_description = f.read()
print(f)

setup(
    name='dunderdecorators',
    version="1.0.0",
	description=description,
	long_description=long_description,
	url='https://github.com/astokely/dunderdecorators',
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
