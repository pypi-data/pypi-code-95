import logging
import json
import os
import time
import random
import multiprocessing

import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.base import clone

from emutils.utils import save_pickle, load_pickle
from emutils.utils import NumpyJSONEncoder
from emutils.parallel import max_cpu_count

from xgboost import XGBClassifier
from xgboost import Booster
from .wrappers import XGBClassifierSKLWrapper

__all__ = [
    'train_model',
    'train_xgb',
]


def _parse_param_and_delete(params, name, default):
    if name in params:
        value = params[name]
        del params[name]
    else:
        value = default
    return params, value


def _parse_param_and_keep(params, name, default):
    if name not in params:
        params[name] = default
    return params


def train_sklearn(Classifier, X, y, save_path=None, params={}):
    X = np.asarray(X)
    y = np.asarray(y).flatten()

    model = Classifier(**params)
    model.fit(X, y.flatten())
    if save_path is not None:
        save_pickle(model, save_path)

    return model


def train_decision_tree(*args, **kwargs):
    return train_sklearn(DecisionTreeClassifier, *args, **kwargs)


def train_adoboost(*args, **kwargs):
    return train_sklearn(AdaBoostClassifier, *args, **kwargs)


def train_rf(*args, **kwargs):
    return train_sklearn(RandomForestClassifier, *args, **kwargs)


def train_xgb(X, y, params, save_path=None, save_path_booster=None):

    # the threshold is not handled by XGB interface
    params, binary_threshold = _parse_param_and_delete(params, 'binary_threshold', .5)

    # n_jobs is handled by XGB SKL interface
    params = _parse_param_and_keep(params, 'n_jobs', max_cpu_count())

    X = np.asarray(X)
    y = np.asarray(y).flatten()

    if not tuple(np.sort(np.unique(y))) == (0, 1):
        raise NotImplementedError('XGB Wrapper currently only support biinary classification.')

    # Fit the model
    model = XGBClassifier(use_label_encoder=False)
    model = clone(model)
    model.set_params(**params)

    logging.info('Training...')
    model.fit(
        X,
        y,
        # early_stopping_rounds=10,
        verbose=True,
    )
    # Save and re-load (feature-agnostic model)
    temp_file = f'temp-{time.time()}-{random.random()}.bin'
    model.get_booster().save_model(temp_file)
    booster = Booster(model_file=temp_file)
    os.remove(temp_file)

    # Wrap
    model = XGBClassifierSKLWrapper(booster, features=X.shape[1], threshold=binary_threshold)

    # Save
    if save_path is not None:
        save_pickle(model, save_path)
    if save_path_booster is not None:
        save_pickle(model.get_booster(), save_path_booster)
    return model


def train_model(
    X,
    y,
    model_type,
    model_filename,
    params_filename,
    params=dict(),
    override=False,
):
    if model_filename is not None:
        logging.warning('No model_filename passed. The model (binary) will not be saved.')
    if params_filename is not None:
        logging.warning('No params_fileanme passed. The model params (JSON) will not be saved.')

    if not override and model_filename is not None:
        try:
            return load_pickle(model_filename)
        except:
            logging.info('Training model from scratch.')

    print(params)

    # Train
    if model_type == 'dt':
        model = train_decision_tree(X, y, save_path=model_filename, **params)
    elif model_type == 'ada':
        model = train_adoboost(X, y, save_path=model_filename, **params)
    elif model_type == 'rf':
        model = train_rf(X, y, save_path=model_filename, **params)
    elif model_type == 'xgb':
        model = train_xgb(
            X,
            y,
            params=dict(params),
            save_path=model_filename,
        )
    else:
        raise ValueError('Invalid model type!')

    # Save parameters used for training
    if params_filename is not None:
        with open(params_filename, "w") as outfile:
            json.dump(params, outfile, cls=NumpyJSONEncoder)

    return model