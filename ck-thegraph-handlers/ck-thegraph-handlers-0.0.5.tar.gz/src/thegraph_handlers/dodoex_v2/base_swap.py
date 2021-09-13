import logging
from datetime import datetime, timezone
from types import TracebackType
from typing import Any, AsyncGenerator, Callable, Dict, Optional, Set, Type, TypeVar

from thegraph_handlers._exceptions import SubgraphError
from thegraph_handlers._protocols import AClosableHTTPClient
from thegraph_handlers._subgraph_client import SubgraphClient
from thegraph_handlers.dodoex_v2.queries import (
    burns_query,
    liquidity_pool_shares_query,
    mints_query,
    swaps_query,
    tokens_query,
)
from thegraph_handlers.models import Burn, LiquidityPoolShare, Mint, Swap, Token

A = TypeVar("A")

logger = logging.getLogger(__name__)


class BaseSwap:
    def __init__(
        self,
        client: AClosableHTTPClient,
        url: str,
        parser_dispatch: Dict[str, Callable[[Dict[str, Any]], A]],
    ) -> None:
        self.parser_dispatch = parser_dispatch
        self.subgraph_client = SubgraphClient(url, client=client)

    async def __aenter__(self) -> "BaseSwap":
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        await self.subgraph_client.aclose()

    async def yield_liquidity_pool_shares(
        self,
        address: str,
        include_withdrawn: bool = False,
    ) -> AsyncGenerator[LiquidityPoolShare, None]:
        """
        If `include_withdrawn=True`, list shares of liquidity pools the `address`
        sometime in the past provided liquidity to.
        """
        variables = {
            "address": address.lower(),
            "min": "-1" if include_withdrawn else "0",
        }

        response = await self._execute(
            liquidity_pool_shares_query,
            variables,
        )

        for position in response["result"]:
            yield self.parser_dispatch["liquidity_position"](position)

    async def _yield(
        self,
        query: str,
        parser: Callable[[Dict[str, Any]], A],
        address: str,
        since: int,
        until: Optional[int] = None,
        limit: int = 500,
        excluded_txs: Optional[Set[str]] = None,
    ) -> AsyncGenerator[A, None]:
        """
        For now, provided `query` needs to have exactly 1 `format` string and
        also return the query under the `result` key.

        Still seems a little clumsy, but time will tell us about proper
        abstraction.
        """
        until = (
            int(datetime.now(tz=timezone.utc).timestamp()) if until is None else until
        )
        variables = {
            "address": address.lower(),
            "since": since,
            "until": until,
        }
        query_formatted = query % (limit,)

        response = await self._execute(
            query_formatted,
            variables,
        )

        excluded_txs = set(excluded_txs) if excluded_txs is not None else set()
        raws = response["result"]
        for raw in raws:
            if raw["id"] in excluded_txs:
                continue
            else:
                yield parser(raw)

        if len(raws) == limit:
            last_ts = int(raws[-1]["timestamp"])
            excluded_txs = {
                raw["id"] for raw in raws if int(raw["timestamp"]) == last_ts
            }
            async for d in self._yield(
                query=query,
                parser=parser,
                address=address,
                since=last_ts,
                until=until,
                limit=limit,
                excluded_txs=excluded_txs,
            ):
                yield d

    async def yield_burns(
        self,
        address: str,
        since: int,
        until: Optional[int] = None,
        limit: int = 500,
        excluded_txs: Optional[Set[str]] = None,
    ) -> AsyncGenerator[Burn, None]:
        async for d in self._yield(
            burns_query,
            self.parser_dispatch["burn"],
            address,
            since,
            until,
            limit,
            excluded_txs,
        ):
            yield d

    async def yield_mints(
        self,
        address: str,
        since: int,
        until: Optional[int] = None,
        limit: int = 500,
        excluded_txs: Optional[Set[str]] = None,
    ) -> AsyncGenerator[Mint, None]:
        async for d in self._yield(
            mints_query,
            self.parser_dispatch["mint"],
            address,
            since,
            until,
            limit,
            excluded_txs,
        ):
            yield d

    async def yield_swaps(
        self,
        address: str,
        since: int,
        until: Optional[int] = None,
        limit: int = 500,
        excluded_txs: Optional[Set[str]] = None,
    ) -> AsyncGenerator[Swap, None]:
        async for d in self._yield(
            swaps_query,
            self.parser_dispatch["swap"],
            address,
            since,
            until,
            limit,
            excluded_txs,
        ):
            yield d

    async def yield_tokens(
        self,
    ) -> AsyncGenerator[Token, None]:

        response = await self._execute(
            tokens_query,
        )

        raws = response["result"]
        for raw in raws:
            yield self.parser_dispatch["token"](raw)

    async def _execute(self, query: str, variables: Dict[str, Any] = None) -> dict:
        try:
            return await self.subgraph_client.execute(query, variables)
        except SubgraphError as exc:
            logger.error("Internal exception for %s fetching - %s", self.name, exc)
            raise exc from None
        except Exception as exc:
            logger.error("HTTP exception for %s fetching - %s", self.name, exc)
            raise exc from None

    @property
    def name(self) -> str:
        return self.__class__.__name__
