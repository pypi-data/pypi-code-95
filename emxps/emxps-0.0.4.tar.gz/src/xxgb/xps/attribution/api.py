from abc import ABC, abstractmethod
from typing import Union
import numpy as np

try:
    from typing import Protocol
    from typing import runtime_checkable
except:
    # Python < 3.8 - Compatibility
    from emutils.utils import import_with_auto_install
    typing_extensions = import_with_auto_install('typing_extensions')
    from typing_extensions import Protocol
    from typing_extensions import runtime_checkable

from ..api import Model, Scaler
from ..counterfactuals import CounterfactualMethod

__all__ = [
    'Explainer',
    'SupportsDynamicBackground',
    'ExplainerSupportsDynamicBackground',
    'BaseExplainer',
    'BaseSupportsDynamicBackground',
]


@runtime_checkable
class SupportsDynamicBackground(Protocol):
    @property
    def data(self):
        pass

    @data.setter
    def data(self, data):
        pass


@runtime_checkable
class Explainer(Protocol):
    model: Model
    scaler: Union[Scaler, None]

    def shap_values(self, X):
        pass


@runtime_checkable
class ExplainerSupportsDynamicBackground(Explainer, SupportsDynamicBackground, Protocol):
    pass


class BaseExplainer(ABC):
    def __init__(self, model: Model, scaler: Union[Scaler, None] = None):
        self.model = model
        self.scaler = scaler

    def preprocess(self, X):
        if not isinstance(X, np.ndarray):
            raise ValueError('Must pass a NumPy array.')

        return X

    def scale(self, X):
        if self.scaler is None:
            return X
        else:
            return self.scaler.transform(X)

    @abstractmethod
    def shap_values(self, X):
        pass


class BaseSupportsDynamicBackground(ABC):
    @property
    def data(self):
        if self._data is None:
            self._raise_data_error()
        return self._data

    def _raise_data_error(self):
        raise ValueError('Must set data first.')

    @data.setter
    @abstractmethod
    def data(self, data):
        pass
