from abc import ABC, abstractmethod, ABCMeta
import numpy as np
import warnings
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

from ..api import Scaler, Model, BaseClass

__all__ = [
    'CounterfactualMethod',
    'DiverseCounterfactualMethod',
    'DiverseCounterfactualMethodSupportsWrapping',
    'DiverseCounterfactualMethodWrappable',
    'BaseCounterfactualMethod',
    'BaseDiverseCounterfactualMethod',
]


@runtime_checkable
class CounterfactualMethod(Protocol):
    model: Model

    def get_counterfactuals(self, X):
        pass


@runtime_checkable
class DiverseCounterfactualMethod(CounterfactualMethod, Protocol):
    def get_diverse_counterfactuals(self, X):
        pass


class BaseCounterfactualMethod(BaseClass, ABC, CounterfactualMethod):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fix_invalid_counterfactuals = True

    def postprocess(self, X, X_counter):
        # Mask with the non-flipped counterfactuals
        not_flipped_mask = (self.model.predict(X) == self.model.predict(X_counter))
        if not_flipped_mask.sum() > 0:
            self._warn_invalid()

        # Set them to nan
        if self.fix_invalid_counterfactuals:
            X_counter[not_flipped_mask, :] = np.nan

        return X_counter

    def _warn_invalid(self):
        warnings.warn(
            '!! ERROR: Some counterfactuals are NOT VALID' +
            (' (will be set to NaN)' if self.fix_invalid_counterfactuals else "")
        )

    @abstractmethod
    def get_counterfactuals(self, X):
        pass


class BaseDiverseCounterfactualMethod(BaseCounterfactualMethod):
    def diverse_postprocess(self, X, X_counter):
        # Reshape (for zero-length arrays)
        X_counter = [X_C.reshape(-1, X.shape[1]) for X_C in X_counter]

        # Mask with the non-flipped counterfactuals
        nb_counters = np.array([X_c.shape[0] for X_c in X_counter])
        not_flipped_mask = np.equal(
            np.repeat(self.model.predict(X), nb_counters),
            self.model.predict(np.concatenate(X_counter, axis=0)),
        )
        if not_flipped_mask.sum() > 0:
            self._warn_invalid()

        sections = np.cumsum(nb_counters[:-1])
        not_flipped_mask = np.split(not_flipped_mask, indices_or_sections=sections)

        # Set them to nan
        if self.fix_invalid_counterfactuals:
            for i, nfm in enumerate(not_flipped_mask):
                X_counter[i][nfm, :] = np.nan

        return X_counter

    @abstractmethod
    def get_diverse_counterfactuals(self, X):
        pass

    def get_counterfactuals(self, X):
        return np.array([X_C[0] for X_C in self.get_diverse_counterfactuals(X)])


@runtime_checkable
class Wrappable(Protocol):
    verbose: Union[int, bool]


@runtime_checkable
class SupportsWrapping(Protocol):
    @property
    def data(self):
        pass

    @data.setter
    @abstractmethod
    def data(self, data):
        pass


@runtime_checkable
class DiverseCounterfactualMethodSupportsWrapping(DiverseCounterfactualMethod, SupportsWrapping, Protocol):
    pass


@runtime_checkable
class DiverseCounterfactualMethodWrappable(DiverseCounterfactualMethod, Wrappable, Protocol):
    pass