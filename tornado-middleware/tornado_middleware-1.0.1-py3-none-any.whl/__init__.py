from typing import Awaitable, Callable, Iterator, List, Literal, Union
from tornado.web import RequestHandler, OutputTransform


class MiddlewareHandler(RequestHandler):
    """
        Middleware support RequestHandler
        to create a middleware you must declare an async function where receive a next function and must start
        with 'middleware' or '_middleware' to be user
    """

    def _get_middlewares(
        self,
    ) -> Iterator[Callable[[Callable], Union[None, Awaitable[None]]]]:
        """
            Get all middlewares declared in the class
        """
        middlewares_name = filter(
            lambda x: x.startswith(("_middleware", "middleware")), dir(self)
        )
        return iter(map(lambda x: getattr(self, x), middlewares_name))

    def __make_next(
        self,
        callback: Callable[[Callable], Union[None, Awaitable[None]]],
        next: Callable[[], Awaitable[bool]],
    ) -> Callable[[], Awaitable[bool]]:
        """
            Wraps a middleware in a next middleware function
        """
        async def next_wrapper() -> Awaitable[bool]:
            res = callback(next)
            if res is not None:
                await res

            return self._finished

        return next_wrapper

    async def __next_execute(self) -> Awaitable[Literal[True]]:
        """
            Wraps execute function into a next middleware function
        """
        res = super(MiddlewareHandler, self)._execute(
            self._transforms,
            *self._execute_args,
            **self._execute_kwargs,
        )

        if res is not None:
            await res

        return True

    async def _execute(
        self, transforms: List["OutputTransform"], *args: bytes, **kwargs: bytes
    ) -> Union[None]:
        self._transforms = transforms
        self._execute_args = args
        self._execute_kwargs = kwargs

        next_middleware = self.__next_execute
        for middleware in self._get_middlewares():
            next_middleware = self.__make_next(middleware, next_middleware)

        await next_middleware()
