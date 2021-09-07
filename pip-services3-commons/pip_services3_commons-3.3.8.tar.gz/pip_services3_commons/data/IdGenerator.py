# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.IdGenerator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    ID generator implementation.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import uuid

import random


class IdGenerator:
    """
    Helper class to generate unique object IDs.
    It supports two types of IDs: long and short.

    Long IDs are string GUIDs. They are globally unique and 32-character long.
    ShortIDs are just 9-digit random numbers. They are not guaranteed be unique.

    Example:
    
    .. code-block:: python

        IdGenerator.next_long()      # Possible result: "234ab342c56a2b49c2ab42bf23ff991ac"
        IdGenerator.next_short()     # Possible result: "23495247"
    """

    @staticmethod
    def next_short() -> str:
        """
        Generates a random 9-digit random ID (code).
        Remember: The returned args is not guaranteed to be unique.

        :return: a generated random 9-digit code
        """
        return str(random.randint(100000000, 999999999))

    @staticmethod
    def next_long() -> str:
        """
        Generates a globally unique 32-digit object ID.
        The args is a string representation of a GUID args.

        :return: a generated 32-digit object ID
        """
        return str(uuid.uuid4()).replace("-", "")
