from __future__ import annotations, with_statement

import functools
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from logging import getLogger
from typing import Awaitable, Callable, TypeVar

from .utils import get_datadog_trace_link, random_str

logger = getLogger(__name__)

# Sessions last the entire duration of the python process
COILED_SESSION_ID = "coiled-session-" + random_str()
logger.debug(f"Coiled Session  ID : {COILED_SESSION_ID}")

# Operations are transient and more granular
# Note: we don't type the actual RHS value due to a bug in some versions of Python
# 3.7 and 3.8: https://bugs.python.org/issue38979
COILED_OP_CONTEXT: ContextVar[str] = ContextVar("coiled-operation-context")

ContextReturnT = TypeVar("ContextReturnT")


@contextmanager
def operation_context(name: str):
    try:
        c_id = COILED_OP_CONTEXT.get()
        # already in a coiled op context, don't create a new one
        yield c_id
    except LookupError:
        # create a new coiled context
        c_id = name + "-" + random_str()
        reset = COILED_OP_CONTEXT.set(c_id)

        logger.debug(f"Entering {c_id}")
        start = datetime.now(tz=timezone.utc)
        yield c_id
        trace_url = get_datadog_trace_link(
            start=start,
            end=datetime.now(tz=timezone.utc),
            **{"coiled-operation-id": c_id},
        )
        logger.debug(f"Exiting {c_id} - DD URL: {trace_url}")
        if reset:
            COILED_OP_CONTEXT.reset(reset)


def track_context(
    func: Callable[..., Awaitable[ContextReturnT]]
) -> Callable[..., Awaitable[ContextReturnT]]:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        with operation_context(name=f"{func.__module__}.{func.__qualname__}"):
            return await func(*args, **kwargs)

    return wrapper
