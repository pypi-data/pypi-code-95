from wire_web.utils import RadixTree
import typing


class BaseRouter:
    """
    Here is the routing magic.
    """
    __slots__ = ["routes"]

    def __init__(self) -> None:
        self.routes = RadixTree()

    def add_route(self, path: str, handler, method: str) -> bool:
        self.routes.insert(path, handler, method)
        return True


class Router(BaseRouter):
    def __init__(self, strict: bool = True):
        self.strict_mode: bool = strict
        super().__init__()

    async def get_handler(self, path: str, method: str) -> typing.Tuple[
        typing.Union[typing.Callable, typing.Awaitable], typing.Optional[dict]]:
        pathFound, handler, params = self.routes.get(path, method.lower())
        return handler, params
