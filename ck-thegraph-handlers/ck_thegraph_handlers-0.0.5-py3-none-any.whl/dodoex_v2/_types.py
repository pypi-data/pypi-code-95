from typing import Any, Callable, Dict, Optional, TypeVar

from thegraph_handlers.models import Burn, LiquidityPoolShare, Mint, Swap, Token

Data = Dict[str, Any]

A = TypeVar("A")

try:
    from typing import TypedDict
except ImportError:
    # Python <=3.7 compatibility
    from typing_extensions import TypedDict


class ParserDispatch(TypedDict, total=False):
    token: Optional[Callable[[Data], Token]]
    mint: Optional[Callable[[Data], Mint]]
    burn: Optional[Callable[[Data], Burn]]
    swap: Optional[Callable[[Data], Swap]]
    liquidity_position: Optional[Callable[[Data], LiquidityPoolShare]]


class TokenRaw(TypedDict, total=False):
    symbol: str
    name: str
    id: str
    decimals: str


class SwapRaw(TypedDict):
    id: str
    fromToken: TokenRaw
    toToken: TokenRaw
    sender: str
    hash: str
    block: str
    timestamp: str
    amountIn: str
    amountOut: str
    volumeUSD: str


class User(TypedDict):
    id: str


class PairRaw(TypedDict):
    baseToken: TokenRaw
    quoteToken: TokenRaw
    baseReserve: str
    quoteReserve: str


class LpTokenRaw(TypedDict, total=False):
    symbol: str
    name: str
    id: str
    decimals: str
    totalSupply: str
    pair: PairRaw


class LiquidityPositionRaw(TypedDict):
    user: User
    liquidityTokenBalance: str
    liquidityTokenInMining: str
    lpToken: LpTokenRaw


class MintRaw(TypedDict):
    # from: str
    id: str
    hash: str
    amount: str
    block: str
    timestamp: str
    baseAmountChange: str
    quoteAmountChange: str
    lpToken: LpTokenRaw


class BurnRaw(TypedDict):
    # from: str
    id: str
    hash: str
    amount: str
    block: str
    timestamp: str
    baseAmountChange: str
    quoteAmountChange: str
    lpToken: LpTokenRaw
