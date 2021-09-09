"""Generated implementation of destination_reference."""

# WARNING DO NOT EDIT
# This code was generated from destination-reference.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import logging  # noqa: F401
import uuid  # noqa: F401
import typing  # noqa: F401
import jsonschema  # noqa: F401

from ..destination import DestinationId


@dataclasses.dataclass(frozen=True)
class DestinationReference(abc.ABC):
    """A location to store data in a destination data store.
    
    Args:
        destinationId (DestinationId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    destinationId: DestinationId
    
    @classmethod
    def json_schema(cls):
        """JSON schema for variant DestinationReference.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        adt_types = [klass.ADT_TYPE for klass in cls.__subclasses__()]
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": adt_types
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of DestinationReference.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of DestinationReference.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            adt_type = data.get("adt_type", None)
            for klass in cls.__subclasses__():
                if klass.ADT_TYPE == adt_type:
                    return klass.from_json(data)
            raise ValueError("Unknown adt_type: '{ty}'".format(ty=adt_type))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing DestinationReference", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class FolderDestinationReference(DestinationReference):
    """Store output data in a folder in the given destination.
    
    Args:
        destinationId (DestinationId): A data field.
        folder (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "folder"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    destinationId: DestinationId
    folder: str
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for FolderDestinationReference data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "destinationId": DestinationId.json_schema(),
                "folder": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "destinationId",
                "folder",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of FolderDestinationReference.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FolderDestinationReference.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FolderDestinationReference(
                destinationId=DestinationId.from_json(data["destinationId"]),
                folder=str(data["folder"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FolderDestinationReference",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "destinationId": self.destinationId.to_json(),
            "folder": str(self.folder)
        }


@dataclasses.dataclass(frozen=True)
class TableDestinationReference(DestinationReference):
    """Store output data in a table in the given destination.
    
    Args:
        destinationId (DestinationId): A data field.
        tableName (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "table"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    destinationId: DestinationId
    tableName: str
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for TableDestinationReference data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "destinationId": DestinationId.json_schema(),
                "tableName": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "destinationId",
                "tableName",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of TableDestinationReference.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableDestinationReference.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableDestinationReference(
                destinationId=DestinationId.from_json(data["destinationId"]),
                tableName=str(data["tableName"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableDestinationReference",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "destinationId": self.destinationId.to_json(),
            "tableName": str(self.tableName)
        }


@dataclasses.dataclass(frozen=True)
class TopicDestinationReference(DestinationReference):
    """Store output data in a topic in the given destination.
    
    Args:
        destinationId (DestinationId): A data field.
        topic (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "topic"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    destinationId: DestinationId
    topic: str
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for TopicDestinationReference data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "destinationId": DestinationId.json_schema(),
                "topic": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "destinationId",
                "topic",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of TopicDestinationReference.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TopicDestinationReference.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TopicDestinationReference(
                destinationId=DestinationId.from_json(data["destinationId"]),
                topic=str(data["topic"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TopicDestinationReference",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "destinationId": self.destinationId.to_json(),
            "topic": str(self.topic)
        }
