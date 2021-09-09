"""Generated implementation of user_group."""

# WARNING DO NOT EDIT
# This code was generated from user-group.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import logging  # noqa: F401
import uuid  # noqa: F401
import typing  # noqa: F401
import jsonschema  # noqa: F401

from ..roles import Role
from ..user import UserId


@dataclasses.dataclass(frozen=True)
class UserGroupId:
    """Unique identifier for a user group.
    
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
        """Return the JSON schema for UserGroupId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: int):
        """Validate and parse JSON data into an instance of UserGroupId.
        
        Args:
            data (int): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserGroupId", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)


@dataclasses.dataclass(frozen=True)
class UserGroupVersionId:
    """Unique identifier a specific version of a user group.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self):
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for UserGroupVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: uuid.UUID):
        """Validate and parse JSON data into an instance of UserGroupVersionId.
        
        Args:
            data (uuid.UUID): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserGroupVersionId", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class UserGroupName:
    """Unique name of a user group.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self):
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for UserGroupName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: str):
        """Validate and parse JSON data into an instance of UserGroupName.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserGroupName", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class UserGroup:
    """Group of Anaml users.
    
    Args:
        id (UserGroupId): A data field.
        version (UserGroupVersionId): A data field.
        name (UserGroupName): A data field.
        description (str): A data field.
        members (typing.List[UserId]): A data field.
        created (datetime.datetime): A data field.
        modified (datetime.datetime): A data field.
        roles (typing.List[Role]): A data field.
        predecessor (typing.Optional[UserGroupVersionId]): A data field.
    """
    
    id: UserGroupId
    version: UserGroupVersionId
    name: UserGroupName
    description: str
    members: typing.List[UserId]
    created: datetime.datetime
    modified: datetime.datetime
    roles: typing.List[Role]
    predecessor: typing.Optional[UserGroupVersionId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for UserGroup data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": UserGroupId.json_schema(),
                "version": UserGroupVersionId.json_schema(),
                "name": UserGroupName.json_schema(),
                "description": {
                    "type": "string"
                },
                "members": {
                    "type": "array",
                    "item": UserId.json_schema()
                },
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "modified": {
                    "type": "string",
                    "format": "date-time"
                },
                "roles": {
                    "type": "array",
                    "item": Role.json_schema()
                },
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        UserGroupVersionId.json_schema(),
                    ]
                }
            },
            "required": [
                "id",
                "version",
                "name",
                "description",
                "members",
                "created",
                "modified",
                "roles",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of UserGroup.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroup.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroup(
                id=UserGroupId.from_json(data["id"]),
                version=UserGroupVersionId.from_json(data["version"]),
                name=UserGroupName.from_json(data["name"]),
                description=str(data["description"]),
                members=[UserId.from_json(v) for v in data["members"]],
                created=datetime.datetime.strptime(data["created"], '%Y-%m-%dT%H:%M:%S.%f%z'),
                modified=datetime.datetime.strptime(data["modified"], '%Y-%m-%dT%H:%M:%S.%f%z'),
                roles=[Role.from_json(v) for v in data["roles"]],
                predecessor=(
                    lambda v: v and UserGroupVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserGroup",
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
            "version": self.version.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "members": [v.to_json() for v in self.members],
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "modified": self.modified.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "roles": [v.to_json() for v in self.roles],
            "predecessor": (lambda v: v and v.to_json())(self.predecessor)
        }


@dataclasses.dataclass(frozen=True)
class UserGroupCreationRequest:
    """Request to create a new user group.
    
    Args:
        name (UserGroupName): A data field.
        description (str): A data field.
        roles (typing.List[Role]): A data field.
        members (typing.List[UserId]): A data field.
    """
    
    name: UserGroupName
    description: str
    roles: typing.List[Role]
    members: typing.List[UserId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for UserGroupCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": UserGroupName.json_schema(),
                "description": {
                    "type": "string"
                },
                "roles": {
                    "type": "array",
                    "item": Role.json_schema()
                },
                "members": {
                    "type": "array",
                    "item": UserId.json_schema()
                }
            },
            "required": [
                "name",
                "description",
                "roles",
                "members",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of UserGroupCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupCreationRequest(
                name=UserGroupName.from_json(data["name"]),
                description=str(data["description"]),
                roles=[Role.from_json(v) for v in data["roles"]],
                members=[UserId.from_json(v) for v in data["members"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserGroupCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "name": self.name.to_json(),
            "description": str(self.description),
            "roles": [v.to_json() for v in self.roles],
            "members": [v.to_json() for v in self.members]
        }
