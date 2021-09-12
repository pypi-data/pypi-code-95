"""
Base Classes
------------
The ``maica.ml.base`` module includes basic classes of machine learning algorithms.
It provides a wrapper class of Scikit-learn models and an abstract class of PyTorch models.
"""


import numpy
import torch
import joblib
import maica.core.env as env
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.tree import DecisionTreeRegressor
from gplearn.genetic import SymbolicRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct
from sklearn.gaussian_process.kernels import WhiteKernel
from xgboost import XGBRegressor


class Model:
    """
    An abstract class of machine learning algorithm in MAICA.
    All machine learning algorithms in MAICA should inherit this class.
    """

    def __init__(self,
                 alg_type: str,
                 alg_name: str):
        """
        :param alg_type: (*str*) A type of the algorithm defined in ``maica.core.env``.
        :param alg_name: (*str*) A name of the algorithm defined in ``maica.core.env``.
        """

        self.alg_type = alg_type
        self.alg_name = alg_name


class SKLearnModel(Model):
    """
    A wrapper class of the machine learning algorithms in the Scikit-learn library.
    This class provides a generic interface of ``fit()`` and ``predict()`` functions in the Scikit-learn algorithms.
    """

    def __init__(self,
                 alg_name: str,
                 **kwargs):
        """
        :param alg_name: (*str*) A name of the algorithm defined in ``maica.core.env``.
        :param kwargs: (*optional*) Hyperparameters of the machine learning algorithms.
        """

        super(SKLearnModel, self).__init__(env.ALG_SKLEARN, alg_name)
        self.alg_name = alg_name
        self.alg = None

        # Initialize machine learning model according to the given argument 'alg_name'.
        self.__init_model(**kwargs)

    def __init_model(self,
                     **kwargs):
        """
        Initialize machine learning model according to the class parameter ``self.alg_name``.

        :param kwargs: (*optional*) Hyperparameters of the machine learning algorithms.
        """

        if self.alg_name == env.ALG_LR:
            # Linear Regression
            self.alg = LinearRegression()
        elif self.alg_name == env.ALG_LASSO:
            # LASSO
            alpha = kwargs['alpha'] if 'alpha' in kwargs.keys() else 0.1
            self.alg = Lasso(alpha=alpha)
        elif self.alg_name == env.ALG_DCTR:
            # Decision Tree Regression
            self.alg = DecisionTreeRegressor()
        elif self.alg_name == env.ALG_SYMR:
            # Symbolic Regression
            population_size = kwargs['population_size'] if 'population_size' in kwargs.keys() else 1000
            generations = kwargs['generations'] if 'generations' in kwargs.keys() else 100
            p_subtree_mutation = kwargs['p_subtree_mutation'] if 'p_subtree_mutation' in kwargs.keys() else 0.01
            p_hoist_mutation = kwargs['p_hoist_mutation'] if 'p_hoist_mutation' in kwargs.keys() else 0.01
            p_point_mutation = kwargs['p_point_mutation'] if 'p_point_mutation' in kwargs.keys() else 0.01
            self.alg = SymbolicRegressor(population_size=population_size, generations=generations,
                                         p_subtree_mutation=p_subtree_mutation, p_hoist_mutation=p_hoist_mutation,
                                         p_point_mutation=p_point_mutation, verbose=1)
        elif self.alg_name == env.ALG_KRR:
            # Kernel Ridge Regression
            alpha = kwargs['alpha'] if 'alpha' in kwargs.keys() else 1.0
            self.alg = KernelRidge(alpha=alpha)
        elif self.alg_name == env.ALG_KNNR:
            # K-Nearest Neighbor Regression
            n_neighbors = kwargs['n_neighbors'] if 'n_neighbors' in kwargs.keys() else 5
            self.alg = KNeighborsRegressor(n_neighbors=n_neighbors)
        elif self.alg_name == env.ALG_GPR:
            # Gaussian Process Regression
            kernel = DotProduct() + WhiteKernel()
            self.alg = GaussianProcessRegressor(kernel=kernel)
        elif self.alg_name == env.ALG_SVR:
            # Support Vector Regression
            c = kwargs['c'] if 'c' in kwargs.keys() else 1.0
            epsilon = kwargs['epsilon'] if 'epsilon' in kwargs.keys() else 0.1
            self.alg = SVR(C=c, epsilon=epsilon)
        elif self.alg_name == env.ALG_GBTR:
            # Gradient Boosting Tree Regression
            max_depth = kwargs['max_depth'] if 'max_depth' in kwargs.keys() else 7
            n_estimators = kwargs['n_estimators'] if 'n_estimators' in kwargs.keys() else 300
            self.alg = XGBRegressor(max_depth=max_depth, n_estimators=n_estimators)

    def fit(self,
            inputs: numpy.ndarray,
            targets: numpy.ndarray):
        """
        Fit model parameters for the given input and target data.

        :param inputs: (*numpy.ndarray*) The input data of the training dataset.
        :param targets: (*numpy.ndarray*) The target data of the training dataset.
        :return: Trained model.
        """

        self.alg.fit(inputs, targets)
        return self

    def predict(self,
                inputs: numpy.ndarray):
        """
        Predict target values of the given input data.

        :param inputs: (*numpy.ndarray*) The input data of the dataset.
        :return: Predicted values for the given ``inputs``.
        """

        return self.alg.predict(inputs)

    def save(self,
             path_model_file: str):
        """
        Save model parameters into a file in ``path_model_file``.

        :param path_model_file: (*str*) The path of the model file.
        """

        joblib.dump(self.alg, path_model_file)

    def load(self,
             path_model_file: str):
        """
        Load model parameters in a file of ``path_model_file``.

        :param path_model_file: (*str*) The path of the model file.
        """

        self.alg = joblib.load(path_model_file)


class PyTorchModel(torch.nn.Module, Model):
    """
    An abstract class of the machine learning algorithms in the PyTorch library.
    In MAICA, all PyTorch algorithms should inherit this class.
    """

    def __init__(self,
                 alg_name: str):
        """
        :param alg_name: (*str*) A name of the algorithm defined in ``maica.core.env``.
        """

        super(PyTorchModel, self).__init__()
        self.alg_type = env.ALG_PYTORCH
        self.alg_name = alg_name

    def gpu(self):
        """
        Move model parameters from CPU to GPU.

        :return: Model object (self) in GPU.
        """

        return self.cuda()

    def save(self,
             path_model_file: str):
        """
        Save model parameters into a file in ``path_model_file``.

        :param path_model_file: (*str*) The path of the model file.
        """

        torch.save(self.state_dict(), path_model_file)

    def load(self,
             path_model_file: str):
        """
        Load model parameters in a file of ``path_model_file``.

        :param path_model_file: (*str*) The path of the model file.
        """

        self.load_state_dict(torch.load(path_model_file))
