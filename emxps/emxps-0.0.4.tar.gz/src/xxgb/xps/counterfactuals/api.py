from abc import ABC, abstractmethod, ABCMeta
import numpy as np
import warnings
from types import MethodType
from copy import deepcopy
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

from ..api import Scaler, Model

__all__ = [
    'CounterfactualMethod',
    'DiverseCounterfactualMethod',
    'BaseCounterfactualMethod',
    'BaseDiverseCounterfactualMethod',
    'SupportsWrapping',
    'Wrappable',
    'CounterfactualComposition',
    'compose_diverse_counterfactual_method',
]


@runtime_checkable
class CounterfactualMethod(Protocol):
    def get_counterfactuals(self, X):
        pass


@runtime_checkable
class DiverseCounterfactualMethod(CounterfactualMethod, Protocol):
    def get_diverse_counterfactuals(self, X):
        pass


class BaseCounterfactualMethod(ABC, CounterfactualMethod):
    def __init__(self, model: Model, scaler: Scaler = None):
        self.model = model
        self.scaler = scaler

        self.fix_invalid_counterfactuals = True

    def preprocess(self, X):
        if not isinstance(X, np.ndarray):
            raise ValueError('Must pass a NumPy array.')

        return X

    def scale(self, X):
        if self.scaler is None:
            return X
        else:
            return self.scaler.transform(X)

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


class CounterfactualComposition(DiverseCounterfactualMethod):
    def __init__(
        self,
        wrapping_instance: DiverseCounterfactualMethodSupportsWrapping,
        wrapped_instance: DiverseCounterfactualMethodWrappable,
    ):

        if wrapping_instance.model != wrapped_instance.model:
            raise ValueError('Models of wrapping and wrapped method differs.')

        if not isinstance(wrapped_instance, DiverseCounterfactualMethodWrappable):
            raise ValueError('wrapped_instance do not implement necessary interface.')

        if not isinstance(wrapping_instance, DiverseCounterfactualMethodSupportsWrapping):
            raise ValueError('wrapping_instance do not implement necessary interface.')

        # Scalers are ignored (they are already into the wrapped/wrapping instances)
        super().__init__(wrapping_instance.model, scaler=None)

        wrapping_instance = deepcopy(wrapping_instance)
        wrapped_instance = deepcopy(wrapped_instance)

        wrapped_instance.verbose = 0

        self.wrapping_instance = wrapping_instance
        self.wrapped_instance = wrapped_instance

        self.data = None

    def get_diverse_counterfactuals(self, X):
        X = self.preprocess(X)

        # Get underlying counterfactuals
        X_Cs = self.wrapped_instance.get_diverse_counterfactuals(X)

        # Postprocess them
        for i, (x, X_C) in enumerate(zip(X, X_Cs)):
            # Set background
            self.data = self.wrapping_instance.data = X_C

            # Compute counterfactuals
            X_Cs[i] = self.wrapping_instance.get_diverse_counterfactuals(np.array([x]))[0]

        return X_Cs


def compose_diverse_counterfactual_method(*args):
    if len(args) < 2:
        raise ValueError('At least 2 counterfactual methods methods must be passed.')

    for wrapped_instance in args[1:]:
        if not isinstance(wrapped_instance, Wrappable):
            raise ValueError('Some methods do not implement Wrappable.')

    for wrapping_instance in args[:-1]:
        if not isinstance(wrapped_instance, SupportsWrapping):
            raise ValueError('Some methods do not implement SupportsWrapping.')

    # Most inner
    composition = args[-1]

    # Iteratively compose
    for wrapping_instance in args[-2::-1]:
        composition = CounterfactualComposition(wrapping_instance, composition)

    return composition


# def compose_diverse_counterfactual_method(
#     wrapping_instance: SupportsWrapping,
#     wrapped_instance: Wrappable
# ):
#     # Deepcopy, we don't want to modify the orginal instance
#     wrapping_instance = deepcopy(wrapping_instance)
#     wrapped_instance = deepcopy(wrapped_instance)

#     wrapped_instance.verbose = 0

#     # Add the wrapped method to the wrapping object
#     wrapping_instance.wrapped_instance = wrapped_instance

#     # Change the generation of counterfactuals
#     wrapping_instance.wrapping_get_diverse_counterfactuals = MethodType(
#         wrapping_instance.get_diverse_counterfactuals, wrapping_instance
#     )
#     wrapping_instance.get_diverse_counterfactuals = MethodType(get_diverse_counterfactuals, wrapping_instance)

#     return wrapping_instance
