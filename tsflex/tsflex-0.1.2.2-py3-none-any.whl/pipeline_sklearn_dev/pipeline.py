"""Pipeline class that wraps sklearn.pipeline."""

__author__ = "Jeroen Van Der Donckt"

import imblearn
import sklearn
import pandas as pd
import numpy as np

from sklearn.utils.validation import check_memory

from sklearn.utils.metaestimators import if_delegate_has_method

from .SegmenterMixin import SegmenterMixin
from ..processing import SKSeriesPipeline
from ..features import SKFeatureCollection
from .dataframe_oprator import to_dataframe_operator

def make_pipeline(steps, memory=None, verbose=False):
        """Create a pipeline."""        
        # Wrap the steps of the pipeline into a DataFrameOperator if necessary
        def wrap_step(step):
            # It is not necessary to wrap SKSeriesPipeline or SKFeatureCollection as
            # these transformers return a dataframe by default :)
            if (
                isinstance(step[1], SKSeriesPipeline) or 
                isinstance(step[1], SKFeatureCollection)
            ):
                return step
            return (step[0], to_dataframe_operator(step[1]))
        steps = [wrap_step(step) for step in steps]
        return Pipeline(steps, memory=memory, verbose=verbose)


class Pipeline(sklearn.pipeline.Pipeline):

    def _validate_steps(self):
        # TODO
        return True

    def _apply_transformers(self, X: pd.DataFrame, y: np.ndarray = None):
        Xt = X
        yt = y
        for _, transform in self.steps[:-1]:
            if transform is None:
                continue
            if hasattr(transform, "segment"):
                segmenter = transform
                Xt, yt = segmenter.segment(Xt, yt)
            elif hasattr(transform, "fit_sample"):
                pass
            else:
               Xt = transform.transform(Xt)
        return Xt, yt

    def _fit(self, X, y=None, **fit_params_steps):
        # shallow copy of steps - this should really be steps_
        self.steps = list(self.steps)
        self._validate_steps()
        # Setup the memory
        memory = check_memory(self.memory)

        fit_transform_one_cached = memory.cache(_fit_transform_one)
        fit_sample_one_cached = memory.cache(_fit_sample_one)

        for (step_idx, name, transformer) in self._iter(
            with_final=False, filter_passthrough=False
        ):
            print(name)
            if transformer is None or transformer == "passthrough":
                continue

            if hasattr(memory, "location"):
                # joblib >= 0.12
                if memory.location is None:
                    # we do not clone when caching is disabled to
                    # preserve backward compatibility
                    cloned_transformer = transformer
                else:
                    cloned_transformer = clone(transformer)
            elif hasattr(memory, "cachedir"):
                # joblib < 0.11
                if memory.cachedir is None:
                    # we do not clone when caching is disabled to
                    # preserve backward compatibility
                    cloned_transformer = transformer
                else:
                    cloned_transformer = clone(transformer)
            else:
                cloned_transformer = clone(transformer)

            if (hasattr(cloned_transformer, "transform") or
                    hasattr(cloned_transformer, "fit_transform")):
                X, fitted_transformer = fit_transform_one_cached(
                    cloned_transformer, X, y, None,
                    **fit_params_steps[name])
            elif hasattr(cloned_transformer, "segment"):
                X, y, fitted_transformer = fit_sample_one_cached(
                    cloned_transformer, X, y,
                    **fit_params_steps[name])

            # Replace the transformer of the step with the fitted
            # transformer. This is necessary when loading the transformer
            # from the cache.
            self.steps[step_idx] = (name, fitted_transformer)
        return X, y

    def fit(self, X, y=None, **fit_params):
        """Fit the model
        Fit all the transforms/samplers one after the other and
        transform/sample the data, then fit the transformed/sampled
        data using the final estimator.
        Parameters
        ----------
        X : iterable
            Training data. Must fulfill input requirements of first step of the
            pipeline.
        y : iterable, default=None
            Training targets. Must fulfill label requirements for all steps of
            the pipeline.
        **fit_params : dict of string -> object
            Parameters passed to the ``fit`` method of each step, where
            each parameter name is prefixed such that parameter ``p`` for step
            ``s`` has key ``s__p``.
        Returns
        -------
        self : Pipeline
            This estimator
        """
        fit_params_steps = self._check_fit_params(**fit_params)
        Xt, yt = self._fit(X, y, **fit_params_steps)
        if self._final_estimator is not None and self._final_estimator != "passthrough":
            fit_params_last_step = fit_params_steps[self.steps[-1][0]]
            self._final_estimator.fit(Xt, yt, **fit_params_last_step)
        
        return self

    @if_delegate_has_method(delegate='_final_estimator')
    def predict(self, X):
        """Apply transformers/samplers to the data, and predict with the final
        estimator
        Parameters
        ----------
        X : iterable
            Data to predict on. Must fulfill input requirements of first step
            of the pipeline.
        Returns
        -------
        y_pred : array-like
        """
        Xt, _ = self._apply_transformers(X)
        return self.steps[-1][-1].predict(Xt)

    @if_delegate_has_method(delegate='_final_estimator')
    def predict_proba(self, X):
        """Apply transformers/samplers, and predict_proba of the final
        estimator
        Parameters
        ----------
        X : iterable
            Data to predict on. Must fulfill input requirements of first step
            of the pipeline.
        Returns
        -------
        y_proba : array-like, shape = [n_samples, n_classes]
        """
        Xt, _ = self._apply_transformers(X)
        return self.steps[-1][-1].predict_proba(Xt)

    @if_delegate_has_method(delegate='_final_estimator')
    def score(self, X, y=None, sample_weight=None):
        """Apply transformers/samplers, and score with the final estimator
        Parameters
        ----------
        X : iterable
            Data to predict on. Must fulfill input requirements of first step
            of the pipeline.
        y : iterable, default=None
            Targets used for scoring. Must fulfill label requirements for all
            steps of the pipeline.
        sample_weight : array-like, default=None
            If not None, this argument is passed as ``sample_weight`` keyword
            argument to the ``score`` method of the final estimator.
        Returns
        -------
        score : float
        """
        Xt, yt = self._apply_transformers(X, y)
        score_params = {}
        if sample_weight is not None:
            score_params['sample_weight'] = sample_weight
        return self.steps[-1][-1].score(Xt, yt, **score_params)


# RECHTSTREEKS GEKOPIEERD
def _fit_transform_one(
    transformer, X, y, weight, message_clsname="", message=None, **fit_params
):
    """
    Fits ``transformer`` to ``X`` and ``y``. The transformed result is returned
    with the fitted transformer. If ``weight`` is not ``None``, the result will
    be multiplied by ``weight``.
    """
    if hasattr(transformer, "fit_transform"):
        res = transformer.fit_transform(X, y, **fit_params)
    else:
        res = transformer.fit(X, y, **fit_params).transform(X)

    if weight is None:
        return res, transformer
    return res * weight, transformer

def _fit_sample_one(sampler, X, y, **fit_params):
    X_res, y_res = sampler.segment(X, y)

    return X_res, y_res, sampler

    # def _validate_steps(self):
    #     names, estimators = zip(*self.steps)

    #     # validate names
    #     self._validate_names(names)

    #     # validate estimators
    #     transformers = estimators[:-1]
    #     estimator = estimators[-1]

    #     for t in transformers:
    #         if t is None:
    #             continue
    #         if (not (hasattr(t, "fit") or
    #                  hasattr(t, "fit_transform") or
    #                  hasattr(t, "fit_sample")) or
    #             not (hasattr(t, "transform") or
    #                  hasattr(t, "sample"))):
    #             raise TypeError(
    #                 "All intermediate steps of the chain should "
    #                 "be estimators that implement fit and transform or sample "
    #                 "(but not both) '%s' (type %s) doesn't)" % (t, type(t)))

    #         # if ((hasattr(t, "fit_sample") and
    #         #      hasattr(t, "fit_transform")) or
    #         #     (hasattr(t, "sample") and
    #         #      hasattr(t, "transform"))):
    #         #     raise TypeError(
    #         #         "All intermediate steps of the chain should "
    #         #         "be estimators that implement fit and transform or sample."
    #         #         " '%s' implements both)" % (t))

    #         if isinstance(t, Pipeline):
    #             raise TypeError(
    #                 "All intermediate steps of the chain should not be"
    #                 " Pipelines")

    #     # We allow last estimator to be None as an identity transformation
    #     if estimator is not None and not hasattr(estimator, "fit"):
    #         raise TypeError("Last step of Pipeline should implement fit. "
    #                         "'%s' (type %s) doesn't")


# class Pipeline(Pipeline):

#     def __init__(self, steps, memory=None, verbose=False):
#         """Create a pipeline."""        
#         # Wrap the steps of the pipeline into a DataFrameOperator if necessary
#         def wrap_step(step):
#             # It is not necessary to wrap SKSeriesPipeline or SKFeatureCollection as
#             # these transformers return a dataframe by default :)
#             if (
#                 isinstance(step[1], SKSeriesPipeline) or 
#                 isinstance(step[1], SKFeatureCollection)
#             ):
#                 return step
#             return (step[0], to_dataframe_operator(step[1]))
#         steps = [wrap_step(step) for step in steps]
#         super().__init__(steps, memory=memory, verbose=verbose)
