#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from abc import ABC, abstractmethod

from aibuilder.common.paconnector.constants import PowerAppsApiSettings
from aibuilder.common.paconnector.request_builder import _RequestBuilder


class DataModelOperator(ABC):
    def __init__(self, url: str, token: str):
        """
        Interface for implementing AI Builder object model handlers

        :param url: URL endpoint
        :param token: Auth token to be added in HTTP request headers
        """
        self._url = url
        self._request_builder = _RequestBuilder(url=self._url, base_path=PowerAppsApiSettings.BASE_URL.value,
                                                token=token)

    @abstractmethod
    def create(self, **kwargs):
        """
        Interface to implement create object method

        """
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, **kwargs):
        """
        Interface to implement retrieve object method

        """
        raise NotImplementedError

    @abstractmethod
    def update(self, **kwargs):
        """
        Interface to implement update object method

        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, **kwargs):
        """
        Interface to implement delete object method

        """
        raise NotImplementedError
