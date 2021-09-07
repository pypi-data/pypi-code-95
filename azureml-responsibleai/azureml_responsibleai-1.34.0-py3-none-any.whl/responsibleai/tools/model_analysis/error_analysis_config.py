# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains the config used for adding error analysis reports to a model analysis.

This can be submitted as a child run of a ModelAnalysisRun
"""
from typing import List, Optional

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.core import RunConfiguration
from azureml.core._experiment_method import experiment_method

from azureml.responsibleai.tools.model_analysis.model_analysis_run import ModelAnalysisRun
from azureml.responsibleai.tools.model_analysis._base_component_config import BaseComponentConfig
from azureml.responsibleai.tools.model_analysis._utilities import component_submit
from azureml.responsibleai.tools.model_analysis._requests import ErrorAnalysisRequest, RequestDTO


@experimental
class ErrorAnalysisConfig(BaseComponentConfig):
    """Class to configure an error-report-generating Run."""

    @experiment_method(submit_function=component_submit)
    def __init__(self,
                 model_analysis_run: ModelAnalysisRun,
                 run_configuration: RunConfiguration = None,
                 comment: Optional[str] = None):
        """Instantiate instance of class."""
        super(ErrorAnalysisConfig, self).__init__(
            model_analysis_run,
            run_configuration
        )
        self._requests: List[ErrorAnalysisRequest] = []

    def add_request(self,
                    max_depth: Optional[int] = None,
                    num_leaves: Optional[int] = None,
                    filter_features: Optional[List[str]] = None,
                    comment: Optional[str] = None):
        """Add an Error Analysis Report to the configuration."""
        self._requests.append(ErrorAnalysisRequest(max_depth=max_depth,
                                                   num_leaves=num_leaves,
                                                   filter_features=filter_features,
                                                   comment=comment))

    def _compute_requests(self,
                          experiment_name: str,
                          requests: Optional[RequestDTO] = None,
                          **kwargs):
        if not requests:
            requests = RequestDTO(error_analysis_requests=self._requests)
        return super()._compute_requests(experiment_name, requests, **kwargs)
