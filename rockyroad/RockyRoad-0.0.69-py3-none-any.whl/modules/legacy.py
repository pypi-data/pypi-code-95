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


class Alerts(object):
    """Inteface to alerts resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url

    def requests(self):
        return self.__Requests(self)

    def reports(self):
        return self.__Reports(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Requests(Consumer):
        """Inteface to alert requests resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("alerts/requests")
        def list(self, creator_email: Query = None):
            """This call will return detailed alert request information for the creator's email specified or all alert requests if no email is specified."""

        @returns.json
        @json
        @post("alerts/requests")
        def insert(self, new_alert_request: Body):
            """This call will create an alert request with the specified parameters."""

        @returns.json
        @delete("alerts/requests")
        def delete(self, brand: Query(type=str), alert_request_id: Query(type=int)):
            """This call will delete the alert request for the specified brand and alert request id."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Reports(Consumer):
        """Inteface to alert reports resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("alerts/reports")
        def list(self, creator_email: Query = None):
            """This call will return detailed alert report information for the creator's email specified or all alert reports if no email is specified."""


@headers({"Ocp-Apim-Subscription-Key": key})
class Machines(Consumer):
    """Inteface to machines resource for the RockyRoad API."""

    from .telematics import Telematics

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def utilData(self):
        return self.__UtilData(self)

    def catalog(self):
        return self.__Catalog(self)

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
    class __Catalog(Consumer):
        """Inteface to Machine Catalog resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("machines/catalog")
        def list(self, machine_catalog_uid: Query(type=str) = None):
            """This call will return detailed machine catalog information for the id specified or all machine catalog information if uid is specified."""

        @returns.json
        @json
        @post("machines/catalog")
        def insert(self, new_machine_catalog: Body):
            """This call will create a Machine Catalog entry with the specified parameters."""

        @returns.json
        @delete("machines/catalog")
        def delete(self, machine_catalog_uid: Query(type=str)):
            """This call will delete the Machine Catalog entry for the specified Machine Catalog uid."""

        @returns.json
        @json
        @patch("machines/catalog")
        def update(self, machine_catalog: Body):
            """This call will update the Machine Catalog with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __UtilData(Consumer):
        """Inteface to machine utildata resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)
            self._base_url = Resource._base_url

        def stats(self):
            return self.__Stats(self)

        @returns.json
        @get("machines/util-data")
        def list(self, brand: Query(type=str), time_period: Query(type=str)):
            """This call will return utilization data for the time period specified in the query parameter."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        class __Stats(Consumer):
            """Inteface to utildata stats resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @get("machines/util-data/stats")
            def list(self):
                """This call will return stats for the utildatastatus table."""

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


@headers({"Ocp-Apim-Subscription-Key": key})
class Parts(Consumer):
    """Inteface to Parts resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def kits(self):
        return self.__Kits(self)

    @returns.json
    @get("parts")
    def list(
        self,
        uid: Query(type=int) = None,
        partNumber: Query(type=str) = None,
        partName: Query(type=str) = None,
        isKit: Query(type=bool) = None,
        isKitPart: Query(type=bool) = None,
    ):
        """This call will return detailed part information for the part(s) specified or all parts if nothing is specified."""

    @returns.json
    @json
    @post("parts")
    def insert(self, part: Body):
        """This call will create a part with the specified parameters."""

    @returns.json
    @delete("parts")
    def delete(self, uid: Query(type=str)):
        """This call will delete the part for the specified uid."""

    @returns.json
    @json
    @patch("parts")
    def update(self, part: Body):
        """This call will update the part with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Kits(Consumer):
        """Inteface to Kits resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("parts/kits")
        def list(
            self,
            uid: Query(type=str) = None,
            kitPartNumber: Query(type=str) = None,
            partNumber: Query(type=str) = None,
        ):
            """This call will return detailed kit line item information for the specified uid, kitPartNumber, or partNumber."""

        @returns.json
        @delete("parts/kits")
        def delete(self, uid: Query(type=str)):
            """This call will delete the kit line item for the specified uid."""

        @returns.json
        @json
        @post("parts/kits")
        def insert(self, kit: Body):
            """This call will create a kit line item with the specified parameters."""

        @returns.json
        @json
        @patch("parts/kits")
        def update(self, kit: Body):
            """This call will update the kit line item with the specified parameters."""


@headers({"Ocp-Apim-Subscription-Key": key})
class Services(Consumer):
    """Inteface to Services resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def maintenanceIntervals(self):
        return self.__Maintenance_Intervals(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Maintenance_Intervals(Consumer):
        """Inteface to Maintenance Intervals resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("services/maintenance-intervals")
        def list(
            self,
            uid: Query(type=str) = None,
            hours: Query(type=int) = None,
            brand: Query(type=str) = None,
            model: Query(type=str) = None,
        ):
            """This call will return detailed information for all maintenance intervals or for those for the specified uid, hours, or brand and model."""

        @returns.json
        @delete("services/maintenance-intervals")
        def delete(self, uid: Query(type=str)):
            """This call will delete the maintenance interval for the specified uid."""

        @returns.json
        @json
        @post("services/maintenance-intervals")
        def insert(self, maintenanceInterval: Body):
            """This call will create a maintenance interval with the specified parameters."""

        @returns.json
        @json
        @patch("services/maintenance-intervals")
        def update(self, maintenanceInterval: Body):
            """This call will update the maintenance interval with the specified parameters."""


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