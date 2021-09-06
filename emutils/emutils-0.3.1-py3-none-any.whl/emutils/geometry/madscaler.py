import numpy as np
from scipy import sparse
from scipy import stats
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import (check_is_fitted, FLOAT_DTYPES)
from sklearn.utils.sparsefuncs import inplace_column_scale
from sklearn.utils import check_array


class MedianAbsoluteDeviationScaler(TransformerMixin, BaseEstimator):
    """


        Based on sklearn StandardScaler and RobustScaler
    """
    def __init__(self, *, copy=True, with_centering=True, with_scaling=True):
        self.with_centering = with_centering
        self.with_scaling = with_scaling
        self.copy = copy

    def fit(self, X, y=None):

        X = self._validate_data(
            X, accept_sparse='csc', estimator=self, dtype=FLOAT_DTYPES, force_all_finite='allow-nan'
        )

        if self.with_centering:
            if sparse.issparse(X):
                raise ValueError(
                    "Cannot center sparse matrices: use `with_centering=False`"
                    " instead. See docstring for motivation and alternatives."
                )
            self.center_ = np.nanmedian(X, axis=0)
        else:
            self.center_ = None

        if self.with_scaling:
            self.scale_ = stats.median_absolute_deviation(X, axis=0)
        else:
            self.scale_ = None

        return self

    def transform(self, X):
        """Center and scale the data.
        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The data used to scale along the specified axis.
        Returns
        -------
        X_tr : {ndarray, sparse matrix} of shape (n_samples, n_features)
            Transformed array.
        """
        check_is_fitted(self)
        X = self._validate_data(
            X,
            accept_sparse=('csr', 'csc'),
            copy=self.copy,
            estimator=self,
            dtype=FLOAT_DTYPES,
            reset=False,
            force_all_finite='allow-nan'
        )

        if sparse.issparse(X):
            if self.with_scaling:
                inplace_column_scale(X, 1.0 / self.scale_)
        else:
            if self.with_centering:
                X -= self.center_
            if self.with_scaling:
                X /= self.scale_
        return X

    def inverse_transform(self, X):
        """Scale back the data to the original representation
        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The rescaled data to be transformed back.
        Returns
        -------
        X_tr : {ndarray, sparse matrix} of shape (n_samples, n_features)
            Transformed array.
        """
        check_is_fitted(self)
        X = check_array(
            X,
            accept_sparse=('csr', 'csc'),
            copy=self.copy,
            estimator=self,
            dtype=FLOAT_DTYPES,
            force_all_finite='allow-nan'
        )

        if sparse.issparse(X):
            if self.with_scaling:
                inplace_column_scale(X, self.scale_)
        else:
            if self.with_scaling:
                X *= self.scale_
            if self.with_centering:
                X += self.center_
        return X

    def _more_tags(self):
        return {'allow_nan': True}
