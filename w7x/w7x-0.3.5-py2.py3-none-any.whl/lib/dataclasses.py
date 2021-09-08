"""
Use this module like dataclasses but dataclasses is wrapped (same behaviour) and property_field
and alias_field are added.

Examples:
    >>> import w7x.lib.dataclasses as dataclasses
    >>> class A:
    ...     def __init__(self, **kwargs):
    ...         if not hasattr(self, '_children'):
    ...             self._children = []


    >>> @dataclasses.dataclass
    ... class B(A):
    ...     # _children: int = 0
    ...     x: list = dataclasses.alias_field('_children', default_factory=lambda: [42])
    ...     y: int = 8
    ...
    ...     def __post_init__(self, **kwargs):
    ...         assert self.y == 8
    ...         self.y = 78
    ...         super().__init__(**kwargs)


    >>> b = B(); b
    B(x=[42], y=78)
    >>> assert b._children == b.x

    'x' is an alias so it is not part of __dict__, only property referencing '_children'
    >>> assert 'x' not in b.__dict__
    >>> assert '_children' in b.__dict__
    >>> b.__dict__
    {'_children': [42], 'y': 78}
    >>> b.__dataclass_fields__['x'].metadata['alias']
    '_children'
"""
import dataclasses
from dataclasses import *  # noqa: F403,F401 pylint:disable=unused-wildcard-import,wildcard-import


# pylint:disable=invalid-name
class property_field:
    """
    Field to use in dataclasses to forward the attribute to a property
    """

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        self._field = dataclasses.field(**kwargs)
        self._property = property(fget, fset, fdel, doc)

    # pylint:disable=missing-function-docstring
    def getter(self, fget):
        self._property = self._property.getter(fget)
        return self

    def setter(self, fset):
        self._property = self._property.setter(fset)
        return self

    def deleter(self, fdel):
        self._property = self._property.deleter(fdel)
        return self


# pylint:disable=invalid-name
class alias_field(property_field):
    """
    Field to use in dataclasses to forward a field as alias to another attribute to a property
    """

    # pylint:disable=too-many-arguments
    def __init__(self, alias, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        if fget is None:

            def fget(self):
                return getattr(self, alias)

        if fset is None:

            def fset(self, value):
                setattr(self, alias, value)

        if "metadata" not in kwargs:
            kwargs.setdefault("metadata", {})
        kwargs["metadata"]["alias"] = alias
        super().__init__(fget=fget, fset=fset, fdel=fdel, doc=doc, **kwargs)


class children_alias(alias_field):
    """
    Specific alias_field for '_children' of the composite pattern
    """

    def __init__(self, **kwargs):
        alias = "_children"

        def fset(self, children):
            setattr(self, alias, [])
            for child in children:
                self.add(child)

        super().__init__(alias, fset=fset, **kwargs)


def is_alias_field(field):
    return "alias" in field.metadata


# pylint:disable=function-redefined
def dataclass(cls=None, **kwargs):
    """
    Wrapper around dataclass. Adding integration for property_field and alias_field
    """
    if cls is None:
        # @property_dataclass(...)
        # def ...
        return lambda cls: dataclass(cls, **kwargs)  # pylint:disable=unnecessary-lambda
    # @property_dataclass
    # def ...
    properties = {}
    for attr in dir(cls):
        if isinstance(getattr(cls, attr), property_field):
            _field = getattr(cls, attr)
            properties[attr] = _field._property  # pylint:disable=protected-access
            setattr(cls, attr, _field._field)  # pylint:disable=protected-access

    wrapped_cls = dataclasses.dataclass(**kwargs)(cls)

    for attr, prop in properties.items():
        setattr(wrapped_cls, attr, prop)
    return wrapped_cls


if __name__ == "__main__":
    import doctest

    doctest.testmod()
