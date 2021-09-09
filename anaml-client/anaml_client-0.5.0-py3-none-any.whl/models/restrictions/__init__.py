"""Generated implementation of restrictions."""

# WARNING DO NOT EDIT
# This code was generated from restrictions.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import logging  # noqa: F401
import uuid  # noqa: F401
import typing  # noqa: F401
import jsonschema  # noqa: F401


@dataclasses.dataclass(frozen=True)
class AttributeRestriction:
    """Attribute restriction rule.
    
    Args:
        key (str): A data field.
        values (typing.Optional[typing.List[str]]): A data field.
    """
    
    key: str
    values: typing.Optional[typing.List[str]]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for AttributeRestriction data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string"
                },
                "values": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "array", "item": {"type": "string"}},
                    ]
                }
            },
            "required": [
                "key",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of AttributeRestriction.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeRestriction.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeRestriction(
                key=str(data["key"]),
                values=(lambda v: v and [str(v) for v in v])(data.get("values", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AttributeRestriction",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "key": str(self.key),
            "values": (lambda v: v and [str(v) for v in v])(self.values)
        }


@dataclasses.dataclass(frozen=True)
class LabelRestriction:
    """Label restriction rule.
    
    Args:
        text (str): A data field.
        emoji (typing.Optional[str]): A data field.
        colour (typing.Optional[str]): A data field.
    """
    
    text: str
    emoji: typing.Optional[str]
    colour: typing.Optional[str]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for LabelRestriction data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string"
                },
                "emoji": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "colour": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "text",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of LabelRestriction.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LabelRestriction.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LabelRestriction(
                text=str(data["text"]),
                emoji=(lambda v: v and str(v))(data.get("emoji", None)),
                colour=(lambda v: v and str(v))(data.get("colour", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing LabelRestriction",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "text": str(self.text),
            "emoji": (lambda v: v and str(v))(self.emoji),
            "colour": (lambda v: v and str(v))(self.colour)
        }


@dataclasses.dataclass(frozen=True)
class AllowedLabelsResponse:
    """Policy for labels permitted by the server configuration.
    
    Args:
        allowedLabels (typing.Optional[typing.List[LabelRestriction]]): A data field.
    """
    
    allowedLabels: typing.Optional[typing.List[LabelRestriction]]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for AllowedLabelsResponse data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "allowedLabels": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "array", "item": LabelRestriction.json_schema()},
                    ]
                }
            },
            "required": []
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of AllowedLabelsResponse.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AllowedLabelsResponse.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AllowedLabelsResponse(
                allowedLabels=(
                    lambda v: v and [LabelRestriction.from_json(v) for v in v]
                )(
                    data.get("allowedLabels", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AllowedLabelsResponse",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "allowedLabels": (lambda v: v and [v.to_json() for v in v])(self.allowedLabels)
        }


@dataclasses.dataclass(frozen=True)
class AllowedAttributesResponse:
    """Policy for attributes permitted by the server configuration.
    
    Args:
        allowedAttributes (typing.Optional[typing.List[AttributeRestriction]]): A data field.
    """
    
    allowedAttributes: typing.Optional[typing.List[AttributeRestriction]]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for AllowedAttributesResponse data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "allowedAttributes": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "array", "item": AttributeRestriction.json_schema()},
                    ]
                }
            },
            "required": []
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of AllowedAttributesResponse.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AllowedAttributesResponse.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AllowedAttributesResponse(
                allowedAttributes=(
                    lambda v: v and [AttributeRestriction.from_json(v) for v in v]
                )(
                    data.get("allowedAttributes", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AllowedAttributesResponse",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "allowedAttributes": (lambda v: v and [v.to_json() for v in v])(self.allowedAttributes)
        }
