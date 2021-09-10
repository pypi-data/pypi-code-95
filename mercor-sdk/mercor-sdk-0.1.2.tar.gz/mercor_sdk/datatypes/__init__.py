"""Package for data transfer objects.
"""
from typing import Any

from pydantic import BaseModel, Field
from eth_typing import ChecksumAddress


class Response(BaseModel):
    response: Any = Field(...)

    def __getattr__(self, name):
        try:
            return self.response.__getattribute__(name)
        except AttributeError:
            raise


class AlgorithmId(BaseModel):
    public_address: ChecksumAddress


class TransactionHash(BaseModel):
    value: str
