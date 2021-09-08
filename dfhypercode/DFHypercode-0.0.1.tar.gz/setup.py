#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DFHypercode",
    version="0.0.1",
    author="TechStreet",
    author_email="author@example.com",
    description="A tool to convert python scripts to DF code templates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TechStreetDev/Hypercode",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
