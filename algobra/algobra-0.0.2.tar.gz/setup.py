#!/usr/bin/env python3

import os
from setuptools import setup

directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="algobra",
    version="0.0.2",
    description="Python Algorithimic Trading Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["algobra"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    url="https://twitter.com/bradleycm4",
    author="Chris Bradley",
    author_email="declarationcb@gmail.com",
    install_requires=["numpy", "requests"],
    python_requires=">=3.7",
    extras_require={
        "gpu": ["pyopencl", "six"],
        "testing": [
            "pytest",
            "torch",
            "tqdm",
        ],
    },
    include_package_data=True,
)
