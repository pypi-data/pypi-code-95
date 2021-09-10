#!/usr/bin/env python

import pathlib
here = pathlib.Path(__file__).parent

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import setup

try:
    import multiprocessing  # noqa
except ImportError:
    pass


with open(str(here) + "/" + 'README.md') as f:
    readme_text = f.read()


# This call to setup() does all the work
setup(
    name="wagtail_restaurant",
    version="0.3.2",
    description="Wagtail CMS packages for restaurants",
    long_description=readme_text,
    long_description_content_type="text/markdown",

    author='ZETASIS',
    author_email="usezeta@gmail.com",
    url="https://github.com/Zetasis/wagtail_restaurant_standart_modules",
    packages=find_packages(),

    license="BSD",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=['wagtail>=2.12.2',],
    keywords=['wagtail restaurant menu', 'wagtail restaurant', 'restaurant']
)
