import datetime
import warnings
import logging
import multiprocessing

import numpy as np
import pandas as pd

from ._hyperopt_monkeypatch import *
from hyperopt import (tpe, fmin, Trials)

from sklearn.base import clone
# from sklearn.model_selection._validation import _fit_and_score
from sklearn.metrics._scorer import _check_multimetric_scoring, _MultimetricScorer
from sklearn.model_selection import StratifiedKFold

from joblib import delayed, Parallel

from emutils.utils import save_pickle, mkdirname_ifnotexist
from emutils.parallel import max_cpu_count


class DummyEnvironment:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self, *args, **kwargs):
        return None

    def __exit__(self, *args, **kwargs):
        pass


def _base_fit_and_score(estimator, parameters, X, y, train, val, scorer):
    # Set parameters
    estimator.set_params(**parameters)

    # Fit estimator with training set
    estimator.fit(X[train], y[train])

    # Evaluate on test set
    return scorer(estimator, X[val], y[val])


class HyperOptSearchCV:
    def __init__(
        self,
        model,
        space,
        scoring,
        opt_scoring=None,
        cv=None,
        n_iter=100,
        random_state=2020,
        maximize=True,
        refit=False,
        n_jobs=-1,
        verbose=2,
        checkpoint_filename=None
    ):
        self.estimator = model
        self.cv = cv
        self.n_iter = n_iter
        self.space = space
        self.random_state = random_state
        self.maximize = maximize
        self.verbose = verbose
        self.checkpoint_filename = checkpoint_filename

        if refit is not False:
            raise NotImplementedError('refit is not implemented.')

        # Cross validation initialization
        if self.cv is None:
            self.cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)

        # Scorer
        scorer = _check_multimetric_scoring(self.estimator, scoring)

        # IF scorer is a tuple (older versions of scikit-learn), we take only the first element
        if isinstance(scorer, tuple):
            scorer = scorer[0]  # This is a dict of scorers

        # score will be a dict
        # name of scoring function : scorer

        # Scorer to use for evaluation (of the Bayesian Search)
        if opt_scoring is None:
            opt_scoring = list(scorer.keys())[0]  # Get the first one by default
            logging.warning(f"No scoring function specified for evaluation. Using the first metric ({opt_scoring}).")
        assert opt_scoring in scorer

        # Make it efficient
        scorer = _MultimetricScorer(**scorer)  # This is a single function returning a dict (with the metrics)

        self.scorer = scorer
        self.opt_score = opt_scoring

        logging.info(f"Using '{self.opt_score}' as scorer for the hypertraining")

        self.cv_results_ = []
        self.best_params = None

        self.trials = Trials()

        assert n_jobs > 0 or n_jobs == -1, 'Invalid number of jobs.'

        # -1 means use all available
        if n_jobs == -1:
            n_jobs = max_cpu_count()

        # The maximum number of jobs is the number of cv splits
        n_jobs = int(min(n_jobs, self.cv.get_n_splits()))

        self.n_jobs = n_jobs

        # Log the parallelism settings
        logging.info(f'HyperOptSearchCV __init__: Search is running with {self.n_jobs} jobs.')
        if 'n_jobs' in dir(self.estimator):
            logging.info(f'HyperOptSearchCV __init__: Estimator is running with {self.estimator.n_jobs} jobs.')

    def _fit_and_score(self, X, y, parameters, pool):
        cv_splits = list(self.cv.split(X, y))

        if pool is None:
            scores = []
            for train, val in cv_splits:
                scores.append(_base_fit_and_score(clone(self.estimator), parameters, X, y, train, val, self.scorer))
        else:
            scores = pool(
                delayed(_base_fit_and_score)(clone(self.estimator), parameters, X, y, train, val, self.scorer)
                for train, val in cv_splits
            )

        # Average
        mean_score = {}
        for key in scores[0].keys():
            mean_score[key] = sum(d[key] for d in scores) / len(scores)
        return mean_score

    def fit(self, X, y):
        if self.n_jobs > 1:
            Environment = Parallel
        else:
            # Will ignore all arguments and return None
            Environment = DummyEnvironment

        with Environment(n_jobs=self.n_jobs) as pool:

            def optimize(params):
                if self.checkpoint_filename is not None:
                    save_pickle(self, self.checkpoint_filename)
                if self.verbose >= 2:
                    logging.info(f'Training {params}')
                try:
                    score = self._fit_and_score(X, y, params, pool)
                except:
                    warnings.warn('This hyper-train combination failed.')
                    return 0.0

                record = {
                    **params,
                    **score,
                    **{
                        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    },
                }
                self.cv_results_.append(record)
                if self.verbose >= 2:
                    logging.info(f'Trained. {score}')

                if self.maximize:
                    return -score[self.opt_score]
                else:
                    return score[self.opt_score]

            return fmin(
                optimize,
                space=self.space,
                algo=tpe.suggest,
                max_evals=self.n_iter,
                trials=self.trials,
                rstate=np.random.RandomState(seed=self.random_state),
                verbose=self.verbose,
            )

    def set_params(self, **params):
        if 'n_iter' in params:
            self.n_iter = params['n_iter']

    def get_best_params(self, num=1, sort_by=None, ascending=None):
        # What do we return? Only parameters (no scores)
        params_names = list(self.space)
        sort_by = [self.opt_score] if sort_by is None else sort_by
        ascending = (not self.maximize) if ascending is None else ascending

        # Get the bests
        df = pd.DataFrame(self.cv_results_).sort_values(sort_by, ascending=False).head(num)[params_names]

        # DataFrame to list of dicts
        # NOTE: using to_dict('records') mess up the casting of the parameters
        lists = df.to_dict('list')
        best_params = [dict(zip(params_names, [lists[k][i] for k in params_names])) for i in range(len(df))]

        # Return the bests
        if num == 1:
            return best_params[0]
        else:
            return best_params

    def get_results(self):
        return self.cv_results_
