# based on the ratelimit plugin in the postomaat project (https://gitlab.com/fumail/postomaat)
# developed by @ledgr

import logging
import typing as tp
from hashlib import md5
import asyncio


class BackendInterface(object):
    """Abstract base class for backends"""
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(f"fuglu.plugins.{self.__class__.__name__}")

    def _fix_eventname(self, eventname) -> str:
        if not isinstance(eventname, str):
            eventname = str(eventname)
        if len(eventname) > 255:
            eventname = md5(eventname.encode()).hexdigest()
        return eventname

    def check_allowed(self,
                      eventname: str,
                      limit: tp.Union[int, float],
                      timespan: tp.Union[int, float],
                      increment: int,
                      ) -> tp.Union[asyncio.Future, tp.Tuple[bool, tp.Union[int, float]]]:
        raise NotImplementedError()

