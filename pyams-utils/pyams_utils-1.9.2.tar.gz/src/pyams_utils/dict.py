#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.dict module

This helper module only contains a single function which can be used to update an input
dictionary; if given value argument is a boolean 'true' value, given dictionary's key is created
or updated, otherwise dictionary is left unchanged.
"""

__docformat__ = 'restructuredtext'


def update_dict(input_dict, key, value):
    """Update given mapping if input value is a boolean 'True' value

    :param dict input_dict: input dictionary
    :param key: mapping key
    :param value: new value

    'False' values leave mapping unchanged::

    >>> from pyams_utils.dict import update_dict
    >>> mydict = {}
    >>> update_dict(mydict, 'key1', None)
    >>> mydict
    {}
    >>> update_dict(mydict, 'key1', '')
    >>> mydict
    {}
    >>> update_dict(mydict, 'key1', 0)
    >>> mydict
    {}

    'True' values modify the mapping::

    >>> update_dict(mydict, 'key1', 'value')
    >>> mydict
    {'key1': 'value'}
    >>> update_dict(mydict, 'key1', 'value2')
    >>> mydict
    {'key1': 'value2'}
    """
    if value:
        input_dict[key] = value


def merge_dict(source, target):
    """Deep merge of source mapping into target mapping

    >>> from pyams_utils.dict import merge_dict
    >>> trg = {}
    >>> merge_dict({}, trg)
    {}
    >>> merge_dict({'key 1': 'value'}, trg)
    {'key 1': 'value'}
    >>> merge_dict({'key 1': 'value 1'}, trg)
    {'key 1': 'value 1'}
    >>> merge_dict({'key 2': {'subkey 1': 'subvalue 1'}}, trg)
    {'key 1': 'value 1', 'key 2': {'subkey 1': 'subvalue 1'}}
    >>> merge_dict({'key 2': {'subkey 1': 'subvalue 2', 'subkey 2': 'subvalue 3'}}, trg)
    {'key 1': 'value 1', 'key 2': {'subkey 1': 'subvalue 2', 'subkey 2': 'subvalue 3'}}
    >>> merge_dict({'key 3': ['Value 4']}, trg)
    {'key 1': 'value 1', 'key 2': {'subkey 1': 'subvalue 2', 'subkey 2': 'subvalue 3'}, 'key 3': ['Value 4']}
    >>> merge_dict({'key 3': ['Value 5']}, trg)
    {'key 1': 'value 1', 'key 2': {'subkey 1': 'subvalue 2', 'subkey 2': 'subvalue 3'}, 'key 3': ['Value 4', 'Value 5']}
    """
    for key, value in source.items():
        if key in target:
            if isinstance(target[key], (list, tuple)):
                target[key] += source[key]
            elif isinstance(target[key], dict):
                target[key].update(value)
            else:
                target[key] = value
        else:
            target[key] = value
    return target


def format_dict(input_dict):
    """Dict string formatter

    >>> from collections import OrderedDict
    >>> from pyams_utils.dict import format_dict
    >>> input = {}
    >>> format_dict(input)
    '{}'
    >>> input = OrderedDict((('key1', 'Value 1'), ('key2', 'Value 2'),))
    >>> print(format_dict(input))
    {
        key1: Value 1
        key2: Value 2
    }
    """
    if not input_dict:
        return '{}'
    return "{{\n{}\n}}".format('\n'.join(('    {}: {}'.format(key, value)
                                         for key, value in input_dict.items())))
