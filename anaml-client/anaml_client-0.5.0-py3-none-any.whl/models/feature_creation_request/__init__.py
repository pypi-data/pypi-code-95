"""Generated implementation of feature_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from feature-creation-request.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import logging  # noqa: F401
import uuid  # noqa: F401
import typing  # noqa: F401
import jsonschema  # noqa: F401

from ..aggregate import AggregateExpression
from ..attribute import Attribute
from ..entity import EntityId
from ..event_window import EventWindow
from ..feature_id import FeatureId, FeatureName
from ..feature_template import TemplateId
from ..filter_expression import FilterExpression
from ..label import Label
from ..post_aggregate_expression import PostAggregateExpression
from ..quality_rating import QualityRating
from ..select_expression import SelectExpression
from ..table import TableId


@dataclasses.dataclass(frozen=True)
class FeatureCreationRequest(abc.ABC):
    """Request to create a new feature.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        name (FeatureName): A data field.
        qualityRating (typing.Optional[QualityRating]): A data field.
        select (SelectExpression): A data field.
        template (typing.Optional[TemplateId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: str
    labels: typing.List[Label]
    name: FeatureName
    qualityRating: typing.Optional[QualityRating]
    select: SelectExpression
    template: typing.Optional[TemplateId]
    
    @classmethod
    def json_schema(cls):
        """JSON schema for variant FeatureCreationRequest.
        
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
        """Validate and parse JSON data into an instance of FeatureCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureCreationRequest.
        
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
            logging.debug("Invalid JSON data received while parsing FeatureCreationRequest", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class EventFeatureCreationRequest(FeatureCreationRequest):
    """Request to create a new feature defined on events.
    
    Args:
        name (FeatureName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        qualityRating (typing.Optional[QualityRating]): A data field.
        table (TableId): A data field.
        window (EventWindow): A data field.
        select (SelectExpression): A data field.
        filter (typing.Optional[FilterExpression]): A data field.
        aggregate (AggregateExpression): A data field.
        postAggregateExpr (typing.Optional[PostAggregateExpression]): A data field.
        template (typing.Optional[TemplateId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "event"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: FeatureName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    qualityRating: typing.Optional[QualityRating]
    table: TableId
    window: EventWindow
    select: SelectExpression
    filter: typing.Optional[FilterExpression]
    aggregate: AggregateExpression
    postAggregateExpr: typing.Optional[PostAggregateExpression]
    template: typing.Optional[TemplateId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for EventFeatureCreationRequest data.
        
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
                "name": FeatureName.json_schema(),
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
                "qualityRating": {
                    "oneOf": [
                        {"type": "null"},
                        QualityRating.json_schema(),
                    ]
                },
                "table": TableId.json_schema(),
                "window": EventWindow.json_schema(),
                "select": SelectExpression.json_schema(),
                "filter": {
                    "oneOf": [
                        {"type": "null"},
                        FilterExpression.json_schema(),
                    ]
                },
                "aggregate": AggregateExpression.json_schema(),
                "postAggregateExpr": {
                    "oneOf": [
                        {"type": "null"},
                        PostAggregateExpression.json_schema(),
                    ]
                },
                "template": {
                    "oneOf": [
                        {"type": "null"},
                        TemplateId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "table",
                "window",
                "select",
                "aggregate",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of EventFeatureCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventFeatureCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventFeatureCreationRequest(
                name=FeatureName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                qualityRating=(
                    lambda v: v and QualityRating.from_json(v)
                )(
                    data.get("qualityRating", None)
                ),
                table=TableId.from_json(data["table"]),
                window=EventWindow.from_json(data["window"]),
                select=SelectExpression.from_json(data["select"]),
                filter=(
                    lambda v: v and FilterExpression.from_json(v)
                )(
                    data.get("filter", None)
                ),
                aggregate=AggregateExpression.from_json(data["aggregate"]),
                postAggregateExpr=(
                    lambda v: v and PostAggregateExpression.from_json(v)
                )(
                    data.get("postAggregateExpr", None)
                ),
                template=(lambda v: v and TemplateId.from_json(v))(data.get("template", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventFeatureCreationRequest",
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
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "qualityRating": (lambda v: v and v.to_json())(self.qualityRating),
            "table": self.table.to_json(),
            "window": self.window.to_json(),
            "select": self.select.to_json(),
            "filter": (lambda v: v and v.to_json())(self.filter),
            "aggregate": self.aggregate.to_json(),
            "postAggregateExpr": (lambda v: v and v.to_json())(self.postAggregateExpr),
            "template": (lambda v: v and v.to_json())(self.template)
        }


@dataclasses.dataclass(frozen=True)
class RowFeatureCreationRequest(FeatureCreationRequest):
    """Request to create a new feature defined on rows.
    
    Args:
        name (FeatureName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        qualityRating (typing.Optional[QualityRating]): A data field.
        over (typing.List[FeatureId]): A data field.
        select (SelectExpression): A data field.
        entityId (EntityId): A data field.
        template (typing.Optional[TemplateId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "row"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: FeatureName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    qualityRating: typing.Optional[QualityRating]
    over: typing.List[FeatureId]
    select: SelectExpression
    entityId: EntityId
    template: typing.Optional[TemplateId]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for RowFeatureCreationRequest data.
        
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
                "name": FeatureName.json_schema(),
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
                "qualityRating": {
                    "oneOf": [
                        {"type": "null"},
                        QualityRating.json_schema(),
                    ]
                },
                "over": {
                    "type": "array",
                    "item": FeatureId.json_schema()
                },
                "select": SelectExpression.json_schema(),
                "entityId": EntityId.json_schema(),
                "template": {
                    "oneOf": [
                        {"type": "null"},
                        TemplateId.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "over",
                "select",
                "entityId",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of RowFeatureCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of RowFeatureCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return RowFeatureCreationRequest(
                name=FeatureName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                qualityRating=(
                    lambda v: v and QualityRating.from_json(v)
                )(
                    data.get("qualityRating", None)
                ),
                over=[FeatureId.from_json(v) for v in data["over"]],
                select=SelectExpression.from_json(data["select"]),
                entityId=EntityId.from_json(data["entityId"]),
                template=(lambda v: v and TemplateId.from_json(v))(data.get("template", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing RowFeatureCreationRequest",
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
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "qualityRating": (lambda v: v and v.to_json())(self.qualityRating),
            "over": [v.to_json() for v in self.over],
            "select": self.select.to_json(),
            "entityId": self.entityId.to_json(),
            "template": (lambda v: v and v.to_json())(self.template)
        }
