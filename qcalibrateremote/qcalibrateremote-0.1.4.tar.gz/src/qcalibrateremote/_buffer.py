#    Copyright 2021 Qruise project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
from queue import Queue
from typing import Callable, Generator, Generic, TypeVar

from icecream import ic

TItem = TypeVar('TItem')


class QueueBuffer(Generic[TItem]):
    def __init__(
        self,
        is_end: Callable[[TItem], bool],
        timeout: float = None
    ) -> None:
        """[summary]

        Parameters
        ----------
        is_end : Callable[[TItem], bool]
            check if an item is terminal message
        timeout : float, optional
            Timeout in seconds to wait for a remote reply, by default None - wait forever
        """
        self._queue = Queue()
        self._timeout = timeout
        self._finished = False
        self._is_end = is_end

    def put(self, request: TItem) -> None:
        """Puts an element in the queue

        Parameters
        ----------
        request : TItem
            item to put in the quue
        """
        if not self._finished:
            if not request or self._is_end(request):
                self._finished = True
            self._queue.put(request)
        else:
            logging.warn("Send after end %s", request)

    def get(self) -> Generator[TItem, None, None]:
        """generator to evaluate for output

        Yields
        -------
        Generator[TItem, None, None]
            The output to iterate over

        Raises
        ------
        queue.Empty
            An item is not available after a specified time-out
                
        """
        run = True
        while run:
            next: TItem = self._queue.get(timeout=self._timeout)
            if next:
                ic("QueueBuffer.__next__", next)
                yield next
                if self._is_end(next):
                    run = False
            else:
                run = False
