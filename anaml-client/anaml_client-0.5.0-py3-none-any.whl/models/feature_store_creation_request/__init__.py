"""Generated implementation of feature_store_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from feature-store-creation-request.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import logging  # noqa: F401
import uuid  # noqa: F401
import typing  # noqa: F401
import jsonschema  # noqa: F401

from ..attribute import Attribute
from ..cluster import ClusterId
from ..destination_reference import DestinationReference
from ..feature_set import FeatureSetId
from ..feature_store import FeatureStoreName, VersionTarget
from ..label import Label
from ..schedule import Schedule


@dataclasses.dataclass(frozen=True)
class FeatureStoreCreationRequest:
    """Request to create a new feature store.
    
    Args:
        name (FeatureStoreName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        featureSet (FeatureSetId): A data field.
        enabled (bool): A data field.
        destinations (typing.List[DestinationReference]): A data field.
        cluster (ClusterId): A data field.
        schedule (Schedule): A data field.
        startDate (typing.Optional[datetime.date]): A data field.
        endDate (typing.Optional[datetime.date]): A data field.
        versionTarget (typing.Optional[VersionTarget]): A data field.
    """
    
    name: FeatureStoreName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    featureSet: FeatureSetId
    enabled: bool
    destinations: typing.List[DestinationReference]
    cluster: ClusterId
    schedule: Schedule
    startDate: typing.Optional[datetime.date]
    endDate: typing.Optional[datetime.date]
    versionTarget: typing.Optional[VersionTarget]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for FeatureStoreCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": FeatureStoreName.json_schema(),
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
                "featureSet": FeatureSetId.json_schema(),
                "enabled": {
                    "type": "boolean"
                },
                "destinations": {
                    "type": "array",
                    "item": DestinationReference.json_schema()
                },
                "cluster": ClusterId.json_schema(),
                "schedule": Schedule.json_schema(),
                "startDate": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date"},
                    ]
                },
                "endDate": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date"},
                    ]
                },
                "versionTarget": {
                    "oneOf": [
                        {"type": "null"},
                        VersionTarget.json_schema(),
                    ]
                }
            },
            "required": [
                "name",
                "description",
                "labels",
                "attributes",
                "featureSet",
                "enabled",
                "destinations",
                "cluster",
                "schedule",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of FeatureStoreCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStoreCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureStoreCreationRequest(
                name=FeatureStoreName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                featureSet=FeatureSetId.from_json(data["featureSet"]),
                enabled=bool(data["enabled"]),
                destinations=[DestinationReference.from_json(v) for v in data["destinations"]],
                cluster=ClusterId.from_json(data["cluster"]),
                schedule=Schedule.from_json(data["schedule"]),
                startDate=(
                    lambda v: v and datetime.date.fromisoformat(v)
                )(
                    data.get("startDate", None)
                ),
                endDate=(
                    lambda v: v and datetime.date.fromisoformat(v)
                )(
                    data.get("endDate", None)
                ),
                versionTarget=(
                    lambda v: v and VersionTarget.from_json(v)
                )(
                    data.get("versionTarget", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureStoreCreationRequest",
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
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "featureSet": self.featureSet.to_json(),
            "enabled": self.enabled,
            "destinations": [v.to_json() for v in self.destinations],
            "cluster": self.cluster.to_json(),
            "schedule": self.schedule.to_json(),
            "startDate": (lambda v: v and v.isoformat())(self.startDate),
            "endDate": (lambda v: v and v.isoformat())(self.endDate),
            "versionTarget": (lambda v: v and v.to_json())(self.versionTarget)
        }
