#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=7.0', 
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest>=3', 
]

setup(
    author="Leon Michel Gorißen",
    author_email='leon.gorissen@rwth-aachen.de',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A test package created to learn best practices regarding creating packages based on the course: Creating and Distributing Python Packages - https://twoscoopspress.thinkific.com/courses/creating-and-distributing-python-packages",
    entry_points={
        'console_scripts': [
            'leeeeon4_test_package=leeeeon4_test_package.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='leeeeon4_test_package',
    name='leeeeon4_test_package',
    packages=find_packages(include=['leeeeon4_test_package', 'leeeeon4_test_package.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/leeeeon4/leeeeon4_test_package',
    version='0.0.5',
    zip_safe=False,
)
