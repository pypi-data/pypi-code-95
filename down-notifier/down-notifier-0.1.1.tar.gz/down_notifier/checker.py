import asyncio
import logging
from typing import List

import aiohttp

from down_notifier.site import Site

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("down-notifier")


class Checker:
    def __init__(self, sites: List[Site]) -> None:
        self._sites = sites
        self._session = aiohttp.ClientSession()

    async def _check(self, site: Site, timeout: int) -> None:
        logger.info(f"{site.name} timeout {timeout}")
        await asyncio.sleep(timeout)
        await site.check(self._session)
        site.check_task = asyncio.create_task(self._check(site, site.timeout))

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        for site in self._sites:
            site.check_task = loop.create_task(self._check(site, 2))

    def start_loop(self) -> None:
        loop = asyncio.get_event_loop()
        self.start(loop)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            tasks = []
            for site in self._sites:
                site.check_task.cancel()
                for task in site.notify_tasks:
                    task.cancel()
                    tasks.append(task)
                tasks.append(site.check_task)
            tasks.append(loop.create_task(self._session.close()))
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            loop.run_until_complete(asyncio.sleep(1))
        finally:
            loop.close()
            logger.info("Done!")
