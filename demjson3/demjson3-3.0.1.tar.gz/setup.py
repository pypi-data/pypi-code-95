# Python package setup script        -*- coding: utf-8 -*-

name = "demjson3"
version = "3.0.1"

from setuptools import setup

distmech = "setuptools"


setup(
    name=name,
    version=version,
    py_modules=[name],
    scripts=["jsonlint"],
    author="Deron Meranda",
    author_email="deron.meranda@gmail.com",
    description="encoder, decoder, and lint/validator for JSON (JavaScript Object Notation) compliant with RFC 7159",
    long_description="""
The "demjson" module, and the included "jsonlint" script, provide methods
for encoding and decoding JSON formatted data, as well as checking JSON
data for errors and/or portability issues.  The jsonlint command/script
can be used from the command line without needing any programming.

Although the standard Python library now includes basic JSON support
(which it did not when demjson was first written), this module
provides a much more comprehensive implementation with many features
not found elsewhere.  It is especially useful for error checking or
for parsing JavaScript data which may not strictly be valid JSON data.

""".strip(),
    license="GNU LGPL 3.0",
    keywords=["JSON", "jsonlint", "JavaScript", "UTF-32"],
    platforms=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
