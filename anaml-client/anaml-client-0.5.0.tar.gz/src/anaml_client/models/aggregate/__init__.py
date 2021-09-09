"""Generated implementation of aggregate."""

# WARNING DO NOT EDIT
# This code was generated from aggregate.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import logging  # noqa: F401
import uuid  # noqa: F401
import typing  # noqa: F401
import jsonschema  # noqa: F401


class AggregateExpression(enum.Enum):
    """Aggregate expressions for Anaml Event features."""
    Sum = "sum"
    Count = "count"
    CountDistinct = "countdistinct"
    Avg = "avg"
    Std = "std"
    Max = "max"
    Min = "min"
    MaxBy = "maxby"
    MinBy = "minby"
    Last = "last"
    PercentageChange = "percentagechange"
    AbsoluteChange = "absolutechange"
    StandardScore = "standardscore"
    CollectList = "collectlist"
    CollectSet = "collectset"
    BasketSum = "basketsum"
    BasketLast = "basketlast"
    
    @classmethod
    def json_schema(cls):
        """JSON schema for 'AggregateExpression'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "sum",
                        "count",
                        "countdistinct",
                        "avg",
                        "std",
                        "max",
                        "min",
                        "maxby",
                        "minby",
                        "last",
                        "percentagechange",
                        "absolutechange",
                        "standardscore",
                        "collectlist",
                        "collectset",
                        "basketsum",
                        "basketlast",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: str):
        """Validate and parse JSON data into an instance of AggregateExpression.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of AggregateExpression.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AggregateExpression(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing AggregateExpression", exc_info=ex)
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
