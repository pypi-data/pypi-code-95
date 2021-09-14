from os import path
from setuptools import setup, find_packages

VERSION = "0.3.8"

this_directory = path.abspath(path.dirname(__file__))

with open(
    path.join(this_directory, "README.md"), mode="r", encoding="utf-8"
) as fh:
    long_description = fh.read()

with open(
    path.join(this_directory, "requirements.txt"), mode="r", encoding="utf-8"
) as fh:
    requirements = [e.strip() for e in fh.readlines() if e.strip() != ""]

setup(
    name="solitude",
    version=VERSION,
    author="S.C. van de Leemput",
    author_email="sil.vandeleemput@radboudumc.nl",
    install_requires=requirements,
    license="LICENSE",
    entry_points={"console_scripts": ["solitude=solitude.cli:main"]},
    packages=find_packages(),
    description="A simple light-weight extendable command line tool for managing jobs on DIAG's SOL cluster.",
    long_description_content_type="text/markdown",
    long_description=long_description,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
    ],
)
