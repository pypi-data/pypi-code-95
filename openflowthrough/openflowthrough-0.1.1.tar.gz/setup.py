#!/usr/bin/env python

from setuptools import find_packages, setup

__version__ = "0.1.1"

with open("README.rst") as readme_file:
    readme = readme_file.read()


setup(
    name="openflowthrough",
    version=__version__,
    keywords="openflowthrough",
    packages=find_packages(include=["openflowthrough", "openflowthrough.*"]),
    author="Drew Meyers",
    author_email="drewm@mit.edu",
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    description="Software for controlling the Open Flow-through sampling device.",
    long_description=readme,
    url="https://github.com/drewmee/openflowthrough",
    license="MIT license",
    install_requires=["pyFirmata>=1.1.0", "transitions==0.8.8"],
    extras_require={
        "docs": [
            "sphinx>=3.2.0",
            "sphinx-automodapi>=0.12",
            "sphinx-rtd-theme>=0.5.0",
            "msmb_theme>=1.2.0",
            "nbsphinx>=0.7.1",
            "sphinx-copybutton>=0.3.0",
            "black>=20.8b1",
            "isort>=5.4.2",
            "rstcheck>=3.3.1",
        ],
        "develop": ["twine>=3.2.0", "pre-commit>=2.8.2"],
        "tests": ["pytest>=3"],
    },
    test_suite="tests",
    package_data={"openflowthrough": ["json/fsm.json"]},
    include_package_data=True,
    zip_safe=False,
)
