# %%
import logging
import multiprocessing
import os
from typing import Union, Any, Callable, List, Dict
from copy import deepcopy

import numpy as np
import pandas as pd

from sklearn.model_selection import GridSearchCV, StratifiedKFold, RandomizedSearchCV

from emutils.utils import save_pickle, load_pickle, mkdirname_ifnotexist
from emutils.parallel import max_cpu_count

from ._hyperopt_search import HyperOptSearchCV
from ._spaces import get_search_space_from_library
from ._utils import get_model_type, get_hyperopt_type, add_constant_parameters, add_random_state

# %%

# We incrementally setup constants for each package handling exceptions
MODEL_CLASS = dict()
MODEL_DEFAULT_ARGUMENTS = dict()

try:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import AdaBoostClassifier
    from sklearn.ensemble import RandomForestClassifier

    MODEL_CLASS.update({
        'dt': DecisionTreeClassifier,
        'rf': RandomForestClassifier,
        'ada': AdaBoostClassifier,
    })
except ModuleNotFoundError:
    pass

try:
    from xgboost import XGBClassifier

    MODEL_CLASS.update({
        'xgb': XGBClassifier,
    })

    MODEL_DEFAULT_ARGUMENTS.update(
        {
            XGBClassifier:
                dict(
                    use_label_encoder=False,
                    verbosity=0,
                    n_jobs=24,  # With more thread is not faster in general
                ),
        }
    )
except ModuleNotFoundError:
    pass

DEFAULT_SCORING = [
    "roc_auc",
    "accuracy",
    "balanced_accuracy",
    "f1",
    "recall",
    "precision",
    "average_precision",
    'jaccard',
    "neg_log_loss",
]


def hyper_train(
    X_train: np.ndarray,
    y_train: np.ndarray,
    model_type: str,
    space: Union[None, str, Dict[str, Any]] = None,
    hyperopt_type: str = 'bayes',
    n_splits: int = 5,
    scoring: List[Union[str, Callable]] = DEFAULT_SCORING,
    constant_params: Union[None, dict] = None,
    random_state: Union[None, int] = None,
    save_path=None,
    checkpoint_filename=None,
    resume: bool = False,
    override: bool = False,
    ret_search: bool = False,
    **kwargs,
):
    """Hyper-training for any kind of sklearn-friendly classifier

    Currently supports:

    Args:
        X_train (np.ndarray): Traning data
        y_train (np.ndarray): Training target
        model_type (str): Model string (e.g., 'xgb', or 'rf').
        hyperopt_type (str, optional): Search type. Defaults to 'bayes' (Bayesian optimization with hyperopt).
            Alternatives are:
            - 'random': sklearn Random Search
            - 'grid': sklearn Grid Search
            - 'bayes' : hyperopt Bayesian optimization
        space (Union[None, str, Dict[str, Union[list, hyperopt.hp.*]]], optional): Hyper-parameter search space. 
            - If None, the default hyper-parameters space for the model type will be used.
            - If it's a str (dataset), the default hyper-parameters space for the dataset on a model type will be used.
            - If dict, it can either be :
                - The grid for sklearn GridSearch
                - The space for hyperopt fmin
            Defaults to None.
        n_splits (int, optional): Number of splits of the cross-validation. Defaults to 5.
        scoring (List[str, Callable], optional): Scoring functions (sklearn.metrics) to evaluate the model. 
            If hyperopt_type == 'bayes', the first metric will be used (maximized, by default) in the Bayesian optimization.
            Defaults to [
                "roc_auc",
                "accuracy",
                "balanced_accuracy",
                "f1",
                "recall",
                "precision",
                "average_precision",
                'jaccard',
                "neg_log_loss",
            ]
        constant_params (Union[None, dict], optional): Constant parameters, this will be always passed to the model constructor. Defaults to None.
        random_state (Union[None, int], optional): Random state. Defaults to None (no random state).
        save_path ([type], optional): Path for the hyper-parameter search results. Defaults to None (it will not save the results).
        checkpoint_filename (str, optional): Path for the checkpoint file (search object). Defaults to None.
        resume (bool, optional): If True, it will try to resume the search from the checkpoint, if any. Defaults to False.
        override (bool, optional): If True, it will force a new search. Defaults to False.
        ret_search (bool, optional): If True, it returns the search object together with the results. Defaults to False.

    Returns:
        By default:
            results (List[dict]), best_params (dict):  Returns the results and the best parameters.

        If ret_search == True:
            results (List[dict]), best_params (dict), search : Returns also the search object.
    """
    if not resume and not override and save_path is not None and os.path.exists(save_path) and ret_search is False:
        return load_pickle(save_path)

    X_train = np.asarray(X_train)
    y_train = np.asarray(y_train).flatten()

    # Instantiate the model
    model_type = get_model_type(model_type)
    ModelClass = MODEL_CLASS[model_type]
    model_arguments = deepcopy(MODEL_DEFAULT_ARGUMENTS[ModelClass])

    # Set the optimal number of threads for XGBoost
    if model_type == 'xgb':
        nb_avail_cpus = max_cpu_count()
        model_arguments['n_jobs'] = int(min(model_arguments['n_jobs'], max(1, int(nb_avail_cpus / n_splits))))

    model = ModelClass(**model_arguments)

    if space is None or isinstance(space, str):
        space, dataset = None, space
    else:
        space, dataset = space, None

    space = get_search_space_from_library(
        model_type,
        dataset,
        space=space,
        hyperopt_type=hyperopt_type,
    )

    space = add_random_state(space, model_type, random_state)
    space = add_constant_parameters(space, constant_params)

    # Cross-validation
    kfold = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    search_params = dict(
        cv=kfold,
        scoring=scoring,
        refit=False,
        **kwargs,
    )

    hyperopt_type = get_hyperopt_type(hyperopt_type)
    if hyperopt_type == 'grid':
        Search = GridSearchCV
    elif hyperopt_type == 'random':
        Search = RandomizedSearchCV
        search_params.update(dict(grid=space, ))
    elif hyperopt_type == 'bayes':
        Search = HyperOptSearchCV
        search_params.update(
            dict(
                space=space,
                checkpoint_filename=checkpoint_filename,  # It will save itself at every iteration
            )
        )
    else:
        raise ValueError('Invalid hyperopt_type.')

    # Create search object
    if resume and not override and checkpoint_filename is not None and os.path.exists(checkpoint_filename):
        search = load_pickle(checkpoint_filename)
        search.set_params(**search_params)
    else:
        logging.info('Hyper training from scatch.')
        search = Search(model, **search_params)

    # Search
    search.fit(X_train, y_train)

    # Save search checkpoint
    if checkpoint_filename is not None:
        mkdirname_ifnotexist(checkpoint_filename)
        save_pickle(search, checkpoint_filename)

    # Results
    results = get_results_from_search(search)
    best_params = get_best_params_from_search(search)

    # Save results
    if save_path is not None:
        mkdirname_ifnotexist(save_path)
        save_pickle((results, best_params), save_path)

    if ret_search:
        return results, best_params, search
    else:
        return results, best_params


def get_results_from_search(search):
    # Load hypertraining results into a DataFrame
    if isinstance(search, (GridSearchCV, RandomizedSearchCV)):
        return {k: v for k, v in search.cv_results_.items() if np.all([x not in k for x in ['split']])}
    elif isinstance(search, HyperOptSearchCV):
        return search.get_results()
    else:
        raise NotImplementedError('Unsupported search object.')


def get_best_params_from_search(search, num=1):
    if isinstance(search, HyperOptSearchCV):
        return search.get_best_params()
    else:
        raise NotImplementedError('Unsupported search object.')