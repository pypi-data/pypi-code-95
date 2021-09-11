from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Type, TypeVar, Union

from dataclasses_json import DataClassJsonMixin

from benchling_api_client.types import Unset, UNSET
from benchling_sdk.models import CustomFields, Field, Fields, SchemaFieldsQueryParam

D = TypeVar("D", bound="DeserializableModel")
T = TypeVar("T")


@dataclass
class SerializableModel(DataClassJsonMixin):
    """For serializing models when using raw API calls (e.g., Benchling.api).
    Override serialize() for customized behavior."""

    # Not named to_dict() to avoid conflicts with DataClassJsonMixin
    def serialize(self) -> Dict[str, Any]:
        all_values = super().to_dict()
        # Filter out any Unset values
        return {key: value for key, value in all_values.items() if not isinstance(value, Unset)}


@dataclass
class DeserializableModel(DataClassJsonMixin):
    """For deserializing models when using raw API calls (e.g., Benchling.api)
    Override deserialize() for customized behavior."""

    # Not named from_dict() to avoid conflicts with DataClassJsonMixin
    @classmethod
    def deserialize(cls: Type[D], source_dict: Dict[str, Any]) -> D:
        return cls.from_dict(source_dict)


@dataclass
class DeserializableModelNoContent(DeserializableModel):
    pass


def optional_array_query_param(inputs: Optional[Iterable[str]]) -> Optional[str]:
    if inputs:
        return array_query_param(inputs)
    return None


def array_query_param(inputs: Iterable[str]) -> str:
    return ",".join(inputs)


def fields(source: Dict[str, Dict[str, Any]]) -> Fields:
    """Marshals a dictionary into a Fields object"""
    deserialized_fields = Fields()
    for field_name, field_dict in source.items():
        # BNCH-22297: Workaround to deal with the fact that `Field` is not correctly deserialized.
        deserialized_fields[field_name] = Field(value=field_dict["value"])
    return deserialized_fields


def custom_fields(source: Dict[str, Any]) -> CustomFields:
    """Marshals a dictionary into a CustomFields object"""
    return CustomFields.from_dict(source)


def unset_as_none(source: Union[Unset, None, T]) -> Optional[T]:
    """Given a value that may be UNSET, produces an Optional[] where UNSET will be treated as None"""
    if source is UNSET:
        return None
    return source  # type: ignore


def schema_fields_query_param(schema_fields: Optional[Dict[str, Any]]) -> Optional[SchemaFieldsQueryParam]:
    return (
        SchemaFieldsQueryParam.from_dict(
            {f"schemaField.{field}": value for field, value in schema_fields.items()}
        )
        if schema_fields
        else None
    )


def none_as_unset(val: Optional[T]) -> Union[T, Unset]:
    return UNSET if val is None else val
