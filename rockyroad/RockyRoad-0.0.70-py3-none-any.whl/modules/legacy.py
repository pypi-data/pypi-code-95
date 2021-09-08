from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class HelloWorld(Consumer):
    def __init__(self, Resource, *args, **kw):
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @get("")
    def list(self):
        """This call will return Hello World."""


@headers({"Ocp-Apim-Subscription-Key": key})
class Dealers(Consumer):
    def __init__(self, Resource, *args, **kw):
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @get("dealers")
    def list(self):
        """This call will return a list of dealers."""


@headers({"Ocp-Apim-Subscription-Key": key})
class Customers(Consumer):
    def __init__(self, Resource, *args, **kw):
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @get("customers")
    def list(self, dealer_name: Query(type=str)):
        """This call will return a list of customers and machines supported by the specified dealer."""
