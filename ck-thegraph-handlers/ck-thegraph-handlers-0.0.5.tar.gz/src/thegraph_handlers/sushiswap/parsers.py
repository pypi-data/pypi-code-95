from datetime import datetime, timezone
from decimal import Decimal
from typing import Tuple

from thegraph_handlers._utils import div_safe, safe_decimal
from thegraph_handlers.models import (
    Burn,
    LiquidityPoolShare,
    LiquidityPoolToken,
    LiquidityPoolUnderlyingToken,
    Mint,
    Swap,
    Token,
)
from thegraph_handlers.shared._types import (
    BurnRaw,
    LiquidityPositionRaw,
    MintRaw,
    PairRaw,
    SwapRaw,
)


def parse_liquidity_position(raw: LiquidityPositionRaw) -> LiquidityPoolShare:
    pool_token_amount = safe_decimal(raw["liquidityTokenBalance"])

    # Some abandonded liquidity pools may have zero balance
    pool_share = div_safe(pool_token_amount, raw["pair"]["totalSupply"])

    pair = raw["pair"]
    tokens = tuple(
        LiquidityPoolUnderlyingToken(
            token=Token(
                symbol=pair[f"token{i}"]["symbol"],
                name=pair[f"token{i}"]["name"],
                contract_address=pair[f"token{i}"]["id"],
                decimals=pair[f"token{i}"]["decimals"],
            ),
            weight=Decimal("0.5"),  # Uniswap has 1:1 ratio
            amount=safe_decimal(pair[f"reserve{i}"]) * pool_share,
        )
        for i in range(2)
    )
    return LiquidityPoolShare(
        user_address=raw["user"]["id"],
        share=pool_share,
        lp_token=LiquidityPoolToken(
            token=Token(
                symbol="SLP",
                name=create_lp_token_name_from_pair(pair),
                contract_address=pair["id"],
            ),
            amount=pool_token_amount,
            underlying_tokens=tokens,
        ),
    )


def parse_swap(raw: SwapRaw) -> Swap:
    in_, out_ = ("1", "0") if raw["amount0In"] == "0" else ("0", "1")

    pair = raw["pair"]
    token_in = Token(
        symbol=pair[f"token{in_}"]["symbol"],
        name=pair[f"token{in_}"]["name"],
        contract_address=pair[f"token{in_}"]["id"],
        decimals=pair[f"token{in_}"]["decimals"],
    )
    token_out = Token(
        symbol=pair[f"token{out_}"]["symbol"],
        name=pair[f"token{out_}"]["name"],
        contract_address=pair[f"token{out_}"]["id"],
        decimals=pair[f"token{out_}"]["decimals"],
    )
    return Swap(
        tx_hash=raw["transaction"]["id"],
        block=int(raw["transaction"]["blockNumber"]),
        datetime=datetime.fromtimestamp(float(raw["timestamp"]), tz=timezone.utc),
        user_address=raw["to"],
        token_in=token_in,
        token_in_amount=safe_decimal(raw[f"amount{in_}In"]),
        token_out=token_out,
        token_out_amount=safe_decimal(raw[f"amount{out_}Out"]),
        fee_usd=safe_decimal(raw["amountUSD"])
        * Decimal("0.003"),  # TODO: Is this correct?
    )


def parse_mint(raw: MintRaw) -> Mint:
    return Mint(
        tx_hash=raw["transaction"]["id"],
        block=int(raw["transaction"]["blockNumber"]),
        datetime=datetime.fromtimestamp(float(raw["timestamp"]), tz=timezone.utc),
        user_address=raw["to"],
        lp_token=LiquidityPoolToken(
            token=Token(
                symbol="SLP",
                name=create_lp_token_name_from_pair(raw["pair"]),
                contract_address=raw["pair"]["id"],
            ),
            amount=safe_decimal(raw["liquidity"]),
            underlying_tokens=create_lp_underlying_tokens(raw),
        ),
    )


def parse_burn(raw: BurnRaw) -> Burn:
    return Burn(
        tx_hash=raw["transaction"]["id"],
        block=int(raw["transaction"]["blockNumber"]),
        datetime=datetime.fromtimestamp(float(raw["timestamp"]), tz=timezone.utc),
        user_address=raw["sender"],
        lp_token=LiquidityPoolToken(
            token=Token(
                symbol="SLP",
                name=create_lp_token_name_from_pair(raw["pair"]),
                contract_address=raw["pair"]["id"],
            ),
            amount=safe_decimal(raw["liquidity"]),
            underlying_tokens=create_lp_underlying_tokens(raw),
        ),
    )


def create_lp_token_name_from_pair(pair: PairRaw) -> str:
    return f"SushiSwap - {pair['token0']['symbol']}/{pair['token1']['symbol']}"


def create_lp_underlying_tokens(
    raw: dict,
) -> Tuple[LiquidityPoolUnderlyingToken, ...]:
    pair: PairRaw = raw["pair"]
    return tuple(
        LiquidityPoolUnderlyingToken(
            token=Token(
                symbol=pair[f"token{i}"]["symbol"],
                name=pair[f"token{i}"]["name"],
                contract_address=pair[f"token{i}"]["id"],
                decimals=pair[f"token{i}"]["decimals"],
            ),
            weight=Decimal("0.5"),  # Uniswap has 1:1 ratio
            amount=safe_decimal(raw[f"amount{i}"]),
        )
        for i in range(2)
    )
