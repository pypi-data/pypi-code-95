from contextlib import asynccontextmanager
from typing import *  # noqa: F403

from scrapli.driver.core import AsyncIOSXEDriver, AsyncNXOSDriver
from scrapli.driver.network.async_driver import AsyncNetworkDriver

from netrunner.connections.base import Base

PLATFORM = {"ios": AsyncIOSXEDriver, "nxos": AsyncNXOSDriver}


class SSH(Base):
    def __init__(self, host: str, username: str, password: str, platform: str, enable: str) -> None:
        self._con: AsyncNetworkDriver = None
        self.host: str = host
        self.username: str = username
        self.password: str = password
        self.enable: str = enable
        self.platform: str = platform

    def get_driver(self) -> None:
        self._con = PLATFORM.get(self.platform)(
            host=self.host,
            auth_username=self.username,
            auth_password=self.password,
            auth_secondary=self.enable,
            auth_strict_key=False,
            transport="asyncssh",
        )

    async def open(self):
        if self._con is None:
            self.get_driver()
        await self._con.open()

    async def close(self):
        await self._con.close()

    @asynccontextmanager
    async def connection_manager(self):
        await self.open()
        print("connection open")
        yield self
        await self.close()
        print("connection closed")

    async def get_connection(self):
        if not self._con.isalive():
            await self.open()
        return self._con

    async def send_command(self, cmd: str, parse: bool = True) -> Union[Dict, str]:
        connection: AsyncNetworkDriver = await self.get_connection()
        result = await connection.send_command(cmd)
        if parse:
            return result.genie_parse_output()
        return result.result
