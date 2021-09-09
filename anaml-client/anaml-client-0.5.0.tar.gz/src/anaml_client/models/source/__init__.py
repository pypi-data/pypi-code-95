"""Generated implementation of source."""

# WARNING DO NOT EDIT
# This code was generated from source.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import logging  # noqa: F401
import uuid  # noqa: F401
import typing  # noqa: F401
import jsonschema  # noqa: F401

from ..attribute import Attribute, SensitiveAttribute
from ..credentials_provider_config import CredentialsProviderConfig
from ..file_format import FileFormat
from ..label import Label


@dataclasses.dataclass(frozen=True)
class SourceId:
    """Unique identifier for a source data store.
    
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
        """Return the JSON schema for SourceId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: int):
        """Validate and parse JSON data into an instance of SourceId.
        
        Args:
            data (int): JSON data to validate and parse.
        
        Returns:
            An instance of SourceId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SourceId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing SourceId", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)


@dataclasses.dataclass(frozen=True)
class SourceVersionId:
    """Unique identifier of a particular version of a source data store.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self):
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for SourceVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: uuid.UUID):
        """Validate and parse JSON data into an instance of SourceVersionId.
        
        Args:
            data (uuid.UUID): JSON data to validate and parse.
        
        Returns:
            An instance of SourceVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SourceVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing SourceVersionId", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class SourceName:
    """Unique name of a source data store.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self):
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for SourceName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: str):
        """Validate and parse JSON data into an instance of SourceName.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of SourceName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SourceName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing SourceName", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class Source(abc.ABC):
    """Details for source data stores.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (str): A data field.
        id (SourceId): A data field.
        labels (typing.List[Label]): A data field.
        name (SourceName): A data field.
        predecessor (typing.Optional[SourceVersionId]): A data field.
        version (SourceVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: str
    id: SourceId
    labels: typing.List[Label]
    name: SourceName
    predecessor: typing.Optional[SourceVersionId]
    version: SourceVersionId
    
    @classmethod
    def json_schema(cls):
        """JSON schema for variant Source.
        
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
        """Validate and parse JSON data into an instance of Source.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Source.
        
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
            logging.debug("Invalid JSON data received while parsing Source", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class S3Source(Source):
    """An input data source on AWS S3.
    
    Args:
        id (SourceId): A data field.
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        version (SourceVersionId): A data field.
        predecessor (typing.Optional[SourceVersionId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "s3"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: SourceId
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bucket: str
    path: str
    fileFormat: FileFormat
    version: SourceVersionId
    predecessor: typing.Optional[SourceVersionId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for S3Source data.
        
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
                "id": SourceId.json_schema(),
                "name": SourceName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "bucket": {
                    "type": "string"
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema(),
                "version": SourceVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        SourceVersionId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "bucket",
                "path",
                "fileFormat",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of S3Source.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of S3Source.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return S3Source(
                id=SourceId.from_json(data["id"]),
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                version=SourceVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and SourceVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing S3Source",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "bucket": str(self.bucket),
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "version": self.version.to_json(),
            "predecessor": (lambda v: v and v.to_json())(self.predecessor)
        }


@dataclasses.dataclass(frozen=True)
class S3ASource(Source):
    """An input data source on S3-compatible object storage.
    
    Args:
        id (SourceId): A data field.
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        endpoint (str): A data field.
        accessKey (str): A data field.
        secretKey (str): A data field.
        version (SourceVersionId): A data field.
        predecessor (typing.Optional[SourceVersionId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "s3a"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: SourceId
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bucket: str
    path: str
    fileFormat: FileFormat
    endpoint: str
    accessKey: str
    secretKey: str
    version: SourceVersionId
    predecessor: typing.Optional[SourceVersionId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for S3ASource data.
        
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
                "id": SourceId.json_schema(),
                "name": SourceName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "bucket": {
                    "type": "string"
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema(),
                "endpoint": {
                    "type": "string"
                },
                "accessKey": {
                    "type": "string"
                },
                "secretKey": {
                    "type": "string"
                },
                "version": SourceVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        SourceVersionId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "bucket",
                "path",
                "fileFormat",
                "endpoint",
                "accessKey",
                "secretKey",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of S3ASource.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of S3ASource.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return S3ASource(
                id=SourceId.from_json(data["id"]),
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                endpoint=str(data["endpoint"]),
                accessKey=str(data["accessKey"]),
                secretKey=str(data["secretKey"]),
                version=SourceVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and SourceVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing S3ASource",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "bucket": str(self.bucket),
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "endpoint": str(self.endpoint),
            "accessKey": str(self.accessKey),
            "secretKey": str(self.secretKey),
            "version": self.version.to_json(),
            "predecessor": (lambda v: v and v.to_json())(self.predecessor)
        }


@dataclasses.dataclass(frozen=True)
class JDBCSource(Source):
    """An input data source using JDBC.
    
    Args:
        id (SourceId): A data field.
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        url (str): A data field.
        schema (str): A data field.
        credentialsProvider (CredentialsProviderConfig): A data field.
        version (SourceVersionId): A data field.
        predecessor (typing.Optional[SourceVersionId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "jdbc"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: SourceId
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    url: str
    schema: str
    credentialsProvider: CredentialsProviderConfig
    version: SourceVersionId
    predecessor: typing.Optional[SourceVersionId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for JDBCSource data.
        
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
                "id": SourceId.json_schema(),
                "name": SourceName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "url": {
                    "type": "string"
                },
                "schema": {
                    "type": "string"
                },
                "credentialsProvider": CredentialsProviderConfig.json_schema(),
                "version": SourceVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        SourceVersionId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "url",
                "schema",
                "credentialsProvider",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of JDBCSource.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of JDBCSource.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return JDBCSource(
                id=SourceId.from_json(data["id"]),
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                url=str(data["url"]),
                schema=str(data["schema"]),
                credentialsProvider=CredentialsProviderConfig.from_json(data["credentialsProvider"]),
                version=SourceVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and SourceVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing JDBCSource",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "url": str(self.url),
            "schema": str(self.schema),
            "credentialsProvider": self.credentialsProvider.to_json(),
            "version": self.version.to_json(),
            "predecessor": (lambda v: v and v.to_json())(self.predecessor)
        }


@dataclasses.dataclass(frozen=True)
class HiveSource(Source):
    """An input data source on Hive.
    
    Args:
        id (SourceId): A data field.
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        database (str): A data field.
        version (SourceVersionId): A data field.
        predecessor (typing.Optional[SourceVersionId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "hive"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: SourceId
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    database: str
    version: SourceVersionId
    predecessor: typing.Optional[SourceVersionId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for HiveSource data.
        
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
                "id": SourceId.json_schema(),
                "name": SourceName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "database": {
                    "type": "string"
                },
                "version": SourceVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        SourceVersionId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "database",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of HiveSource.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of HiveSource.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return HiveSource(
                id=SourceId.from_json(data["id"]),
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                database=str(data["database"]),
                version=SourceVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and SourceVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing HiveSource",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "database": str(self.database),
            "version": self.version.to_json(),
            "predecessor": (lambda v: v and v.to_json())(self.predecessor)
        }


@dataclasses.dataclass(frozen=True)
class BigQuerySource(Source):
    """An input data source on Google BigQuery.
    
    Args:
        id (SourceId): A data field.
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        path (str): A data field.
        version (SourceVersionId): A data field.
        predecessor (typing.Optional[SourceVersionId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "bigquery"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: SourceId
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    path: str
    version: SourceVersionId
    predecessor: typing.Optional[SourceVersionId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for BigQuerySource data.
        
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
                "id": SourceId.json_schema(),
                "name": SourceName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "path": {
                    "type": "string"
                },
                "version": SourceVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        SourceVersionId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "path",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of BigQuerySource.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BigQuerySource.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BigQuerySource(
                id=SourceId.from_json(data["id"]),
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                path=str(data["path"]),
                version=SourceVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and SourceVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BigQuerySource",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "path": str(self.path),
            "version": self.version.to_json(),
            "predecessor": (lambda v: v and v.to_json())(self.predecessor)
        }


@dataclasses.dataclass(frozen=True)
class GCSSource(Source):
    """An input data source on Google Cloud Storage.
    
    Args:
        id (SourceId): A data field.
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        version (SourceVersionId): A data field.
        predecessor (typing.Optional[SourceVersionId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "gcs"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: SourceId
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bucket: str
    path: str
    fileFormat: FileFormat
    version: SourceVersionId
    predecessor: typing.Optional[SourceVersionId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for GCSSource data.
        
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
                "id": SourceId.json_schema(),
                "name": SourceName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "bucket": {
                    "type": "string"
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema(),
                "version": SourceVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        SourceVersionId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "bucket",
                "path",
                "fileFormat",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of GCSSource.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of GCSSource.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return GCSSource(
                id=SourceId.from_json(data["id"]),
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                version=SourceVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and SourceVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing GCSSource",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "bucket": str(self.bucket),
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "version": self.version.to_json(),
            "predecessor": (lambda v: v and v.to_json())(self.predecessor)
        }


@dataclasses.dataclass(frozen=True)
class LocalSource(Source):
    """An input data source on the local filesystem.
    
    Args:
        id (SourceId): A data field.
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        version (SourceVersionId): A data field.
        predecessor (typing.Optional[SourceVersionId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "local"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: SourceId
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    path: str
    fileFormat: FileFormat
    version: SourceVersionId
    predecessor: typing.Optional[SourceVersionId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for LocalSource data.
        
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
                "id": SourceId.json_schema(),
                "name": SourceName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema(),
                "version": SourceVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        SourceVersionId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "path",
                "fileFormat",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of LocalSource.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LocalSource.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LocalSource(
                id=SourceId.from_json(data["id"]),
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                version=SourceVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and SourceVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing LocalSource",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "version": self.version.to_json(),
            "predecessor": (lambda v: v and v.to_json())(self.predecessor)
        }


@dataclasses.dataclass(frozen=True)
class HDFSSource(Source):
    """An input data source on HDFS.
    
    Args:
        id (SourceId): A data field.
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        version (SourceVersionId): A data field.
        predecessor (typing.Optional[SourceVersionId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "hdfs"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: SourceId
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    path: str
    fileFormat: FileFormat
    version: SourceVersionId
    predecessor: typing.Optional[SourceVersionId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for HDFSSource data.
        
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
                "id": SourceId.json_schema(),
                "name": SourceName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema(),
                "version": SourceVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        SourceVersionId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "path",
                "fileFormat",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of HDFSSource.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of HDFSSource.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return HDFSSource(
                id=SourceId.from_json(data["id"]),
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                version=SourceVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and SourceVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing HDFSSource",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "version": self.version.to_json(),
            "predecessor": (lambda v: v and v.to_json())(self.predecessor)
        }


@dataclasses.dataclass(frozen=True)
class KafkaSource(Source):
    """An input data source on Kafka.
    
    Args:
        id (SourceId): A data field.
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bootstrapServers (str): A data field.
        schemaRegistryUrl (str): A data field.
        kafkaPropertiesProviders (typing.List[SensitiveAttribute]): A data field.
        version (SourceVersionId): A data field.
        predecessor (typing.Optional[SourceVersionId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "kafka"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: SourceId
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bootstrapServers: str
    schemaRegistryUrl: str
    kafkaPropertiesProviders: typing.List[SensitiveAttribute]
    version: SourceVersionId
    predecessor: typing.Optional[SourceVersionId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for KafkaSource data.
        
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
                "id": SourceId.json_schema(),
                "name": SourceName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "bootstrapServers": {
                    "type": "string"
                },
                "schemaRegistryUrl": {
                    "type": "string"
                },
                "kafkaPropertiesProviders": {
                    "type": "array",
                    "item": SensitiveAttribute.json_schema()
                },
                "version": SourceVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        SourceVersionId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "bootstrapServers",
                "schemaRegistryUrl",
                "kafkaPropertiesProviders",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of KafkaSource.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of KafkaSource.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return KafkaSource(
                id=SourceId.from_json(data["id"]),
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bootstrapServers=str(data["bootstrapServers"]),
                schemaRegistryUrl=str(data["schemaRegistryUrl"]),
                kafkaPropertiesProviders=[SensitiveAttribute.from_json(v) for v in data["kafkaPropertiesProviders"]],
                version=SourceVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and SourceVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing KafkaSource",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "bootstrapServers": str(self.bootstrapServers),
            "schemaRegistryUrl": str(self.schemaRegistryUrl),
            "kafkaPropertiesProviders": [v.to_json() for v in self.kafkaPropertiesProviders],
            "version": self.version.to_json(),
            "predecessor": (lambda v: v and v.to_json())(self.predecessor)
        }
