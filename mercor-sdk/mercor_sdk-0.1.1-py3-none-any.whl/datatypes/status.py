import enum
from typing import Union

from pydantic import BaseModel, validator

from mercor_sdk.datatypes import AlgorithmId, Response, TransactionHash


class StatusRequest(BaseModel):
    algorithm_id: AlgorithmId
    transaction_hash: TransactionHash
    timeout_in_seconds: int

    @validator("timeout_in_seconds")
    def timeout_range(cls, timeout_value):
        assert 120 >= timeout_value >= 0
        return timeout_value


class TradeStatus(str, enum.Enum):
    TRADE_SUCCESSFUL = "TRADE_SUCCESSFUL"
    TRADE_IN_PROGRESS_OR_NOT_FOUND = "TRADE_IN_PROGRESS_OR_NOT_FOUND"
    TRADE_FAILED = "TRADE_FAILED"


class TradeSuccessfulResponse(BaseModel):
    code: TradeStatus = TradeStatus.TRADE_SUCCESSFUL
    message: str = "Trade successful."


class TradeInProgressOrNotFoundResponse(BaseModel):
    code: TradeStatus = TradeStatus.TRADE_IN_PROGRESS_OR_NOT_FOUND
    message: str = "Trade is in progress or cannot be found."


class TradeFailedResponse(BaseModel):
    code: TradeStatus = TradeStatus.TRADE_FAILED
    message: str = "Trade failed."


class TradeStatusResponse(Response):
    response: Union[TradeSuccessfulResponse, TradeInProgressOrNotFoundResponse, TradeFailedResponse]
