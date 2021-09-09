"""Generated implementation of webhook."""

# WARNING DO NOT EDIT
# This code was generated from webhook.mcn

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
class WebhookId:
    """Unique identifier of a webhook.
    
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
        """Return the JSON schema for WebhookId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: int):
        """Validate and parse JSON data into an instance of WebhookId.
        
        Args:
            data (int): JSON data to validate and parse.
        
        Returns:
            An instance of WebhookId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return WebhookId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing WebhookId", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)


@dataclasses.dataclass(frozen=True)
class WebhookName:
    """Unique name of a webhook.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self):
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for WebhookName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: str):
        """Validate and parse JSON data into an instance of WebhookName.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of WebhookName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return WebhookName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing WebhookName", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EmptyRecord:
    """As yet empty webhook configuration."""
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for EmptyRecord data.
        
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
        """Validate and parse JSON data into an instance of EmptyRecord.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EmptyRecord.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EmptyRecord(
                
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EmptyRecord",
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
class Webhook:
    """Configuration for a webhook.
    
    Args:
        id (WebhookId): A data field.
        name (WebhookName): A data field.
        description (str): A data field.
        url (str): A data field.
        mergeRequests (typing.Optional[EmptyRecord]): A data field.
        mergeRequestComments (typing.Optional[EmptyRecord]): A data field.
        commits (typing.Optional[EmptyRecord]): A data field.
        featureStoreRuns (typing.Optional[EmptyRecord]): A data field.
        monitoringRuns (typing.Optional[EmptyRecord]): A data field.
        cachingRuns (typing.Optional[EmptyRecord]): A data field.
    """
    
    id: WebhookId
    name: WebhookName
    description: str
    url: str
    mergeRequests: typing.Optional[EmptyRecord]
    mergeRequestComments: typing.Optional[EmptyRecord]
    commits: typing.Optional[EmptyRecord]
    featureStoreRuns: typing.Optional[EmptyRecord]
    monitoringRuns: typing.Optional[EmptyRecord]
    cachingRuns: typing.Optional[EmptyRecord]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for Webhook data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": WebhookId.json_schema(),
                "name": WebhookName.json_schema(),
                "description": {
                    "type": "string"
                },
                "url": {
                    "type": "string"
                },
                "mergeRequests": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                },
                "mergeRequestComments": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                },
                "commits": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                },
                "featureStoreRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                },
                "monitoringRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                },
                "cachingRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                }
            },
            "required": [
                "id",
                "name",
                "description",
                "url",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of Webhook.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Webhook.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Webhook(
                id=WebhookId.from_json(data["id"]),
                name=WebhookName.from_json(data["name"]),
                description=str(data["description"]),
                url=str(data["url"]),
                mergeRequests=(
                    lambda v: v and EmptyRecord.from_json(v)
                )(
                    data.get("mergeRequests", None)
                ),
                mergeRequestComments=(
                    lambda v: v and EmptyRecord.from_json(v)
                )(
                    data.get("mergeRequestComments", None)
                ),
                commits=(lambda v: v and EmptyRecord.from_json(v))(data.get("commits", None)),
                featureStoreRuns=(
                    lambda v: v and EmptyRecord.from_json(v)
                )(
                    data.get("featureStoreRuns", None)
                ),
                monitoringRuns=(
                    lambda v: v and EmptyRecord.from_json(v)
                )(
                    data.get("monitoringRuns", None)
                ),
                cachingRuns=(
                    lambda v: v and EmptyRecord.from_json(v)
                )(
                    data.get("cachingRuns", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Webhook",
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
            "name": self.name.to_json(),
            "description": str(self.description),
            "url": str(self.url),
            "mergeRequests": (lambda v: v and v.to_json())(self.mergeRequests),
            "mergeRequestComments": (lambda v: v and v.to_json())(self.mergeRequestComments),
            "commits": (lambda v: v and v.to_json())(self.commits),
            "featureStoreRuns": (lambda v: v and v.to_json())(self.featureStoreRuns),
            "monitoringRuns": (lambda v: v and v.to_json())(self.monitoringRuns),
            "cachingRuns": (lambda v: v and v.to_json())(self.cachingRuns)
        }


@dataclasses.dataclass(frozen=True)
class WebhookCreationRequest:
    """Request to create or update a webhook.
    
    Args:
        id (WebhookId): A data field.
        name (WebhookName): A data field.
        description (str): A data field.
        url (str): A data field.
        mergeRequests (typing.Optional[EmptyRecord]): A data field.
        mergeRequestComments (typing.Optional[EmptyRecord]): A data field.
        commits (typing.Optional[EmptyRecord]): A data field.
        featureStoreRuns (typing.Optional[EmptyRecord]): A data field.
        monitoringRuns (typing.Optional[EmptyRecord]): A data field.
        cachingRuns (typing.Optional[EmptyRecord]): A data field.
    """
    
    id: WebhookId
    name: WebhookName
    description: str
    url: str
    mergeRequests: typing.Optional[EmptyRecord]
    mergeRequestComments: typing.Optional[EmptyRecord]
    commits: typing.Optional[EmptyRecord]
    featureStoreRuns: typing.Optional[EmptyRecord]
    monitoringRuns: typing.Optional[EmptyRecord]
    cachingRuns: typing.Optional[EmptyRecord]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for WebhookCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": WebhookId.json_schema(),
                "name": WebhookName.json_schema(),
                "description": {
                    "type": "string"
                },
                "url": {
                    "type": "string"
                },
                "mergeRequests": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                },
                "mergeRequestComments": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                },
                "commits": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                },
                "featureStoreRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                },
                "monitoringRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                },
                "cachingRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EmptyRecord.json_schema(),
                    ]
                }
            },
            "required": [
                "id",
                "name",
                "description",
                "url",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of WebhookCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of WebhookCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return WebhookCreationRequest(
                id=WebhookId.from_json(data["id"]),
                name=WebhookName.from_json(data["name"]),
                description=str(data["description"]),
                url=str(data["url"]),
                mergeRequests=(
                    lambda v: v and EmptyRecord.from_json(v)
                )(
                    data.get("mergeRequests", None)
                ),
                mergeRequestComments=(
                    lambda v: v and EmptyRecord.from_json(v)
                )(
                    data.get("mergeRequestComments", None)
                ),
                commits=(lambda v: v and EmptyRecord.from_json(v))(data.get("commits", None)),
                featureStoreRuns=(
                    lambda v: v and EmptyRecord.from_json(v)
                )(
                    data.get("featureStoreRuns", None)
                ),
                monitoringRuns=(
                    lambda v: v and EmptyRecord.from_json(v)
                )(
                    data.get("monitoringRuns", None)
                ),
                cachingRuns=(
                    lambda v: v and EmptyRecord.from_json(v)
                )(
                    data.get("cachingRuns", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing WebhookCreationRequest",
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
            "name": self.name.to_json(),
            "description": str(self.description),
            "url": str(self.url),
            "mergeRequests": (lambda v: v and v.to_json())(self.mergeRequests),
            "mergeRequestComments": (lambda v: v and v.to_json())(self.mergeRequestComments),
            "commits": (lambda v: v and v.to_json())(self.commits),
            "featureStoreRuns": (lambda v: v and v.to_json())(self.featureStoreRuns),
            "monitoringRuns": (lambda v: v and v.to_json())(self.monitoringRuns),
            "cachingRuns": (lambda v: v and v.to_json())(self.cachingRuns)
        }
