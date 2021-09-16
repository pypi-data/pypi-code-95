from tornado.web import HTTPError
from tornado_middleware import MiddlewareHandler
from typing import Awaitable

class LoginMiddlewareHandler(MiddlewareHandler):
	"""
		A simple login middleware handler
	"""

	async def login(self, username: str, password: str) -> Awaitable[bool]:
		raise NotImplementedError('please define login function')

	async def _middleware_login(self, next):
		if "Authorization" not in self.request.headers:
            raise HTTPError(403, '"Authorization" header was not set')

        if not auth.startswith("Basic "):
        	raise HTTPError(400, '"Authorization" header must be a Basic authentication')

        username, password = base64.b64decode(auth.split(" ")[1].encode()).decode().split(":")
        if await self.login(username, password):
        	await next()
        else:
        	raise HTTPError(401)