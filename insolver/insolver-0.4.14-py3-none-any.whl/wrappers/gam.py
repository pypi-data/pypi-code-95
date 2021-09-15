from functools import partial

from pandas import DataFrame, Series, concat
from numpy import sum, sqrt, repeat

from h2o.frame import H2OFrame
from h2o.estimators.gam import H2OGeneralizedAdditiveEstimator

from .base import InsolverBaseWrapper
from .extensions import InsolverH2OExtension, InsolverPDPExtension


class InsolverGAMWrapper(InsolverBaseWrapper, InsolverH2OExtension, InsolverPDPExtension):
    """Insolver wrapper for Generalized Additive Models.

    Attributes:
        backend (str): Framework for building GAM, currently 'h2o' is supported.
        family (:obj:`str`, :obj:`float`, :obj:`int`, optional): Distribution for GAM. Supports any family from h2o as
        str. By default, Gaussian GAM is fitted.
        link (:obj:`str`, optional): Link function for GAM. If `None`, sets to default value for h2o.
        standardize (:obj:`bool`, optional): Whether to standardize data before fitting the model. Enabled by default.
        h2o_init_params (:obj:`dict`, optional): Parameters passed to `h2o.init()`, when `backend` == 'h2o'.
        load_path (:obj:`str`, optional): Path to GAM model to load from disk.
        **kwargs: Parameters for GAM estimator (for H2OGeneralizedAdditiveEstimator) except `family` and `link`.
        """
    def __init__(self, backend, family=None, link=None, standardize=True, h2o_init_params=None,
                 load_path=None, **kwargs):
        super(InsolverGAMWrapper, self).__init__(backend)
        self.algo, self._backends = 'gam', ['h2o']
        self._back_load_dict = {'h2o': partial(self._h2o_load, h2o_init_params=h2o_init_params)}
        self._back_save_dict = {'h2o': self._h2o_save}

        if backend not in self._backends:
            raise NotImplementedError(f'Error with the backend choice. Supported backends: {self._backends}')

        self.params, self.standardize = None, standardize
        if load_path is not None:
            self.load_model(load_path)
        else:
            family = family if family is not None else 'gaussian'
            link = link if link is not None else 'family_default' if backend == 'h2o' else 'auto'
            if backend == 'h2o':
                self._h2o_init(h2o_init_params)
                self.model = H2OGeneralizedAdditiveEstimator(family=family, link=link, standardize=self.standardize,
                                                             **kwargs)
        self._update_meta()

    def fit(self, X, y, sample_weight=None, X_valid=None, y_valid=None, sample_weight_valid=None, **kwargs):
        """Fit a Generalized Additive Model.

        Args:
            X (:obj:`pd.DataFrame`, :obj:`pd.Series`): Training data.
            y (:obj:`pd.DataFrame`, :obj:`pd.Series`): Training target values.
            sample_weight (:obj:`pd.DataFrame`, :obj:`pd.Series`, optional): Training sample weights.
            X_valid (:obj:`pd.DataFrame`, :obj:`pd.Series`, optional): Validation data (only h2o supported).
            y_valid (:obj:`pd.DataFrame`, :obj:`pd.Series`, optional): Validation target values (only h2o supported).
            sample_weight_valid (:obj:`pd.DataFrame`, :obj:`pd.Series`, optional): Validation sample weights.
            **kwargs: Other parameters passed to H2OGeneralizedAdditiveEstimator.
        """
        if (self.backend == 'h2o') & isinstance(self.model, H2OGeneralizedAdditiveEstimator):
            features, target, train_set, params = self._x_y_to_h2o_frame(X, y, sample_weight, {**kwargs}, X_valid,
                                                                         y_valid, sample_weight_valid)
            self.model.train(y=target, x=features, training_frame=train_set, **params)
        else:
            raise NotImplementedError(f'Error with the backend choice. Supported backends: {self._backends}')
        self._update_meta()

    def predict(self, X, sample_weight=None, **kwargs):
        """Predict using GAM with feature matrix X.

        Args:
            X (:obj:`pd.DataFrame`, :obj:`pd.Series`): Samples.
            sample_weight (:obj:`pd.DataFrame`, :obj:`pd.Series`, optional): Test sample weights.
            **kwargs: Other parameters passed to H2OGeneralizedAdditiveEstimator.predict().

        Returns:
            array: Returns predicted values.
        """
        if (self.backend == 'h2o') & isinstance(self.model, H2OGeneralizedAdditiveEstimator):
            if self.model.parms['offset_column']['actual_value'] is not None and sample_weight is None:
                offset_name = self.model.parms['offset_column']['actual_value']['column_name']
                sample_weight = Series(repeat(0, len(X)), name=offset_name, index=X.index)
            if sample_weight is not None:
                X = concat([X, sample_weight], axis=1)
            h2o_predict = X if isinstance(X, H2OFrame) else H2OFrame(X)
            predictions = self.model.predict(h2o_predict, **kwargs).as_data_frame().values.reshape(-1)
        else:
            raise NotImplementedError(f'Error with the backend choice. Supported backends: {self._backends}')
        return predictions

    def coef_norm(self):
        """Output GAM coefficients for standardized data.

        Returns:
            dict: {:obj:`str`: :obj:`float`} Dictionary containing GAM coefficients for standardized data.
        """
        if self.standardize:
            if (self.backend == 'h2o') & isinstance(self.model, H2OGeneralizedAdditiveEstimator):
                coefs = self.model.coef_norm()
            else:
                raise NotImplementedError(f'Error with the backend choice. Supported backends: {self._backends}')
        else:
            raise Exception('Normalized coefficients unavailable since model fitted on non-standardized data.')
        return coefs

    def coef(self):
        """Output GAM coefficients for non-standardized data. Also calculated when GAM fitted on standardized data.

        Returns:
            dict: {:obj:`str`: :obj:`float`} Dictionary containing GAM coefficients for non-standardized data.
        """
        if (self.backend == 'h2o') & isinstance(self.model, H2OGeneralizedAdditiveEstimator):
            coefs = self.model.coef()
        else:
            raise NotImplementedError(f'Error with the backend choice. Supported backends: {self._backends}')
        return coefs
