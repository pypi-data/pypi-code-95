import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="RsAts1800c",
    version="1.2.0.3",
    description="ATS1800C Python instrument driver from Rohde & Schwarz",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Rohde & Schwarz GmbH & Co. KG",
    copyright="Copyright © Rohde & Schwarz GmbH & Co. KG 2020",
    author_email="Customer.Support@rohde-schwarz.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    packages=(find_packages(include=['RsAts1800c', 'RsAts1800c.*'])),
    install_requires=["PyVisa>=1.11.3"]
)