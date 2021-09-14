from decimal import Decimal
from typing import Optional

from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import Field

from .base import BasePaymentIDRequest
from .base import BaseResponse


class BaseAgreementResponse(BaseModel):
    paymentID: str
    agreementID: str
    customerMsisdn: str
    payerReference: str
    agreementExecuteTime: str
    agreementStatus: str


class CreateAgreementRequest(BaseModel):
    mode: str = Field("0000", const=True)
    payerReference: str
    callbackURL: AnyHttpUrl
    amount: Decimal
    currency: str = "BDT"
    intent: str = Field("Sale", const=True)
    merchantInvoiceNumber: Optional[str]


class CreateAgreementResponse(BaseResponse, BaseModel):
    paymentID: str
    bkashURL: AnyHttpUrl
    callbackURL: AnyHttpUrl
    successCallbackURL: AnyHttpUrl
    failureCallbackURL: AnyHttpUrl
    cancelledCallbackURL: AnyHttpUrl


class ExecuteAgreementRequest(BasePaymentIDRequest):
    pass


class BaseAgreementIDRequest(BaseModel):
    agreementID: str


class ExecuteAgreementResponse(BaseResponse, BaseAgreementResponse):
    pass


class QueryAgreementRequest(BaseAgreementIDRequest):
    pass


class QueryAgreementResponse(BaseResponse, BaseAgreementResponse):
    agreementCreateTime: str
    agreementVoidTime: str


class CancelAgreementRequest(BaseAgreementIDRequest):
    pass


class CancelAgreementResponse(BaseResponse, BaseModel):
    paymentID: str
    agreementID: str
    payerReference: str
    agreementVoidTime: str
    agreementStatus: str
