from typing import Union, Iterable, ValuesView

import numpy as np
import scipy as sp

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin

from ..utils import keydefaultdict

from .madscaler import MedianAbsoluteDeviationScaler
from .quantiletransformer import EfficientQuantileTransformer

NORMALIZATION_ = ['std', 'minmax', 'mad', 'percshift']

DISTANCE_TO_NORMALIZATION = {
    'euclidean': 'std',
    'manhattan': 'mad',
    'cityblock': 'mad',
    'quantile': 'percshift',
}

NORMALIZATION_TO_NAME = {
    'percshift': 'Percentile Shift',
    'std': 'STD Deviation',
    'mad': 'MAD Deviation',
    'minmax': 'MinMax Deviation',
}


def _get_method_safe(method):
    if method is None or method in NORMALIZATION_:
        return method
    elif method in list(DISTANCE_TO_NORMALIZATION.keys()):
        return DISTANCE_TO_NORMALIZATION[method]
    else:
        raise ValueError('Invalid normalization method.')


def get_normalization_name(method):
    return NORMALIZATION_TO_NAME[_get_method_safe(method)]


class NullScaler(TransformerMixin, BaseEstimator):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        self.scale_ = np.ones(X.shape[1])
        return self

    def transform(self, X):
        return X

    def inverse_transform(self, X):
        return X


def get_transformer_class(method):
    method = _get_method_safe(method)

    if method is None:
        return NullScaler
    elif method == 'std':
        return StandardScaler
    elif method == 'minmax':
        return MinMaxScaler
    elif method == 'mad':
        return MedianAbsoluteDeviationScaler
    elif method == 'percshift':
        return EfficientQuantileTransformer  # PercentileShifterCached


class Normalizer:
    """Class to support the normalization of the features

    Raises:
        Exception: If an invalid normalization is used

    """
    NORMALIZATION = NORMALIZATION_

    def __init__(self, data: np.ndarray):
        """Constructor

        Args:
            data (pd.DataFrame): A dataframe with the features

        """
        self.data = np.asarray(data)

        self.transformers = keydefaultdict(lambda method: get_transformer_class(method)().fit(self.data))

        def single_transformer(method, f):
            return get_transformer_class(method)().fit(self.data[:, f].reshape(-1, 1))

        self.single_transformers = keydefaultdict(lambda args: single_transformer(*args))
        self.data_transformed = keydefaultdict(lambda method: self.transform(self.data, method))

        self.covs = keydefaultdict(lambda method, lib: self.__compute_covariance_matrix(self.data, method, lib))

        self.__suppress_warning = False

    def suppress_warnings(self, value=True):
        self.__suppress_warning = value

    def __compute_covariance_matrix(self, data, method, lib):
        if lib == 'np':
            return sp.linalg.inv(np.cov((self.transform(data, method=method)), rowvar=False))
        elif lib == 'tf':
            from ..tf import inv_cov as tf_inv_cov
            return tf_inv_cov(self.transform(data, method=method))
        else:
            raise ValueError('Invalid lib.')

    def transform(self, data: np.ndarray, method: str, **kwargs):
        """Normalize the data according to the "method" passed

        Args:
            data (np.ndarray): The data to be normalized (nb_samples x nb_features)
            method (str, optional): Normalization ('mad', 'std' or 'minmax'). Defaults to 'std'.

        Raises:
            ValueError: Invalid normalization

        Returns:
            np.ndarray: Normalized array
        """
        method = _get_method_safe(method)
        return self.transformers[method].transform(data)

    def inverse_transform(self, data: np.ndarray, method: str = 'std'):
        """Un-normalize the data according to the "method" passes

        Args:
            data (np.ndarray): The data to be un-normalized (nb_samples x nb_features)
            method (str, optional): Normalization ('mad', 'std' or 'minmax'). Defaults to 'std'.

        Raises:
            ValueError: Invalid normalization

        Returns:
            np.ndarray: Un-normalized array
        """
        method = _get_method_safe(method)
        return self.transformers[method].inverse_transform(data)

    def feature_deviation(self, method: str = 'std', phi: Union[float, int] = 1):
        """Get the deviation of each feature according to the normalization method

        Args:
            method (str): method (str, optional): Normalization ('mad', 'std' or 'minmax'). Defaults to 'std'.
            phi (Union[float, int]): The fraction of the STD/MAD/MINMAX. Default to 1.

        Raises:
            ValueError: Invalid normalization

        Returns:
            np.ndarray: Deviations, shape = (nb_features, )
        """
        method = _get_method_safe(method)
        transformer = self.transformers[method]
        if 'scale_' in dir(transformer):
            return transformer.scale_ * phi
        else:
            return np.ones(self.data.shape[1]) * phi

    def feature_transform(self, x: np.ndarray, f: int, method: str):
        x = np.asarray(x)
        transformer = self.get_feature_transformer(method, f)
        return transformer.transform(x.reshape(-1, 1))[:, 0]

    def shift_transform(self, X, shifts, method, **kwargs):
        transformer = self.get_transformer(method)
        if 'shift' in dir(transformer):
            return transformer.shift_transform(X, shifts=shifts, **kwargs)
        else:
            return X + shifts

    def move_transform(self, X, costs, method, **kwargs):
        transformer = self.get_transformer(method)
        assert costs.shape[0] == X.shape[1]
        return transformer.inverse_transform(transformer.transform(X) + np.tile(costs, (X.shape[0], 1)))

    def get_transformer(self, method: str):
        return self.transformers[_get_method_safe(method)]

    def get_feature_transformer(self, method: str, f: int):
        return self.single_transformers[(_get_method_safe(method), f)]

    def single_transform(self, x, *args, **kwargs):
        return self.transform(np.array([x]), *args, **kwargs)[0]

    def single_inverse_transform(self, x, *args, **kwargs):
        return self.inverse_transform(np.array([x]), *args, **kwargs)[0]

    def single_shift_transform(self, x, shift, **kwargs):
        return self.shift_transform(np.array([x]), np.array([shift]), **kwargs)[0]

    def covariance_matrix(self, data: np.ndarray, method: Union[None, str], lib='np'):
        if data is None:
            return self.covs[(method, lib)]
        else:
            return self.__compute_covariance_matrix(data, method, lib)

    def covariance_matrices(self, data: np.ndarray, methods=None, lib='np'):
        """Compute the covariance matrices

        Args:
            data (np.ndarray): The data from which to extract the covariance

        Returns:
            Dict[np.ndarray]: Dictionary (for each normalization method) of covariance matrices
        """
        # If no method is passed we compute for all of them
        if methods is None:
            methods = self.NORMALIZATION

        return {method: self.covariance_matrix(data, method, lib) for method in methods}
