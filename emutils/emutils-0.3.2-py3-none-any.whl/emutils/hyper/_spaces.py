import warnings
from copy import deepcopy

import numpy as np

from hyperopt import hp
from hyperopt.pyll import scope

from ._utils import get_model_type, get_hyperopt_type, add_random_state

DEFAULT_RANDOM_STATE = 2020


class SpaceNotFoundWarning(UserWarning):
    pass


# Three-levels dict
# First  : model
# Second : dataset, optional (None, by default)
# Third  : search type (grid, or hyperopt)
SEARCH_SPACES = {
    'xgb':
        {
            None:
                dict(
                    grid=dict(
                        learning_rate=[.001, .005, .01, .05, .1],
                        max_depth=[2, 3, 4, 5, 6, 8, 10, 12, 15],
                        n_estimators=[10, 20, 50, 100, 200, 300, 500],
                    ),
                    bayes=dict(
                        learning_rate=hp.loguniform('learning_rate', np.log(.005), np.log(.1)),
                        max_depth=scope.int(hp.quniform('max_depth', 2, 20, q=1)),
                        min_child_weight=scope.int(hp.uniform('min_child_weight', 1, 10)),
                        gamma=hp.uniform('gamma', 0.0, 100.0),
                        n_estimators=hp.choice('n_estimators', [10, 20, 50, 100, 200, 300, 500]),
                        subsample=hp.uniform('subsample', 0.5, 1.0),
                        colsample_bytree=hp.uniform('colsample_bytree', 0.5, 1.0),
                        scale_pos_weight=hp.loguniform('scale_pos_weight', np.log(1), np.log(1000)),
                    )
                ),
            'heloc':
                dict(
                    grid=None,
                    bayes=dict(
                        learning_rate=hp.loguniform('learning_rate', np.log(.005), np.log(.05)),
                        max_depth=scope.int(hp.quniform('max_depth', 2, 20, q=1)),
                        min_child_weight=scope.int(hp.uniform('min_child_weight', 1, 50)),
                        gamma=hp.uniform('gamma', 0.0, 100.0),
                        n_estimators=hp.choice('n_estimators', [50, 100, 200, 300]),
                        subsample=hp.uniform('subsample', 0.5, 1.0),
                        colsample_bytree=hp.uniform('colsample_bytree', 0.5, 1.0),
                        scale_pos_weight=hp.uniform('scale_pos_weight', .5, 2.0),
                    )
                ),
            'gmsc':
                dict(
                    grid=None,
                    bayes=dict(
                        learning_rate=hp.loguniform('learning_rate', np.log(.01), np.log(.1)),
                        max_depth=scope.int(hp.quniform('max_depth', 2, 10, q=1)),
                        min_child_weight=scope.int(hp.uniform('min_child_weight', 1, 100)),
                        gamma=hp.uniform('gamma', 0.0, 100.0),
                        n_estimators=hp.choice('n_estimators', [20, 50, 100, 200]),
                        subsample=hp.uniform('subsample', 0.5, 1.0),
                        colsample_bytree=hp.uniform('colsample_bytree', 0.5, 1.0),
                        scale_pos_weight=hp.uniform('scale_pos_weight', 1, 1000.0),
                    )
                ),
            'lendingclub':
                dict(
                    grid=None,
                    bayes=dict(
                        learning_rate=hp.loguniform('learning_rate', np.log(.005), np.log(.05)),
                        max_depth=scope.int(hp.quniform('max_depth', 2, 20, q=1)),
                        min_child_weight=scope.int(hp.uniform('min_child_weight', 25, 1000)),
                        gamma=hp.uniform('gamma', 0.0, 100.0),
                        n_estimators=hp.choice('n_estimators', [50, 100, 200, 300, 500]),
                        subsample=hp.uniform('subsample', 0.5, 1.0),
                        colsample_bytree=hp.uniform('colsample_bytree', 0.5, 1.0),
                        scale_pos_weight=hp.uniform('scale_pos_weight', 1.0, 1000.0),
                    )
                ),
        },
    'dt': None,
    'rf': None,
    'ada': None,
}


def get_search_space_from_library(
    model_type,
    dataset=None,
    space=None,
    hyperopt_type='bayes',
):
    model_type = get_model_type(model_type)
    hyperopt_type = get_hyperopt_type(hyperopt_type)

    if space is None:
        # Model type
        spaces = SEARCH_SPACES
        if model_type not in spaces or spaces[model_type] is None:
            raise ValueError(f'No space available for {model_type} model.')
        spaces = spaces[model_type]

        # Dataset
        def __dataset_space(dataset):
            if dataset not in spaces or spaces[dataset] is None:
                warnings.warn(
                    f"No space available for '{model_type}' model and '{dataset}' dataset. Using default space for '{model_type}' model.",
                    SpaceNotFoundWarning
                )
                return __dataset_space(None)
            return spaces[dataset]

        spaces = __dataset_space(dataset)

        # Search type
        def __hyperopt_type_space(hyperopt_type):
            if hyperopt_type not in spaces or spaces[hyperopt_type] is None:
                if hyperopt_type == 'random':
                    warnings.warn(
                        "No space available for 'random' search. Using space for 'grid' search.", SpaceNotFoundWarning
                    )
                    return __hyperopt_type_space('grid')
                else:
                    raise ValueError(f"No space available for '{hyperopt_type}' search on '{model_type}/{dataset}'.")
            return spaces[hyperopt_type]

        space = __hyperopt_type_space(hyperopt_type)

    # Copy (other-wise we edit the library)
    space = deepcopy(space)

    return space