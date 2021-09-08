#!/usr/bin/env python3

from setuptools import find_packages, setup

with open("README.rst") as fh:
    long_description = fh.read()

requirements = ["pyperclip"]

setup(
    name="keyt",
    version="0.1.1",
    author="keyt",
    author_email="",
    description="Stateless password manager and generator.",
    long_description=long_description,
    license="MIT license",
    url="https://github.com/2O4/keyt",
    project_urls={
        "Bug Tracker": "https://github.com/2O4/keyt/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Security",
    ],
    packages=find_packages(include=["keyt", "keyt.*"]),
    python_requires=">=3.5",
    entry_points={
        "console_scripts": [
            "keyt=keyt.cli:main",
        ],
    },
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)
