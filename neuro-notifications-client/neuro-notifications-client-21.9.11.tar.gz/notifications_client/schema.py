from datetime import timezone
from enum import Enum
from typing import Any, Optional, Type

from marshmallow import Schema, fields, post_load, validate

from notifications_client.notifications import (
    CreditsWillRunOutSoon,
    JobCannotStartLackResources,
    JobCannotStartNoCredits,
    JobCannotStartQuotaReached,
    JobTransition,
    QuotaResourceType,
    QuotaWillBeReachedSoon,
)


class StringEnum(fields.String):
    def __init__(self, enum: Type[Enum], *args: Any, **kwargs: Any) -> None:
        super().__init__(
            *args, validate=validate.OneOf([item.value for item in enum]), **kwargs
        )
        self.enum = enum

    def _deserialize(self, *args: Any, **kwargs: Any) -> Enum:
        res: str = super()._deserialize(*args, **kwargs)
        return self.enum(res)

    def _serialize(
        self, value: Optional[Enum], *args: Any, **kwargs: Any
    ) -> Optional[str]:
        if value is None:
            return None
        return super()._serialize(value.value, *args, **kwargs)


class JobCannotStartLackResourcesSchema(Schema):
    job_id = fields.String(required=True)

    @post_load
    def make_notification(
        self, data: Any, **kwargs: Any
    ) -> JobCannotStartLackResources:
        return JobCannotStartLackResources(**data)


class JobTransitionSchema(Schema):
    job_id = fields.String(required=True)
    status = fields.String(required=True)
    transition_time = fields.AwareDateTime(required=True, default_timezone=timezone.utc)
    reason = fields.String(required=False, allow_none=True)
    description = fields.String(required=False, allow_none=True)
    exit_code = fields.Integer(required=False, allow_none=True)
    prev_status = fields.String(required=False, allow_none=True)
    prev_transition_time = fields.AwareDateTime(
        required=False, allow_none=True, default_timezone=timezone.utc
    )

    @post_load
    def make_notification(self, data: Any, **kwargs: Any) -> JobTransition:
        return JobTransition(**data)


class JobCannotStartNoCreditsSchema(Schema):
    user_id = fields.String(required=True)
    cluster_name = fields.String(required=True)

    @post_load
    def make_notification(self, data: Any, **kwargs: Any) -> JobCannotStartNoCredits:
        return JobCannotStartNoCredits(**data)


class CreditsWillRunOutSoonSchema(Schema):
    user_id = fields.String(required=True)
    cluster_name = fields.String(required=True)
    credits = fields.Decimal(required=True, as_string=True)

    @post_load
    def make_notification(self, data: Any, **kwargs: Any) -> CreditsWillRunOutSoon:
        return CreditsWillRunOutSoon(**data)


class JobCannotStartQuotaReachedSchema(Schema):
    user_id = fields.String(required=True)
    cluster_name = fields.String(required=True)
    resource = StringEnum(enum=QuotaResourceType, required=True)
    quota = fields.Float(required=True)

    @post_load
    def make_notification(self, data: Any, **kwargs: Any) -> JobCannotStartQuotaReached:
        return JobCannotStartQuotaReached(**data)


class QuotaWillBeReachedSoonSchema(Schema):
    user_id = fields.String(required=True)
    cluster_name = fields.String(required=True)
    resource = StringEnum(enum=QuotaResourceType, required=True)
    used = fields.Float(required=True)
    quota = fields.Float(required=True)

    @post_load
    def make_notification(self, data: Any, **kwargs: Any) -> QuotaWillBeReachedSoon:
        data["resource"] = QuotaResourceType(data["resource"])
        return QuotaWillBeReachedSoon(**data)


SLUG_TO_SCHEMA = {
    JobCannotStartLackResources.slug(): JobCannotStartLackResourcesSchema,
    JobTransition.slug(): JobTransitionSchema,
    JobCannotStartNoCredits.slug(): JobCannotStartNoCreditsSchema,
    CreditsWillRunOutSoon.slug(): CreditsWillRunOutSoonSchema,
    QuotaWillBeReachedSoon.slug(): QuotaWillBeReachedSoonSchema,
    JobCannotStartQuotaReached.slug(): JobCannotStartQuotaReachedSchema,
}
