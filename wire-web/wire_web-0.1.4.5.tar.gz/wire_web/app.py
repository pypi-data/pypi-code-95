from wire_web.router import Router
from wire_web.request import Request
from wire_web.response import HTMLResponse, Response, PlainTextResponse, JsonResponse
from wire_web.groups import Group
from wire_web.static import StaticFiles
import inspect
import typing


class Wire:
    def __init__(self, strict: bool = True) -> None:
        self.router: Router = Router(strict=strict)
        self.static: StaticFiles = None

    async def __call__(self, scope: dict, receive, send) -> None:
        req = Request(scope, receive, send)
        try:
            if self.static is not None and req.path.startswith(self.static.route):
                content, typ = self.static.provide(req.path)
                resp = Response(content, headers={"content-type": typ})
                await resp(scope, receive, send)
            func, params = await self.router.get_handler(req.path, req.method)
            if func:
                if inspect.iscoroutinefunction(func):
                    response: typing.Union[Response, typing.Any] = await func(req, **params)
                    if not isinstance(response, Response):
                        if type(response) == str:
                            response = PlainTextResponse(response, 200)
                        elif type(response) == dict:
                            response = JsonResponse(response, 200)
                    await response(scope, receive, send)
        except Exception as e:
            print(e)
            response = HTMLResponse("Error occured", 404)
            await response(scope, receive, send)

    def get(self, path: str):
        def wrapper(handler: typing.Union[typing.Callable, typing.Awaitable]) -> typing.Union[
            typing.Callable, typing.Awaitable]:
            self.router.add_route(path, handler, "get")
            return handler

        return wrapper

    def post(self, path: str):
        def wrapper(handler: typing.Union[typing.Callable, typing.Awaitable]) -> typing.Union[
            typing.Callable, typing.Awaitable]:
            self.router.add_route(path, handler, "post")
            return handler

        return wrapper

    def put(self, path: str):
        def wrapper(handler: typing.Union[typing.Callable, typing.Awaitable]) -> typing.Union[
            typing.Callable, typing.Awaitable]:
            self.router.add_route(path, handler, "put")
            return handler

        return wrapper

    def delete(self, path: str):
        def wrapper(handler: typing.Union[typing.Callable, typing.Awaitable]) -> typing.Union[
            typing.Callable, typing.Awaitable]:
            self.router.add_route(path, handler, "delete")
            return handler

        return wrapper

    def mount(self, plugin: typing.Union[Group, StaticFiles], prefix: str = None):
        if isinstance(plugin, StaticFiles):
            plugin.route = prefix
            self.static = plugin
            return True
        if not prefix.startswith("/"):
            raise Exception(f"Invalid prefix for router {plugin}")
        else:
            for route in plugin.routes:
                self.router.add_route(prefix + route[0], route[1], route[2])
            print(f"Mounted router: {plugin}")
            return True
