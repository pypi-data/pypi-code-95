import asyncio
import logging
from typing import List

import aiohttp

from down_notifier.channel import BaseChannel

logger = logging.getLogger("down-notifier")


class Site:
    check_task: asyncio.Task
    notify_tasks: List[asyncio.Task] = []

    def __init__(
        self,
        name: str,
        url: str,
        status_code: int,
        timeout: int,
        channels: List[BaseChannel],
    ) -> None:
        self.name = name
        self.url = url
        self.status_code = status_code
        self.timeout = timeout
        self.channels = channels

    async def check(self, session: aiohttp.ClientSession) -> None:
        self.notify_tasks = [task for task in self.notify_tasks if not task.done()]

        logger.info(f"{self.name} checking {self.url}")
        async with session.get(self.url) as res:
            logger.info(f"{self.name} status {res.status}, expected {self.status_code}")
            if res.status != self.status_code:
                logger.info(f"{self.name} is sending notifications...")
                for channel in self.channels:
                    logger.info(f"{self.name} is notifying {channel.name}")
                    self.notify_tasks.append(
                        asyncio.create_task(channel.notify(self.url, res.status))
                    )
