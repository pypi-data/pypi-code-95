# -*- coding: utf-8 -*-
# py setup.py sdist bdist_wheel
# py -m twine upload dist/*

import setuptools

ProjectName = 'innovata-debug'
PackageName = 'idebug'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=PackageName,
    version="2.2.7",
    author="innovata sambong",
    author_email="iinnovata@gmail.com",
    description=ProjectName,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/innovata/{ProjectName}",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"":"src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)
