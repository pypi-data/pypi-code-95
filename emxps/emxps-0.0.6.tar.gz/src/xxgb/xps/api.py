from abc import ABC
from typing import Union

try:
    from typing import Protocol
    from typing import runtime_checkable
except:
    # Python < 3.8 - Compatibility
    from emutils.utils import import_with_auto_install
    typing_extensions = import_with_auto_install('typing_extensions')
    from typing_extensions import Protocol
    from typing_extensions import runtime_checkable

import numpy as np

from emutils.utils import np_sample

__all__ = ['Scaler', 'Model', 'ModelWithDecisionFunction']


@runtime_checkable
class Scaler(Protocol):
    def transform(self, X):
        pass

    def inverse_transform(self, X):
        pass


@runtime_checkable
class XGBWrapping(Protocol):
    def get_booster(self):
        pass


@runtime_checkable
class Model(Protocol):
    def predict(self, X) -> np.ndarray:
        pass

    def predict_proba(self, X) -> np.ndarray:
        pass


@runtime_checkable
class ModelWithDecisionFunction(Model, Protocol):
    def decision_function(self, X) -> np.ndarray:
        pass


class BaseClass(ABC):
    def __init__(self, model: Model, scaler: Union[Scaler, None] = None):
        self.model = model
        self.scaler = scaler

    def preprocess(self, X, n=None):
        if not isinstance(X, np.ndarray):
            raise ValueError('Must pass a NumPy array.')

        return X

    def sample(self, X, n):
        if n is not None:
            X = np_sample(X, n, random_state=self.random_state, safe=True)

        return X

    def scale(self, X):
        if self.scaler is None:
            return X
        else:
            return self.scaler.transform(X)
