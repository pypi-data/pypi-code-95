"""GraphQLDuration type"""

from datetime import timedelta
from typing import Any, Optional

from graphql.error import GraphQLError
from graphql.language import StringValueNode, ValueNode, print_ast
from graphql.type.definition import GraphQLScalarType
from graphql.pyutils import inspect

from jetblack_iso8601 import iso8601_to_timedelta


def _serialize_duration(output_value: Any) -> timedelta:
    if isinstance(output_value, timedelta):
        return output_value

    try:
        if isinstance(output_value, str):
            value = iso8601_to_timedelta(output_value)
            if value is not None:
                return value
        raise ValueError("Invalid duration")
    except ValueError as error:
        raise GraphQLError(
            "Duration cannot represent value: " + inspect(output_value)
        ) from error


def _coerce_duration(input_value: Any) -> timedelta:
    if isinstance(input_value, timedelta):
        return input_value

    try:
        if isinstance(input_value, str):
            value = iso8601_to_timedelta(input_value)
            if value is not None:
                return value
        raise ValueError('Unable to parse duration')
    except ValueError as error:
        raise GraphQLError(
            "Duration cannot represent value: " + inspect(input_value)
        ) from error


def _parse_duration_literal(
        value_node: ValueNode,
        _variables: Optional[Any] = None
) -> timedelta:
    if not isinstance(value_node, StringValueNode):
        raise GraphQLError(
            "Duration cannot represent non-string value: " +
            print_ast(value_node)
        )
    value = iso8601_to_timedelta(value_node.value)
    if value is not None:
        return value

    raise GraphQLError(
        "Duration cannot represent  value: " +
        print_ast(value_node)
    )


GraphQLDuration = GraphQLScalarType(
    name="Duration",
    description="The `Duration` type represents ISO 8601 durations",
    serialize=_serialize_duration,
    parse_value=_coerce_duration,
    parse_literal=_parse_duration_literal
)
