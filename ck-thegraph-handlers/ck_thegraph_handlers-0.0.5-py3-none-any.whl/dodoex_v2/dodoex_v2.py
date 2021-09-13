from thegraph_handlers._protocols import AClosableHTTPClient
from thegraph_handlers.dodoex_v2._types import ParserDispatch
from thegraph_handlers.dodoex_v2.base_swap import BaseSwap
from thegraph_handlers.dodoex_v2.parsers import (
    parse_burn,
    parse_liquidity_position,
    parse_lp_token,
    parse_mint,
    parse_swap,
)


class DodoexV2(BaseSwap):
    def __init__(
        self,
        client: AClosableHTTPClient,
        url: str = "http://api.thegraph.com/subgraphs/name/dodoex/dodoex-v2",
    ) -> None:
        parsers = ParserDispatch(
            liquidity_position=parse_liquidity_position,
            swap=parse_swap,
            burn=parse_burn,
            mint=parse_mint,
            token=parse_lp_token,
        )
        BaseSwap.__init__(self, client, url, parsers)
