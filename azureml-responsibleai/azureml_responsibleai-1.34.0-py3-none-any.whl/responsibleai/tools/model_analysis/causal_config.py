# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Configuration for causal analysis runs.

This can be submitted as a child run of a ModelAnalysisRun
"""

from typing import List, Optional, Union

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.core import RunConfiguration
from azureml.core._experiment_method import experiment_method

from azureml.responsibleai.tools.model_analysis.model_analysis_run import ModelAnalysisRun
from azureml.responsibleai.tools.model_analysis._base_component_config import BaseComponentConfig
from azureml.responsibleai.tools.model_analysis._utilities import component_submit
from azureml.responsibleai.tools.model_analysis._requests import CausalRequest, RequestDTO


class _CausalConstants:
    LINEAR_MODEL = 'linear'
    AUTOML_MODEL = 'automl'

    DEFAULT_ALPHA = 0.05
    DEFAULT_UPPER_BOUND_ON_CAT_EXPANSION = 50
    DEFAULT_TREATMENT_COST = 0
    DEFAULT_MIN_TREE_LEAF_SAMPLES = 2
    DEFAULT_MAX_TREE_DEPTH = 2
    DEFAULT_SKIP_CAT_LIMIT_CHECKS = False
    DEFAULT_CATEGORIES = 'auto'
    DEFAULT_N_JOBS = -1
    DEFAULT_VERBOSE = 0
    DEFAULT_RANDOM_STATE = None

    DEFAULT_COMMENT = 'Causal analysis'


@experimental
class CausalConfig(BaseComponentConfig):
    """Configuration for causal analysis runs."""

    @experiment_method(submit_function=component_submit)
    def __init__(self,
                 model_analysis_run: ModelAnalysisRun,
                 run_configuration: RunConfiguration = None):
        """Construct a CausalConfig."""
        super(CausalConfig, self).__init__(model_analysis_run, run_configuration)
        self._requests: List[CausalRequest] = []

    def add_request(
        self,
        treatment_features: List[str],
        heterogeneity_features: Optional[List[str]] = None,
        nuisance_model: str = _CausalConstants.LINEAR_MODEL,
        heterogeneity_model: Optional[str] = _CausalConstants.LINEAR_MODEL,
        alpha: Optional[float] = _CausalConstants.DEFAULT_ALPHA,
        upper_bound_on_cat_expansion: int = _CausalConstants.DEFAULT_UPPER_BOUND_ON_CAT_EXPANSION,
        treatment_cost: float = _CausalConstants.DEFAULT_TREATMENT_COST,
        min_tree_leaf_samples: int = _CausalConstants.DEFAULT_MIN_TREE_LEAF_SAMPLES,
        max_tree_depth: int = _CausalConstants.DEFAULT_MAX_TREE_DEPTH,
        skip_cat_limit_checks: bool = _CausalConstants.DEFAULT_SKIP_CAT_LIMIT_CHECKS,
        n_jobs: int = _CausalConstants.DEFAULT_N_JOBS,
        categories: Union[str, list] = _CausalConstants.DEFAULT_CATEGORIES,
        verbose: int = _CausalConstants.DEFAULT_VERBOSE,
        random_state: Union[None, int] = _CausalConstants.DEFAULT_RANDOM_STATE,
        comment: Optional[str] = _CausalConstants.DEFAULT_COMMENT,
    ) -> None:
        """Add a causal insights request to the configuration."""
        request = CausalRequest(
            treatment_features,
            heterogeneity_features=heterogeneity_features,
            nuisance_model=nuisance_model,
            heterogeneity_model=heterogeneity_model,
            alpha=alpha,
            upper_bound_on_cat_expansion=upper_bound_on_cat_expansion,
            treatment_cost=treatment_cost,
            min_tree_leaf_samples=min_tree_leaf_samples,
            max_tree_depth=max_tree_depth,
            skip_cat_limit_checks=skip_cat_limit_checks,
            n_jobs=n_jobs,
            categories=categories,
            verbose=verbose,
            random_state=random_state,
            comment=comment,
        )
        self._requests.append(request)

    def _compute_requests(self,
                          experiment_name: str,
                          requests: Optional[RequestDTO] = None,
                          **kwargs):
        if not requests:
            requests = RequestDTO(causal_requests=self._requests)
        return super()._compute_requests(experiment_name, requests, **kwargs)
