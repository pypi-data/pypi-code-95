# -*- encoding: utf-8 -*-
from copy import copy

__all__ = ["Attr", "YwhApiObject"]

class Attr(object):
    """
    Class Attribute for forgery mecanism and set attribute in
        YwhApiObject
    """

    def __init__(self, name, type_=None, default=None):
        """
        Initialize Attr

        :param str name: attribute name
        :param type type_: If supplied set a control type
        :param object default: default value (None by default), according to type_ if is set
        """
        if type_ is not None and not isinstance(type_, type):
            raise TypeError(
                "type_ argument need to be instance of type `type`"
            )
        if not isinstance(name, str):
            raise TypeError("name argument need to be instance of type `str`")
        self.type = type_
        self.value = default
        self.name = name

    def control(self, value):
        """
        Control if the providing value is in aggreement with
        this Attr object.

        :param object value: value to control
        :return: True if aggree, False otherwise
        :rtype: bool
        """
        return (
            value is None or self.type is None or isinstance(value, self.type)
        )

    def __str__(self):
        return "name : {}, value : {}, type : {}".format(
            self.name, self.value, self.type
        )

    def __repr__(self):
        return self.__str__()


class YwhApiObject(object):
    """
    Yes We Hack Api framework base class.

    This class need to be inherited.
    It declare attribute setting mecanism and forgery element recuperation
    """

    def __init__(self, **kwargs):
        """
        Initialize YwhApiObject and set kwargs element
            according to _attrs class attribute.

        :param `**kwargs`: named parameters according to _attrs attributes
            names.
        """
        self.__set_attrs__(**kwargs)

    @classmethod
    def __get_attrs__(cls):
        """return _attrs value for inherited class caller"""
        return cls._attrs

    def __setattr__(self, name, value):
        """
        Set an attribute with `name` name and value `value`.

        It control the given value and raise TypeError if value is
            not in aggreement with the Attr attibute.

        :param str name: instance attribute name
        :param object value: instance attribute value
        :raise: TypeError if the value is incorrect
        """
        item = self.__get_elem__(name)
        if not item.control(value):
            raise TypeError(
                "value `{}` in `{}` class need to be of type `{}` instead of `{}`".format(
                    name, type(self), item.type, type(value)
                )
            )
        object.__setattr__(self, name, value)

    def __get_elem__(self, name):
        """
        Return the Attr instance for the given name.

        :param str name: name of the attribute
        :return: Attr instance corresponding to param name
        :rtype: Attr
        """
        return [i for i in self.__get_attrs__() if i.name == name][0]

    def __set_attrs__(self, **kwargs):
        """Set all element from _attrs with value in kwargs if exist"""
        attrs = self.__get_attrs__()
        for attr in attrs:
            name = attr.name
            if name in kwargs:
                value = kwargs[name]
            else:
                value = copy(attr.value)
            self.__setattr__(name, value)

    def to_dict(self):
        dict_repr = {}
        based_dict = self.__dict__
        for attr in self._attrs:
            if isinstance(based_dict[attr.name], YwhApiObject):
                value = based_dict[attr.name].to_dict()
            else:
                value = based_dict[attr.name]
            dict_repr[attr.name] = value
        return dict_repr
