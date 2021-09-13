"""
Annotated JSON structures as returned from TheGraph.
https://thegraph.com/explorer/subgraph/uniswap/uniswap-v2

For completion, consult official GraphQL schema for Uniswap 2.
https://github.com/Uniswap/uniswap-v2-subgraph/blob/master/schema.graphql

Conversion is done later in the code, this is just selling what was bought :D.
"""

try:
    from typing import TypedDict
except ImportError:
    # Python <=3.7 compatibility
    from typing_extensions import TypedDict


class UserRaw(TypedDict):
    id: str  # ETH address of the user


class TokenRaw(TypedDict, total=False):
    id: str  # ETH address of the token
    symbol: str
    name: str
    derivedETH: str  # Price of the token in ethers
    decimals: str  # For some reason returned as a string
    totalSupply: str


class PairRaw(TypedDict, total=False):
    id: str  # ETH address of the token (representing the liquidity pool pair)
    token0: TokenRaw
    token1: TokenRaw
    reserve0: str
    reserve1: str
    reserveUSD: str
    reserveETH: str
    totalSupply: str


class TransactionRaw(TypedDict):
    id: str  # hash of the transaction
    blockNumber: str  # Returned as str from the API
    timestamp: str  # Returned as str from the API


class LiquidityPositionRaw(TypedDict):
    user: UserRaw
    pair: PairRaw
    liquidityTokenBalance: str


class SwapRaw(TypedDict):
    user: UserRaw
    pair: PairRaw
    id: str  # hash of the swap transaction + "-" + index in swaps Transaction array
    sender: str  # ETH address
    to: str  # ETH address of the DEX router
    transaction: TransactionRaw
    amount0In: str
    amount0Out: str
    amount1In: str
    amount1Out: str
    timestamp: str
    amountUSD: str


class BurnRaw(TypedDict):
    pair: PairRaw
    id: str  # hash of the burn transaction + "-" + index in burns Transaction array
    sender: str  # ETH address
    to: str  # ETH address of the DEX router
    transaction: TransactionRaw
    amount0: str
    amount1: str
    timestamp: str
    liquidity: str  # Amount of pool tokens burned


class MintRaw(TypedDict):
    pair: PairRaw
    id: str  # hash of the mint transaction + "-" + index in mints Transaction array
    sender: str  # ETH address of the DEX router
    to: str  # ETH address
    transaction: TransactionRaw
    amount0: str
    amount1: str
    timestamp: str
    liquidity: str  # Amount of pool tokens minted
