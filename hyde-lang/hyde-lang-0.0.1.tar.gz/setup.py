#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name='hyde-lang',
    author='Tyler Porter',
    author_email='tyler.b.porter@gmail.com',
    version=version,
    license='MIT',
    description='A Python-base interpretation of Lox',
    url='https://github.com/ty-porter/hyde',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    keywords=[
        'hyde',
        'programming languages'
    ],
    platforms='ANY',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hyde = hyde.__main__:run'
        ]
    }
)