# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List

from azureml._common._error_definition import AzureMLError
from azureml._restclient.models import Asset
from azureml.exceptions import AzureMLException, UserErrorException

from azureml.interpret.common.constants import ExplainType, History

from azureml.responsibleai.common._errors.error_definitions import \
    DuplicateItemFoundError, AssetNotFoundError
from azureml.responsibleai.tools.model_analysis._constants import (
    AnalysisTypes, AzureMLTypes, PropertyKeys, ExplanationVersion
)
from azureml.responsibleai.tools.model_analysis._model_analysis_explanation_client import (
    ModelAnalysisExplanationClient)

from .base_manager import BaseManager


class ExplanationManager(BaseManager):
    def __init__(self,
                 service_context,
                 experiment_name: str,
                 analysis_id: str):
        super(ExplanationManager, self).__init__(service_context,
                                                 experiment_name,
                                                 analysis_id)
        # The following is to work around a difference of opinion between
        # mypy (which wants the type hint to exist) and flake8 (which
        # doesn't count a type hint as a 'use' of an import)
        self._explanation_assets: List[Asset] = [Asset('some string')]
        del self._explanation_assets[0]

    def list(self) -> List[Dict[str, str]]:
        """List the Explanation metrics which have been computed."""
        query_props = {
            PropertyKeys.ANALYSIS_TYPE: AnalysisTypes.EXPLANATION_TYPE,
            PropertyKeys.ANALYSIS_ID: self.analysis_id,
            PropertyKeys.VERSION: str(ExplanationVersion.V_0)
        }
        self._explanation_assets = list(
            self._assets_client.list_assets_with_query(
                properties=query_props,
                asset_type=AzureMLTypes.MODEL_ANALYSIS
            )
        )

        summary_list = []
        for ea in self._explanation_assets:
            props = ea.properties
            summary_dict = {
                History.ID: props.get(History.EXPLANATION_ID, None),
                History.COMMENT: props.get(History.COMMENT, None),
                ExplainType.DATA: props.get(ExplainType.DATA, None),
                ExplainType.EXPLAIN: props.get(ExplainType.EXPLAIN, None),
                ExplainType.MODEL: props.get(ExplainType.MODEL, None),
                ExplainType.IS_RAW: props.get(ExplainType.IS_RAW, None),
                ExplainType.IS_ENG: props.get(ExplainType.IS_ENG, None),
                History.UPLOAD_TIME: ea.created_time
            }
            summary_list.append(summary_dict)

        if len(summary_list) == 0:
            raise UserErrorException._with_error(
                AzureMLError.create(
                    AssetNotFoundError,
                    asset_name=AzureMLTypes.MODEL_ANALYSIS,
                    attributes=query_props,
                )
            )

        return summary_list

    def download_by_id(self, id: str):
        # Make sure our Asset list is up-to-date
        self.list()

        # Get the one we want
        filtered = [
            x
            if x.properties.get(History.EXPLANATION_ID, None) == id
            else None
            for x in self._explanation_assets
        ]
        # Sanity check - the following should never trigger
        if len(filtered) > 1:
            raise AzureMLException._with_error(
                AzureMLError.create(
                    DuplicateItemFoundError,
                    item_type=AnalysisTypes.EXPLANATION_TYPE,
                    id=id
                )
            )

        # Download it
        client = ModelAnalysisExplanationClient(service_context=self._service_context,
                                                experiment_name=self._experiment_name,
                                                run_id=filtered[0].runid,
                                                analysis_id=self.analysis_id,
                                                model_analysis=None)
        explain_id = filtered[0].properties[History.EXPLANATION_ID]
        return client.download_model_explanation(explanation_id=explain_id)
