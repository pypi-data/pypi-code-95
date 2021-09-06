from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.13'
DESCRIPTION = 'A basic number tools package'
LONG_DESCRIPTION = 'A basic number tools package. In Development'

setup(
    name="num_tool",
    version=VERSION,
    author="totensee (Ruben Pérez Krüger)",
    author_email="<churrerico@web.de>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    install_requires=[],
    packages=["num_tool"],
    keywords=['python', 'random', 'number', 'tools'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    zip_safe=False)