"""Generated implementation of item."""

# WARNING DO NOT EDIT
# This code was generated from item.mcn

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
class ItemId:
    """Identifier of item and unique per ItemType.
    
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
        """Return the JSON schema for ItemId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: int):
        """Validate and parse JSON data into an instance of ItemId.
        
        Args:
            data (int): JSON data to validate and parse.
        
        Returns:
            An instance of ItemId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ItemId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ItemId", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)


class ItemType(enum.Enum):
    """Type of item."""
    EntityItemType = "entityitemtype"
    EntityMappingItemType = "entitymappingitemtype"
    FeatureItemType = "featureitemtype"
    FeatureTemplateItemType = "featuretemplateitemtype"
    FeatureSetItemType = "featuresetitemtype"
    FeatureStoreItemType = "featurestoreitemtype"
    TableItemType = "tableitemtype"
    
    @classmethod
    def json_schema(cls):
        """JSON schema for 'ItemType'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "entityitemtype",
                        "entitymappingitemtype",
                        "featureitemtype",
                        "featuretemplateitemtype",
                        "featuresetitemtype",
                        "featurestoreitemtype",
                        "tableitemtype",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: str):
        """Validate and parse JSON data into an instance of ItemType.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of ItemType.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ItemType(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ItemType", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}


@dataclasses.dataclass(frozen=True)
class ItemData:
    """Item data including id and type.
    
    Args:
        id (ItemId): A data field.
        type (ItemType): A data field.
    """
    
    id: ItemId
    type: ItemType
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for ItemData data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": ItemId.json_schema(),
                "type": ItemType.json_schema()
            },
            "required": [
                "id",
                "type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of ItemData.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ItemData.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ItemData(
                id=ItemId.from_json(data["id"]),
                type=ItemType.from_json(data["type"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ItemData",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "id": self.id.to_json(),
            "type": self.type.to_json()
        }
