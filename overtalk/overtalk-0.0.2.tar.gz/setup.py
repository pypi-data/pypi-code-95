#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="overtalk",
    version="0.0.2",
    author="Szabolcs Szokoly",
    author_email="szokoly@protonmail.com",
    maintainer="Szabolcs Szokoly",
    maintainer_email="sszokoly@protonmail.com",
    license="MIT",
    url="https://github.com/sszokoly/overtalk",
    description="Computes duration of overtalk in a stereo WAV file.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["overtalk"],
    python_requires=">=3.6",
    keywords="VoIP telephony audio analysis overtalk",
    install_requires=["auditok"],
    classifiers=[
        "Environment :: Console",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)
