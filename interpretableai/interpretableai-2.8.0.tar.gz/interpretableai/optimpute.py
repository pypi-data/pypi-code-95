from .iai import _IAI, _Main
from .iaibase import UnsupervisedLearner


def impute(*args, **kwargs):
    """Impute the missing values in `X` using either a specified `method` or
    through grid search validation.

    Julia Equivalent:
    `IAI.impute <https://docs.interpretable.ai/v2.2.0/OptImpute/reference/#IAI.impute>`

    Examples
    --------
    >>> iai.impute(X, *args, **kwargs)

    Parameters
    ----------
    Refer to the Julia documentation for available parameters.
    """
    return _IAI.impute_convert(*args, **kwargs)


def impute_cv(*args, **kwargs):
    """Impute the missing values in `X` using cross validation.

    Julia Equivalent:
    `IAI.impute_cv <https://docs.interpretable.ai/v2.2.0/OptImpute/reference/#IAI.impute_cv>`

    Examples
    --------
    >>> iai.impute_cv(X, *args, **kwargs)

    Parameters
    ----------
    Refer to the Julia documentation for available parameters.
    """
    return _IAI.impute_cv_convert(*args, **kwargs)


class ImputationLearner(UnsupervisedLearner):
    """Abstract type containing all imputation learners.

    Julia Equivalent:
    `IAI.ImputationLearner <https://docs.interpretable.ai/v2.2.0/OptImpute/reference/#IAI.ImputationLearner>`

    Examples
    --------
    >>> iai.ImputationLearner(method='opt_knn', **kwargs)

    Parameters
    ----------
    Can be used to construct instances of imputation learners using the
    `method` keyword argument.

    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        # Check whether it's an internal `__init__` call with `jl_obj` or
        # a user calling `ImputationLearner()`
        if (len(args) == 1 and len(kwargs) == 0 and
                _Main.isa(args[0], _IAI.ImputationLearner)):
            jl_obj = args[0]
        else:
            jl_obj = _IAI.ImputationLearner_convert(*args, **kwargs)
        super().__init__(jl_obj)

    def fit_transform(self, *args, **kwargs):
        """Fit the imputation learner using the training data `X` and impute the
        missing values in the training data.

        Similar to calling
        `fit <https://docs.interpretable.ai/v2.2.0/IAI-Python/reference/#fit-Tuple%7BLearner%7D>`
        followed by
        `transform <https://docs.interpretable.ai/v2.2.0/IAI-Python/reference/#transform%7BImputationLearner%7D>`
        .

        Julia Equivalent:
        `IAI.fit_transform! <https://docs.interpretable.ai/v2.2.0/IAIBase/reference/#IAI.fit_transform!>`

        Examples
        --------
        >>> lnr.fit_transform(X, **kwargs)

        Parameters
        ----------
        Refer to the documentation on
        `data preparation <https://docs.interpretable.ai/v2.2.0/IAI-Python/data/#Python-Data-Preparation-Guide-1>`
        for information on how to format and supply the data.
        """
        return _IAI.fit_transform_convert(self._jl_obj, *args, **kwargs)

    def transform(self, *args, **kwargs):
        """Impute missing values in `X` using the fitted imputation model in
        `lnr`.

        Julia Equivalent:
        `IAI.transform <https://docs.interpretable.ai/v2.2.0/IAIBase/reference/#IAI.transform>`

        Examples
        --------
        >>> lnr.transform(X)

        Parameters
        ----------
        Refer to the documentation on
        `data preparation <https://docs.interpretable.ai/v2.2.0/IAI-Python/data/#Python-Data-Preparation-Guide-1>`
        for information on how to format and supply the data.
        """
        return _IAI.transform_convert(self._jl_obj, *args, **kwargs)


class OptKNNImputationLearner(ImputationLearner):
    """Learner for conducting optimal k-NN imputation.

    Julia Equivalent:
    `IAI.OptKNNImputationLearner <https://docs.interpretable.ai/v2.2.0/OptImpute/reference/#IAI.OptKNNImputationLearner>`

    Examples
    --------
    >>> iai.OptKNNImputationLearner(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.OptKNNImputationLearner_convert(*args, **kwargs)
        super().__init__(jl_obj)


class OptSVMImputationLearner(ImputationLearner):
    """Learner for conducting optimal SVM imputation.

    Julia Equivalent:
    `IAI.OptSVMImputationLearner <https://docs.interpretable.ai/v2.2.0/OptImpute/reference/#IAI.OptSVMImputationLearner>`

    Examples
    --------
    >>> iai.OptSVMImputationLearner(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.OptSVMImputationLearner_convert(*args, **kwargs)
        super().__init__(jl_obj)


class OptTreeImputationLearner(ImputationLearner):
    """Learner for conducting optimal tree-based imputation.

    Julia Equivalent:
    `IAI.OptTreeImputationLearner <https://docs.interpretable.ai/v2.2.0/OptImpute/reference/#IAI.OptTreeImputationLearner>`

    Examples
    --------
    >>> iai.OptTreeImputationLearner(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.OptTreeImputationLearner_convert(*args, **kwargs)
        super().__init__(jl_obj)


class SingleKNNImputationLearner(ImputationLearner):
    """Learner for conducting heuristic k-NN imputation.

    Julia Equivalent:
    `IAI.SingleKNNImputationLearner <https://docs.interpretable.ai/v2.2.0/OptImpute/reference/#IAI.SingleKNNImputationLearner>`

    Examples
    --------
    >>> iai.SingleKNNImputationLearner(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.SingleKNNImputationLearner_convert(*args, **kwargs)
        super().__init__(jl_obj)


class MeanImputationLearner(ImputationLearner):
    """Learner for conducting mean imputation.

    Julia Equivalent:
    `IAI.MeanImputationLearnerer <https://docs.interpretable.ai/v2.2.0/OptImpute/reference/#IAI.MeanImputationLearner>`

    Examples
    --------
    >>> iai.MeanImputationLearner(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.MeanImputationLearner_convert(*args, **kwargs)
        super().__init__(jl_obj)


class RandImputationLearner(ImputationLearner):
    """Learner for conducting random imputation.

    Julia Equivalent:
    `IAI.RandImputationLearnerer <https://docs.interpretable.ai/v2.2.0/OptImpute/reference/#IAI.RandImputationLearner>`

    Examples
    --------
    >>> iai.RandImputationLearner(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.RandImputationLearner_convert(*args, **kwargs)
        super().__init__(jl_obj)
