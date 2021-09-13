from datetime import datetime, timezone
from decimal import Decimal

from thegraph_handlers._utils import div_safe, safe_decimal
from thegraph_handlers.dodoex_v2._types import (
    BurnRaw,
    LiquidityPositionRaw,
    LpTokenRaw,
    MintRaw,
    SwapRaw,
    TokenRaw,
)
from thegraph_handlers.models import (
    Burn,
    LiquidityPoolShare,
    LiquidityPoolToken,
    LiquidityPoolUnderlyingToken,
    Mint,
    Swap,
    Token,
)


def parse_lp_token(raw: LpTokenRaw) -> Token:
    return Token(
        symbol=raw["symbol"],
        name=create_lp_token_name(raw),
        contract_address=raw["id"],
        decimals=raw["decimals"],
    )


def parse_swap(raw: SwapRaw) -> Swap:
    token_out = Token(
        symbol=raw["fromToken"]["symbol"],
        name=raw["fromToken"]["name"],
        contract_address=raw["fromToken"]["id"],
        decimals=raw["fromToken"]["decimals"],
    )

    token_in = Token(
        symbol=raw["toToken"]["symbol"],
        name=raw["toToken"]["name"],
        contract_address=raw["toToken"]["id"],
        decimals=raw["toToken"]["decimals"],
    )

    return Swap(
        user_address=raw["sender"],
        token_in=token_in,
        token_out=token_out,
        tx_hash=raw["hash"],
        block=int(raw["block"]),
        datetime=datetime.fromtimestamp(float(raw["timestamp"]), tz=timezone.utc),
        token_in_amount=safe_decimal(raw["amountIn"]),
        token_out_amount=safe_decimal(raw["amountOut"]),
        fee_usd=safe_decimal(raw["volumeUSD"]) * Decimal("0.003"),
    )


def parse_liquidity_position(raw: LiquidityPositionRaw) -> LiquidityPoolShare:
    pool_token_amount = safe_decimal(raw["liquidityTokenBalance"])

    # Some abandonded liquidity pools may have zero balance
    pool_share = div_safe(pool_token_amount, raw["lpToken"]["totalSupply"])

    return LiquidityPoolShare(
        user_address=raw["user"]["id"],
        share=pool_share,
        lp_token=LiquidityPoolToken(
            token=Token(
                symbol=raw["lpToken"]["symbol"],
                name=create_lp_token_name(raw["lpToken"]),
                contract_address=raw["lpToken"]["id"],
            ),
            amount=pool_token_amount,
            underlying_tokens=(
                create_lp_underlying_token(
                    raw["lpToken"]["pair"]["baseToken"],
                    safe_decimal(raw["lpToken"]["pair"]["baseReserve"]) * pool_share,
                ),
                create_lp_underlying_token(
                    raw["lpToken"]["pair"]["quoteToken"],
                    safe_decimal(raw["lpToken"]["pair"]["quoteReserve"]) * pool_share,
                ),
            ),
        ),
    )


def parse_mint(mint_dict: MintRaw) -> Mint:
    raw: MintRaw = mint_dict
    return Mint(
        tx_hash=raw["hash"],
        block=int(raw["block"]),
        datetime=datetime.fromtimestamp(float(raw["timestamp"]), tz=timezone.utc),
        user_address=mint_dict["from"],
        lp_token=create_lp_token(raw),
    )


def parse_burn(burn_dict: BurnRaw) -> Burn:
    raw: BurnRaw = burn_dict
    return Burn(
        tx_hash=raw["hash"],
        block=int(raw["block"]),
        datetime=datetime.fromtimestamp(float(raw["timestamp"]), tz=timezone.utc),
        user_address=burn_dict["from"],
        lp_token=create_lp_token(raw),
    )


def create_lp_token(raw: dict):
    return LiquidityPoolToken(
        token=Token(
            symbol=raw["lpToken"]["symbol"],
            name=create_lp_token_name(raw["lpToken"]),
            contract_address=raw["lpToken"]["id"],
        ),
        amount=safe_decimal(raw["amount"]),
        underlying_tokens=(
            create_lp_underlying_token(
                raw["lpToken"]["pair"]["baseToken"], raw["baseAmountChange"]
            ),
            create_lp_underlying_token(
                raw["lpToken"]["pair"]["quoteToken"], raw["quoteAmountChange"]
            ),
        ),
    )


def create_lp_token_name(lp_token: LpTokenRaw) -> str:
    if lp_token["pair"] is None:
        return lp_token["name"]
    else:
        return f"Dodo V2 - {lp_token['pair']['baseToken']['symbol']}/{lp_token['pair']['quoteToken']['symbol']}"


def create_lp_underlying_token(
    token: TokenRaw,
    amount: Decimal,
) -> LiquidityPoolUnderlyingToken:
    return LiquidityPoolUnderlyingToken(
        token=Token(
            symbol=token["symbol"],
            name=token["name"],
            contract_address=token["id"],
            decimals=token["decimals"],
        ),
        weight=Decimal("0.5"),  # todo verify correctness
        amount=safe_decimal(amount),
    )
