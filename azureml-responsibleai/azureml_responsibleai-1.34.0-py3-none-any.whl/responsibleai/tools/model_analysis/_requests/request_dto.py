# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional

from .causal_request import CausalRequest
from .counterfactual_request import CounterfactualRequest
from .error_analysis_request import ErrorAnalysisRequest
from .explain_request import ExplainRequest


class RequestDTO:
    """Pickleable object for transmitting the requests to remote compute.

    Ideally we ought to be able to convert this to JSON as well."""

    def __init__(self,
                 *,
                 causal_requests: Optional[List[CausalRequest]] = None,
                 counterfactual_requests: Optional[List[CounterfactualRequest]] = None,
                 error_analysis_requests: Optional[List[ErrorAnalysisRequest]] = None,
                 explanation_requests: Optional[List[ExplainRequest]] = None):
        self._causal_requests = causal_requests if causal_requests is not None else []
        self._counterfactual_requests = counterfactual_requests if counterfactual_requests is not None else []
        self._explain_requests = explanation_requests if explanation_requests is not None else []
        self._error_analysis_requests = error_analysis_requests if error_analysis_requests is not None else []

    @property
    def causal_requests(self) -> List[CausalRequest]:
        return self._causal_requests

    @property
    def error_analysis_requests(self) -> List[ErrorAnalysisRequest]:
        return self._error_analysis_requests

    @property
    def explanation_requests(self) -> List[ExplainRequest]:
        return self._explain_requests

    @property
    def counterfactual_requests(self) -> List[CounterfactualRequest]:
        return self._counterfactual_requests
