# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List

from azureml._common._error_definition import AzureMLError
from azureml._restclient.models import Asset
from azureml.exceptions import AzureMLException, UserErrorException
from azureml.core import Experiment, Run, Workspace

from azureml.responsibleai.common._constants import AssetProperties
from azureml.responsibleai.common._errors.error_definitions import AssetNotFoundError
from azureml.responsibleai.tools.model_analysis._constants import (
    AnalysisTypes, AzureMLTypes, PropertyKeys, CausalVersion)

from azureml.responsibleai.tools.causal.causal_client import download_causal_insights

from .base_manager import BaseManager


class CausalManager(BaseManager):
    ID = 'id'
    COMMENT = 'comment'

    def __init__(self,
                 service_context,
                 experiment_name: str,
                 analysis_id: str):
        super().__init__(service_context, experiment_name, analysis_id)
        self._assets: List[Asset] = []

    def list(self) -> List[Dict[str, str]]:
        """List the computed causal analyses."""
        query_props = {
            PropertyKeys.ANALYSIS_TYPE: AnalysisTypes.CAUSAL_TYPE,
            PropertyKeys.ANALYSIS_ID: self.analysis_id,
            PropertyKeys.VERSION: str(CausalVersion.V_0)
        }
        self._assets = list(
            self._assets_client.list_assets_with_query(
                properties=query_props,
                asset_type=AzureMLTypes.MODEL_ANALYSIS))

        summary_list = []
        for asset in self._assets:
            props = asset.properties
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

    def _get_asset(self, id: str) -> Asset:
        for asset in self._assets:
            props = asset.properties
            if props.get(AssetProperties.UPLOAD_ID, None) == id:
                return asset

        raise AzureMLException._with_error(
            AzureMLError.create(
                AssetNotFoundError,
                asset_name=AnalysisTypes.CAUSAL_TYPE,
                attributes={AssetProperties.UPLOAD_ID: id}
            )
        )

    def download_by_id(self, id: str):
        # Make sure the Asset list is up-to-date
        self.list()

        asset = self._get_asset(id)
        service_context = self._service_context
        workspace = Workspace(
            service_context.subscription_id,
            service_context.resource_group_name,
            service_context.workspace_name,
            auth=service_context.get_auth(),
            _disable_service_check=True)
        experiment = Experiment(workspace, self._experiment_name)
        run = Run(experiment, run_id=asset.runid)
        upload_id = asset.properties[AssetProperties.UPLOAD_ID]
        return download_causal_insights(run, upload_id=upload_id, asset_type=AzureMLTypes.MODEL_ANALYSIS)
