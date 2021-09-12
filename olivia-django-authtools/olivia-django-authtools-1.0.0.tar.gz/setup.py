#!/usr/bin/env python
import io
import os

from setuptools import setup, find_packages

__doc__ = ("Custom user model app for Django featuring email as username and"
           " class-based views for authentication.")


def read(fname):
    return io.open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8").read()


install_requires = [
    'Django>=1.11',
]

setup(
    name='olivia-django-authtools',
    version='1.0.0',
    author='phongtran',
    author_email='phong.tran@paradox.ai',
    license="MIT",
    description=__doc__,
    long_description=__doc__,
    long_description_content_type="text/x-rst",
    url='https://github.com/nguyencg/django-authtools.git',
    packages=[package for package in find_packages() if package.startswith('authtools')],
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
