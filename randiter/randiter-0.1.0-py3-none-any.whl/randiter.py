import random
from collections.abc import Iterator
from typing import TypeVar

DEFAULT_BUFFER_SIZE = 10000

T = TypeVar("T")


def randiter(seq: Iterator[T], buffer_size: int = DEFAULT_BUFFER_SIZE) -> Iterator[T]:
    """Returns a random iterator for the given object.

    Args:
        seq: An iterable object.
        buffer_size: Buffer size used for shuffling. To perform perfect shuffling,
        specify a buffer size greater than or equal to the size of the sequence.

    """
    iterator = iter(seq)

    buf = []
    try:
        for _ in range(buffer_size):
            buf.append(next(iterator))
    except StopIteration:
        buffer_size = len(buf)

    while True:
        try:
            elem = next(iterator)
            idx = random.randint(0, buffer_size - 1)
            yield buf[idx]
            buf[idx] = elem
        except StopIteration:
            break

    while len(buf) > 0:
        idx = random.randint(0, len(buf) - 1)
        yield buf.pop(idx)
