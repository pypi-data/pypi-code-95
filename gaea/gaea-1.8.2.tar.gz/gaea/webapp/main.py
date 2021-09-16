import fastapi
from fastapi.middleware.cors import CORSMiddleware

from .monitoring import router as monitoring_router


class AppClient:
    def __init__(self, routers, middleware=None):
        self.app = fastapi.FastAPI()

        if not isinstance(routers, (list, tuple)):
            routers = [routers]

        self.app.include_router(monitoring_router)
        for router in routers:
            self.app.include_router(router)

        self.middleware = middleware

    def _add_middleware(self):
        if self.middleware:
            self.app.middleware("http")(self.middleware)

    def add_cors_middleware(
        self,
        allow_origins=None,
        allow_origin_regex=None,
        allow_methods=None,
        allow_headers=None,
        allow_credentials=False,
    ):
        params = dict(
            allow_methods=allow_methods or ["*"],
            allow_headers=allow_headers or ["*"],
            allow_credentials=allow_credentials,
        )

        if allow_origin_regex:
            params["allow_origin_regex"] = allow_origin_regex
        else:
            params["allow_origins"] = allow_origins or ["*"]

        self.app.add_middleware(CORSMiddleware, **params)

    def get_app(self):
        self._add_middleware()
        return self.app
