from benchling_api_client.client import Client
from benchling_sdk.helpers.retry_helpers import RetryStrategy
from benchling_sdk.services.assay_result_schema_service import AssayResultSchemaService
from benchling_sdk.services.assay_run_schema_service import AssayRunSchemaService
from benchling_sdk.services.base_service import BaseService
from benchling_sdk.services.batch_schema_service import BatchSchemaService
from benchling_sdk.services.box_schema_service import BoxSchemaService
from benchling_sdk.services.container_schema_service import ContainerSchemaService
from benchling_sdk.services.dropdown_service import DropdownService
from benchling_sdk.services.entity_schema_service import EntitySchemaService
from benchling_sdk.services.entry_schema_service import EntrySchemaService
from benchling_sdk.services.location_schema_service import LocationSchemaService
from benchling_sdk.services.plate_schema_service import PlateSchemaService
from benchling_sdk.services.request_schema_service import RequestSchemaService
from benchling_sdk.services.request_task_schema_service import RequestTaskSchemaService


class SchemaService(BaseService):
    _assay_result_schema_service: AssayResultSchemaService
    _assay_run_schema_service: AssayRunSchemaService
    _batch_schema_service: BatchSchemaService
    _box_schema_service: BoxSchemaService
    _container_schema_service: ContainerSchemaService
    _entity_schema_service: EntitySchemaService
    _entry_schema_service: EntrySchemaService
    _location_schema_service: LocationSchemaService
    _plate_schema_service: PlateSchemaService
    _request_schema_service: RequestSchemaService
    _request_task_schema_service: RequestTaskSchemaService

    def __init__(
        self,
        client: Client,
        retry_strategy: RetryStrategy,
    ):
        super().__init__(client, retry_strategy)
        self._assay_result_schema_service = AssayResultSchemaService(client, retry_strategy)
        self._assay_run_schema_service = AssayRunSchemaService(client, retry_strategy)
        self._batch_schema_service = BatchSchemaService(client, retry_strategy)
        self._box_schema_service = BoxSchemaService(client, retry_strategy)
        self._container_schema_service = ContainerSchemaService(client, retry_strategy)
        self._dropdown_service = DropdownService(client, retry_strategy)
        self._entity_schema_service = EntitySchemaService(client, retry_strategy)
        self._entry_schema_service = EntrySchemaService(client, retry_strategy)
        self._location_schema_service = LocationSchemaService(client, retry_strategy)
        self._plate_schema_service = PlateSchemaService(client, retry_strategy)
        self._request_schema_service = RequestSchemaService(client, retry_strategy)
        self._request_task_schema_service = RequestTaskSchemaService(client, retry_strategy)

    @property
    def assay_results(self) -> AssayResultSchemaService:
        return self._assay_result_schema_service

    @property
    def assay_runs(self) -> AssayRunSchemaService:
        return self._assay_run_schema_service

    @property
    def batches(self) -> BatchSchemaService:
        return self._batch_schema_service

    @property
    def boxes(self) -> BoxSchemaService:
        return self._box_schema_service

    @property
    def containers(self) -> ContainerSchemaService:
        return self._container_schema_service

    @property
    def dropdowns(self) -> DropdownService:
        return self._dropdown_service

    @property
    def entities(self) -> EntitySchemaService:
        return self._entity_schema_service

    @property
    def entries(self) -> EntrySchemaService:
        return self._entry_schema_service

    @property
    def locations(self) -> LocationSchemaService:
        return self._location_schema_service

    @property
    def plates(self) -> PlateSchemaService:
        return self._plate_schema_service

    @property
    def requests(self) -> RequestSchemaService:
        return self._request_schema_service

    @property
    def request_tasks(self) -> RequestTaskSchemaService:
        return self._request_task_schema_service
