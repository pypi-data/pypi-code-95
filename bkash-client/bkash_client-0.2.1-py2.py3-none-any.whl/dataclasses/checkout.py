from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import Field

from .base import BasePaymentIDRequest
from .base import BaseResponse
from .base import IntentEnum
from .base import PaymentTransactionStatus
from .base import TransactionChannelType


# Payment
class UserVerificationEnum(str, Enum):
    INCOMPLETE = "Incomplete"
    COMPLETE = "Complete"


class BasePaymentResponse(BaseModel):
    paymentID: str
    amount: Decimal
    currency: str
    intent: IntentEnum

    class Config:
        arbitrary_types_allowed = True


class CreatePaymentRequest(BaseModel):
    amount: Decimal
    currency: str = "BDT"
    intent: IntentEnum.SALE = Field(IntentEnum.SALE, const=True)
    merchantInvoiceNumber: str
    merchantAssociationInfo: Optional[str]

    class Config:
        arbitrary_types_allowed = True


class CreateTokenizedPaymentRequest(CreatePaymentRequest):

    payerReference: str
    callbackURL: AnyHttpUrl
    agreementID: Optional[str]

    @property
    def mode(self):
        return "0001" if self.agreementID else "0011"

    class Config:
        arbitrary_types_allowed = True


class CreatePaymentResponse(BasePaymentResponse):
    createTime: str
    orgLogo: str
    orgName: str
    transactionStatus: PaymentTransactionStatus
    merchantInvoiceNumber: str


class CreateTokenizedPaymentResponse(BaseResponse, BasePaymentResponse):
    paymentCreateTime: str
    transactionStatus: PaymentTransactionStatus
    merchantInvoiceNumber: str
    bkashURL: AnyHttpUrl
    callbackURL: AnyHttpUrl
    successCallbackURL: AnyHttpUrl
    failureCallbackURL: AnyHttpUrl
    cancelledCallbackURL: AnyHttpUrl
    agreementID: Optional[str]


class ExecutePaymentRequest(BasePaymentIDRequest):
    paymentID: str


class ExecutePaymentResponse(BasePaymentResponse):
    createTime: str
    updateTime: str
    trxID: str
    transactionStatus: PaymentTransactionStatus
    merchantInvoiceNumber: str


class ExecuteTokenizedPaymentResponse(BaseResponse, BasePaymentResponse):
    customerMsisdn: str
    payerReference: str
    paymentExecuteTime: str
    trxID: str
    transactionStatus: PaymentTransactionStatus
    merchantInvoiceNumber: str
    agreementID: Optional[str]


class QueryPaymentRequest(BasePaymentIDRequest):
    pass


class QueryPaymentResponse(ExecutePaymentResponse):
    refundAmount: Decimal


class QueryTokenizedPaymentResponse(BaseResponse, BasePaymentResponse):
    payerReference: str
    paymentCreateTime: str
    paymentExecuteTime: str
    trxID: str
    transactionStatus: PaymentTransactionStatus
    merchantInvoiceNumber: str
    userVerificationStatus: UserVerificationEnum


class SearchTransactionDetailsRequest(BaseModel):
    trxID: str


class SearchTransactionResponse(BaseModel):
    amount: str
    completedTime: str
    currency: str
    customerMsisdn: str
    initiationTime: str
    organizationShortCode: str
    transactionReference: str
    transactionStatus: str
    transactionType: TransactionChannelType
    trxID: str


class SearchTokenizedTransactionResponse(BaseResponse, SearchTransactionResponse):
    pass


# Authorized and Capture, Void


class VoidPaymentRequest(BasePaymentIDRequest):
    pass


class CapturePaymentRequest(BasePaymentIDRequest):
    pass


class BasePaymentOperationResponse(BaseModel):
    paymentID: str
    createTime: str
    updateTime: str
    trxID: str
    transactionStatus: PaymentTransactionStatus


class CapturePaymentResponse(BasePaymentOperationResponse):
    pass


class VoidPaymentResponse(BasePaymentOperationResponse):
    pass
