from typing import Any, Callable, Dict, TypedDict

from thegraph_handlers.models import Burn, LiquidityPoolShare, Mint, Swap

ParserArgs = Dict[str, Any]


class ParserDispatch(TypedDict):
    burn: Callable[[ParserArgs], Burn]
    liquidity_position: Callable[[ParserArgs], LiquidityPoolShare]
    mint: Callable[[ParserArgs], Mint]
    swap: Callable[[ParserArgs], Swap]
