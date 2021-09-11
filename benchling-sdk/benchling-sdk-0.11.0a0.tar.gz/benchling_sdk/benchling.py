import re
from typing import Optional
import urllib.parse

from typing_extensions import Protocol

from benchling_api_client.benchling_client import BenchlingApiClient
from benchling_api_client.client import Client
from benchling_sdk.helpers.retry_helpers import RetryStrategy
from benchling_sdk.services.aa_sequence_service import AaSequenceService
from benchling_sdk.services.api_service import ApiService
from benchling_sdk.services.assay_result_service import AssayResultService
from benchling_sdk.services.assay_run_service import AssayRunService
from benchling_sdk.services.blob_service import BlobService
from benchling_sdk.services.box_service import BoxService
from benchling_sdk.services.container_service import ContainerService
from benchling_sdk.services.custom_entity_service import CustomEntityService
from benchling_sdk.services.dna_alignments_service import DnaAlignmentsService
from benchling_sdk.services.dna_sequence_service import DnaSequenceService
from benchling_sdk.services.dropdown_service import DropdownService
from benchling_sdk.services.entries_service import EntriesService
from benchling_sdk.services.event_service import EventService
from benchling_sdk.services.export_service import ExportService
from benchling_sdk.services.folder_service import FolderService
from benchling_sdk.services.inventory_service import InventoryService
from benchling_sdk.services.lab_automation_service import LabAutomationService
from benchling_sdk.services.label_template_service import LabelTemplateService
from benchling_sdk.services.location_service import LocationService
from benchling_sdk.services.oligo_service import OligoService
from benchling_sdk.services.plate_service import PlateService
from benchling_sdk.services.printer_service import PrinterService
from benchling_sdk.services.project_service import ProjectService
from benchling_sdk.services.registry_service import RegistryService
from benchling_sdk.services.request_service import RequestService
from benchling_sdk.services.schema_service import SchemaService
from benchling_sdk.services.task_service import TaskService
from benchling_sdk.services.warehouse_service import WarehouseService


class BenchlingApiClientDecorator(Protocol):
    def __call__(self, client: BenchlingApiClient) -> BenchlingApiClient:
        ...


class Benchling(object):

    _client: Client
    _aa_sequence_service: AaSequenceService
    _api_service: ApiService
    _assay_result_service: AssayResultService
    _assay_run_service: AssayRunService
    _blob_service: BlobService
    _box_service: BoxService
    _container_service: ContainerService
    _custom_entity_service: CustomEntityService
    _dropdown_service: DropdownService
    _dna_alignments_service: DnaAlignmentsService
    _dna_sequence_service: DnaSequenceService
    _entries_service: EntriesService
    _event_service: EventService
    _export_service: ExportService
    _folder_service: FolderService
    _inventory_service: InventoryService
    _lab_automation_service: LabAutomationService
    _label_templates_service: LabelTemplateService
    _location_service: LocationService
    _oligo_service: OligoService
    _plate_service: PlateService
    _printer_service: PrinterService
    _project_service: ProjectService
    _registry_service: RegistryService
    _request_service: RequestService
    _schema_service: SchemaService
    _task_service: TaskService
    _warehouse_service: WarehouseService

    def __init__(
        self,
        url: str,
        api_key: str,
        base_path: Optional[str] = "/api/v2",
        retry_strategy: Optional[RetryStrategy] = RetryStrategy(),
        client_decorator: Optional[BenchlingApiClientDecorator] = None,
    ):
        """
        :param url: A server URL (host and optional port) including scheme such as https://benchling.com
        :param api_key: A valid Benchling API token for authentication and authorization
        :param base_path: If provided, will append to the host. Otherwise, assumes the V2 API. This is
                          a workaround until the generated client supports the servers block. See BNCH-15422
        :param retry_strategy: An optional retry strategy for retrying HTTP calls on failure. Setting to None
                               will disable retries
        :param client_decorator: An optional function that accepts a BenchlingApiClient configured with
                                 default settings and mutates its state as desired
        """
        full_url = self._format_url(url, base_path)
        client = BenchlingApiClient(base_url=full_url, token=api_key, timeout=10)
        if client_decorator:
            client = client_decorator(client)
        self._client = client
        if retry_strategy is None:
            retry_strategy = RetryStrategy.no_retries()
        self._aa_sequence_service = AaSequenceService(client, retry_strategy=retry_strategy)
        self._api_service = ApiService(client, retry_strategy=retry_strategy)
        self._assay_result_service = AssayResultService(client, retry_strategy=retry_strategy)
        self._assay_run_service = AssayRunService(client, retry_strategy=retry_strategy)
        self._blob_service = BlobService(client, retry_strategy=retry_strategy)
        self._box_service = BoxService(client, retry_strategy=retry_strategy)
        self._container_service = ContainerService(client, retry_strategy=retry_strategy)
        self._custom_entity_service = CustomEntityService(client, retry_strategy=retry_strategy)
        self._dna_alignments_service = DnaAlignmentsService(client, retry_strategy=retry_strategy)
        self._dna_sequence_service = DnaSequenceService(client, retry_strategy=retry_strategy)
        self._dropdown_service = DropdownService(client, retry_strategy=retry_strategy)
        self._entries_service = EntriesService(client, retry_strategy=retry_strategy)
        self._event_service = EventService(client, retry_strategy=retry_strategy)
        self._export_service = ExportService(client, retry_strategy=retry_strategy)
        self._folder_service = FolderService(client, retry_strategy=retry_strategy)
        self._inventory_service = InventoryService(client, retry_strategy=retry_strategy)
        self._lab_automation_service = LabAutomationService(client, retry_strategy=retry_strategy)
        self._label_templates_service = LabelTemplateService(client, retry_strategy=retry_strategy)
        self._location_service = LocationService(client, retry_strategy=retry_strategy)
        self._oligo_service = OligoService(client, retry_strategy=retry_strategy)
        self._plate_service = PlateService(client, retry_strategy=retry_strategy)
        self._printer_service = PrinterService(client, retry_strategy=retry_strategy)
        self._project_service = ProjectService(client, retry_strategy=retry_strategy)
        self._registry_service = RegistryService(client, retry_strategy=retry_strategy)
        self._request_service = RequestService(client, retry_strategy=retry_strategy)
        self._schema_service = SchemaService(client, retry_strategy=retry_strategy)
        self._task_service = TaskService(client, retry_strategy=retry_strategy)
        self._warehouse_service = WarehouseService(client, retry_strategy=retry_strategy)

    @property
    def client(self) -> Client:
        return self._client

    @property
    def aa_sequences(self) -> AaSequenceService:
        return self._aa_sequence_service

    @property
    def api(self) -> ApiService:
        return self._api_service

    @property
    def assay_results(self) -> AssayResultService:
        return self._assay_result_service

    @property
    def assay_runs(self) -> AssayRunService:
        return self._assay_run_service

    @property
    def blobs(self) -> BlobService:
        return self._blob_service

    @property
    def boxes(self) -> BoxService:
        return self._box_service

    @property
    def containers(self) -> ContainerService:
        return self._container_service

    @property
    def custom_entities(self) -> CustomEntityService:
        return self._custom_entity_service

    @property
    def dna_alignments(self) -> DnaAlignmentsService:
        return self._dna_alignments_service

    @property
    def dna_sequences(self) -> DnaSequenceService:
        return self._dna_sequence_service

    @property
    def dropdowns(self) -> DropdownService:
        return self._dropdown_service

    @property
    def entries(self) -> EntriesService:
        return self._entries_service

    @property
    def events(self) -> EventService:
        return self._event_service

    @property
    def exports(self) -> ExportService:
        return self._export_service

    @property
    def folders(self) -> FolderService:
        return self._folder_service

    @property
    def inventory(self) -> InventoryService:
        return self._inventory_service

    @property
    def lab_automation(self) -> LabAutomationService:
        return self._lab_automation_service

    @property
    def label_templates(self) -> LabelTemplateService:
        return self._label_templates_service

    @property
    def locations(self) -> LocationService:
        return self._location_service

    @property
    def oligos(self) -> OligoService:
        return self._oligo_service

    @property
    def plates(self) -> PlateService:
        return self._plate_service

    @property
    def printers(self) -> PrinterService:
        return self._printer_service

    @property
    def projects(self) -> ProjectService:
        return self._project_service

    @property
    def registry(self) -> RegistryService:
        return self._registry_service

    @property
    def requests(self) -> RequestService:
        return self._request_service

    @property
    def schemas(self) -> SchemaService:
        return self._schema_service

    @property
    def tasks(self) -> TaskService:
        return self._task_service

    @property
    def warehouse(self) -> WarehouseService:
        return self._warehouse_service

    @staticmethod
    def _format_url(url: str, base_path: Optional[str]) -> str:
        if base_path:
            joined_url = urllib.parse.urljoin(url, base_path)
            # Strip any trailing slashes, the API client will lead with them
            joined_url = re.sub(r"/+$", "", joined_url)
            return joined_url
        return url
