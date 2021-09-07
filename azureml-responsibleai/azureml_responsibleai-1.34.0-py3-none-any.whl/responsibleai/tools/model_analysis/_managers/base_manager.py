# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC, abstractmethod
from typing import List

from azureml._restclient.assets_client import AssetsClient


class BaseManager(ABC):
    def __init__(self,
                 service_context,
                 experiment_name: str,
                 analysis_id: str):
        """Initialize the BaseManager."""
        super(BaseManager, self).__init__()
        self._experiment_name = experiment_name
        self._analysis_id = analysis_id
        self._ac = AssetsClient(service_context)
        self._sc = service_context

    @property
    def experiment_name(self) -> str:
        return self._experiment_name

    @property
    def analysis_id(self) -> str:
        """Return the id of the parent ModelAnalysisRun"""
        return self._analysis_id

    @property
    def _assets_client(self) -> AssetsClient:
        return self._ac

    @property
    def _service_context(self):
        return self._sc

    @abstractmethod
    def list(self) -> List:
        """List the objects which have been computed by this manager."""
        pass

    @abstractmethod
    def download_by_id(self, id: str):
        """Download a particular object."""
        pass
