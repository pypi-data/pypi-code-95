import json
import logging

import httpx

from .connection import Connection
from .const import BALANCE_URL, HOST, TOKEN_URL, PROTOCOL_URL, COMPLEX_PROTOCOL_URL
from .wallet import Wallet


class Debank:

    """Initialize the Debank object"""

    def __init__(self, address, websession: httpx.AsyncClient):
        self._address = address
        self._connection = Connection(websession, HOST)
        self._wallet = None
        self._defiWalletContents = {}

        self._protocolResultsJson = None
        self._debank_defi_wallet_balance = 0.0
        return

    async def connect(self) -> bool:
        if await self._getEndpoint(BALANCE_URL.format(self._address)):
            return True
        else:
            return False

    def getDefiWalletBalance(self):
        return self._debank_defi_wallet_balance

    def getDefiWalletItems(self):
        return self._defiWalletContents

    async def update(self) -> None:
        await self._setDefiWalletList()
        return

    async def _getEndpoint(self, pageURL) -> json:
        results = await self._connection.get(pageURL.format(self._address))
        logging.debug("Results: %s", results.json())
        if results.status_code == httpx.codes.OK:
            try:
                return results.json()
            except json.JSONDecodeError:
                raise

        elif results.status_code == 401:
            return False
        else:
            results.raise_for_status()
        return True

    async def _setDefiWalletList(self) -> None:
        total = 0

        # Get Tokens and add to total balance
        tokenJSON = await self._getEndpoint(TOKEN_URL)
        for t in range(len(tokenJSON)):
            total += (tokenJSON[t]["price"]
                      * tokenJSON[t]["amount"])
            logging.debug("Name: %s - Value: $%s", tokenJSON[t]["name"], (
                tokenJSON[t]["price"] * tokenJSON[t]["amount"]))
            self._defiWalletContents.update({tokenJSON[t]["name"]: {"value": (tokenJSON[t]["price"] * tokenJSON[t]["amount"]),
                                                                    "price": tokenJSON[t]["price"]}})

        # Get Farming and add to balance
        farmJSON = await self._getEndpoint(COMPLEX_PROTOCOL_URL)
        for f in range(len(farmJSON[0]["portfolio_item_list"])):
            name = f"{farmJSON[0]['portfolio_item_list'][f]['detail']['supply_token_list'][0]['name']}-{farmJSON[0]['portfolio_item_list'][f]['detail']['supply_token_list'][1]['name']}"
            value = farmJSON[0]["portfolio_item_list"][f]["stats"]["net_usd_value"]
            logging.debug("Name: %s - Value: $%s", name, value)
            total += value
            self._defiWalletContents.update({name: {"value": value,
                                                    "price": 0.0}})
        self._setDefiWalletBalance(total)
        return

    def _setDefiWalletBalance(self, balance) -> None:
        self._debank_defi_wallet_balance = balance
        return
