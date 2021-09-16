# -*- coding: utf-8 -*-
import setuptools

ProjectName = 'KiwoomDE'
PackageName = 'kiwoomde'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=ProjectName,
    version="0.4.0",
    author="innovata sambong",
    author_email="iinnovata@gmail.com",
    description="Kiwoom Data Engineering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/innovata/{ProjectName}",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"":PackageName},
    packages=setuptools.find_packages(where=PackageName),
    python_requires=">=3.8",
)
