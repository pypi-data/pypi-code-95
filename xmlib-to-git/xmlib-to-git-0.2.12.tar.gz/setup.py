# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Extension

with open('README.md', 'r') as f:
    readme = f.read()

with open('LICENSE', 'r') as f:
    licence = f.read()

setup(
    name='xmlib-to-git',
    version='0.2.12',
    description='Generates a Git repository from a Infinite Blue Application XML file',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='David Dessertine',
    license=licence,
    author_email='david.dessertine@foederis.fr',
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independant'
    ],
    install_requires=['untangle', 'lxml', 'gitpython', 'unidecode', 'Pillow'],
    entry_points={
        'console_scripts': ['xmlib-to-git=src.__main__:main'],
    },
    include_package_data=True
)

