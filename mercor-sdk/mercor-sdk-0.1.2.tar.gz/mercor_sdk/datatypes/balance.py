from decimal import Decimal
from typing import Union

from pydantic import BaseModel

from mercor_sdk.datatypes import AlgorithmId, Response


class TotalSupply(BaseModel):
    amount: Decimal


class RelativeAmount(BaseModel):
    amount: Decimal


class AlgorithmBalance(BaseModel):
    supply: TotalSupply
    ratio: RelativeAmount


class BlockChainError(BaseModel):
    algorithm_id: AlgorithmId
    reason: str = "Blockchain error occurred."


class AlgorithmBalanceResponse(Response):
    response: Union[AlgorithmBalance, BlockChainError]
