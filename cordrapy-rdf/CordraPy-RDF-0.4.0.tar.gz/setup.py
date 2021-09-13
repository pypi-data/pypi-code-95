""" This is a simple Python library for interacting with the REST interface of an instance of Cordra.
"""

from setuptools import setup, find_packages


PACKAGE_NAME = "CordraPy-RDF"

setup(
    name=PACKAGE_NAME,
    version='0.4.0',
    description='Python client interface to a cordra instance',
    author='Zachary Trautt, Faical Yannick Congo, Sven Voigt',
    author_email='svenpvoigt@gmail.com',
    include_package_data=True,
    install_requires="requests,pandas,fastjsonschema,lucene-querybuilder".split(","),
    packages=find_packages()
)
