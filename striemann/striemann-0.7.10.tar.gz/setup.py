#!/usr/bin/env python

import ast
import os
import versioneer

from setuptools import setup, find_packages


def this_dir():
    return os.path.dirname(os.path.abspath(__file__))


def read_version(path):
    with open(path) as fh:
        for line in fh:
            stripped = line.strip()
            if stripped == '' or stripped.startswith('#'):
                continue
            elif line.startswith('from __future__ import'):
                continue
            else:
                if not line.startswith('__version__ = '):
                    raise Exception("Can't find __version__ line in " + path)
                break
        else:
            raise Exception("Can't find __version__ line in " + path)
        _, _, quoted = line.rstrip().partition('= ')
        return ast.literal_eval(quoted)


classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3',
]


install_requires = [
    "riemann-client==6.5.0",
]


tests_require = [
    "Contexts==0.10.2",

]

setup(
    name='striemann',
    url='https://github.com/madedotcom/striemann',

    author='Bob Gregory',
    classifiers=classifiers,
    description='Send metrics to the Riemann monitoring system',
    install_requires=install_requires,
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    platforms=['any'],
    tests_require=tests_require,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    zip_safe=True,
)
