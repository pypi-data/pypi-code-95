from copy import deepcopy
import numpy as np

from .api import (
    BaseDiverseCounterfactualMethod, DiverseCounterfactualMethodSupportsWrapping, DiverseCounterfactualMethodWrappable
)

__all__ = [
    'CounterfactualComposition',
    'compose_diverse_counterfactual_method',
]


class CounterfactualComposition(BaseDiverseCounterfactualMethod):
    def __init__(
        self,
        wrapping_instance: DiverseCounterfactualMethodSupportsWrapping,
        wrapped_instance: DiverseCounterfactualMethodWrappable,
    ):

        if wrapping_instance.model != wrapped_instance.model:
            raise ValueError('Models of wrapping and wrapped method differs.')

        super().__init__(wrapping_instance.model, None)

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
