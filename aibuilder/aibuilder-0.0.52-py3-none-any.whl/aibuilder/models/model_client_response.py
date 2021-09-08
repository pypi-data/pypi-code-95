#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from aibuilder.models.constants import ModelClientResponseStatus


class ModelClientResponse:
    def __init__(self, status: ModelClientResponseStatus, model_name: str, model_id: str, **kwargs: dict):
        """
        Response expected to be returned by model host operations like create, delete and publish

        :param status: ModelClientResponseStatus enum representing Success or Failure
        :param model_name: Name of the model
        :param model_id: Model id from the host
        :param kwargs: Additional operation status returned
        """
        if not isinstance(status, ModelClientResponseStatus):
            raise ValueError(f"Status should be of type ModelClientResponseStatus, but got {type(status)}")
        if not isinstance(model_name, str):
            raise ValueError(f"model_name should be of type str, but got {type(model_name)}")
        if not isinstance(model_id, str):
            raise ValueError(f"model_id should be of type str, but got {type(model_id)}")

        self._status = status
        self._model_id = model_id
        self._model_name = model_name
        self._status_info = dict(kwargs)

    @property
    def status(self) -> ModelClientResponseStatus:
        return self._status

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def status_info(self) -> dict:
        return self._status_info
