import enum
from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel

from mercor_sdk.datatypes import AlgorithmId, Response, TransactionHash


class Slippage(BaseModel):
    amount: Decimal


class BuyTrade(BaseModel):
    algorithm_id: AlgorithmId
    slippage: Slippage
    relative_amount: Decimal


class SellTrade(BaseModel):
    algorithm_id: AlgorithmId
    slippage: Slippage
    relative_amount: Decimal


class TradeRequest(BaseModel):
    trade: Union[BuyTrade, SellTrade]


class NewAlgorithmLock(BaseModel):
    algorithm_id: AlgorithmId


class TradeResponseLockType(str, enum.Enum):
    NOW_LOCKED = "SUCCESS:ALGORITHM-IS-NOW-LOCKED"
    WAS_LOCKED = "DENIED:ALGORITHM-ALREADY-LOCKED"


class AlgorithmIsLocked(BaseModel):
    lock: NewAlgorithmLock
    transaction_hash: TransactionHash
    lock_type: TradeResponseLockType = TradeResponseLockType.NOW_LOCKED


class AlgorithmWasLocked(BaseModel):
    lock: NewAlgorithmLock
    transaction_hash: Optional[TransactionHash]
    lock_type: TradeResponseLockType = TradeResponseLockType.WAS_LOCKED


class InsufficientFunds(BaseModel):
    algorithm_id: AlgorithmId
    reason: str = "Not enough funds in algorithm contract to trade."


class BlockChainError(BaseModel):
    algorithm_id: AlgorithmId
    reason: str = "Blockchain error occurred."


class TradeRequestResponse(Response):
    response: Union[AlgorithmIsLocked, AlgorithmWasLocked, InsufficientFunds, BlockChainError]
