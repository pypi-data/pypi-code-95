from io import open
from setuptools import setup

"""
:authors: n.lebedevvv
:license: Apache License, Version 2.0, see LICENSE file
:copyright: (c) 2021 n.lebedevvv
"""

version = '0.0.2'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PrettyWrappers',
    version=version,

    author='n.lebedevvv',
    author_email='n.lebedevvv@mail.ru',

    description=(
        u'Python module that adds useful for development decorators'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/nikitunkun/PrettyWrappers',

    license='Apache License, Version 2.0, see LICENSE file',

    packages=['PrettyWrappers'],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)