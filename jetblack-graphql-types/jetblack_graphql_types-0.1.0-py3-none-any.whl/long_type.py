"""GraphQLLong type"""

from math import isfinite
from typing import Any

from graphql.error import GraphQLError
from graphql.language.ast import IntValueNode, ValueNode
from graphql.language.printer import print_ast
from graphql.pyutils import inspect
from graphql.type.definition import GraphQLScalarType

MAX_LONG = 2 ** 53 - 1
MIN_LONG = -MAX_LONG


def _serialize_long(output_value: Any) -> int:
    if isinstance(output_value, bool):
        return 1 if output_value else 0
    try:
        if isinstance(output_value, int):
            num = output_value
        elif isinstance(output_value, float):
            num = int(output_value)
            if num != output_value:
                raise ValueError
        elif not output_value and isinstance(output_value, str):
            output_value = ""
            raise ValueError
        else:
            num = int(output_value)  # raises ValueError if not an integer
    except (OverflowError, ValueError, TypeError) as error:
        raise GraphQLError(
            "Long cannot represent non-integer value: " + inspect(output_value)
        ) from error
    if not MIN_LONG <= num <= MAX_LONG:
        raise GraphQLError(
            "Long cannot represent non 53-bit signed integer value: "
            + inspect(output_value)
        )
    return num


def _coerce_long(input_value: Any) -> int:
    if not (
        isinstance(input_value, int) and not isinstance(input_value, bool)
    ) and not (
        isinstance(input_value, float)
        and isfinite(input_value)
        and int(input_value) == input_value
    ):
        raise GraphQLError(
            "Long cannot represent non-integer value: " + inspect(input_value)
        )
    if not MIN_LONG <= input_value <= MAX_LONG:
        raise GraphQLError(
            "Long cannot represent non 53-bit signed integer value: "
            + inspect(input_value)
        )
    return int(input_value)


def _parse_long_literal(value_node: ValueNode, _variables: Any = None) -> int:
    """Parse a long integer value node in the AST."""
    if not isinstance(value_node, IntValueNode):
        raise GraphQLError(
            "Long cannot represent non-integer value: " +
            print_ast(value_node),
            value_node,
        )
    num = int(value_node.value)
    if not MIN_LONG <= num <= MAX_LONG:
        raise GraphQLError(
            "Long cannot represent non 32-bit signed integer value: "
            + print_ast(value_node),
            value_node,
        )
    return num


GraphQLLong = GraphQLScalarType(
    name="Long",
    description="The `Long` scalar type represents"
    " non-fractional signed whole numeric values."
    " Int can represent values between -(2^53) and 2^53 - 1.",
    serialize=_serialize_long,
    parse_value=_coerce_long,
    parse_literal=_parse_long_literal,
)
