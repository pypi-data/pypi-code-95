import numpy as np

from shap import TreeExplainer as SHAPTreeExplainer
from shap.maskers import Independent as SHAPIndependent

from ..api import XGBWrapping
from .api import BaseExplainer, BaseSupportsDynamicBackground

__all__ = [
    'TreeExplainer',
]


class TreeExplainer(BaseExplainer, BaseSupportsDynamicBackground):
    def __init__(self, model, data=None, max_samples=1e10, class_index=1, **kwargs):
        """Monkey-patched and improved constructor for TreeSHAP

        Args:
            model (any): Tree-based  model
            data (np.ndarray, optional): Reference data. Defaults to None.
            max_samples (int, optional): Maximum number of samples in the reference data. Defaults to 1e10.
            class_index (int, optional): Class for which SHAP values will be computed. Defaults to 1.
        """

        super().__init__(model, None)

        self.data = data
        self.kwargs = kwargs
        self.max_samples = max_samples
        self.class_index = class_index

    @property
    def explainer(self):
        if self._data is None:
            self._raise_data_error()
        return self._explainer

    @BaseSupportsDynamicBackground.data.setter
    def data(self, data):
        if data is not None:
            self._explainer = SHAPTreeExplainer(
                self.model.get_booster() if isinstance(self.model, XGBWrapping) else self.model,
                data=SHAPIndependent(self.preprocess(data), max_samples=self.max_samples),
                **self.kwargs,
            )
            self._data = self.explainer.data
        else:
            self._data = None

    def shap_values(self, *args, **kwargs):
        """Compute SHAP values

        Returns:
            np.ndarray: nb_samples x nb_features array with SHAP values of class self.class_index
        """
        r = self.explainer.shap_values(*args, **kwargs)
        if isinstance(r, list):
            return r[self.class_index]
        else:
            return r

    def get_background_data(self, X):
        return np.broadcast_to(self.data, [X.shape[0], *self.data.shape])
