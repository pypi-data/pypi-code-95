"""Generated implementation of branch."""

# WARNING DO NOT EDIT
# This code was generated from branch.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import logging  # noqa: F401
import uuid  # noqa: F401
import typing  # noqa: F401
import jsonschema  # noqa: F401

from ..commit import CommitId


@dataclasses.dataclass(frozen=True)
class BranchName:
    """Unique name of a branch.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self):
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for BranchName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: str):
        """Validate and parse JSON data into an instance of BranchName.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of BranchName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BranchName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing BranchName", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class BranchRequest:
    """Request to create a new branch.
    
    Args:
        name (str): A data field.
        commit (CommitId): A data field.
    """
    
    name: str
    commit: CommitId
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for BranchRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "commit": CommitId.json_schema()
            },
            "required": [
                "name",
                "commit",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of BranchRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BranchRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BranchRequest(
                name=str(data["name"]),
                commit=CommitId.from_json(data["commit"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BranchRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "name": str(self.name),
            "commit": self.commit.to_json()
        }


@dataclasses.dataclass(frozen=True)
class BranchUpdateRequest:
    """Request to update a branch to point to a new commit.
    
    Args:
        commit (CommitId): A data field.
        force (typing.Optional[bool]): A data field.
    """
    
    commit: CommitId
    force: typing.Optional[bool]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for BranchUpdateRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "commit": CommitId.json_schema(),
                "force": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "boolean"},
                    ]
                }
            },
            "required": [
                "commit",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of BranchUpdateRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BranchUpdateRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BranchUpdateRequest(
                commit=CommitId.from_json(data["commit"]),
                force=(lambda v: v and bool(v))(data.get("force", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BranchUpdateRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "commit": self.commit.to_json(),
            "force": (lambda v: v and v)(self.force)
        }
