import json
import typing

from aio_pika import IncomingMessage
from marshmallow import Schema, types


def load_from_msg(
        schema: Schema,
        msg: IncomingMessage,
        *,
        many: typing.Optional[bool] = None,
        partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None,
        unknown: typing.Optional[str] = None,
        **kwargs
):
    """Deserialize bytes from message body via json to schema."""
    return schema.load(
        json.loads(msg.body),
        many=many,
        partial=partial,
        unknown=unknown,
        **kwargs,  # noqa
    )
