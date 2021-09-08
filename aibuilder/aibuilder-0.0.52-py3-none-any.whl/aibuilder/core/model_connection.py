#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from abc import ABC, abstractmethod
import os


class ModelConnection(ABC):
    @abstractmethod
    def __init__(self) -> None:
        """
        Model connection abstract class.

        """
        pass


class LocalFileConnection(ModelConnection):
    def __init__(self, swagger_file_path: str) -> None:
        """
        Takes local file path of swagger as input.

        :param swagger_file_path: Local file path to swagger file
        """
        super().__init__()
        if not os.path.isfile(swagger_file_path):
            raise ValueError(f"Please provide a valid local file path. Got: {swagger_file_path}")
        self.swagger_file_path = swagger_file_path
