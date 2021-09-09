"""Generated implementation of user."""

# WARNING DO NOT EDIT
# This code was generated from user.mcn

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


@dataclasses.dataclass(frozen=True)
class UserId:
    """Unique identifier of a user.
    
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
        """Return the JSON schema for UserId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: int):
        """Validate and parse JSON data into an instance of UserId.
        
        Args:
            data (int): JSON data to validate and parse.
        
        Returns:
            An instance of UserId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserId", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)


@dataclasses.dataclass(frozen=True)
class UserName:
    """Unique name of a user.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self):
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for UserName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: str):
        """Validate and parse JSON data into an instance of UserName.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of UserName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserName", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class User:
    """Details of a user account.
    
    Args:
        id (UserId): A data field.
        name (UserName): A data field.
        email (typing.Optional[str]): A data field.
        givenName (typing.Optional[str]): A data field.
        surname (typing.Optional[str]): A data field.
        lastLogin (typing.Optional[datetime.datetime]): A data field.
        created (typing.Optional[datetime.datetime]): A data field.
        modified (typing.Optional[datetime.datetime]): A data field.
        roles (typing.List[Role]): A data field.
    """
    
    id: UserId
    name: UserName
    email: typing.Optional[str]
    givenName: typing.Optional[str]
    surname: typing.Optional[str]
    lastLogin: typing.Optional[datetime.datetime]
    created: typing.Optional[datetime.datetime]
    modified: typing.Optional[datetime.datetime]
    roles: typing.List[Role]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for User data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": UserId.json_schema(),
                "name": UserName.json_schema(),
                "email": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "givenName": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "surname": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "lastLogin": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "created": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "modified": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "roles": {
                    "type": "array",
                    "item": Role.json_schema()
                }
            },
            "required": [
                "id",
                "name",
                "roles",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of User.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of User.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return User(
                id=UserId.from_json(data["id"]),
                name=UserName.from_json(data["name"]),
                email=(lambda v: v and str(v))(data.get("email", None)),
                givenName=(lambda v: v and str(v))(data.get("givenName", None)),
                surname=(lambda v: v and str(v))(data.get("surname", None)),
                lastLogin=(
                    lambda v: v and datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f%z')
                )(
                    data.get("lastLogin", None)
                ),
                created=(
                    lambda v: v and datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f%z')
                )(
                    data.get("created", None)
                ),
                modified=(
                    lambda v: v and datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f%z')
                )(
                    data.get("modified", None)
                ),
                roles=[Role.from_json(v) for v in data["roles"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing User",
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
            "email": (lambda v: v and str(v))(self.email),
            "givenName": (lambda v: v and str(v))(self.givenName),
            "surname": (lambda v: v and str(v))(self.surname),
            "lastLogin": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.lastLogin),
            "created": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.created),
            "modified": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.modified),
            "roles": [v.to_json() for v in self.roles]
        }


@dataclasses.dataclass(frozen=True)
class UserCreationRequest:
    """Request to create a new user account.
    
    Args:
        name (UserName): A data field.
        password (typing.Optional[str]): A data field.
        email (typing.Optional[str]): A data field.
        givenName (typing.Optional[str]): A data field.
        surname (typing.Optional[str]): A data field.
        roles (typing.List[Role]): A data field.
    """
    
    name: UserName
    password: typing.Optional[str]
    email: typing.Optional[str]
    givenName: typing.Optional[str]
    surname: typing.Optional[str]
    roles: typing.List[Role]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for UserCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": UserName.json_schema(),
                "password": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "email": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "givenName": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "surname": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "roles": {
                    "type": "array",
                    "item": Role.json_schema()
                }
            },
            "required": [
                "name",
                "roles",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of UserCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserCreationRequest(
                name=UserName.from_json(data["name"]),
                password=(lambda v: v and str(v))(data.get("password", None)),
                email=(lambda v: v and str(v))(data.get("email", None)),
                givenName=(lambda v: v and str(v))(data.get("givenName", None)),
                surname=(lambda v: v and str(v))(data.get("surname", None)),
                roles=[Role.from_json(v) for v in data["roles"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserCreationRequest",
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
            "password": (lambda v: v and str(v))(self.password),
            "email": (lambda v: v and str(v))(self.email),
            "givenName": (lambda v: v and str(v))(self.givenName),
            "surname": (lambda v: v and str(v))(self.surname),
            "roles": [v.to_json() for v in self.roles]
        }


@dataclasses.dataclass(frozen=True)
class UserUpdateRequest:
    """Request to update a user account.
    
    Args:
        name (UserName): A data field.
        email (typing.Optional[str]): A data field.
        givenName (typing.Optional[str]): A data field.
        surname (typing.Optional[str]): A data field.
    """
    
    name: UserName
    email: typing.Optional[str]
    givenName: typing.Optional[str]
    surname: typing.Optional[str]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for UserUpdateRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": UserName.json_schema(),
                "email": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "givenName": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "surname": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "name",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of UserUpdateRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserUpdateRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserUpdateRequest(
                name=UserName.from_json(data["name"]),
                email=(lambda v: v and str(v))(data.get("email", None)),
                givenName=(lambda v: v and str(v))(data.get("givenName", None)),
                surname=(lambda v: v and str(v))(data.get("surname", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserUpdateRequest",
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
            "email": (lambda v: v and str(v))(self.email),
            "givenName": (lambda v: v and str(v))(self.givenName),
            "surname": (lambda v: v and str(v))(self.surname)
        }


@dataclasses.dataclass(frozen=True)
class UserUpdateRequestWithRoles:
    """Request to update a user account and roles they are assigned.
    
    Args:
        name (UserName): A data field.
        email (typing.Optional[str]): A data field.
        givenName (typing.Optional[str]): A data field.
        surname (typing.Optional[str]): A data field.
        roles (typing.List[Role]): A data field.
    """
    
    name: UserName
    email: typing.Optional[str]
    givenName: typing.Optional[str]
    surname: typing.Optional[str]
    roles: typing.List[Role]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for UserUpdateRequestWithRoles data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": UserName.json_schema(),
                "email": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "givenName": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "surname": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "roles": {
                    "type": "array",
                    "item": Role.json_schema()
                }
            },
            "required": [
                "name",
                "roles",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of UserUpdateRequestWithRoles.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserUpdateRequestWithRoles.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserUpdateRequestWithRoles(
                name=UserName.from_json(data["name"]),
                email=(lambda v: v and str(v))(data.get("email", None)),
                givenName=(lambda v: v and str(v))(data.get("givenName", None)),
                surname=(lambda v: v and str(v))(data.get("surname", None)),
                roles=[Role.from_json(v) for v in data["roles"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserUpdateRequestWithRoles",
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
            "email": (lambda v: v and str(v))(self.email),
            "givenName": (lambda v: v and str(v))(self.givenName),
            "surname": (lambda v: v and str(v))(self.surname),
            "roles": [v.to_json() for v in self.roles]
        }
