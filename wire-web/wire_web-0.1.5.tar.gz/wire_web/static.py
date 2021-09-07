from wire_web.response import PlainTextResponse
from mimetypes import MimeTypes

import os


class StaticFiles:
    def __init__(self, path: str, route_prefix: str = "/static") -> None:
        self.path = path
        self.route = route_prefix
        if not self.route.startswith("/"):
            raise Exception("No proper route name")

    def provide(self, filepath: str):
        mime = MimeTypes()
        typ = mime.guess_type("." + filepath)
        with open("." + filepath, "rb") as f:
            content = f.read()
        return content, typ[0]
