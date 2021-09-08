from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Machines(Consumer):
    """Inteface to machines resource for the RockyRoad API."""

    from .machine_catalog import Catalog
    from .util_data import UtilData
    from .telematics import Telematics

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def utilData(self):
        return self.UtilData(self)

    def catalog(self):
        return self.Catalog(self)

    def models(self):
        return self.__Models(self)

    def product_types(self):
        return self.__Products(self)

    def serials(self):
        return self.__Serials(self)

    def telematics(self):
        return self.Telematics(self)

    @returns.json
    @get("machines")
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
        include_util_data: Query(type=str) = None,
    ):
        """This call will return machine information for the machine or account specified or all machines if nothing is specified."""

    @returns.json
    @json
    @post("machines")
    def insert(self, new_machine: Body):
        """This call will create a machine with the specified parameters."""

    @returns.json
    @delete("machines")
    def delete(self, machine_uid: Query(type=str)):
        """This call will delete the machine for the specified id."""

    @returns.json
    @json
    @patch("machines")
    def update(self, machine: Body):
        """This call will update the machine with the specified parameters."""

    @returns.json
    @json
    @post("machines/assign-to-default-dealer")
    def assign_machines_to_default_dealer(
        self,
        customer_account: Query(type=str),
        ignore_machines_with_dealer: Query(type=bool) = None,
    ):
        """This call will set the supporting dealer for machines owned by the customer to the default dealer for the customer."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Models(Consumer):
        """Inteface to machine model resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("machines/models")
        def list(
            self,
            baseOnly: Query(type=bool) = None,
            brand: Query(type=str) = None,
            productType: Query(type=str) = None,
        ):
            """This call will return machine models for the specified criteria."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Products(Consumer):
        """Inteface to machine product-type resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("machines/product-types")
        def list(self, brand: Query(type=str) = None):
            """This call will return machine product types for the specified criteria."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Serials(Consumer):
        """Inteface to machine serial resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("machines/models/serials")
        def list(
            self,
            model: Query(type=str) = None,
        ):
            """This call will return machine serials for the specified criteria."""
