from enum import Enum
from typing import Optional
from typing import Union

from pydantic import BaseModel


class ClientTypeEnum(str, Enum):
    IFRAME_BASED = "iframe"
    URL_BASED = "url_based"
    TOKENIZED = "tokenized"
    AUTH_AND_CAPTURE = "auth_and_capture"


class RequestHeader(BaseModel):
    authorization: str
    x_app_key: str

    @property
    def header(self):
        return {"Authorization": self.authorization, "X-APP-KEY": self.x_app_key}


class IntentEnum(str, Enum):
    SALE = "sale"
    AUTHORIZATION = "authorization"


class TokenRequestHeader(BaseModel):
    username: str
    password: str


class CreateTokenRequest(BaseModel):
    app_key: str
    app_secret: str


class RefreshTokenRequest(CreateTokenRequest):
    refresh_token: str


class TokenCredentials(BaseModel):
    expires_in: str
    id_token: str
    refresh_token: str
    token_type: str
    statusCode: Optional[str]
    statusMessage: Optional[str]


class PaymentTransactionStatus(str, Enum):
    INITIATED = "Initiated"
    COMPLETED = "Completed"
    PENDING_AUTHORIZED = "Pending Authorized"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"
    DECLINED = "Declined"


class TransactionChannelType(str, Enum):
    USSD = "USSD"
    APP = "APP"
    PGW = "PGW"
    WEB = "WEB"
    SYSTEM = "SYSTEM"
    API = "bKash Checkout via API"


class ErrorCodeEnum(str, Enum):
    INVALID_APP_KEY = "2001"
    INVALID_PAYMENT_ID = "2002"
    PROCESS_FAILED = "2003"
    INVALID_FIRST_PAYMENT_DATE = "2004"
    INVALID_FREQUENCY = "2005"
    INVALID_AMOUNT = "2006"
    INVALID_CURRENCY = "2007"
    INVALID_INTENT = "2008"
    INVALID_WALLET = "2009"
    INVALID_OTP = "2010"
    INVALID_PIN = "2011"
    INVALID_RECEIVER_MSISDN = "2012"
    RESEND_LIMIT_EXCEED = "2013"
    WRONG_PIN = "2014"
    WRONG_PIN_COUNT_EXCEED = "2015"
    WRONG_VERIFICATION_CODE = "2016"
    WRONG_VERIFICATION_CODE_LIMIT_EXCEED = "2017"
    OTP_VERIFICATION_TIME_EXPIRED = "2019"
    PIN_VERIFICATION_TIME_EXPIRED = "2020"
    INVALID_MANDATE_ID = "2021"
    MANDATE_DOES_NOT_EXIST = "2022"
    INSUFFICIENT_BALANCE = "2023"
    EXCEPTION_OCCURRED = "2024"
    INVALID_REQUEST_BODY = "2025"
    INVALID_REVERSAL_AMOUNT = "2026"
    MANDATE_ALREADY_EXISTS = "2027"
    REVERSAL_FAILED_ON_TRANSACTION_NUMBER_DOES_NOT_EXISTS = "2028"
    DUPLICATE_FOR_ALL_TRANSACTIONS = "2029"
    INVALID_MANDATE_REQUEST_TYPE = "2030"
    INVALID_MARCHANT_INVOICE_NUMBER = "2031"
    INVALID_TRANSFER_TYPE = "2032"
    TRANSACTION_NOT_FOUND = "2033"
    ALREADY_REVERSED = "2034"
    INVALID_REVERSE_INITIATOR = "2035"
    INACTIVE_DIRECT_DEBIT_MANDATE = "2036"
    PROHIBITTED_DEBIT_ACCOUNT = "2037"
    PROHIBITTED_DEBIT_IDENTITY_TAG = "2038"
    PROHIBITTED_CREDIT_ACCOUNT = "2039"
    PROHIBITTED_CREDIT_IDENTITY_TAG = "2040"
    PROHIBITTED_CREDIT_CURRENT_SERVICE = "2041"
    INVALID_REVERSE_INITIATOR2 = "2042"  # Clarification needed
    INCORRECT_SECURITY_CREDENTIAL = "2043"
    IDENTITY_IS_NOT_SUBSCRIBED_OR_INACTIVE = "2044"
    MSISDN_DOES_NOT_EXISTS = "2045"
    IDENTITY_IS_NOT_SUBSCRIBED = "2046"
    TLV_DATA_FORMAT_ERROR = "2047"
    INVALID_PAYER_REFERENCE = "2048"
    INVALID_MERCHANT_CALLBACK_URL = "2049"
    AGREEMENT_ALREADY_EXISTS = "2050"
    INVALID_AGREEMENT_ID = "2051"
    AGREEMENT_INCOMPLETE = "2052"
    AGREEMENT_CANCELLED = "2053"
    UNMET_AGREEMENT_EXECUTION_PREREQUISITE = "2054"
    INVALID_AGREEMENT_STATE = "2055"
    INVALID_PAYMENT_STATE = "2056"
    NOT_A_BKASH_ACCOUNT = "2057"
    NOT_A_CUSTOMER_WALLET = "2058"
    MULTI_OTP_FOR_A_SESSION = "2059"
    UNMET_PAYMENT_EXECUTION_PREREQUISITE = "2060"
    ACTION_REQUIRES_AGREEMENT = "2061"
    PAYMENT_ALREADY_COMPLETED = "2062"
    INVALID_MODE_PER_REQUEST = "2063"
    UNAVAILABLE_PRODUCT_MODE = "2064"
    MANDATORY_FIELD_MISSING = "2065"
    AGREEMENT_NOT_SHARED = "2066"
    INVALID_PERMISSION = "2067"
    TRANSACTION_ALREADY_COMPLETED = "2068"
    TRANSACTION_ALREADY_CANCELLED = "2069"

    SYSTEM_UNDER_MAINTENANCE = "503"
    # Refund-specific
    MERCHANT_NOT_PERMITTED = "2082"
    REFUND_PROHIBITTED = "2081"
    IDENTITY_NOT_PERMITTED = "2080"
    INVALID_APP_TOKEN = "2079"
    INVALID_REFUND_REASON = "2078"
    INVALID_TRXID = "2077"
    REASON_CHARACTER_LIMIT_EXCEED = "2076"
    SKU_CHARACTER_LIMIT_EXCEED = "2075"
    IRREVERSIBLE = "2074"
    INVALID_SKU = "2073"
    INVALID_REFUND_AMOUNT = "2072"
    REFUND_TIME_EXCEEDED = "2071"


class ErrorResponse(BaseModel):
    errorCode: Union[ErrorCodeEnum, str]
    errorMessage: str


class BaseResponse(BaseModel):
    statusCode: str
    statusMessage: str


class BasePaymentIDRequest(BaseModel):
    paymentID: str


class Credential(BaseModel):
    username: str
    password: str
    app_key: str
    app_secret: str
