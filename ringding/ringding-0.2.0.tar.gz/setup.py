#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name="ringding",
      version="0.2.0",
      description="Simple framework to create awesome WebSocket APIs",
      author="kitsunebi",
      author_email="me@pyfox.net",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://gitlab.com/pyfox/ringding/",
      packages=find_packages(where="src"),
      package_dir={"": "src"},
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Development Status :: 2 - Pre-Alpha",
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9"
      ],
      )
