# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains the functionality for managing model analyses in Azure Machine Learning.

This module contains methods for retrieving model analyses, dashboards, and snapshotted data.
"""
from collections import OrderedDict
import joblib
import json
import os
import pandas as pd
import pickle as pkl
import pyarrow.parquet as pq
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional  # noqa: F401

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._common._error_definition import AzureMLError
from azureml._common.exceptions import AzureMLException
from azureml._restclient.constants import RunStatus
from azureml.core import Datastore, Run, Workspace
from azureml.core.run import RUNNING_STATES
from azureml.data.abstract_datastore import AbstractDatastore
from azureml.exceptions import UserErrorException
from azureml.responsibleai.tools.model_analysis._aml_init_dto import AMLInitDTO
from azureml.responsibleai.tools.model_analysis._constants import PropertyKeys, ModelAnalysisFileNames
from azureml.responsibleai.tools.model_analysis._managers.explanation_manager import ExplanationManager
from azureml.responsibleai.tools.model_analysis._managers.causal_manager import CausalManager
from azureml.responsibleai.tools.model_analysis._managers.counterfactual_manager import CounterfactualManager
from azureml.responsibleai.tools.model_analysis._managers.error_analysis_manager import ErrorAnalysisManager

from azureml.responsibleai.common._errors.error_definitions import (
    AnalysisInitFailedSystemError, AnalysisInitFailedUserError, AnalysisInitNotCompletedError)


@experimental
class ModelAnalysisRun(Run):
    """Run object containing pointers to other model analyses."""

    def __init__(self, experiment, run_id, run_display_name=None, *args, **kwargs):
        """
        Initialize a ModelAnalysisRun.

        :param experiment: The experiment associated with the run.
        :type experiment: azureml.core.Experiment
        :param run_id: The ID of the run.
        :type run_id: str
        :param run_display_name: The run display name of the model analysis parent run
        :type run_display_name: str
        """
        super().__init__(experiment, run_id, *args, **kwargs)
        self._settings = None  # type: Optional[AMLInitDTO]
        self._output_directory = None  # type: Optional[str]
        self._datastore = None  # type: Optional[Datastore]
        if run_display_name is not None:
            self.display_name = run_display_name

    @property
    def settings(self) -> AMLInitDTO:
        """Get the settings used when creating this run."""
        if not self._settings:
            self._assert_initialize_finished()
            with TemporaryDirectory() as td:
                self.download_file(ModelAnalysisFileNames.SETTINGS, output_file_path=td)
                self._settings = joblib.load(os.path.join(td, ModelAnalysisFileNames.SETTINGS))
        # Following assert needed for return type
        assert self._settings
        return self._settings

    @property
    def datastore(self) -> AbstractDatastore:
        """
        Get the datastore where the analysis artifacts are stored.

        This may differ from the workspace's default datastore, and may not be accessible in some environments.
        """
        if not self._datastore:
            self._datastore = Datastore.get(self.experiment.workspace, self.settings.confidential_datastore_name)
        return self._datastore

    @property
    def analysis_id(self) -> str:
        """Get the id for this model analysis, used for linking other analyses together."""
        return str(self.settings.analysis_id)

    @property
    def _is_failed(self):
        failed_states = [RunStatus.FAILED, RunStatus.CANCELED, RunStatus.CANCEL_REQUESTED]
        return self.get_status() in failed_states

    @property
    def _is_running(self):
        return self.get_status() in RUNNING_STATES

    @property
    def _is_completed(self):
        return not self._is_running and not self._is_failed

    def _assert_initialize_finished(self):
        if self._is_failed:
            error_code = self.get_details().get("error", {}).get("error", {}).get("code")
            if error_code == "UserError":
                raise UserErrorException._with_error(
                    AzureMLError.create(
                        AnalysisInitFailedUserError,
                        portal_url=str(self.get_portal_url())
                    )
                )
            else:
                raise AzureMLException._with_error(
                    AzureMLError.create(
                        AnalysisInitFailedSystemError,
                        portal_url=str(self.get_portal_url())
                    )
                )
        elif self._is_running:
            raise UserErrorException._with_error(
                AzureMLError.create(
                    AnalysisInitNotCompletedError,
                    portal_url=str(self.get_portal_url())
                )
            )

    @property
    def causal_manager(self) -> CausalManager:
        """Get an CausalManager for accessing the computed causal analyses."""
        return CausalManager(self.experiment.workspace.service_context,
                             self.experiment.name,
                             self.analysis_id)

    @property
    def counterfactual_manager(self) -> CounterfactualManager:
        """Get a CounterfactualManager for accessing the computed examples."""
        return CounterfactualManager(self.experiment.workspace.service_context,
                                     self.experiment.name,
                                     self.analysis_id)

    @property
    def error_analysis_manager(self) -> ErrorAnalysisManager:
        """Get an ErrorAnalysisManager for accessing the computed ErrorReport."""
        return ErrorAnalysisManager(self.experiment.workspace.service_context,
                                    self.experiment.name,
                                    self.analysis_id)

    @property
    def explanation_manager(self) -> ExplanationManager:
        """Get an ExplanationManager for accessing the computed explanations."""
        return ExplanationManager(self.experiment.workspace.service_context,
                                  self.experiment.name,
                                  self.analysis_id)

    @staticmethod
    def get_model_analysis_runs(
            workspace: Workspace,
            model_analysis_id: Optional[str] = None,
            model_id: Optional[str] = None) -> List['ModelAnalysisRun']:
        """
        Fetch the model analysis assets for this workspace.

        :param workspace: The workspace to fetch assets from.
        :param model_analysis_id: The specific model analysis run to fetch.
        :param model_id: Which model to fetch the assets for.
        """
        model_analysis_runs: List['ModelAnalysisRun'] = []
        property_filters = {}
        if model_analysis_id:
            property_filters[PropertyKeys.ANALYSIS_ID] = model_analysis_id
        if model_id:
            property_filters[PropertyKeys.MODEL_ID] = model_id
        for _, experiment in workspace.experiments.items():
            # TODO mark these as type _MODEL_ANALYSIS_RUN_TYPE and pass type=_MODEL_ANALYSIS_RUN_TYPE
            assets = Run.list(experiment=experiment, properties=property_filters, status=RunStatus.COMPLETED)
            # Once these are marked correctly, run.list should return the correct type, but until then we manually case
            model_analysis_runs.extend(
                [ModelAnalysisRun(experiment, asset.id) for asset in assets
                 if PropertyKeys.ANALYSIS_ID in asset.properties])
        return model_analysis_runs

    def download_data(self, output_directory: str = None) -> None:
        """
        Download all the data associated with this model analysis.

        :param output_directory: The directory in which the files will be saved.
        """
        self.datastore.download(target_path=output_directory, prefix=self.settings.train_snapshot_id)
        self.datastore.download(target_path=output_directory, prefix=self.settings.test_snapshot_id)
        self._output_directory = output_directory

    def get_train_data(self) -> pd.DataFrame:
        """Fetch the training data used for this model analysis."""
        return self._get_data_from_snapshot(
            file_name=ModelAnalysisFileNames.TRAIN_DATA,
            datastore_prefix=self.settings.datastore_prefix,
            snapshot_id=self.settings.train_snapshot_id)

    def get_train_labels(self) -> pd.DataFrame:
        """Fetch the training labels used for this model analysis."""
        return self._get_data_from_snapshot(
            file_name=ModelAnalysisFileNames.TRAIN_Y_PRED,
            datastore_prefix=self.settings.datastore_prefix,
            snapshot_id=self.settings.train_snapshot_id)

    def get_test_data(self) -> pd.DataFrame:
        """Fetch the test data used for this model analysis."""
        return self._get_data_from_snapshot(
            file_name=ModelAnalysisFileNames.TEST_DATA,
            datastore_prefix=self.settings.datastore_prefix,
            snapshot_id=self.settings.test_snapshot_id)

    def get_test_labels(self) -> pd.DataFrame:
        """Fetch the test labels used for this model analysis."""
        return self._get_data_from_snapshot(
            file_name=ModelAnalysisFileNames.TEST_Y_PRED,
            datastore_prefix=self.settings.datastore_prefix,
            snapshot_id=self.settings.test_snapshot_id)

    def _get_data_types(self) -> Dict:
        """Fetch the data types for the data."""
        return self._get_data_from_run(
            file_name=ModelAnalysisFileNames.DATA_TYPES)

    def _get_data_from_snapshot(self, file_name: str,
                                datastore_prefix: Optional[str],
                                snapshot_id: str) -> pd.DataFrame:
        if datastore_prefix is not None:
            prefix = '{}/{}'.format(datastore_prefix, snapshot_id)
        else:
            prefix = snapshot_id
        # if a user already called download, see if we can reuse that, else download
        if self._output_directory:
            data_path = os.path.join(os.getcwd(), self._output_directory, prefix, file_name)
            if os.path.isfile(data_path):
                return ModelAnalysisRun._read_file(data_path)
        with TemporaryDirectory() as td:
            self.datastore.download(target_path=td, prefix=prefix)
            path = os.path.join(td, prefix, file_name)
            return ModelAnalysisRun._read_file(path)

    def _get_data_from_run(self, file_name):
        if self._output_directory:
            data_path = os.path.join(os.getcwd(), self._output_directory, file_name)
            if os.path.isfile(data_path):
                return ModelAnalysisRun._read_file(data_path)
        with TemporaryDirectory() as td:
            if os.path.split(file_name)[0] == ModelAnalysisFileNames.DATA_PREFIX:
                temp_data_path = os.path.join(td, ModelAnalysisFileNames.DATA_PREFIX)
                os.makedirs(temp_data_path)
            else:
                temp_data_path = td
            self.download_file(name=file_name, output_file_path=temp_data_path)
            path = os.path.join(td, file_name)
            return ModelAnalysisRun._read_file(path)

    def _get_base_info_dict(self) -> OrderedDict:
        """Return information about the run. This is called by __str__ and __repr__."""
        run_info = super()._get_base_info_dict()
        run_info['Title'] = self.settings.title
        run_info['AnalysisId'] = self.settings.analysis_id
        return run_info

    @staticmethod
    def _read_file(data_path: str):
        if data_path.endswith("json"):
            with open(data_path, "r") as file:
                return pd.DataFrame(json.load(file))
        elif data_path.endswith('parquet'):
            return pq.read_table(data_path).to_pandas()
        else:
            with open(data_path, "rb") as data_file:
                return pkl.load(data_file)
