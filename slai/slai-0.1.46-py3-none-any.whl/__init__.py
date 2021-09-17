from slai.model_version import ModelVersion
from slai.model_inputs import ModelInputs
from slai.base_handler import BaseModelHandler
from slai.login import Login
from slai import loaders
from slai.model import Model
from slai.dataset import DataSet

__version__ = "0.1.46"


# most used slai actions go here
model = Model
model_version = ModelVersion
loaders = loaders
inputs = ModelInputs
login = Login
dataset = DataSet
BaseModelHandler = BaseModelHandler

__all__ = [
    "__version__",
    "model_version",
    "dataset",
    "model",
    "inputs",
    "base_handler",
    "loaders",
    "login",
]
