from typing import Iterable, List

from benchling_api_client.api.registry import (
    bulk_get_registered_entities,
    list_registries,
    register_entities,
    unregister_entities,
)
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.models import (
    AsyncTaskLink,
    CustomEntity,
    NamingStrategy,
    RegisterEntities,
    Registry,
    UnregisterEntities,
)
from benchling_sdk.services.base_service import BaseService


class RegistryService(BaseService):
    @api_method
    def register(
        self,
        registry_id: str,
        entity_ids: Iterable[str],
        naming_strategy: NamingStrategy = NamingStrategy.NEW_IDS,
    ) -> AsyncTaskLink:
        registration_body = RegisterEntities(entity_ids=list(entity_ids), naming_strategy=naming_strategy)
        response = register_entities.sync_detailed(
            client=self.client, registry_id=registry_id, json_body=registration_body
        )
        return model_from_detailed(response)

    @api_method
    def unregister(
        self,
        registry_id: str,
        entity_ids: Iterable[str],
        folder_id: str,
    ) -> None:
        registration_body = UnregisterEntities(entity_ids=list(entity_ids), folder_id=folder_id)
        response = unregister_entities.sync_detailed(
            client=self.client, registry_id=registry_id, json_body=registration_body
        )
        # Raise for error but return nothing
        model_from_detailed(response)

    @api_method
    def registries(self) -> List[Registry]:
        response = list_registries.sync_detailed(client=self.client)
        registry_list = model_from_detailed(response)
        if not registry_list.registries:
            return []
        return registry_list.registries

    # TODO Currently this payload does not deserialize properly until
    # https://github.com/triaxtec/openapi-python-client/issues/219

    @api_method
    def entities(self, registry_id: str, entity_registry_ids: Iterable[str]) -> List[CustomEntity]:
        response = bulk_get_registered_entities.sync_detailed(
            client=self.client, registry_id=registry_id, entity_registry_ids=list(entity_registry_ids)
        )
        entity_list = model_from_detailed(response)
        if not entity_list.entities:
            return []
        return entity_list.entities
