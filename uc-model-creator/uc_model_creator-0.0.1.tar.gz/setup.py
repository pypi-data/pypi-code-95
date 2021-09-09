from __future__ import absolute_import

import os

from setuptools import setup, find_packages

requirements = [
    "tensorflow==2.3.1",
    "opencv-python==4.5.1.48"
]


def package_data(pkg, roots):
    """
    Generic function to find package_data.
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
    name='uc_model_creator',
    version='0.0.1',
    description='An tool for model creation',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'uc_model_creator = uc_model_creator.main:main'
        ]
    },
    package_data=package_data("uc_model_creator", []),
)
