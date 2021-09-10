from .iai import _IAI, _requires_iai_version, _iai_version_less_than
from .iaibase import (SupervisedLearner, ClassificationLearner,
                      RegressionLearner, SurvivalLearner, GridSearch)
import warnings as _warnings


def _process_estimators(f, propensity_type, outcome_type, *args,
                        propensity_estimator=None, outcome_estimator=None,
                        **kwargs):
    if propensity_estimator:
        lnr = propensity_estimator
        if isinstance(lnr, GridSearch):
            lnr = lnr.get_learner()
        if not isinstance(lnr, propensity_type):
            raise TypeError("`propensity_estimator` needs to be a `" +
                            str(propensity_type) + "`")
        propensity_estimator = propensity_estimator._jl_obj

    if outcome_estimator:
        lnr = outcome_estimator
        if isinstance(lnr, GridSearch):
            lnr = lnr.get_learner()
        if not isinstance(lnr, outcome_type):
            raise TypeError("`outcome_estimator` needs to be a `" +
                            outcome_type + "`")
        outcome_estimator = outcome_estimator._jl_obj

    return f(*args, propensity_estimator=propensity_estimator,
             outcome_estimator=outcome_estimator, **kwargs)


class CategoricalRewardEstimationLearner(SupervisedLearner):
    """Abstract type encompassing all learners for reward estimation with
    categorical treatments."""

    def fit_predict(self, *args, **kwargs):
        """Fit a reward estimation model and return predicted counterfactual
        rewards for each observation along with the scores of the internal
        estimators during training.

        Julia Equivalent:
        `IAI.fit_predict! <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.fit_predict!-Tuple%7BLearner%7BIAIBase.CategoricalRewardEstimationTask%7D%7D>`

        Examples
        --------

        For problems with classification or regression outcomes, fit reward
        estimation model on features `X`, treatments `treatments`, and outcomes
        `outcomes` and predict rewards for each observation.

        >>> lnr.fit_predict(X, treatments, outcomes)

        For problems with survival outcomes, fit reward estimation model on
        features `X`, treatments `treatments`, death indicator `deaths` and
        event times `times` and predict rewards for each observation.

        >>> lnr.fit_predict(X, treatments, deaths, times)

        Compatibility
        -------------
        Requires IAI version 2.0 or higher.
        """
        _requires_iai_version("2.0.0", "fit_predict")
        return _IAI.fit_predict_convert(self._jl_obj, *args, **kwargs)

    def predict(self, *args, **kwargs):
        """Return counterfactual rewards estimated by the learner for each
        observation in the supplied data.

        Julia Equivalent:
        `IAI.predict <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.predict-Tuple%7BCategoricalRewardEstimator%2CUnion%7BDataFrames.AbstractDataFrame%2C%2520AbstractArray%7Bvar%2522%23s39%2522%2C2%7D%2520where%2520var%2522%23s39%2522%253C%3AReal%7D%7D>`

        Examples
        --------

        For problems with classification or regression outcomes, predict
        rewards for each observation in the data given by `X`, `treatments` and
        `outcomes`. If using the direct method, `treatments` and `outcomes` can
        be omitted.

        >>> lnr.predict(X, treatments, outcomes)

        For problems with survival outcomes, predict rewards for each
        observation in the data given by `X`, `treatments`, `deaths` and
        `times`. If using the direct method, `treatments`, `deaths` and `times`
        can be omitted.

        >>> lnr.predict(X, treatments, deaths, times)

        Compatibility
        -------------
        Requires IAI version 2.0 or higher.
        """
        _requires_iai_version("2.0.0", "predict")
        return _IAI.predict_convert(self._jl_obj, *args, **kwargs)

    def score(self, *args, **kwargs):
        """Calculate the scores of the internal estimators in the learner on
        the supplied data.

        Returns a `dict` with the following entries:

        - `'propensity'`: the score for the propensity estimator
        - `':outcome'`: a `dict` where the keys are the possible treatments,
                        and the values are the scores of the outcome estimator
                        corresponding to each treatment

        Julia Equivalent:
        `IAI.score <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.score-Tuple%7BCategoricalRewardEstimator%2CUnion%7BDataFrames.AbstractDataFrame%2C%2520AbstractArray%7Bvar%22%23s39%22%2C2%7D%2520where%2520var%22%23s39%22%3C%3AReal%7D%2CArray%7BT%2C1%7D%2520where%2520T%2CArray%7BT%2C1%7D%2520where%2520T%7D>`

        Examples
        --------

        For problems with classification or regression outcomes, calculate the
        scores of the internal estimators using the data given by `X`,
        `treatments` and `outcomes`.

        >>> lnr.score(X, treatments, outcomes)

        For problems with survival outcomes, calculate the scores of the
        internal estimators using the data given by `X`, `treatments`,
        `deaths` and `times`.

        >>> lnr.score(X, treatments, deaths, times)

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "score")
        return _IAI.score_convert(self._jl_obj, *args, **kwargs)


class CategoricalClassificationRewardEstimator(CategoricalRewardEstimationLearner):
    """Learner for reward estimation with categorical treatments and
    classification outcomes.

    Julia Equivalent:
    `IAI.CategoricalClassificationRewardEstimator <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.CategoricalClassificationRewardEstimator>`

    Examples
    --------
    >>> iai.CategoricalClassificationRewardEstimator(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.2 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.2.0",
                              "CategoricalClassificationRewardEstimator")

        jl_obj = _process_estimators(
            _IAI.CategoricalClassificationRewardEstimator_convert,
            ClassificationLearner, ClassificationLearner, *args, **kwargs)

        super().__init__(jl_obj)


class CategoricalRegressionRewardEstimator(CategoricalRewardEstimationLearner):
    """Learner for reward estimation with categorical treatments and regression
    outcomes.

    Julia Equivalent:
    `IAI.CategoricalRegressionRewardEstimator <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.CategoricalRegressionRewardEstimator>`

    Examples
    --------
    >>> iai.CategoricalRegressionRewardEstimator(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.2 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.2.0", "CategoricalRegressionRewardEstimator")

        jl_obj = _process_estimators(
            _IAI.CategoricalRegressionRewardEstimator_convert,
            ClassificationLearner, RegressionLearner, *args, **kwargs)

        super().__init__(jl_obj)


class CategoricalSurvivalRewardEstimator(CategoricalRewardEstimationLearner):
    """Learner for reward estimation with categorical treatments and survival
    outcomes.

    Julia Equivalent:
    `IAI.CategoricalSurvivalRewardEstimator <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.CategoricalSurvivalRewardEstimator>`

    Examples
    --------
    >>> iai.CategoricalSurvivalRewardEstimator(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.2 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.2.0", "CategoricalSurvivalRewardEstimator")

        jl_obj = _process_estimators(
            _IAI.CategoricalSurvivalRewardEstimator_convert,
            ClassificationLearner, SurvivalLearner, *args, **kwargs)

        super().__init__(jl_obj)


class EqualPropensityEstimator(ClassificationLearner):
    """Learner that estimates equal propensity for all treatments.

    For use with data from randomized experiments where treatments are known to
    be randomly assigned.

    Julia Equivalent:
    `IAI.EqualPropensityEstimator <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.EqualPropensityEstimator>`

    Examples
    --------
    >>> iai.EqualPropensityEstimator(**kwargs)

    Compatibility
    -------------
    Requires IAI version 2.1 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.1.0", "EqualPropensityEstimator")
        jl_obj = _IAI.EqualPropensityEstimator_convert(*args, **kwargs)
        super().__init__(jl_obj)


class NumericRewardEstimationLearner(SupervisedLearner):
    """Abstract type encompassing all learners for reward estimation with
    numeric treatments."""

    def fit_predict(self, *args, **kwargs):
        """Fit a reward estimation model and return predicted counterfactual
        rewards for each observation under each treatment option in
        `treatment_candidates`, as well as the score of the internal outcome
        estimator.

        Julia Equivalent:
        `IAI.fit_predict! <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.fit_predict!-Tuple%7BLearner%7BIAIBase.NumericRewardEstimationTask%7D%7D>`

        Examples
        --------

        For problems with classification or regression outcomes, fit reward
        estimation model on features `X`, treatments `treatments`, and outcomes
        `outcomes` and predict rewards for each observation under each
        treatment option in `treatment_candidates`.

        >>> lnr.fit_predict(X, treatments, outcomes, treatment_candidates)

        For problems with survival outcomes, fit reward estimation model on
        features `X`, treatments `treatments`, death indicator `deaths` and
        event times `times` and predict rewards for each observation under each
        treatment option in `treatment_candidates`.

        >>> lnr.fit_predict(X, treatments, deaths, times, treatment_candidates)

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "fit_predict")
        return _IAI.fit_predict_convert(self._jl_obj, *args, **kwargs)

    def predict(self, *args, **kwargs):
        """Return counterfactual rewards estimated by the learner for each
        observation in the supplied data.

        Julia Equivalent:
        `IAI.predict <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.predict-Tuple%7BNumericRewardEstimator%2CUnion%7BDataFrames.AbstractDataFrame%2C%2520AbstractArray%7Bvar%22%23s39%22%2C2%7D%2520where%2520var%22%23s39%22%3C%3AReal%7D%2CArray%7BT%2C1%7D%2520where%2520T%7D>`

        Examples
        --------

        IAI versions 2.2 and greater: For problems with classification or
        regression outcomes, predict rewards for each observation in the data given by `X`, `treatments` and `outcomes`. If using the direct method,
        `treatments` and `outcomes` can be omitted.

        >>> lnr.predict(X, treatments, outcomes)

        IAI versions 2.2 and greater: For problems with survival outcomes,
        predict rewards for each observation in the data given by `X`,
        `treatments`, `deaths` and `times`. If using the direct method,
        `treatments`, `deaths` and `times` can be omitted.

        >>> lnr.predict(X, treatments, deaths, times)

        IAI version 2.1: Predicted reward for each observation in the data
        given by `X`, `treatments` and `outcomes` under each treatment option
        in `treatment_candidates`. If using the direct method, `treatments`,
        `deaths` and `times` can be omitted.

        >>> lnr.predict(X, treatments, outcomes, treatment_candidates)

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "predict")
        return _IAI.predict_convert(self._jl_obj, *args, **kwargs)

    def score(self, *args, **kwargs):
        """Calculate the scores of the internal estimator in the learner on
        the supplied data.

        Julia Equivalent:
        `IAI.score <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.score-Tuple%7BNumericRewardEstimator%2CUnion%7BDataFrames.AbstractDataFrame%2C%2520AbstractArray%7Bvar%22%23s39%22%2C2%7D%2520where%2520var%22%23s39%22%3C%3AReal%7D%2CArray%7BT%2C1%7D%2520where%2520T%2CArray%7BT%2C1%7D%2520where%2520T%7D>`

        On IAI versions 2.2 and greater, returns a `dict` with the following
        entries:

        - `'propensity'`: a `dict` where the keys are the treatment candidates,
                          and the values are the scores of the propensity
                          estimator corresponding to each candidate
        - `':outcome'`: a `dict` where the keys are the treatment candidates,
                        and the values are the scores of the outcome estimator
                        corresponding to each candidate

        On IAI version 2.1, returns a `float` giving the score of the outcome
        estimator.

        Examples
        --------

        For problems with classification or regression outcomes, calculate the
        scores of the internal estimators using the data given by `X`,
        `treatments` and `outcomes`.

        >>> lnr.score(X, treatments, outcomes)

        For problems with survival outcomes, calculate the scores of the
        internal estimators using the data given by `X`, `treatments`,
        `deaths` and `times`.

        >>> lnr.score(X, treatments, deaths, times)

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "score")
        return _IAI.score_convert(self._jl_obj, *args, **kwargs)

    def get_estimation_densities(self, *args, **kwargs):
        """Return the total kernel density surrounding each treatment candidate
        for the propensity/outcome estimation problems in the fitted learner.

        Julia Equivalent:
        `IAI.get_estimation_densities <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.get_estimation_densities>`

        Examples
        --------
        >>> lnr.get_estimation_densities()

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "get_estimation_densities")
        return _IAI.get_estimation_densities_convert(self._jl_obj, *args,
                                                     **kwargs)

    def tune_reward_kernel_bandwidth(self, *args, **kwargs):
        """Conduct the reward kernel bandwidth tuning procedure using the
        learner for each starting value in `input_bandwidths` and return the
        final tuned values.

        Julia Equivalent:
        `IAI.tune_reward_kernel_bandwidth <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.tune_reward_kernel_bandwidth>`

        Examples
        --------
        >>> lnr.tune_reward_kernel_bandwidth(input_bandwidths)

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "tune_reward_kernel_bandwidth")
        return _IAI.tune_reward_kernel_bandwidth_convert(self._jl_obj, *args,
                                                         **kwargs)

    def set_reward_kernel_bandwidth(self, *args, **kwargs):
        """Save the new value of `bandwidth` as the reward kernel bandwidth
        inside the learner, and return new reward predictions generated using
        this bandwidth for the original data used to train the learner.

        Julia Equivalent:
        `IAI.set_reward_kernel_bandwidth! <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.set_reward_kernel_bandwidth!>`

        Examples
        --------
        >>> lnr.set_reward_kernel_bandwidth(bandwidth)

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "set_reward_kernel_bandwidth")
        return _IAI.set_reward_kernel_bandwidth_convert(self._jl_obj, *args,
                                                        **kwargs)


class NumericClassificationRewardEstimator(NumericRewardEstimationLearner):
    """Learner for reward estimation with numeric treatments and classification
    outcomes.

    Julia Equivalent:
    `IAI.NumericClassificationRewardEstimator <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.NumericClassificationRewardEstimator>`

    Examples
    --------
    >>> iai.NumericClassificationRewardEstimator(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.2 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.2.0", "NumericClassificationRewardEstimator")

        jl_obj = _process_estimators(
            _IAI.NumericClassificationRewardEstimator_convert,
            RegressionLearner, ClassificationLearner, *args, **kwargs)

        super().__init__(jl_obj)


class NumericRegressionRewardEstimator(NumericRewardEstimationLearner):
    """Learner for reward estimation with numeric treatments and regression
    outcomes.

    Julia Equivalent:
    `IAI.NumericRegressionRewardEstimator <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.NumericRegressionRewardEstimator>`

    Examples
    --------
    >>> iai.NumericRegressionRewardEstimator(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.2 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.2.0", "NumericRegressionRewardEstimator")

        jl_obj = _process_estimators(
            _IAI.NumericRegressionRewardEstimator_convert,
            RegressionLearner, RegressionLearner, *args, **kwargs)

        super().__init__(jl_obj)


class NumericSurvivalRewardEstimator(NumericRewardEstimationLearner):
    """Learner for reward estimation with numeric treatments and survival
    outcomes.

    Julia Equivalent:
    `IAI.NumericSurvivalRewardEstimator <https://docs.interpretable.ai/v2.2.0/RewardEstimation/reference/#IAI.NumericSurvivalRewardEstimator>`

    Examples
    --------
    >>> iai.NumericSurvivalRewardEstimator(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.2 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.2.0", "NumericSurvivalRewardEstimator")

        jl_obj = _process_estimators(
            _IAI.NumericSurvivalRewardEstimator_convert,
            RegressionLearner, SurvivalLearner, *args, **kwargs)

        super().__init__(jl_obj)


def all_treatment_combinations(*args, **kwargs):
    """Return a `pandas.DataFrame` containing all treatment combinations of one
    or more treatment vectors, ready for use as `treatment_candidates` in
    `fit_predict!` or `predict`.

    Examples
    --------
    >>> iai.all_treatment_combinations(*args, **kwargs)

    Compatibility
    -------------
    Requires IAI version 2.1 or higher.
    """
    _requires_iai_version("2.1.0", "all_treatment_combinations")
    return _IAI.all_treatment_combinations_convert(*args, **kwargs)


def convert_treatments_to_numeric(*args, **kwargs):
    """Convert `treatments` from symbol/string format into numeric values.

    Examples
    --------
    >>> iai.convert_treatments_to_numeric(treatments)

    Compatibility
    -------------
    Requires IAI version 2.1 or higher.
    """
    _requires_iai_version("2.1.0", "convert_treatments_to_numeric")
    return _IAI.convert_treatments_to_numeric_convert(*args, **kwargs)


# DEPRECATED


class RewardEstimationLearner(CategoricalRewardEstimationLearner):
    """Abstract type encompassing all learners for reward estimation with
    categorical treatments.

    This class was deprecated and renamed to CategoricalRewardEstimationLearner
    in interpretableai 2.3.0. This is for consistency with the IAI v2.1.0 Julia
    release.
    """


class CategoricalRewardEstimator(CategoricalRewardEstimationLearner):
    """Learner for reward estimation with categorical treatments.

    This class was deprecated in interpretableai 2.6.0, and
    CategoricalClassificationRewardEstimator or
    CategoricalRegressionRewardEstimator should be used instead. This is for
    consistency with the IAI v2.1.0 Julia release. This deprecation is no
    longer supported as of the IAI v3 release.

    Examples
    --------
    >>> iai.CategoricalRewardEstimator(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.0, 2.1 or 2.2.
    """
    def __init__(self, *args, propensity_estimator=None,
                 outcome_estimator=None, **kwargs):
        if not _iai_version_less_than("2.3.0"):
            raise RuntimeError(
                "'CategoricalRewardEstimator' was removed in IAI v3")

        _requires_iai_version("2.0.0", "CategoricalRewardEstimator")
        _warnings.warn(
            "'CategoricalRewardEstimator' is deprecated, use " +
            "'CategoricalClassificationRewardEstimator' or " +
            "'CategoricalRegressionRewardEstimator'",
            FutureWarning
        )

        if _iai_version_less_than("2.1.0"):
            jl_obj = _IAI.RewardEstimator_convert(*args, **kwargs)
        else:
            if propensity_estimator:
                lnr = propensity_estimator
                if isinstance(lnr, GridSearch):
                    lnr = lnr.get_learner()
                if not isinstance(lnr, ClassificationLearner):
                    raise TypeError("`propensity_estimator` needs to be a " +
                                    "`ClassificationLearner`")
                propensity_estimator = propensity_estimator._jl_obj

            if outcome_estimator:
                lnr = outcome_estimator
                if isinstance(lnr, GridSearch):
                    lnr = lnr.get_learner()
                if not (isinstance(lnr, ClassificationLearner) or
                        isinstance(lnr, RegressionLearner)):
                    raise TypeError("`outcome_estimator` needs to be a " +
                                    "`ClassificationLearner` or " +
                                    "`RegressionLearner`")
                outcome_estimator = outcome_estimator._jl_obj

            jl_obj = _IAI.CategoricalRewardEstimator_convert(
                *args, propensity_estimator=propensity_estimator,
                outcome_estimator=outcome_estimator, **kwargs)

        super().__init__(jl_obj)


class RewardEstimator(CategoricalRewardEstimator, RewardEstimationLearner):
    """Learner for reward estimation with categorical treatments.

    This class was deprecated and renamed to CategoricalRewardEstimator in
    interpretableai 2.3.0. This is for consistency with the IAI v2.1.0 Julia
    release. This deprecation is no longer supported as of the IAI v3 release.

    Compatibility
    -------------
    Requires IAI version 2.2 or lower.
    """
    def __init__(self, *args, **kwargs):
        if not _iai_version_less_than("2.3.0"):
            raise RuntimeError("'RewardEstimator' was removed in IAI v3")

        _warnings.warn(
            "'RewardEstimator' is deprecated, use " +
            "'CategoricalRewardEstimator'",
            FutureWarning
        )
        super().__init__(*args, **kwargs)


class NumericRewardEstimator(NumericRewardEstimationLearner):
    """Learner for reward estimation with numeric treatments.

    This class was deprecated in interpretableai 2.6.0, and
    RegressionClassificationRewardEstimator or
    RegressionRegressionRewardEstimator should be used instead. This is for
    consistency with the IAI v2.1.0 Julia release. This deprecation is no
    longer supported as of the IAI v3 release.

    Examples
    --------
    >>> iai.NumericRewardEstimator(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.1 or 2.2.
    """
    def __init__(self, *args, outcome_estimator=None, **kwargs):
        if not _iai_version_less_than("2.3.0"):
            raise RuntimeError(
                "'NumericRewardEstimator' was removed in IAI v3")

        _requires_iai_version("2.1.0", "NumericRewardEstimator")
        _warnings.warn(
            "'NumericRewardEstimator' is deprecated, use " +
            "'NumericClassificationRewardEstimator' or " +
            "'NumericRegressionRewardEstimator'",
            FutureWarning
        )

        if outcome_estimator:
            lnr = outcome_estimator
            if isinstance(lnr, GridSearch):
                lnr = lnr.get_learner()
            if not (isinstance(lnr, ClassificationLearner) or
                    isinstance(lnr, RegressionLearner)):
                raise TypeError("`outcome_estimator` needs to be a " +
                                "`ClassificationLearner` or " +
                                "`RegressionLearner`")
            outcome_estimator = outcome_estimator._jl_obj

        jl_obj = _IAI.NumericRewardEstimator_convert(
            *args, outcome_estimator=outcome_estimator, **kwargs)
        super().__init__(jl_obj)
