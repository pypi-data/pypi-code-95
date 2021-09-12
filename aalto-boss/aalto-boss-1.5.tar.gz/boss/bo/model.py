from abc import ABC, abstractmethod
import GPy
import numpy as np


class BaseModel(ABC):
    """
    Base class for surrogate models used in Bayesian optimization.
    """

    # predictions:

    @abstractmethod
    def predict(self, x, noise=True):
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise).
        """
        pass

    @abstractmethod
    def predict_grads(self, x):
        """
        Returns prediction mean and variance gradients with respect to input
        at point x.
        """
        pass

    @abstractmethod
    def predict_mean_sd_grads(self, x, noise=True):
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise).
        """
        pass

    @abstractmethod
    def predict_mean_grad(self, x):
        """
        Returns model mean and its gradient at point x.
        """
        pass

    @abstractmethod
    def estimate_num_local_minima(self, search_bounds):
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        pass

    # model parameters:

    @abstractmethod
    def get_all_params(self):
        """
        Returns model parameters as a dictionary.
        """
        pass

    @abstractmethod
    def get_unfixed_params(self):
        """
        Returns the unfixed parameters of the model in an array.
        """
        pass

    @abstractmethod
    def sample_unfixed_params(self, num_samples):
        """
        Sample unfixed model parameters.
        """
        pass

    @abstractmethod
    def set_unfixed_params(self, params):
        """
        Sets the unfixed parameters of the model to given values.
        """
        pass

    @abstractmethod
    def optimize(self):
        """
        Updates unfixed model parameters.
        """
        pass

    # observations:

    @abstractmethod
    def add_data(self, X_new, Y_new):
        """
        Updates the model evidence (observations) dataset appending.
        """
        pass

    @abstractmethod
    def redefine_data(self, X, Y):
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        pass

    @abstractmethod
    def get_best_xy(self):
        """
        Returns the lowest energy acquisition (x, y).
        """
        pass

    @property
    @abstractmethod
    def kernel(self):
        pass

    @property
    @abstractmethod
    def X(self):
        pass

    @property
    @abstractmethod
    def Y(self):
        pass


class Model(BaseModel):
    """
    Functionality for creating, refitting and optimizing a GP model
    """

    def __init__(self, X, Y, kernel, noise, ynorm):
        """
        Initializes the Model class.
        """
        self.dim = kernel.input_dim
        # normalise observation mean:
        self.normmean = np.mean(Y)
        # scale normalisation is not used unless ynorm is true:
        self.use_norm = ynorm
        # previous boss code used normsd to normalise observation variance:
        # if self.ynorm: self.normsd = np.std(Y)
        # current version normalises observation range:
        self.normsd = np.ptp(Y) if self.use_norm else 1
        # note that the choice betweeen variance or range normalisation needs
        # to be taken into account when we set kernel parameter priors
        # normalised data:
        Y_norm = (Y - self.normmean) / self.normsd
        # initialise model
        self.model = GPy.models.GPRegression(
            X,
            Y_norm,
            kernel=kernel,
            noise_var=noise
        )
        self.model.likelihood.fix()

    # predictions:

    def predict(self, x, noise=True):
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise).
        """
        m, v = self.model.predict(np.atleast_2d(x), include_likelihood=noise)
        v = np.clip(v, 1e-12, np.inf)
        return m*self.normsd+self.normmean, v*(self.normsd**2)

    def predict_grads(self, x):
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x.
        """
        dmdx, dvdx = self.model.predictive_gradients(np.atleast_2d(x))
        return dmdx*self.normsd, dvdx*(self.normsd**2)

    def predict_mean_sd_grads(self, x, noise=True):
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise).

        This method is a wrapper used primarily during calculations
        of acquisition functions and their derivatives.
        """
        m, v = self.predict(np.atleast_2d(x), noise=noise)
        dmdx, dvdx = self.predict_grads(np.atleast_2d(x))
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(self, x):
        """Returns model mean and its gradient at point x.

        This method is a wrapper used primarily when the 
        mean function is minimized in order to obtain a
        global minimum prediction.
        """
        m, v = self.predict(np.atleast_2d(x))
        dmdx, dvdx = self.predict_grads(np.atleast_2d(x))
        scipygradient = np.asmatrix(dmdx).transpose()
        return m, scipygradient

    def estimate_num_local_minima(self, search_bounds):
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        # For the ith dimension, the number of local minima along a slice
        # is approximately n(i) = boundlength(i)/(2*lengthscale(i)). Note
        # that periodic kernels operate on normalised distances: distance
        # between inputs that are period(i)/2 apart is 1. To get the total
        # number of minima for all of the search space, multiply together
        # n(i) over all i.
        numpts = 1
        ks = self.model.kern.parameters if self.dim > 1 else [self.model.kern]
        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, 'period'):
                bound_distance = (bounds[1]-bounds[0])/float(kern.period)
            else:
                bound_distance = (bounds[1]-bounds[0])/2
            numpts *= max(1, bound_distance/float(kern.lengthscale))
        return int(numpts)

    # model parameters:

    def get_all_params(self):
        """
        Returns model parameters as a dictionary with entries::
        noise, variance, lengthscales, periods
        where the last two are 1D lists. There exists a period only for those
        dimensions which are using a periodic kernel.
        """
        noise = float(self.model.likelihood.variance)
        sigma = float(self.model.kern.param_array[0])
        lss = []
        pers = []
        ks = self.model.kern.parameters if self.dim > 1 else [self.model.kern]
        for kern in ks:
            lss.append(float(kern.lengthscale))
            if hasattr(kern, 'period'):
                pers.append(float(kern.period))

        # the variables are returned in a dict:
        params = {}
        params['noise'] = noise
        params['variance'] = sigma
        params['lengthscales'] = lss
        params['periods'] = pers

        return params

    def get_unfixed_params(self):
        """
        Returns the unfixed parameters of the model in an array.
        """
        return np.array(self.model.unfixed_param_array.copy()).astype(float)

    def sample_unfixed_params(self, num_samples):
        """
        Sample unfixed model parameters.
        """
        hmc = GPy.inference.mcmc.HMC(self.model)
        burnin = hmc.sample(int(num_samples * 0.33))
        return hmc.sample(num_samples)

    def set_unfixed_params(self, params):
        """
        Sets the unfixed parameters of the model to given values.
        """
        self.model[self.model._fixes_] = params
        self.model.parameters_changed()

    def optimize(self, restarts=1):
        """
        Updates the model hyperparameters by maximizing marginal likelihood.
        """
        self.model.optimization_runs = []
        if restarts == 1:
            self.model.optimize()
        else:
            self.model.optimize_restarts(
                num_restarts=restarts, verbose=False, messages=False
            )

    # observations:

    def add_data(self, X_new, Y_new):
        """
        Updates the model evidence (observations) dataset appending.
        """
        # construct new unnormalised dataset
        X = np.vstack([self.X, np.atleast_2d(X_new)])
        Y = np.vstack([self.Y, Y_new])
        # update model
        self.redefine_data(X, Y)

    def redefine_data(self, X, Y):
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        # update normalisation
        self.normmean = np.mean(Y)
        if self.use_norm:
            self.normsd = np.ptp(Y)
        # update model
        Y_norm = (Y - self.normmean) / self.normsd
        self.model.set_XY(np.atleast_2d(X), np.atleast_2d(Y_norm))

    def get_best_xy(self):
        """
        Returns the lowest energy acquisition (x, y).
        """
        xbest = np.array(self.X[np.argmin(self.Y)])
        ybest = np.min(self.Y)
        return xbest, ybest

    @property
    def kernel(self):
        return self.model.kern

    @property
    def X(self):
        return self.model.X

    @property
    def Y(self):
        return self.model.Y*self.normsd+self.normmean
