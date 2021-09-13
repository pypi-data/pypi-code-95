from datetime import datetime
from decimal import Decimal
from typing import Optional, Sequence, Tuple

import attr
from web3 import Web3


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Token:
    symbol: str
    name: str
    contract_address: str = attr.ib(converter=Web3.toChecksumAddress)
    decimals: Optional[str] = attr.ib(default=None, repr=False)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class LiquidityPoolToken:
    token: Token
    amount: Decimal
    underlying_tokens: Tuple["LiquidityPoolUnderlyingToken", ...] = attr.ib()

    @underlying_tokens.validator
    def _validate_token_weights(
        self, attribute, value: Sequence["LiquidityPoolUnderlyingToken"]
    ) -> None:
        if sum(t.weight for t in value) != 1:
            raise ValueError("Token weights must add up to 1!")


@attr.s(auto_attribs=True, slots=True, frozen=True)
class LiquidityPoolUnderlyingToken:
    token: Token
    weight: Decimal = attr.ib()
    amount: Decimal

    @weight.validator
    def _validate_weight(self, attribute, value: Decimal) -> None:
        if not 0 < value < 1:
            raise ValueError("Token weight must be between 0 and 1 (exclusive)!")


@attr.s(auto_attribs=True, slots=True, frozen=True)
class LiquidityPoolShare:
    user_address: str = attr.ib(converter=Web3.toChecksumAddress)
    share: Decimal = attr.ib()
    lp_token: LiquidityPoolToken


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Swap:
    tx_hash: str
    block: int
    datetime: datetime
    user_address: str = attr.ib(converter=Web3.toChecksumAddress)

    token_in: Token
    token_in_amount: Decimal
    token_out: Token
    token_out_amount: Decimal
    fee_usd: Decimal  # TODO: Include this field?


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Mint:
    tx_hash: str
    block: int
    datetime: datetime
    user_address: str = attr.ib(converter=Web3.toChecksumAddress)
    lp_token: LiquidityPoolToken


# TODO: `Burn` and `Mint` have the same structure for now
@attr.s(auto_attribs=True, slots=True, frozen=True)
class Burn:
    tx_hash: str
    block: int
    datetime: datetime
    user_address: str = attr.ib(converter=Web3.toChecksumAddress)
    lp_token: LiquidityPoolToken
