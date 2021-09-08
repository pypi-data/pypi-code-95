# SPDX-License-Identifier: MIT
# Copyright 2021 Max-Julian Pogner <max-julian@pogner.at>
# Copyright 2021 Tobias Hajszan <tobias.hajszan@outlook.com>
# This file forms part of the 'enijo-connector' project, see the
# project's readme, notes, and other documentation for further details.

"""
This module provides some builders to some of the model classes
(see package rest_api_client.models)

While alignment with builder patterns predominent in the python
ecosystem is a task for the future (which first demands properly
analysing what builder patterns are actually widely used within the
python ecosystem AND practical for the use-case at hand), currently
the following pattern is follows.

Instances of class ``FooBarBuilder``, each, build an instance of class
``FooBar``. The bare constructor of the builder class starts in a state
that builds a minimal instance; even to the point that the remote API
maybe would reject such instance. Class methods may be present that
provide a more rich initial state, see the respective builder class'
docstring.

Given an instance of a builder, to set "simple" attributes of the
subject instance, like string or numbers, use the ``set`` method with
keyword arguments. For example

  mybldr.set(name="Some Name")

will set, or cause the eventually built instance to have value
``"Some Name"`` for the attribute ``name``. For method chaining, the
``set()`` method returns the builder again.

To set more complex attributes, nested builders are used. The nested
builder is returned by a method with that attribute's name, e.g.
attribute ``person`` and method ``person()``. This nested builder then
is used the same way as the parent builder, providing a ``set()`` method
for "simple" attributes and may even provide even more nested builders
in the same way as described above.
Additionally a nested builder has a ``return_up()`` method which returns
the parent builder again; this is to facility certain styles of method
chaining.


TODO: At the moment, all builders are manually written. But due to the
generic nature of the structure, all builders could be auto-generated
from the respective models, or directly from the openapi specification.
"""

from __future__ import annotations

import datetime

from enijo.connector.rest_api_client.models.metadata import Metadata
from enijo.connector.rest_api_client.models.metadata_creators_item import (
    MetadataCreatorsItem,
)
from enijo.connector.rest_api_client.models.metadata_creators_item_person_or_org import (
    MetadataCreatorsItemPersonOrOrg,
)
from enijo.connector.rest_api_client.models.metadata_creators_item_person_or_org_type import (
    MetadataCreatorsItemPersonOrOrgType,
)
from enijo.connector.rest_api_client.models.metadata_resource_type import (
    MetadataResourceType,
)
from enijo.connector.rest_api_client.models.record_new import RecordNew
from enijo.connector.rest_api_client.models.resource_type_id import ResourceTypeId


class RecordNewBuilder:
    """
    Instances of this builder class eventually build instances of
    class models.record_new.RecordNew.
    """

    def __init__(self, *, parent=None):
        """
        constructs a new builder with minimal attribute values stored
        for the eventually built object.

        Args:
            parent: the parent builder
        """
        self._parent = parent
        self._attributes = dict()
        self._nested = dict()

    @classmethod
    def with_defaults(Clazz) -> RecordNewBuilder:
        """
        constructs a new builder with certain attribute values already
        set to default values.

        The exact default values are subject to change, but strive to
        be usable for the largest (sub-)group of users.

        Implementation Notes: Currently, the following defaults are
        set (but this list is subject to change):

          - metadata().resource_type().set(id=ResourceTypeId.DATASET)
          - metadata().set(publication_date=datetime.date.today().isoformat())
        """
        bldr = Clazz()
        bldr.metadata().resource_type().set(id=ResourceTypeId.DATASET)
        bldr.metadata().set(publication_date=datetime.date.today().isoformat())
        return bldr

    def set(self, **kwargs) -> RecordNewBuilder:
        """
        Set the given values for the given simple attributes.

        Use value UNSET to explicitely unset/clear an attribute.
        """
        if 0 < len(kwargs):
            raise ValueError("the given attributes do not exist", kwargs.keys())
        return self

    def metadata(self) -> MetadataBuilder:
        """
        Returns the nested builder for the complex attribute of the
        same name.
        """
        if "metadata" not in self._nested:
            self._nested["metadata"] = MetadataBuilder(parent=self)
        return self._nested["metadata"]

    def return_up(self):
        """
        Returns:
            the parent builder
        """
        return self._parent

    def build(self) -> RecordNew:
        """
        Returns a new instance of the built class. The new instance is
        independent from the builder.
        """
        ctorargs = dict(self._attributes.items())
        for (name, attribute) in self._nested.items():
            if isinstance(attribute, list):
                value = list()
                for bldr in attribute:
                    value.append(bldr.build())
            else:
                value = attribute.build()
            ctorargs[name] = value
        obj = RecordNew(**ctorargs)
        return obj


class MetadataBuilder:
    """
    Instances of this builder class eventually build instances of
    class models.metadata.Metadata.
    """

    def __init__(self, *, parent=None):
        """
        constructs a new builder with minimal attribute values stored
        for the eventually built object.

        Args:
            parent: the parent builder
        """
        self._parent = parent
        self._attributes = dict()
        self._nested = dict()

    def set(self, *, title=None, description=None, publication_date=None, **kwargs) -> MetadataBuilder:
        """
        Set the given values for the given simple attributes.

        Use value UNSET to explicitely unset/clear an attribute.
        """
        if None != title:
            self._attributes["title"] = title
        if None != publication_date:
            self._attributes["publication_date"] = publication_date
        if None != description:
            self._attributes["description"] = description
        if 0 < len(kwargs):
            raise ValueError("the given attributes do not exist", kwargs.keys())
        return self

    def resource_type(self) -> MetadataResourceTypeBuilder:
        """
        Returns the nested builder for the complex attribute of the
        same name.
        """
        if "resource_type" not in self._nested:
            self._nested["resource_type"] = MetadataResourceTypeBuilder(parent=self)
        return self._nested["resource_type"]

    def creator(self) -> MetadataCreatorsItemBuilder:
        """
        Adds a new item to the complex attribute ``creators`` and
        returns the builder for that new item.
        """
        if "creators" not in self._nested:
            self._nested["creators"] = list()
        bldr = MetadataCreatorsItemBuilder(parent=self)
        self._nested["creators"].append(bldr)
        return bldr

    def return_up(self):
        """
        Returns:
            the parent builder
        """
        return self._parent

    def build(self) -> Metadata:
        """
        Returns a new instance of the built class. The new instance is
        independent from the builder.
        """
        ctorargs = dict(self._attributes.items())
        for (name, attribute) in self._nested.items():
            if isinstance(attribute, list):
                value = list()
                for bldr in attribute:
                    value.append(bldr.build())
            else:
                value = attribute.build()
            ctorargs[name] = value
        obj = Metadata(**ctorargs)
        return obj


class MetadataResourceTypeBuilder:
    """
    Instances of this builder class eventually build instances of
    class models.metadata.MetadataResourceType.
    """

    def __init__(self, *, parent=None):
        """
        constructs a new builder with minimal attribute values stored
        for the eventually built object.

        Args:
            parent: the parent builder
        """
        self._parent = parent
        self._attributes = dict()
        self._nested = dict()

    def set(self, *, id=None, **kwargs) -> MetadataResourceTypeBuilder:
        """
        Set the given values for the given simple attributes.

        Use value UNSET to explicitely unset/clear an attribute.
        """
        if None != id:
            self._attributes["id"] = id
        if 0 < len(kwargs):
            raise ValueError("the given attributes do not exist", kwargs.keys())
        return self

    def resource_type(self) -> MetadataResourceTypeBuilder:
        """
        Returns the nested builder for the complex attribute of the
        same name.
        """
        if "resource_type" not in self._nested:
            self._nested["resource_type"] = MetadataResourceTypeBuilder(parent=self)
        return self._nested["resource_type"]

    def creator(self) -> MetadataCreatorsItemBuilder:
        """
        Adds a new item to the complex attribute ``creators`` and
        returns the builder for that new item.
        """
        if "creators" not in self._nested:
            self._nested["creators"] = list()
        bldr = MetadataCreatorsItemBuilder(parent=self)
        self._nested["creators"].append(bldr)
        return bldr

    def return_up(self):
        """
        Returns:
            the parent builder
        """
        return self._parent

    def build(self) -> MetadataResourceType:
        """
        Returns a new instance of the built class. The new instance is
        independent from the builder.
        """
        ctorargs = dict(self._attributes.items())
        for (name, attribute) in self._nested.items():
            if isinstance(attribute, list):
                value = list()
                for bldr in attribute:
                    value.append(bldr.build())
            else:
                value = attribute.build()
            ctorargs[name] = value
        obj = MetadataResourceType(**ctorargs)
        return obj


class MetadataCreatorsItemBuilder:
    """
    Instances of this builder class eventually build instances of
    class models.metadata_creators_item.MetadataCreatorsItem
    """

    def __init__(self, *, parent=None):
        """
        constructs a new builder with minimal attribute values stored
        for the eventually built object.

        Args:
            parent: the parent builder
        """
        self._parent = parent
        self._attributes = dict()
        self._nested = dict()

    def set(self, **kwargs) -> MetadataCreatorsItemBuilder:
        """
        Set the given values for the given simple attributes.

        Use value UNSET to explicitely unset/clear an attribute.
        """
        if 0 < len(kwargs):
            raise ValueError("the given attributes do not exist", kwargs.keys())
        return self

    def person(self) -> MetadataCreatorsItemPersonOrOrgBuilder:
        """
        Returns the nested builder for the complex attribute
        ``person_or_org``, already with defaults set to make the
        value a person-
        """
        if "person_or_org" not in self._nested:
            self._nested["person_or_org"] = MetadataCreatorsItemPersonOrOrgBuilder(
                parent=self
            )
        self._nested["person_or_org"].set(
            type=MetadataCreatorsItemPersonOrOrgType.PERSONAL
        )
        return self._nested["person_or_org"]

    def return_up(self):
        """
        Returns:
            the parent builder
        """
        return self._parent

    def build(self) -> MetadataCreatorsItem:
        """
        Returns a new instance of the built class. The new instance is
        independent from the builder.
        """
        ctorargs = dict(self._attributes.items())
        for (name, attribute) in self._nested.items():
            if isinstance(attribute, list):
                value = list()
                for bldr in attribute:
                    value.append(bldr.build())
            else:
                value = attribute.build()
            ctorargs[name] = value
        obj = MetadataCreatorsItem(**ctorargs)
        return obj


class MetadataCreatorsItemPersonOrOrgBuilder:
    """
    Instances of this builder class eventually build instances of
    class models.metadata_creators_item_person_or_org.MetadataCreatorsItemPersonOrOrg
    """

    def __init__(self, *, parent=None):
        """
        constructs a new builder with minimal attribute values stored
        for the eventually built object.

        Args:
            parent: the parent builder
        """
        self._parent = parent
        self._attributes = dict()
        self._nested = dict()

    def set(
        self, *, type=None, given_name=None, family_name=None, **kwargs
    ) -> MetadataCreatorsItemPersonOrOrgBuilder:
        """
        Set the given values for the given simple attributes.

        Use value UNSET to explicitely unset/clear an attribute.
        """
        if None != type:
            self._attributes["type"] = type
        if None != given_name:
            self._attributes["given_name"] = given_name
        if None != family_name:
            self._attributes["family_name"] = family_name
        if 0 < len(kwargs):
            raise ValueError("the given attributes do not exist", kwargs.keys())
        return self

    def return_up(self):
        """
        Returns:
            the parent builder
        """
        return self._parent

    def build(self) -> MetadataCreatorsItemPersonOrOrg:
        """
        Returns a new instance of the built class. The new instance is
        independent from the builder.
        """
        ctorargs = dict(self._attributes.items())
        for (name, attribute) in self._nested.items():
            if isinstance(attribute, list):
                value = list()
                for bldr in attribute:
                    value.append(bldr.build())
            else:
                value = attribute.build()
            ctorargs[name] = value
        obj = MetadataCreatorsItemPersonOrOrg(**ctorargs)
        return obj
