
from abc import ABCMeta, abstractmethod

import pandas as pd
from imblearn.base import SamplerMixin

class SegmenterMixin(SamplerMixin, metaclass=ABCMeta):

    def _check_X_y(self, X, y):
        assert len(X) == len(y)

    @abstractmethod
    def _sample(self, X, y=None) -> pd.DataFrame:
        pass

    def _fit_resample(self, X, y):
        return self._sample(X, y)

    def fit_resample(self, X, y) -> pd.DataFrame:
        self._check_X_y(X, y)
        return self._fit_resample(X, y)

    def segment(self, X, y = None) -> pd.DataFrame:
        return self._sample(X, y)        
