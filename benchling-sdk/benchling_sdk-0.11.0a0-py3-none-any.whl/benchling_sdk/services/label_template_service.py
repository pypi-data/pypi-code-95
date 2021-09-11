from typing import List

from benchling_api_client.api.label_templates import list_label_templates
from benchling_api_client.models.label_template import LabelTemplate
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.services.base_service import BaseService


class LabelTemplateService(BaseService):
    @api_method
    def get_list(self, registry_id: str) -> List[LabelTemplate]:
        response = list_label_templates.sync_detailed(client=self.client, registry_id=registry_id)
        results = model_from_detailed(response)
        return results.label_templates
