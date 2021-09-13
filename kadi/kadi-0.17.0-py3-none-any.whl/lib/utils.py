# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import math
import operator
import string
from collections import namedtuple
from datetime import datetime
from datetime import timezone
from importlib import import_module
from random import SystemRandom


class SimpleReprMixin:
    """Mixin to add a simple implementation of ``__repr__`` to a class.

    The provided implementation uses all instance or class attributes specified in the
    ``Meta.representation`` attribute of the inheriting class. It should be a list of
    strings specifying the attributes to use in the representation.

    **Example:**

    .. code-block:: python3

        class Foo:
            class Meta:
                representation = ["bar", "baz"]

            bar = 1

            baz = 2
    """

    def __repr__(self):
        attrs = ", ".join(
            f"{attr}={getattr(self, attr)!r}" for attr in self.Meta.representation
        )
        return f"{self.__class__.__name__}({attrs})"


def named_tuple(tuple_name, **kwargs):
    r"""Convenience function to build a ``namedtuple`` from keyword arguments.

    :param tuple_name: The name of the tuple.
    :param \**kwargs: The keys and values of the tuple.
    :return: The ``namedtuple`` instance.
    """
    NamedTuple = namedtuple(tuple_name, list(kwargs.keys()))
    return NamedTuple(*list(kwargs.values()))


def find_dict_in_list(dict_list, key, value):
    """Find a dictionary with a specific key and value in a list.

    :param dict_list: A list of dictionaries to search.
    :param key: The key to search for.
    :param value: The value to search for.
    :return: The dictionary or ``None`` if it was not found.
    """
    for item in dict_list:
        if key in item and item[key] == value:
            return item

    return None


def get_truth(left, op, right):
    """Compare two values with a given operator.

    :param left: The left value.
    :param op: One of ``"=="``, ``"!="``, ``">"``, ``"<"``, ``">="`` or ``"<="``.
    :param right: The right value.
    :return: The boolean result of the comparison.
    """
    ops = {
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
    }
    return ops[op](left, right)


def rgetattr(obj, name, default=None):
    """Get a nested attribute of an object.

    :param obj: The object to get the attribute from.
    :param name: The name of the attribute in the form of ``"foo.bar.baz"``.
    :param default: (optional) The default value to return if the attribute could not be
        found.
    :return: The attribute or the default value if it could not be found.
    """
    attr = obj

    for _name in name.split("."):
        try:
            attr = getattr(attr, _name)
        except AttributeError:
            return default

    return attr


def get_class_by_name(name):
    """Get a class given its name.

    :param name: The complete name of the class in the form of ``"foo.bar.Baz"``.
    :return: The class or ``None`` if it could not be found.
    """
    names = name.rsplit(".", 1)
    if len(names) <= 1:
        return None

    try:
        mod = import_module(names[0])
    except ImportError:
        return None

    return getattr(mod, names[1], None)


def is_special_float(value):
    """Check if a float value is a special value, i.e. ``nan`` or ``inf``.

    :param value: The float value to check.
    :return: ``True`` if the value is a special float value, ``False`` otherwise.
    """
    return math.isnan(value) or math.isinf(value)


def is_iterable(value, include_string=False):
    """Check if a value is an iterable.

    :param value: The value to check.
    :param include_string: (optional) Flag indicating whether a string value should be
        treated as a valid iterable or not.
    :return: ``True`` if the value is iterable, ``False`` otherwise.
    """
    if not include_string and isinstance(value, str):
        return False

    try:
        iter(value)
    except TypeError:
        return False

    return True


def utcnow():
    """Create a timezone aware datetime object of the current time in UTC.

    :return: A datetime object as specified in Python's ``datetime`` module.
    """
    return datetime.now(timezone.utc)


def random_alnum(length=16):
    """Generate a (cryprographically secure) random alphanumeric string.

    :param length: (optional) The length of the string.
    :return: The generated string.
    """

    alphanum = string.ascii_letters + string.digits
    return "".join(SystemRandom().choice(alphanum) for _ in range(length))


def compact_json(data):
    """Serialize data to a JSON formatted string without any unnecessary spaces.

    :param data: The data to serialize.
    :return: The JSON formatted string.
    """
    return json.dumps(data, separators=(",", ":"))
