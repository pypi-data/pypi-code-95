from typing import Optional

import attr
from levo_commons.events import Event


@attr.s()
class CorruptedConfigFile(Exception):
    """Levo's config file appears to be corrupted."""

    path: str = attr.ib()


@attr.s()
class UnexpectedEndOfStream(Exception):
    """Event steam exhausted without yielding a terminal event."""

    last_event: Optional[Event] = attr.ib()
