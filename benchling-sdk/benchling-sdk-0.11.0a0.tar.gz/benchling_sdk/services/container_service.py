from typing import Any, Dict, Iterable, List, Optional

from benchling_api_client.api.containers import (
    archive_containers,
    bulk_create_containers,
    bulk_get_containers,
    bulk_update_containers,
    checkin_containers,
    checkout_containers,
    create_container,
    delete_container_content,
    get_container,
    get_container_content,
    list_container_contents,
    list_containers,
    print_labels,
    reserve_containers,
    transfer_into_container,
    transfer_into_containers,
    unarchive_containers,
    update_container,
    update_container_content,
)
from benchling_api_client.types import Response
from benchling_sdk.errors import raise_for_status
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import (
    none_as_unset,
    optional_array_query_param,
    schema_fields_query_param,
)
from benchling_sdk.models import (
    AsyncTaskLink,
    Container,
    ContainerBulkUpdateItem,
    ContainerContent,
    ContainerContentUpdate,
    ContainerCreate,
    ContainersArchivalChange,
    ContainersArchive,
    ContainersArchiveReason,
    ContainersBulkCreateRequest,
    ContainersBulkUpdateRequest,
    ContainersCheckin,
    ContainersCheckout,
    ContainersPaginatedList,
    ContainersUnarchive,
    ContainerTransfer,
    ContainerUpdate,
    ListContainersCheckoutStatus,
    ListContainersSort,
    Measurement,
    MultipleContainersTransfer,
    MultipleContainersTransfersList,
    PrintLabels,
)
from benchling_sdk.services.base_service import BaseService


class ContainerService(BaseService):
    @api_method
    def get_by_id(self, container_id: str) -> Container:
        response = get_container.sync_detailed(client=self.client, container_id=container_id)
        return model_from_detailed(response)

    @api_method
    def containers_page(
        self,
        *,
        page_size: Optional[int] = 50,
        next_token: Optional[str] = None,
        sort: Optional[ListContainersSort] = None,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ancestor_storage_id: Optional[str] = None,
        storage_contents_id: Optional[str] = None,
        storage_contents_ids: Optional[List[str]] = None,
        checkout_status: Optional[ListContainersCheckoutStatus] = None,
        ids: Optional[Iterable[str]] = None,
        barcodes: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
    ) -> Response[ContainersPaginatedList]:
        return list_containers.sync_detailed(  # type: ignore
            client=self.client,
            sort=none_as_unset(sort),
            schema_id=none_as_unset(schema_id),
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            ancestor_storage_id=none_as_unset(ancestor_storage_id),
            storage_contents_id=none_as_unset(storage_contents_id),
            storage_contents_ids=none_as_unset(storage_contents_ids),
            checkout_status=none_as_unset(checkout_status),
            ids=none_as_unset(optional_array_query_param(ids)),
            barcodes=none_as_unset(optional_array_query_param(barcodes)),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            archive_reason=none_as_unset(archive_reason),
            schema_fields=none_as_unset(schema_fields_query_param(schema_fields)),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        sort: Optional[ListContainersSort] = None,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ancestor_storage_id: Optional[str] = None,
        storage_contents_id: Optional[str] = None,
        storage_contents_ids: Optional[List[str]] = None,
        checkout_status: Optional[ListContainersCheckoutStatus] = None,
        ids: Optional[Iterable[str]] = None,
        barcodes: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[Container]:
        def api_call(next_token: NextToken) -> Response[ContainersPaginatedList]:
            return self.containers_page(
                sort=sort,
                schema_id=schema_id,
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                ancestor_storage_id=ancestor_storage_id,
                storage_contents_id=storage_contents_id,
                storage_contents_ids=storage_contents_ids,
                checkout_status=checkout_status,
                ids=ids,
                barcodes=barcodes,
                names_any_of=names_any_of,
                archive_reason=archive_reason,
                next_token=next_token,
                schema_fields=schema_fields,
                page_size=page_size,
            )

        def results_extractor(body: ContainersPaginatedList) -> Optional[List[Container]]:
            return body.containers

        return PageIterator(api_call, results_extractor)

    @api_method
    def bulk_get(
        self, *, container_ids: Optional[Iterable[str]] = None, barcodes: Optional[Iterable[str]] = None
    ) -> Optional[List[Container]]:
        container_id_string = optional_array_query_param(container_ids)
        barcode_string = optional_array_query_param(barcodes)
        response = bulk_get_containers.sync_detailed(
            client=self.client,
            container_ids=none_as_unset(container_id_string),
            barcodes=none_as_unset(barcode_string),
        )
        containers_list = model_from_detailed(response)
        return containers_list.containers

    @api_method
    def bulk_create(self, containers: Iterable[ContainerCreate]) -> AsyncTaskLink:
        body = ContainersBulkCreateRequest(list(containers))
        response = bulk_create_containers.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)

    @api_method
    def bulk_update(self, containers: Iterable[ContainerBulkUpdateItem]) -> AsyncTaskLink:
        body = ContainersBulkUpdateRequest(list(containers))
        response = bulk_update_containers.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)

    @api_method
    def create(self, container: ContainerCreate) -> Container:
        response = create_container.sync_detailed(client=self.client, json_body=container)
        return model_from_detailed(response)

    @api_method
    def update(self, container_id: str, container: ContainerUpdate) -> Container:
        response = update_container.sync_detailed(
            client=self.client, container_id=container_id, json_body=container
        )
        return model_from_detailed(response)

    @api_method
    def archive(
        self, container_ids: Iterable[str], reason: ContainersArchiveReason, should_remove_barcodes: bool
    ) -> ContainersArchivalChange:
        archive_request = ContainersArchive(
            container_ids=list(container_ids), reason=reason, should_remove_barcodes=should_remove_barcodes
        )
        response = archive_containers.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, container_ids: Iterable[str]) -> ContainersArchivalChange:
        unarchive_request = ContainersUnarchive(container_ids=list(container_ids))
        response = unarchive_containers.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def print_labels(self, print_request: PrintLabels) -> None:
        response = print_labels.sync_detailed(client=self.client, json_body=print_request)
        raise_for_status(response)

    @api_method
    def contents_by_id(self, container_id: str, containable_id: str) -> ContainerContent:
        response = get_container_content.sync_detailed(
            client=self.client, container_id=container_id, containable_id=containable_id
        )
        return model_from_detailed(response)

    @api_method
    def list_contents(self, container_id: str) -> List[ContainerContent]:
        response = list_container_contents.sync_detailed(client=self.client, container_id=container_id)
        contents_list = model_from_detailed(response)
        return contents_list.contents

    @api_method
    def update_contents(
        self, container_id: str, containable_id: str, concentration: Measurement
    ) -> ContainerContent:
        update = ContainerContentUpdate(concentration=concentration)
        response = update_container_content.sync_detailed(
            client=self.client, container_id=container_id, containable_id=containable_id, json_body=update
        )
        return model_from_detailed(response)

    @api_method
    def delete_contents(self, container_id: str, containable_id: str) -> None:
        response = delete_container_content.sync_detailed(
            client=self.client, container_id=container_id, containable_id=containable_id
        )
        raise_for_status(response)

    @api_method
    def reserve(self, reservation: ContainersCheckout) -> None:
        response = reserve_containers.sync_detailed(client=self.client, json_body=reservation)
        raise_for_status(response)

    @api_method
    def checkout(self, checkout: ContainersCheckout) -> None:
        response = checkout_containers.sync_detailed(client=self.client, json_body=checkout)
        raise_for_status(response)

    @api_method
    def checkin(self, checkin: ContainersCheckin) -> None:
        response = checkin_containers.sync_detailed(client=self.client, json_body=checkin)
        raise_for_status(response)

    @api_method
    def transfer_into_container(
        self, destination_container_id: str, transfer_request: ContainerTransfer
    ) -> None:
        response = transfer_into_container.sync_detailed(
            client=self.client, destination_container_id=destination_container_id, json_body=transfer_request
        )
        raise_for_status(response)

    @api_method
    def transfer_into_containers(
        self, transfer_requests: Iterable[MultipleContainersTransfer]
    ) -> AsyncTaskLink:
        multiple_requests = MultipleContainersTransfersList(transfers=list(transfer_requests))
        response = transfer_into_containers.sync_detailed(client=self.client, json_body=multiple_requests)
        return model_from_detailed(response)
