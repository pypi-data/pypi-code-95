from enum import Enum
from typing import Any

from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import Field


class WebhookRequestTypeEnum(str, Enum):
    SUBSCRIPTION_CONFIRMATION = ("SubscriptionConfirmation",)
    NOTIFICATION = "Notification"


class BaseWebhookRequest(BaseModel):
    Type: WebhookRequestTypeEnum
    MessageId: str
    Token: str
    TopicArn: str
    Message: str
    SubscribeURL: AnyHttpUrl
    Timestamp: str
    SignatureVersion: str
    Signature: str
    SigningCertURL: AnyHttpUrl


class SubscriptionConfirmationRequest(BaseWebhookRequest):
    Type: WebhookRequestTypeEnum = Field(
        WebhookRequestTypeEnum.SUBSCRIPTION_CONFIRMATION, const=True
    )


class NotificationRequest(BaseWebhookRequest):
    Type: WebhookRequestTypeEnum = Field(
        WebhookRequestTypeEnum.NOTIFICATION, const=True
    )
    Message: Any
    UnsubscribeURL: AnyHttpUrl
