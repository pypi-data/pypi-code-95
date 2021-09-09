"""Generated implementation of feature_id."""

# WARNING DO NOT EDIT
# This code was generated from feature-id.mcn

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
class FeatureId:
    """Unique identifier for a feature.
    
    Args:
        value (int): A data field.
    """
    
    value: int
    
    def __str__(self):
        """Return a str of the wrapped value."""
        return str(self.value)
    
    def __int__(self):
        """Return an int of the wrapped value."""
        return int(self.value)
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for FeatureId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: int):
        """Validate and parse JSON data into an instance of FeatureId.
        
        Args:
            data (int): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureId", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)


@dataclasses.dataclass(frozen=True)
class FeatureName:
    """Unique name for a feature.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self):
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for FeatureName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: str):
        """Validate and parse JSON data into an instance of FeatureName.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureName", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class FeatureVersionId:
    """Unique identifier of a specific versions of a feature.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self):
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for FeatureVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: uuid.UUID):
        """Validate and parse JSON data into an instance of FeatureVersionId.
        
        Args:
            data (uuid.UUID): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureVersionId", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
