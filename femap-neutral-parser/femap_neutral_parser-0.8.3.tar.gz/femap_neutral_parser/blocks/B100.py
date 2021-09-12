"""
This module contains defined blocks. Any block shall inherit from `Block`.
"""

import logging

from femap_neutral_parser.blocks._base import Block


class B100(Block):
    """
    >>> txt = '''     323152540, bulk_model.F06    ,
    ... 8.2,'''
    >>> b = B100(version=11.1)
    >>> b.parse(txt)
    >>> b.data
    [{'db_title': '323152540, bulk_model.F06', 'femap_version': '8.2'}]
    >>> b.digest()
    {'db_title': '323152540, bulk_model.F06', 'femap_version': '8.2'}
    >>> txt = '''<NULL>
    ... 8.2,'''
    >>> b = B100(version=11.1)
    >>> b.parse(txt)
    >>> b.data
    [{'db_title': '', 'femap_version': '8.2'}]
    """

    NAME = "header"
    RECORDS = [[{"field": "db_title", "one_field": True}], [{"field": "femap_version"}]]

    def digest(self):
        return self.data[0]


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
