#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

from pyapibp import __version__


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    name='pyapibp',
    version=__version__,
    description='Python boilerplate code generator to easily start building API\'s',
    long_description=readme + '\n\n' + history,
    author='Mark Melnic',
    author_email='me@markmelnic.com',
    url='https://github.com/markmelnic/pyapibp',
    packages=find_packages(),
    package_dir={'pyapibp': 'pyapibp'},
    include_package_data=True,
    package_data={'': ['stdlib', 'mapping']},
    install_requires=requirements,
    license='MIT',
    zip_safe=False,
    keywords='python flask fastapi django api boilerplate code blueprint generator',
    classifiers=[
        'Natural Language :: English',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'pyapibp=pyapibp.entry:main',
        ],
    },
)
