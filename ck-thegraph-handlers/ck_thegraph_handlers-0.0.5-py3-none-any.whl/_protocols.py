from types import TracebackType
from typing import Any, Type, TypeVar

try:
    from typing import Protocol
except ImportError:
    # Python <=3.7 compatibility
    from typing_extensions import Protocol


A = TypeVar("A")


class Response(Protocol):
    def json(self, **kwargs: Any) -> Any:
        ...

    def raise_for_status(self) -> None:
        ...


class AClosableHTTPClient(Protocol):
    async def __aenter__(self: A) -> A:
        ...

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        ...

    async def post(self, *args: Any, **kwargs: Any) -> Response:
        ...

    async def aclose(self) -> None:
        ...

    async def close(self) -> None:
        ...
