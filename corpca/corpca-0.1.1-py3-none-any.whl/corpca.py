import numpy as np
import numpy.typing as npt
from sklearn.decomposition._base import _BasePCA


class CorPCA(_BasePCA):
    def __init__(self, n_components: int = None):
        self.n_components = n_components

        # Currently whiten is not supported
        self.whiten = False
        self.mean_ = None

    def fit(self, X: npt.ArrayLike, y=None):
        """
        X: np.array which has shape (N, D)
        """

        n, d = X.shape

        cormat = np.dot(X.T, X) / n
        lamb, vecs = np.linalg.eigh(cormat)

        # sort by descending order
        lamb = lamb[::-1]
        vecs = vecs[:, ::-1]

        lamb = lamb[:self.n_components]
        # (d x n_compontns)
        vecs = vecs[:, :self.n_components].T

        self.components_ = vecs
        self.explained_variance_ratio_ = lamb / lamb.sum()
        self.n_samples_, self.n_features_ = n, d

    def fit_transform(self, X: npt.ArrayLike, y=None) -> np.ndarray:
        self.fit(X)
        return self.transform(X)
