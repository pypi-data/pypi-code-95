from typing import Dict

from pydantic import BaseModel

from mercor_sdk.datatypes import Response


class PancakeSwapTicker(BaseModel):
    name: str
    symbol: str
    price: str
    price_BNB: str


class PancakeSwapTickerResponse(BaseModel):
    updated_at: int
    data: PancakeSwapTicker

    def __getattr__(self, name):
        try:
            return self.data.__getattribute__(name)
        except AttributeError:
            raise


class PancakeSwapTickerListResponse(BaseModel):
    updated_at: int
    data: Dict[str, PancakeSwapTicker]

    def __getitem__(self, key):
        try:
            return self.data.__getitem__(key)
        except KeyError:
            raise


class TickerResponse(Response):
    response: PancakeSwapTickerResponse

    def __getattr__(self, name):
        try:
            return self.response.__getattr__(name)
        except AttributeError:
            raise


class TickerListResponse(Response):
    response: PancakeSwapTickerListResponse

    def __getattr__(self, name):
        try:
            return self.response.__getattr__(name)
        except AttributeError:
            raise

    def __getitem__(self, key):
        try:
            return self.response.__getitem__(key)
        except KeyError:
            raise
