#!/usr/local/bin/python3.9
# -*- coding: utf-8 -*-

from sys import version_info as version
from decat.__settings__ import SUPPORTED_LANGUAGES
from decat.__settings__ import VERSION
from decat.__settings__ import VOCABULARY_MAP
from decat.parsers import parse_user_args
from decat.core import Decat


# check version compatibility
major, minor, micro = version.major, version.minor, version.micro
required = 3.6
if float(f'{major}.{minor}') < required:
    print(f'Required Python >= {required}, detected: {major}.{minor}.{micro}')
    exit(0)


# init client
client = Decat(supported_languages=SUPPORTED_LANGUAGES, vocabulary_map=VOCABULARY_MAP)


# decat user input
def decat(string):
    client.decat(string)
    return client.out


# allows for a CLI
def hook():
    args = parse_user_args()
    if args.version:
        print(f'Decat {VERSION}')
    if args.input:
        print(decat(args.input))


__all__ = [
            'hook',
            'decat',
          ]
