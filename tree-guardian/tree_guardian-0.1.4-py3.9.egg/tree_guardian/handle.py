import os
import sys

from typing import Iterable, Callable, Union
from threading import Thread, Event as TEvent

from .hash_observer import HashObserver
from .constants import EXCLUDE_RECOMMENDED

__all__ = [
    'observe',
]

TIP = """Observing path "{path}" triggering `{function}()` excluding:
"{excluded}".
"""


def observe(
    callback: Callable,
    path: str = '.',
    exclude: Iterable[str] = None,
    run_async: bool = False,
    approach: Union[Thread] = None,
    event: Union[TEvent] = None
):
    """Observe directory and trigger callback on change detection.
 
    :param callback: Target function to be called
    :param path: The observable root path
    :param exclude: Excluded files (default is tree_guardian.EXCLUDE_RECOMMENDED)
    :param run_async: Run in background
    :param approach: Processor object
    :param event: Stop event
    """

    if exclude is None:
        exclude = EXCLUDE_RECOMMENDED

    if approach is None:
        approach = Thread

    if run_async:
        sys.stdout.write('Running in background.\n')
        sys.stdout.flush()

        if event is None:
            sys.stderr.write('(!) No event provided\n')
            sys.stderr.flush()

    sys.stdout.write(TIP.format(
        path=os.path.abspath(path),
        function=callback.__name__,
        excluded='"; "'.join(exclude)
    ))
    sys.stdout.flush()

    observer = HashObserver(path=path, exclude=exclude)

    if not run_async:
        observer.observe(callback=callback)
        return

    handler = approach(
        target=observer.observe,
        daemon=True,
        kwargs={
            'callback': callback,
            'event': event
        }
    )
    handler.start()
