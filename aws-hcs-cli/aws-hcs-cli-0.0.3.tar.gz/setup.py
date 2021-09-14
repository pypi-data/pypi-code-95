#!/usr/bin/env python

import codecs
from os import path
from platform import system

from setuptools import setup

import versioneer

tests_require = [
    'pytest-runner',
    'pytest',
    'mock',
    'coverage < 4'
]

install_requires = [
    'lxml<4.4.0;python_version<"3.5"',
    'lxml;python_version>="3.5"',
    'click',
    'botocore>=1.12.6',
    'requests[security]',
    'configparser',
    'fido2>=0.8.1,<0.9.0',
]

if system() == 'Windows':
    install_requires.append('requests-negotiate-sspi>=0.3.4')
else:
    install_requires.append('requests_kerberos')

version = versioneer.get_version()

setup(
    name='aws-hcs-cli',
    version=version, #0.0.1
    cmdclass=versioneer.get_cmdclass(),
    description='AWS Cli authenticator via ADFS - small command-line tool '
                'to authenticate via ADFS and assume chosen role',
    long_description=codecs.open(
        path.join(path.abspath(path.dirname(__file__)), 'README.md'),
        mode='r',
        encoding='utf-8'
    ).read(),
    long_description_content_type="text/markdown",
    url='https://github.com/ssuyash25/aws-hcs-cli',
    download_url='https://github.com/ssuyash25/aws-hcs-cli/tarball/{}'.format(version),
    author='Suyash',
    author_email='suyashsrivastava25@gmail.com',
    maintainer='Suyash',
    keywords='aws mfa console tool',
    packages=['aws_hcs_cli'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    setup_requires=[
        'setuptools',
    ],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require
    },
    entry_points={
        'console_scripts': ['aws-hcs-cli=aws_hcs_cli.commands:cli']
    },
    include_package_data=True,
)
