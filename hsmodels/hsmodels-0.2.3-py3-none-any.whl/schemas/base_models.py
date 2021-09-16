from datetime import datetime
from typing import Any, Dict, Union

from pydantic import BaseModel


class BaseMetadata(BaseModel):

    def dict(
            self,
            *,
            include: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
            exclude: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
            by_alias: bool = False,
            skip_defaults: bool = None,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
    ) -> 'DictStrAny':
        """
        Checks the config for a schema_config dictionary_field and converts a dictionary to a list of key/value pairs.
        This converts the dictionary to a format that can be described in a json schema (which can be found below in the
        schema_extra staticmethod.

        """
        d = super().dict(include=include, exclude=exclude, by_alias=by_alias, skip_defaults=skip_defaults,
                         exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none)

        if hasattr(self.Config, "schema_config"):
            schema_config = self.Config.schema_config
            if "dictionary_field" in schema_config:
                for field in schema_config["dictionary_field"]:
                    field_value = d[field]
                    d[field] = [{"key": key, "value": value} for key, value in field_value.items()]
        return d

    class Config:
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model) -> None:
            if hasattr(model.Config, "schema_config"):
                schema_config = model.Config.schema_config
                if "read_only" in schema_config:
                    # set readOnly in json schema
                    for field in schema_config["read_only"]:
                        schema['properties'][field]['readOnly'] = True
                if "dictionary_field" in schema_config:
                    for field in schema_config["dictionary_field"]:
                        prop = schema["properties"][field]
                        prop.pop('default', None)
                        prop.pop('additionalProperties', None)
                        prop['type'] = "array"
                        prop['items'] = \
                            {
                                "type": "object",
                                "title": "Key-Value",
                                "description": "A key-value pair",
                                "properties": {
                                    "key": {
                                        "type": "string"
                                    },
                                    "value": {
                                        "type": "string"
                                    }
                                },
                                "required": [
                                    "key",
                                    "value"
                                ]
                            }


class BaseCoverage(BaseMetadata):
    def __str__(self):
        return "; ".join(
            [
                "=".join([key, val.isoformat() if isinstance(val, datetime) else str(val)])
                for key, val in self.__dict__.items()
                if key != "type" and val
            ]
        )
