"""
    Made more efficient from Scikit-Learn QuantileTransformer
    https://github.com/scikit-learn/scikit-learn/blob/2beed5584/sklearn/preprocessing
    
"""
# %%
import warnings
import numpy as np
from scipy import sparse
from scipy import stats
from sklearn.utils import check_random_state
from sklearn.utils.validation import (check_is_fitted, FLOAT_DTYPES)
from sklearn.preprocessing import QuantileTransformer

BOUNDS_THRESHOLD = 1e-7


class EfficientQuantileTransformer(QuantileTransformer):
    """
        This is more efficient of both QuantileTransformer (sklearn)
        And also, PercentileShifter (in this folder)
    """
    def __init__(self, *, ignore_implicit_zeros=False, subsample=np.inf, random_state=None, copy=True):
        self.n_quantiles = np.inf
        self.output_distribution = 'uniform'
        self.ignore_implicit_zeros = ignore_implicit_zeros
        self.subsample = subsample
        self.random_state = random_state
        self.copy = copy

    def _smart_fit(self, X, random_state):
        """Compute percentiles for dense matrices.
        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            The data used to scale along the features axis.
        """
        if self.ignore_implicit_zeros:
            warnings.warn(
                "'ignore_implicit_zeros' takes effect only with"
                " sparse matrix. This parameter has no effect."
            )

        n_samples, n_features = X.shape
        self.references_ = []
        self.quantiles_ = []
        for col in X.T:
            # Do sampling if necessary
            if self.subsample < n_samples:
                subsample_idx = random_state.choice(n_samples, size=self.subsample, replace=False)
                col = col.take(subsample_idx, mode='clip')
            col = np.sort(col)
            quantiles = np.sort(np.unique(col))
            references = 0.5 * np.array(
                [np.searchsorted(col, v, side='left') + np.searchsorted(col, v, side='right') for v in quantiles]
            ) / n_samples
            self.quantiles_.append(quantiles)
            self.references_.append(references)

    def fit(self, X, y=None):
        """Compute the quantiles used for transforming.
        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The data used to scale along the features axis. If a sparse
            matrix is provided, it will be converted into a sparse
            ``csc_matrix``. Additionally, the sparse matrix needs to be
            nonnegative if `ignore_implicit_zeros` is False.
        y : None
            Ignored.
        Returns
        -------
        self : object
           Fitted transformer.
        """
        if self.n_quantiles <= 0:
            raise ValueError(
                "Invalid value for 'n_quantiles': %d. "
                "The number of quantiles must be at least one." % self.n_quantiles
            )

        if self.subsample <= 0:
            raise ValueError(
                "Invalid value for 'subsample': %d. "
                "The number of subsamples must be at least one." % self.subsample
            )

        if self.n_quantiles > self.subsample:
            raise ValueError(
                "The number of quantiles cannot be greater than"
                " the number of samples used. Got {} quantiles"
                " and {} samples.".format(self.n_quantiles, self.subsample)
            )

        X = self._check_inputs(X, in_fit=True, copy=False)
        n_samples = X.shape[0]

        if self.n_quantiles > n_samples:
            warnings.warn(
                "n_quantiles (%s) is greater than the total number "
                "of samples (%s). n_quantiles is set to "
                "n_samples." % (self.n_quantiles, n_samples)
            )
        self.n_quantiles_ = max(1, min(self.n_quantiles, n_samples))

        rng = check_random_state(self.random_state)

        # Create the quantiles of reference
        self.smart_fit_ = n_samples <= self.n_quantiles_ and not sparse.issparse(X)
        if self.smart_fit_:  # <<<<<- New case
            self._smart_fit(X, rng)
        else:
            warnings.warn('NOT using SmartFit for QuantileTransformer, execution will be unefficient.')
            self.references_ = np.linspace(0, 1, self.n_quantiles_, endpoint=True)
            if sparse.issparse(X):
                self._sparse_fit(X, rng)
            else:
                self._dense_fit(X, rng)

        return self

    def _smart_transform_col(self, X_col, quantiles, references, inverse):
        """Private function to transform a single feature."""

        isfinite_mask = ~np.isnan(X_col)
        X_col_finite = X_col[isfinite_mask]
        # Simply Interpolate
        if not inverse:
            X_col[isfinite_mask] = np.interp(X_col_finite, quantiles, references)
        else:
            X_col[isfinite_mask] = np.interp(X_col_finite, references, quantiles)

        return X_col

    def _check_inputs(self, X, in_fit, accept_sparse_negative=False, copy=False):
        """Check inputs before fit and transform."""
        X = self._validate_data(
            X, reset=in_fit, accept_sparse='csc', copy=copy, dtype=FLOAT_DTYPES, force_all_finite='allow-nan'
        )
        # we only accept positive sparse matrix when ignore_implicit_zeros is
        # false and that we call fit or transform.
        with np.errstate(invalid='ignore'):  # hide NaN comparison warnings
            if (
                not accept_sparse_negative and not self.ignore_implicit_zeros and
                (sparse.issparse(X) and np.any(X.data < 0))
            ):
                raise ValueError('QuantileTransformer only accepts' ' non-negative sparse matrices.')

        # check the output distribution
        if self.output_distribution not in ('normal', 'uniform'):
            raise ValueError(
                "'output_distribution' has to be either 'normal'"
                " or 'uniform'. Got '{}' instead.".format(self.output_distribution)
            )

        return X

    def _transform(self, X, inverse=False):
        """Forward and inverse transform.
        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            The data used to scale along the features axis.
        inverse : bool, default=False
            If False, apply forward transform. If True, apply
            inverse transform.
        Returns
        -------
        X : ndarray of shape (n_samples, n_features)
            Projected data.
        """
        if self.smart_fit_:
            for feature_idx in range(X.shape[1]):
                X[:, feature_idx] = self._smart_transform_col(
                    X[:, feature_idx], self.quantiles_[feature_idx], self.references_[feature_idx], inverse
                )
        else:
            if sparse.issparse(X):
                for feature_idx in range(X.shape[1]):
                    column_slice = slice(X.indptr[feature_idx], X.indptr[feature_idx + 1])
                    X.data[column_slice] = self._transform_col(
                        X.data[column_slice], self.quantiles_[:, feature_idx], inverse
                    )
            else:
                for feature_idx in range(X.shape[1]):
                    X[:, feature_idx] = self._transform_col(X[:, feature_idx], self.quantiles_[:, feature_idx], inverse)

        return X

    def transform(self, X):
        """Feature-wise transformation of the data.
        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The data used to scale along the features axis. If a sparse
            matrix is provided, it will be converted into a sparse
            ``csc_matrix``. Additionally, the sparse matrix needs to be
            nonnegative if `ignore_implicit_zeros` is False.
        Returns
        -------
        Xt : {ndarray, sparse matrix} of shape (n_samples, n_features)
            The projected data.
        """
        check_is_fitted(self)
        X = self._check_inputs(X, in_fit=False, copy=self.copy)

        return self._transform(X, inverse=False)

    def inverse_transform(self, X):
        """Back-projection to the original space.
        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The data used to scale along the features axis. If a sparse
            matrix is provided, it will be converted into a sparse
            ``csc_matrix``. Additionally, the sparse matrix needs to be
            nonnegative if `ignore_implicit_zeros` is False.
        Returns
        -------
        Xt : {ndarray, sparse matrix} of (n_samples, n_features)
            The projected data.
        """
        check_is_fitted(self)
        X = self._check_inputs(X, in_fit=False, accept_sparse_negative=True, copy=self.copy)

        return self._transform(X, inverse=True)


# %%
