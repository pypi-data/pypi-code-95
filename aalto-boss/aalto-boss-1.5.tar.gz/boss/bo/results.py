import copy
import numpy as np


class BOResults:
    """Provides easy access to the most important results from a BOSS run.

    This is a wrapper class around BOMain that provides access to the
    main results from an optimization run. In addition to defining methods for convenient
    evaluation of the predictive mean, variance and acquisition function of the GP model,
    the following optimization results are stored as attributes:

    Attributes:
    -----------
    exit_ok: bool
        Whether BOSS exited successfully, i.e. reached convergence or the maximum
        number of iterations.
    X: np.ndarray
        2D array containing all the X-data used during the optimization, this includes
        both initial random points as well as acquistions.
    Y: np.ndarray
        2D array containing the user function evaluations corresponding to the X-data.
    fmin: float
        The global minimum value as determined by BOSS.
    xmin: np.ndarray
        The global minimum, as determined by BOSS.
    xbest: The x-acquisition with the smallest user function value out
            of all the acquisitions.
    ybest: The user function value corresponding to xbest.
    fevals: The number of times the user function was evaluated.
    hyperparams: The final values of the unfixed hyperparameters in the GP model.
    """

    def __init__(self, bo_main):
        """Iinitializes the results from a BOMain object. """
        self.bo = bo_main
        bo = self.bo
        self.exit_ok = bo_main.exit_ok
        self.settings = bo.settings
        self.X = self.bo.get_x()
        self.Y = self.bo.get_y()

        self.convergence = bo.convergence
        if bo.convergence.shape[0] > 0:
            self.fmin = bo.convergence[-1, 3]
            self.xmin = bo.convergence[-1, 2]
            self.xbest = bo.convergence[-1, 0]
            self.ybest = bo.convergence[-1, 1]
        else:
            self.fmin = None
            self.xmin = None
            self.xbest = None
            self.ybest = None

        self.fevals = max(self.X.shape[0] - self.settings["initpts"], 0)
        self.hyperparams = bo.unfixed_model_params

    def f(self, x):
        """Evaluates the predictive mean of the GP model.

        Parameters
        ----------
        x: np.ndarray
            A single x-value given as a 1d array, or multiple x-values
            given as rows in a 2d array.

        Returns
        -------
        float or np.ndarray
            The mean value(s) corresponding to x. If single x-value was given this
            is a scalar and for multiple x-values an 1d array is returned.
        """
        nd = max(np.ndim(x), 1)
        return self.bo.get_mu(x).T[(0,) * (3 - nd)]

    def fvar(self, x):
        """Evaluates the predictive variance of the GP model.

        Parameters
        ----------
        x: np.ndarray
            A single x-value given as a 1d array, or multiple x-values
            given as rows in a 2d array.

        Returns
        -------
        float or np.ndarray
            The variance value(s) corresponding to x. If single x-value was given this
            is a scalar and for multiple x-values an 1d array is returned.
        """
        nd = max(np.ndim(x), 1)
        m, v = self.bo.model.predict(np.atleast_2d(x))
        return v.T[(0,) * (3 - nd)]

    def acqfn(self, x):
        """Evaluates the acquisition function using the final GP model.

        Parameters
        ----------
        x: np.ndarray
            A single x-value given as a 1d array, or multiple x-values
            given as rows in a 2d array.

        Returns
        -------
        float or np.ndarray
            The acquisiton function value(s) corresponding to x. If single x-value was given this
            is a scalar and for multiple x-values an 1d array is returned.
        """
        bo = self.bo
        nd = max(np.ndim(x), 1)
        return bo.acqfn(x, bo.model, bo.acqfnpars)[0].T[(0,) * (3 - nd)]

    def copy(self):
        return copy.deepcopy(self)
