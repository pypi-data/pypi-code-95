from .module_imports import *


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