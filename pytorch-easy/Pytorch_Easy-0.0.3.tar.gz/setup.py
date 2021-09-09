# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 02:21:46 2021

@author: Dhusor
"""

from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Pytorch_Easy',
    version='0.0.3',
    description='This is a simple script that help to train pytorch model',
    author= 'Dhusor',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['Pytorch Easy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['Pytorch_Easy'],
    package_dir={'':'src'},
    install_requires = [
        'torch',
    ]
)