"""Generated implementation of generated_features."""

# WARNING DO NOT EDIT
# This code was generated from generated-features.mcn

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
class FeatureData:
    """Map of feature data."""
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for FeatureData data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
            
            },
            "required": []
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of FeatureData.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureData.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureData(
                
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureData",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
        
        }


@dataclasses.dataclass(frozen=True)
class GeneratedFeatures:
    """Features generated for a specific entity.
    
    Args:
        id (str): A data field.
        date (datetime.date): A data field.
        features (FeatureData): A data field.
    """
    
    id: str
    date: datetime.date
    features: FeatureData
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for GeneratedFeatures data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string"
                },
                "date": {
                    "type": "string",
                    "format": "date"
                },
                "features": FeatureData.json_schema()
            },
            "required": [
                "id",
                "date",
                "features",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of GeneratedFeatures.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of GeneratedFeatures.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return GeneratedFeatures(
                id=str(data["id"]),
                date=datetime.date.fromisoformat(data["date"]),
                features=FeatureData.from_json(data["features"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing GeneratedFeatures",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "id": str(self.id),
            "date": self.date.isoformat(),
            "features": self.features.to_json()
        }
