# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List

from azureml.core import Experiment, Run, Workspace
from azureml._common._error_definition import AzureMLError
from azureml._restclient.models import Asset
from azureml.exceptions import AzureMLException, UserErrorException

from azureml.responsibleai.common._constants import AssetProperties
from azureml.responsibleai.common._errors.error_definitions import DuplicateItemFoundError, \
    AssetNotFoundError
from azureml.responsibleai.tools.counterfactual.counterfactual_examples_client import download_counterfactual_examples
from azureml.responsibleai.tools.model_analysis._constants import (
    AnalysisTypes, AzureMLTypes, PropertyKeys, CounterfactualVersion
)

from .base_manager import BaseManager


class CounterfactualManager(BaseManager):
    ID = 'id'
    COMMENT = 'comment'

    def __init__(self,
                 service_context,
                 experiment_name: str,
                 analysis_id: str):
        super().__init__(service_context, experiment_name, analysis_id)
        self._assets: List[Asset] = [Asset('some string')]
        del self._assets[0]

    def list(self) -> List[Dict[str, str]]:
        """List the counterfactual examples"""
        query_props = {
            PropertyKeys.ANALYSIS_TYPE: AnalysisTypes.COUNTERFACTUAL_TYPE,
            PropertyKeys.ANALYSIS_ID: self.analysis_id,
            PropertyKeys.VERSION: str(CounterfactualVersion.V_0)
        }
        self._assets = list(
            self._assets_client.list_assets_with_query(
                properties=query_props,
                asset_type=AzureMLTypes.MODEL_ANALYSIS
            )
        )

        summary_list = []
        for cf_asset in self._assets:
            props = cf_asset.properties
            summary_dict = {
                self.ID: props.get(AssetProperties.UPLOAD_ID, None),
                self.COMMENT: props.get(self.COMMENT, None),
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
        """Download counterfactual example by id"""
        self.list()

        # Get the one we want
        filtered = [
            x
            if x.properties.get(AssetProperties.UPLOAD_ID, None) == id
            else None
            for x in self._assets
        ]
        # Sanity check - the following should never trigger
        if len(filtered) > 1:
            raise AzureMLException._with_error(
                AzureMLError.create(
                    DuplicateItemFoundError,
                    item_type=AnalysisTypes.COUNTERFACTUAL_TYPE,
                    id=id
                )
            )
        sc = self._service_context
        workspace = Workspace(sc.subscription_id, sc.resource_group_name, sc.workspace_name,
                              auth=sc.get_auth(), _disable_service_check=True)
        experiment = Experiment(workspace, self._experiment_name)
        run = Run(experiment, run_id=filtered[0].runid)
        cf_example_id = filtered[0].properties[AssetProperties.UPLOAD_ID]
        return download_counterfactual_examples(run=run,
                                                counterfactual_examples_upload_id=cf_example_id,
                                                asset_type=AzureMLTypes.MODEL_ANALYSIS)
