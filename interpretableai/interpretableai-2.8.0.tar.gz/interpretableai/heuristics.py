from .iai import _IAI, _requires_iai_version
from .iaibase import (Learner, ClassificationLearner, RegressionLearner,
                      SurvivalLearner)


class RandomForestLearner(Learner):
    """Abstract type encompassing all random forest learners."""
    pass


class RandomForestClassifier(RandomForestLearner, ClassificationLearner):
    """Learner for training random forests for classification problems.

    Julia Equivalent:
    `IAI.RandomForestClassifier <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.RandomForestClassifier>`

    Examples
    --------
    >>> iai.RandomForestClassifier(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.1 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.1.0", "RandomForestClassifier")
        jl_obj = _IAI.RandomForestClassifier_convert(*args, **kwargs)
        super().__init__(jl_obj)


class RandomForestRegressor(RandomForestLearner, RegressionLearner):
    """Learner for training random forests for regression problems.

    Julia Equivalent:
    `IAI.RandomForestRegressor <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.RandomForestRegressor>`

    Examples
    --------
    >>> iai.RandomForestRegressor(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.1 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.1.0", "RandomForestRegressor")
        jl_obj = _IAI.RandomForestRegressor_convert(*args, **kwargs)
        super().__init__(jl_obj)


class RandomForestSurvivalLearner(RandomForestLearner, SurvivalLearner):
    """Learner for training random forests for survival problems.

    Julia Equivalent:
    `IAI.RandomForestSurvivalLearner <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.RandomForestSurvivalLearner>`

    Examples
    --------
    >>> iai.RandomForestSurvivalLearner(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.2 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.2.0", "RandomForestSurvivalLearner")
        jl_obj = _IAI.RandomForestSurvivalLearner_convert(*args, **kwargs)
        super().__init__(jl_obj)


class XGBoostLearner(Learner):
    """Abstract type encompassing all XGBoost learners."""

    def write_booster(self, filename, **kwargs):
        """Write the internal booster saved in the learner to `filename`.

        Julia Equivalent:
        `IAI.write_booster <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.write_booster>`

        Examples
        --------
        >>> lnr.write_booster(filename)

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "write_booster")
        return _IAI.write_booster_convert(filename, self._jl_obj)

    def predict_shap(self, *args, **kwargs):
        """Calculate SHAP values for all points in the features `X` using `lnr`.

        Julia Equivalent:
        `IAI.predict_shap <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.predict_shap>`

        Examples
        --------
        >>> lnr.predict_shap(X)

        Compatibility
        -------------
        Requires IAI version 2.2 or higher.
        """
        _requires_iai_version("2.2.0", "predict_shap")
        return _IAI.predict_shap_convert(self._jl_obj, *args, **kwargs)


class XGBoostClassifier(XGBoostLearner, ClassificationLearner):
    """Learner for training XGBoost models for classification problems.

    Julia Equivalent:
    `IAI.XGBoostClassifier <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.XGBoostClassifier>`

    Examples
    --------
    >>> iai.XGBoostClassifier(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.1 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.1.0", "XGBoostClassifier")
        jl_obj = _IAI.XGBoostClassifier_convert(*args, **kwargs)
        super().__init__(jl_obj)


class XGBoostRegressor(XGBoostLearner, RegressionLearner):
    """Learner for training XGBoost models for regression problems.

    Julia Equivalent:
    `IAI.XGBoostRegressor <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.XGBoostRegressor>`

    Examples
    --------
    >>> iai.XGBoostRegressor(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.1 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.1.0", "XGBoostRegressor")
        jl_obj = _IAI.XGBoostRegressor_convert(*args, **kwargs)
        super().__init__(jl_obj)


class XGBoostSurvivalLearner(XGBoostLearner, SurvivalLearner):
    """Learner for training XGBoost models for survival problems.

    Julia Equivalent:
    `IAI.XGBoostSurvivalLearner <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.XGBoostSurvivalLearner>`

    Examples
    --------
    >>> iai.XGBoostSurvivalLearner(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.2 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.2.0", "XGBoostSurvivalLearner")
        jl_obj = _IAI.XGBoostSurvivalLearner_convert(*args, **kwargs)
        super().__init__(jl_obj)


class GLMNetLearner(Learner):
    """Abstract type encompassing all GLMNet learners."""

    def get_num_fits(self):
        """Return the number of fits along the path in the trained learner.

        Julia Equivalent:
        `IAI.get_num_fits <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.get_num_fits>`

        Examples
        --------
        >>> lnr.get_num_fits()

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "get_num_fits")
        return _IAI.get_num_fits_convert(self._jl_obj)

    def get_prediction_constant(self, *args, **kwargs):
        """Return the constant term in the prediction in the trained learner.

        Julia Equivalent:
        `IAI.get_prediction_constant <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.get_prediction_constant>`

        Examples
        --------
        Return the constant term in the prediction made by the best fit on the
        path in the learner.

        >>> lnr.get_prediction_constant()

        Return the constant term in the prediction made by the fit at
        `fit_index` on the path in the learner.

        >>> lnr.get_prediction_constant(fit_index)

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "get_prediction_constant")
        return _IAI.get_prediction_constant_convert(self._jl_obj, *args,
                                                    **kwargs)

    def get_prediction_weights(self, *args, **kwargs):
        """Return the weights for numeric and categoric features used for
        prediction in the trained learner.

        Julia Equivalent:
        `IAI.get_prediction_weights <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.get_prediction_weights>`

        Examples
        --------
        Return the weights for each feature in the prediction made by the best
        fit on the path in the learner.

        >>> lnr.get_prediction_weights()

        Return the weights for each feature in the prediction made by the fit
        at `fit_index` on the path in the learner.

        >>> lnr.get_prediction_weights(fit_index)

        Compatibility
        -------------
        Requires IAI version 2.1 or higher.
        """
        _requires_iai_version("2.1.0", "get_prediction_weights")
        return _IAI.get_prediction_weights_convert(self._jl_obj, *args,
                                                   **kwargs)


class GLMNetCVLearner(GLMNetLearner):
    """Abstract type encompassing all GLMNet learners using
    cross-validation."""
    pass


class GLMNetCVRegressor(GLMNetCVLearner, RegressionLearner):
    """Learner for training GLMNet models for regression problems with
    cross-validation.

    Julia Equivalent:
    `IAI.GLMNetCVRegressor <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.GLMNetCVRegressor>`

    Examples
    --------
    >>> iai.GLMNetCVRegressor(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.1 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.1.0", "GLMNetCVRegressor")
        jl_obj = _IAI.GLMNetCVRegressor_convert(*args, **kwargs)
        super().__init__(jl_obj)


class GLMNetCVClassifier(GLMNetCVLearner, ClassificationLearner):
    """Learner for training GLMNet models for classification problems with
    cross-validation.

    Julia Equivalent:
    `IAI.GLMNetCVClassifier <https://docs.interpretable.ai/v2.2.0/Heuristics/reference/#IAI.GLMNetCVClassifier>`

    Examples
    --------
    >>> iai.GLMNetCVClassifier(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 2.3 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("2.3.0", "GLMNetCVClassifier")
        jl_obj = _IAI.GLMNetCVClassifier_convert(*args, **kwargs)
        super().__init__(jl_obj)
