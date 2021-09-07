# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Model loader for models serialized using pickle."""
import pickle

from pathlib import Path

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.responsibleai.common.model_loader import ModelLoader


@experimental
class PickleModelLoader(ModelLoader):
    """Model loader for models serialized using pickle."""

    def __init__(self, filepath):
        """
        Construct a ModelLoader.

        :param filepath: Path to the pickle file within the AzureML model directory.
        """
        self._filepath = filepath

    def load(self, dirpath):
        """
        Load the model from the specified directory.

        :param dirpath: Directory into which the AzureML model has been downloaded.
        :return: Python model with fit and predict methods.
        """
        full_filepath = Path(dirpath) / self._filepath
        with open(full_filepath, 'rb') as f:
            return pickle.load(f)
