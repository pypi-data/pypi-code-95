#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from abc import ABC, abstractmethod

from aibuilder.models.constants import _AIBModelType
from aibuilder.models.model_client_response import ModelClientResponse


class ModelManagementClient(ABC):
    """Interface for implementing model client.
    This interface will mainly be used to implement AI Builder model client

    """

    @classmethod
    @abstractmethod
    def create(cls, model_name: str,
               org_url: str,
               api_specification_file_path: str,
               data_binding: str,
               token: str,
               model_type: _AIBModelType = _AIBModelType.generic_prediction,
               **kwargs) -> ModelClientResponse:
        """
        Create a model with using the model name

        :param model_name: Name of the model to be created on the hosting service
        :param org_url: Model host URL
        :param api_specification_file_path: Open API specification file path
        :param data_binding: Data Binding
        :param token: Bearer token
        :param model_type: AI Builder model type
        :param kwargs: Additional key value parameters required to create a model
        :return: Returns a model host response object indicating the status of the operation
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def delete(cls, model_name: str) -> ModelClientResponse:
        """
        Deletes the model using the model name

        :param model_name: Name of the model to be deleted
        :return: Returns a model host response object indicating the status of the operation
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def publish(cls, model_name: str, **kwargs: dict) -> ModelClientResponse:
        """
        Publish an existing model which makes the model ready for consumption

        :param model_name: Name of the model to be published
        :param kwargs: Additional key value parameters required to publish a model
        :return: Returns a model host response object indicating the status of model publish
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def unpublish(cls, model_name: str, **kwargs: dict) -> ModelClientResponse:
        """
        Un-publish an existing model which marks the model as not ready for consumption

        :param model_name: Name of the model to un-publish
        :param kwargs: Additional key value parameters required to un-publish a model
        :return: Returns a model host response object indicating the status of model un-publish
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def predict(cls, model_name: str, **kwargs: dict) -> ModelClientResponse:
        """
        Schedule prediction runs on the model using the model name

        :param model_name: Name of the model to schedule predict
        :param kwargs: Additional key value parameters required to schedule prediction runs
        :return: Returns a model host response object indicating the status of scheduling prediction
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def test(cls, model_name: str, payload: object) -> ModelClientResponse:
        """
        Run model test on an existing model

        :param model_name: Name of the model
        :param payload: Json serializable python object to be passed to the model end point
        :return: Returns a model host response object indicating the status of the test
        """
        raise NotImplementedError
