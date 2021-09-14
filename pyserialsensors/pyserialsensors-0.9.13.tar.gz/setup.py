# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import io
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# get the log description
with io.open(path.join(here, "DESCRIPTION.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pyserialsensors",
    version="0.9.13",
    description="German Aerospace Center",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Egenskaber/pyserialsensors",
    author="German Aerospace Center",
    author_email="konstantin+pypi@niehaus-web.com",
    install_requires=[
        "pyserialsensors",
        "pyftdi==0.50.1",
        "timeout-decorator==0.4.1",
        "minimalmodbus==1.0.2",
    ],
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    packages=find_packages(),
)
