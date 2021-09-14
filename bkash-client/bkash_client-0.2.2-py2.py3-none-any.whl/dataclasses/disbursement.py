from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class B2CPaymentRequest(BaseModel):
    amount: Decimal
    currency: str = "BDT"
    merchantInvoiceNumber: str
    receiverMSISDN: str


class B2CPaymentResponse(BaseModel):
    completedTime: str
    trxID: str
    transactionStatus: str
    amount: str
    currency: str
    merchantInvoiceNumber: str
    receiverMSISDN: str
    b2cFee: str


class OrganizationBalance(BaseModel):
    accountHolderName: str
    accountStatus: str
    accountTypeName: str
    availableBalance: str
    currency: str
    currentBalance: str
    updateTime: str


class OrganizationBalanceResponse(BaseModel):
    organizationBalane: OrganizationBalance


class IntraAccountTransferTypeEnum(str, Enum):
    COLLECTION_2_DISBURSEMENT = "Collection2Disbursement"
    DISBURSEMENT_2_COLLECTION = "Disbursement2Collection"


class IntraAccountTransferRequest(BaseModel):
    amount: Decimal
    currency: str = "BDT"
    transferType: IntraAccountTransferTypeEnum


class IntraAccountTransferResponse(BaseModel):
    amount: Decimal
    completedTime: str
    currency: str
    transactionStatus: str
    transferType: IntraAccountTransferTypeEnum
    trxID: str
