"""Generated implementation of quality_rating."""

# WARNING DO NOT EDIT
# This code was generated from quality-rating.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import logging  # noqa: F401
import uuid  # noqa: F401
import typing  # noqa: F401
import jsonschema  # noqa: F401


class QualityRating(enum.Enum):
    """Data quality ratings."""
    Tin = "tin"
    Bronze = "bronze"
    Silver = "silver"
    Gold = "gold"
    Platinum = "platinum"
    
    @classmethod
    def json_schema(cls):
        """JSON schema for 'QualityRating'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "tin",
                        "bronze",
                        "silver",
                        "gold",
                        "platinum",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: str):
        """Validate and parse JSON data into an instance of QualityRating.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of QualityRating.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return QualityRating(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing QualityRating", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
