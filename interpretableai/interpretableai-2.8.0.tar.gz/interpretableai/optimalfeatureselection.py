from .iai import _IAI, _requires_iai_version
from .iaibase import (SupervisedLearner, ClassificationLearner,
                      RegressionLearner)


class OptimalFeatureSelectionLearner(SupervisedLearner):
    """Abstract type encompassing all Optimal Feature Selection learners."""

    def get_prediction_constant(self):
        """Return the constant term in the prediction in the trained learner.

        Julia Equivalent:
        `IAI.get_prediction_constant <https://docs.interpretable.ai/v2.2.0/OptimalFeatureSelection/reference/#IAI.get_prediction_constant>`

        Examples
        --------
        >>> lnr.get_prediction_constant()

        Compatibility
        -------------
        Requires IAI version 1.1 or higher.
        """
        _requires_iai_version("1.1.0", "get_prediction_constant")
        return _IAI.get_prediction_constant_convert(self._jl_obj)

    def get_prediction_weights(self):
        """Return the weights for numeric and categoric features used for
        prediction in the trained learner.

        Julia Equivalent:
        `IAI.get_prediction_weights <https://docs.interpretable.ai/v2.2.0/OptimalFeatureSelection/reference/#IAI.get_prediction_weights>`

        Examples
        --------
        >>> lnr.get_prediction_weights()

        Compatibility
        -------------
        Requires IAI version 1.1 or higher.
        """
        _requires_iai_version("1.1.0", "get_prediction_weights")
        return _IAI.get_prediction_weights_convert(self._jl_obj)


class OptimalFeatureSelectionClassifier(OptimalFeatureSelectionLearner, ClassificationLearner):
    """Learner for conducting Optimal Feature Selection on classification
    problems.

    Julia Equivalent:
    `IAI.OptimalFeatureSelectionClassifier <https://docs.interpretable.ai/v2.2.0/OptimalFeatureSelection/reference/#IAI.OptimalFeatureSelectionClassifier>`

    Examples
    --------
    >>> iai.OptimalFeatureSelectionClassifier(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 1.1 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("1.1.0", "OptimalFeatureSelectionClassifier")
        jl_obj = _IAI.OptimalFeatureSelectionClassifier_convert(*args, **kwargs)
        super().__init__(jl_obj)


class OptimalFeatureSelectionRegressor(OptimalFeatureSelectionLearner, RegressionLearner):
    """Learner for conducting Optimal Feature Selection on regression problems.

    Julia Equivalent:
    `IAI.OptimalFeatureSelectionRegressor <https://docs.interpretable.ai/v2.2.0/OptimalFeatureSelection/reference/#IAI.OptimalFeatureSelectionRegressor>`

    Examples
    --------
    >>> iai.OptimalFeatureSelectionRegressor(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.

    Compatibility
    -------------
    Requires IAI version 1.1 or higher.
    """
    def __init__(self, *args, **kwargs):
        _requires_iai_version("1.1.0", "OptimalFeatureSelectionRegressor")
        jl_obj = _IAI.OptimalFeatureSelectionRegressor_convert(*args, **kwargs)
        super().__init__(jl_obj)
