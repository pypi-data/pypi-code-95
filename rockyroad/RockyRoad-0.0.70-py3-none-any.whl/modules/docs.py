from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Docs(Consumer):
    def __init__(self, Resource, *args, **kw):
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @get("docs/swagger")
    def swagger(self):
        """This call will return swagger ui."""

    @get("docs/redocs")
    def redocs(self):
        """This call will return redoc ui."""

    @returns.json
    @get("docs/openapi.json")
    def openapi(self):
        """This call will return OpenAPI json."""