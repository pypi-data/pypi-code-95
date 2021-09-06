from wire_web.enums import HttpStatusCode
import typing
import json
from tex_engine import Template

class Response:
    """
    This is the base answer class. All other answer classes are based on it.
    """
    media_type = None
    charset = "utf-8"

    def __init__(self, content: typing.Any, status: typing.Union[int, HttpStatusCode] = 200, headers: dict = None,
                 media_type: str = None) -> None:
        self.status = status if isinstance(status, int) else status.value
        self.content: typing.Any = content
        if media_type:
            self.media_type = media_type
        self.body = self.render(content)
        self.set_headers(headers)

    def render(self, content: typing.Any):
        if content is None:
            return b""
        if isinstance(content, bytes):
            return content
        return content.encode(self.charset)

    def set_headers(self, headers: typing.Mapping[str, str] = None) -> None:
        if headers is None:
            raw_headers: typing.List[typing.Tuple[bytes, bytes]] = []
        else:
            raw_headers = [(k.lower().encode(self.charset), v.encode(
                self.charset)) for k, v in headers.items()]
        body: bytes = getattr(self, "body", b"")
        if body:
            raw_headers.append(
                (b"content-length", str(len(body)).encode(self.charset)))
        ctype: str = self.media_type
        if ctype is not None:
            if ctype.startswith("text/"):
                ctype += ";" + "charset=" + self.charset + ";"
            raw_headers.append((b"content-type", ctype.encode(self.charset)))
        self.raw_headers = raw_headers

    async def __call__(self, scope, receive, send) -> None:
        await send({"type": "http.response.start", "status": self.status, "headers": self.raw_headers})
        await send({"type": "http.response.body", "body": self.body})


class HTMLResponse(Response):
    media_type = "text/html"


class JsonResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any):
        return json.dumps(content, indent=None).encode(self.charset)


class PlainTextResponse(Response):
    media_type = "text/plain"


class TemplateResponse(HTMLResponse):
    def __init__(self, filename: str, **kwargs):
        content = filename
        self.args = kwargs
        super().__init__(filename)

    def render(self, filename: str):
        with open(filename, "r") as f:
            data = f.read()
        html = Template(data).render(**self.args)
        return html 



