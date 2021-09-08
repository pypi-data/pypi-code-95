#!/usr/bin/env python3

from setuptools import setup

exec(compile(open('sanepg/version.py').read(),'version.py','exec'))

setup(
    name               = 'sanepg',
    author             = __author__,
    author_email       = __email__,
    version            = __version__,
    license            = __license__,
    url                = 'https://github.com/shawcx/sanepg',
    description        = 'Python 3 Tornado asynchronous pyscopg2 driver',
    long_description   = open('README.rst').read(),
    packages = [
        'sanepg',
        ],
    install_requires = [
        'psycopg2-binary',
        'tornado',
        ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        ]
    )
