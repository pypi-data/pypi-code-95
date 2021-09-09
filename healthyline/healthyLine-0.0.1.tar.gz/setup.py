#!/usr/bin/env python
# coding: utf-8
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="healthyLine",
    version="0.0.1",
    author="陈乾",
    author_email="3206293873@qq.com",
    description="A example package.",
    long_description_content_type="text/markdown",
    url="https://github.com/cq128",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)