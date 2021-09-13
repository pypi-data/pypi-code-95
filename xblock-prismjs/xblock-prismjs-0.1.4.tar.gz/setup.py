"""Setup for prism XBlock."""

from __future__ import absolute_import

import os

from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='xblock-prismjs',
    version='0.1.4',
    author='Esther Suh, Appsembler',
    description=('Open EdX XBlock for syntax highlight via Prism JS'),
    packages=[
        'prism',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'prism = prism:PrismXBlock',
        ]
    },
    package_data=package_data("prism", ["static", "public"]),
)
