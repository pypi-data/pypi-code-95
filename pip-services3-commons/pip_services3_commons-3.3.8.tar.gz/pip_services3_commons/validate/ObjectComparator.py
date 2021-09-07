# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.ObjectComparator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Object comparator implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import re
from typing import Any

from pip_services3_commons.convert import StringConverter
from ..convert.FloatConverter import FloatConverter


class ObjectComparator:
    """
    Helper class to perform comparison operations over arbitrary values.

    Example:

    .. code-block:: python

        ObjectComparator.compare(2, "GT", 1)        # Result: true
        ObjectComparator.areEqual("A", "B")         # Result: false
    """

    @staticmethod
    def compare(value1: Any, operation: str, value2: Any) -> bool:
        """
        Perform comparison operation over two arguments.
        The operation can be performed over values of any type.

        :param value1: the first argument to compare

        :param operation: the comparison operation: "==" ("=", "EQ"), "!= " ("<>", "NE"); "<"/">"
                                                    ("LT"/"GT"), "<="/">=" ("LE"/"GE"); "LIKE".

        :param value2: the second argument to compare

        :return: result of the comparison operation
        """

        operation = operation.upper()

        if operation in ["=", "==", "EQ"]:
            return ObjectComparator.are_equal(value1, value2)
        if operation in ["!=", "<>", "NE"]:
            return ObjectComparator.are_not_equal(value1, value2)
        if operation in ["<", "LT"]:
            return ObjectComparator.is_less(value1, value2)
        if operation in ["<=", "LE", "LTE"]:
            return ObjectComparator.are_equal(value1, value2) or ObjectComparator.is_less(value1, value2)
        if operation in [">", "GT"]:
            return ObjectComparator.is_greater(value1, value2)
        if operation in [">=", "GE", "GTE"]:
            return ObjectComparator.are_equal(value1, value2) or ObjectComparator.is_greater(value1, value2)
        if operation == "LIKE":
            return ObjectComparator.match(value1, value2)

        return False

    @staticmethod
    def are_equal(value1: Any, value2: Any) -> bool:
        """
        Checks if two values are equal. The operation can be performed over values of any type.

        :param value1: the first args to compare

        :param value2: the second args to compare

        :return: true if values are equal and false otherwise
        """
        if value1 is None and value2 is None:
            return True
        if value1 is None or value2 is None:
            return False

        if hasattr(value1, '__eq__'):
            return value1.__eq__(value2)

        number1 = FloatConverter.to_nullable_float(value1)
        number2 = FloatConverter.to_nullable_float(value2)
        if number1 is not None and number2 is not None:
            return number1 == number2

        str1 = StringConverter.to_nullable_string(value1)
        str2 = StringConverter.to_nullable_string(value1)
        if str1 is not None and str2 is not None:
            return str1 == str2

        return value1 == value2

    @staticmethod
    def are_not_equal(value1: Any, value2: Any) -> bool:
        """
        Checks if two values are NOT equal. The operation can be performed over values of any type.

        :param value1: the first args to compare

        :param value2: the second args to compare

        :return: true if values are NOT equal and false otherwise
        """
        return not ObjectComparator.are_equal(value1, value2)

    @staticmethod
    def is_less(value1: Any, value2: Any) -> bool:
        """
        Checks if first args is less than the second one.
        The operation can be performed over numbers or strings.

        :param value1: the first args to compare

        :param value2: the second args to compare

        :return: true if the first args is less than second and false otherwise.
        """
        number1 = FloatConverter.to_nullable_float(value1)
        number2 = FloatConverter.to_nullable_float(value2)

        if number1 is None or number2 is None:
            return False

        return number1 < number2

    @staticmethod
    def is_greater(value1: Any, value2: Any) -> bool:
        """
        Checks if first args is greater than the second one.
        The operation can be performed over numbers or strings.

        :param value1: the first args to compare

        :param value2: the second args to compare

        :return: true if the first args is greater than second and false otherwise.
        """
        number1 = FloatConverter.to_nullable_float(value1)
        number2 = FloatConverter.to_nullable_float(value2)

        if number1 is None or number2 is None:
            return False

        return number1 > number2

    @staticmethod
    def match(value1: Any, regexp: Any) -> bool:
        """
        Checks if string matches a regular expression

        :param value1: a string args to match

        :param regexp: a regular expression string

        :return: true if the args matches regular expression and false otherwise.
        """
        if value1 is None and regexp is None:
            return True
        if value1 is None or regexp is None:
            return False

        string1 = StringConverter.to_string(value1)
        string2 = StringConverter.to_string(regexp)

        return re.match(string2, string1) is not None
