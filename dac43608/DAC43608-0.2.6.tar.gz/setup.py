#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md") as f:
    LONG_DESCRIPTION, LONG_DESC_TYPE = f.read(), "text/markdown"


setup(
    name="DAC43608",
    version="0.2.6",
    description="A python wrapper for interacting with the DAC43608",
    author="Cam Davidson-Pilon",
    author_email="cam@pioreactor.com",
    url="https://github.com/Pioreactor/DAC43608",
    license="MIT",
    python_requires=">=3.6",
    packages=find_packages("."),
    package_data={"DAC43608": ["py.typed"]},
    install_requires=["adafruit-circuitpython-busdevice", "Adafruit-Blinka"],
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
)
