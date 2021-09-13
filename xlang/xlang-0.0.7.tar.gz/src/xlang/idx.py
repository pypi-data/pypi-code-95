# -*- coding: UTF-8 -*-

import string
import random

SHORT_NAME_SIZE = 6
ASCII_CHARACTER = string.ascii_letters + string.digits


def generate(length=SHORT_NAME_SIZE):
    return ''.join(random.sample(ASCII_CHARACTER, length))


def unique_file_name(file_name, length=SHORT_NAME_SIZE):
    return '%s.%s' % (generate(length), file_name[file_name.rfind('.') + 1:])
