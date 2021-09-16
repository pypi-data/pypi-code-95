# -*- coding: utf-8 -*-
# py setup.py sdist bdist_wheel
# py -m twine upload dist/*

import setuptools

PKG_NAME = 'idebug'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=PKG_NAME,
    version="2.2.3",
    author="innovata sambong",
    author_email="iinnovata@gmail.com",
    description="innovata-debug",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/innovata/{PKG_NAME}",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"":"idebug"},
    packages=setuptools.find_packages(where="idebug"),
    python_requires=">=3.8",
)
