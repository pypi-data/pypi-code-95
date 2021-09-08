"""GraphQLJson type"""

import json
from typing import Any

from graphql.error import GraphQLError
from graphql.language.ast import StringValueNode, ValueNode
from graphql.language.printer import print_ast
from graphql.pyutils import inspect
from graphql.type.definition import GraphQLScalarType


def _is_json_type(value: Any) -> bool:
    return (
        value is None or isinstance(value, (dict, list, int, float, bool))
    )


def _serialize_json(output_value: Any) -> Any:
    if _is_json_type(output_value):
        return output_value

    try:
        if isinstance(output_value, str):
            return json.loads(output_value)
        raise ValueError('JSON must be a string')
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise GraphQLError(
            "JSON cannot represent value: " + inspect(output_value)
        ) from error


def _coerce_json(input_value: Any) -> Any:
    if not _is_json_type(input_value):
        raise GraphQLError(
            "JSON cannot represent value: " + inspect(input_value)
        )

    return input_value


def _parse_json_literal(value_node: ValueNode, _variables: Any = None) -> Any:
    if not isinstance(value_node, StringValueNode):
        raise GraphQLError(
            "JSON cannot represent value: " + print_ast(value_node)
        )

    return json.loads(value_node.value)


GraphQLJson = GraphQLScalarType(
    name='JSON',
    description="The `JSON` scalar type",
    serialize=_serialize_json,
    parse_value=_coerce_json,
    parse_literal=_parse_json_literal
)
