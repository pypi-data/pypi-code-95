from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Summaries(Consumer):
    """Inteface to Summaries resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def machineParts(self):
        return self.__Machine_Parts(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Machine_Parts(Consumer):
        """Inteface to Machine Parts resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("summaries/machine-parts")
        def list(
            self,
            machine_uid: Query(type=str) = None,
            brand: Query(type=str) = None,
            model: Query(type=str) = None,
            serial: Query(type=str) = None,
            account: Query(type=str) = None,
            account_uid: Query(type=str) = None,
            dealer_account: Query(type=str) = None,
            dealer_account_uid: Query(type=str) = None,
            account_association_uid: Query(type=str) = None,
        ):
            """This call will return detailed summary information of machine parts for the specified search criteria."""