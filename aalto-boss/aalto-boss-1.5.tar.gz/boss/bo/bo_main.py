import os

import numpy as np

from pathlib import Path

from scipy.spatial.distance import euclidean

from boss.bo.acq.explore import explore
from boss.bo.hmc import HMCwrapper
from boss.bo.initmanager import InitManager
from boss.bo.kernel_factory import KernelFactory
from boss.bo.model import Model
from boss.bo.rstmanager import RstManager
from boss.io.main_output import MainOutput
import boss.io.parse as parse
from boss.settings import Settings, standardize_signature
from boss.utils.minimization import Minimization
from boss.utils.timer import Timer
from boss.bo.results import BOResults
import boss.keywords as bkw


class BOMain:
    """
    Class for handling Bayesian Optimization
    """

    def __init__(self, f, bounds, **keywords):
        keywords["bounds"] = bounds
        settings = Settings(keywords, f=f)
        self.settings = settings
        self.rst_manager = None
        self._setup()

    @classmethod
    def from_file(cls, ipfile, f=None, **new_keywords):
        """Initialize BOMain from a BOSS input or rst file.

        Parameters
        ----------
        ipfile : path_like
            The input file to initialize from, can be either a boss input or rst file.
        **new_keywords
            Any new BOSS keywords.
        """
        self = cls.__new__(cls)
        input_data = parse.parse_input_file(ipfile)
        rst_data = input_data.get("rst_data", np.array([]))
        keywords = input_data.get("keywords", {})
        keywords.update(new_keywords)
        self.settings = Settings(keywords, f=f)
        self.rst_manager = RstManager(self.settings, rst_data)
        cls._setup(self)
        return self

    @classmethod
    def from_settings(cls, settings, rst_data=None):
        """Construction from a Settings object. """
        self = cls.__new__(cls)
        self.settings = settings
        self.rst_manager = RstManager(self.settings, rst_data)
        cls._setup(self)
        return self

    def _setup(self):
        """Common setup for all factory methods. """
        settings = self.settings
        self.main_output = MainOutput(settings)
        if not self.rst_manager:
            self.rst_manager = RstManager(settings)

        self.init_manager = InitManager(
            settings["inittype"], settings["bounds"], settings["initpts"]
        )

        self.dim = settings.dim
        self.initpts = settings["initpts"]
        self.iterpts = settings["iterpts"]
        self.updatefreq = settings["updatefreq"]
        self.initupdate = settings["initupdate"]
        self.updateoffset = settings["updateoffset"]
        self.updaterestarts = settings["updaterestarts"]
        self.hmciters = settings["hmciters"]
        self.cores = settings["cores"]
        self.f = settings.f
        self.periods = settings["periods"]
        self.bounds = settings["bounds"]
        self.acqfn = settings.acqfn
        self.acqfnpars = settings["acqfnpars"]
        self.acqtol = settings["acqtol"]
        self.min_dist_acqs = settings["min_dist_acqs"]
        self.minzacc = settings["minzacc"]
        self.kerntype = settings["kernel"]
        self.noise = settings["noise"]
        self.ynorm = settings["ynorm"]
        self.timer = Timer()
        self.dir = settings.dir
        self.gm_tol = settings["gm_tol"]

        self.kernel = KernelFactory.construct_kernel(settings)
        self.model = None
        self.X_init = np.array([]).reshape(0, self.dim)
        self.Y_init = np.array([]).reshape(0, 1)
        self.convergence = np.array([]).reshape(0, 5)
        self.est_yrange = 0
        self.hmcsample = []
        self.exit_ok = False  # successful exit from main loop

        Minimization.set_parallel(self.settings["parallel_optims"])

    def get_x(self):
        """
        Returns the points where the objective function has been evaluated,
        in order of acquisition.
        """
        if self.model == None:
            return self.X_init
        else:
            return self.model.X

    def get_y(self):
        """
        Returns the evaluated values of the objective function, in order of
        acquisition. This method should always be called instead of
        BOMain.model.Y for any use outside of the BOMain class.
        """
        if self.model == None:
            return self.Y_init
        else:
            return self.model.Y

    def get_mu_and_nu(self, x):
        """
        Returns the model prediction (mu) and its standard deviation (nu)
        at point x.
        The standard deviation is calculated based on predictive variance
        with noise (model variance).
        """
        if self.model is None:
            return None, None
        else:
            mu, var = self.model.predict(x)
            nu = np.sqrt(var)
            return mu, nu

    def get_mu(self, x):
        """
        Returns the model prediction at point x.
        """
        return self.get_mu_and_nu(x)[0]

    def get_nu(self, x):
        """
        Returns the standard deviation of the model prediction at point x,
        calculated based on predictive variance with noise (model variance).
        """
        return self.get_mu_and_nu(x)[1]

    def get_grad(self, x):
        """
        Returns the predictive gradients.
        """
        g = self.model.predict_grads(x)
        return np.array([g[0], None])

    def _add_xy(self, x_new, y_new):
        """
        Internal functionality for saving a new acquisition (x, y).
        Initializes the GP model when the number ofacquisitions meets the
        pre-specified number of initialization points.
        """
        if self.model == None:
            self.X_init = np.vstack([self.X_init, x_new])
            self.Y_init = np.vstack([self.Y_init, y_new])
            if self.get_x().shape[0] == self.initpts:
                self._init_model()
        else:
            self.model.add_data(x_new, y_new)
            self.est_yrange = np.max(self.model.Y) - np.min(self.model.Y)

    def add_xy_list(self, x_new, y_new):
        """
        Saves multiple acquisitions. Initializes the GP model when the number
        of acquisitions meets the pre-specified number of initialization
        points.
        """
        for i in range(x_new.shape[0]):
            self._add_xy(x_new[i, :], y_new[i])

    def _init_model(self):
        """
        Initializes the GP model. This should be called when all initialization
        points have been evaluated. Further acquisition locations can then be
        queried by optimizing an acquisition function.
        """
        self.est_yrange = np.max(self.Y_init) - np.min(self.Y_init)
        self.model = Model(
            self.X_init,
            self.Y_init,
            self.kernel,
            self.noise,
            self.ynorm,
        )
        n = len(self.model.get_unfixed_params())
        self.unfixed_model_params = np.array([]).reshape(0, n)

    def _should_optimize(self, i_iter):
        """
        Returns True if the model should be optimized at iteration i.
        """
        bo_i = np.max([0, i_iter + 1 - self.initpts])  # == 0 means initial iters

        # No model -> no optimization
        if self.model == None:
            return False

        # Check if initialization has just completed and we want to optimize
        elif bo_i == 0:
            if self.initupdate:
                return True
            else:
                return False

        # Check if optimization threshold and interval have passed
        elif bo_i >= self.updateoffset and bo_i % self.updatefreq == 0:
            return True

        # Otherwise there is no need to optimize
        else:
            return False

    def run(self):
        """
        The Bayesian optimization main loop. Evaluates first the initialization
        points, then creates a GP model and uses it and an acquisition function
        to locate the next points where to evaluate. Stops when a pre-specified
        number of initialization points and BO points have been acquired or a
        convergence criterion is met.

        Returns
        -------
        BOResults
            An object that provides convenient access to the most
            important results from the optimization.
        """
        self.exit_ok = False

        # Resolve current iteration and set optimisation parameters
        i_current = len(self.get_x())
        if i_current == 0:
            self.main_output.new_file()
            self.rst_manager.new_file()

        initpts = self.settings["initpts"]
        iterpts = self.settings["iterpts"]
        minfreq = self.settings["minfreq"]

        totalpts = initpts + iterpts

        x_next = self._get_x_next(i_current)

        # BO main loop
        for i_iter in np.arange(i_current, totalpts):

            self.main_output.iteration_start(i_iter + 1)
            self.timer.startLap()

            # Evaluation
            x_new, y_new = self._evaluate(i_iter, x_next)

            # Store new data and refit model.
            #  - Create the model when all initial data has been acquired.
            for i in range(len(y_new)):
                self._add_xy(x_new[i], y_new[i])
                self.rst_manager.new_data(x_new[i], y_new[i])

            # Optimize model if needed.
            if self._should_optimize(i_iter):
                self._optimize_model(i_iter)

            # Find next acquisition point.
            x_next = self._get_x_next(i_iter + 1)

            # Add model parameters to rst-file.
            if self.model != None:
                mod_unfixed_par = self.model.get_unfixed_params()
                self.rst_manager.new_model_params(mod_unfixed_par)

                # Also store model parameters directly on BOMain
                self.unfixed_model_params = np.vstack(
                    (self.unfixed_model_params, mod_unfixed_par)
                )
            else:
                mod_unfixed_par = None

            # Convergence diagnostics, calculate iteration specific info
            iconv = i_iter - initpts + 1
            write_conv = iconv >= 0 and (
                iconv == iterpts or (minfreq > 0 and (iconv % minfreq == 0))
            )
            if write_conv:
                self._add_convergence()

            # Output to boss outfile
            # Print a summary of important iteration data
            self.main_output.iteration_summary(
                i_iter,
                self.get_y().size,
                x_new,
                y_new,
                self.convergence,
                x_next,
                self.est_yrange,
                mod_unfixed_par,
                self.timer,
            )

            # Stopping criterion: convergence
            if self._has_converged(i_iter):
                self.main_output.convergence_stop()
                break

        # If we get here, the optimization finished successfully.
        self.exit_ok = True
        res = self.get_results()
        return res

    def resume(self, iterpts):
        """Resumes an optimization.

        If the BOMain object still exists and has an initialized model,
        this method will continue where the previous optimization left off
        for a given number of new iterations. Existing out and rst files will
        be updated with data form the new iterations, but changes done to the settings upon
        resuming will not be reflected in the beginning of these files.

        Parameters
        ----------
        iterpts : int
            The number of iterations for the resumed optimization.
            This includes the number of iterations from the previous run,
            thus if you first ran for 10 iterations and now want 10 more,
            you should set iterpts=20.

        Returns
        -------
        BOResults
            A dict-like object that provides convenient access to the most
            important results from the optimization.
        """
        self.settings["iterpts"] = iterpts
        return self.run()

    def get_results(self):
        return BOResults(self)

    def _has_converged(self, i_iter):
        """
        Checks whether dxhat has been within tolerance for long enough
        TODO: should use dxmuhat instead?
        """
        if self.gm_tol is not None:
            conv_tol, conv_it = self.gm_tol
            if i_iter > self.initpts + conv_it:
                curr_xhat = self.convergence[-1, -3]
                within_tol = True
                for test_i in range(2, conv_it - 1):
                    if euclidean(self.convergence[-test_i, -3], curr_xhat) > conv_tol:
                        within_tol = False
                return within_tol
        return False

    def _get_x_next(self, i_iter):
        """
        Get a new point to evaluate by either reading it from the rst-file or,
        in case it doesn't contain the next point to evaluate, by obtaining
        a new initial point (when run is in initialization stage) or
        minimizing the acquisition function (when the run is in BO stage).
        """
        x_next = self.rst_manager.get_x(i_iter)
        if np.any(x_next == None):
            if i_iter < self.initpts:
                x_next = self.init_manager.get_x(i_iter)
            else:
                x_next, acqfn = self._acqnext(i_iter)
        return x_next

    def _acqnext(self, i_iter):
        """
        Selects the acquisition function to use and returns its x_next location
        as well as the used acquisition function.
        """
        if self.hmciters == 0:
            acqfn = self.acqfn
            expfn = explore
        else:
            hmc = HMCwrapper(self.hmcsample)
            acqfn = hmc.averageacq(self.acqfn, self.cores)
            expfn = hmc.averageacq(explore, self.cores)

        x_next = self._minimize_acqfn(acqfn)

        # check if x_next indicates we should trigger pure exploration
        if self._location_overconfident(x_next):
            x_next = self._minimize_acqfn(expfn)
            return x_next, expfn
        else:
            return x_next, acqfn

    def _minimize_acqfn(self, acqfn):
        """
        Minimizes the acquisition function to find the next
        sampling location 'x_next'.
        """
        # Calculate the number of local minimizers to start. This has two
        # steps:

        # 1. Estimate the number of local minima in the surrogate model.
        estimated_numpts = self.model.estimate_num_local_minima(self.bounds)

        # 2. Increase the estimate to approximate the number of local
        # minima in the acquisition function. Here we assume that the
        # increase is proportional to the estimated number of local minima
        # per dimension.
        minima_multiplier = 1.7
        estimated_numpts = (minima_multiplier ** self.dim) * estimated_numpts

        num_pts = min(len(self.model.X), int(estimated_numpts))

        # minimize acqfn to obtain sampling location
        gmin = Minimization.minimize_from_random(
            acqfn,
            self.bounds,
            num_pts=num_pts,
            shift=0.1 * np.array(self.periods),
            args=[self.model, self.acqfnpars],
        )
        return np.atleast_1d(np.array(gmin[0]))

    def _location_overconfident(self, x_next):
        """
        Checks is model variance is lower than tolerance at suggested x_next.
        """
        if self.acqtol is None:
            return False
        else:
            nu_x_next = np.sqrt(self.model.predict(x_next)[1])
            if nu_x_next >= self.acqtol:
                return False
            else:
                self.main_output.progress_msg(
                    "Acquisition location " + "too confident, doing pure exploration", 1
                )
                return True

    def _evaluate(self, i_iter, x_next):
        """
        Get a new evaluation either from the rst-file or, in case it doesn't
        contain the corresponding evaluation, by evaluating the user function
        """
        y_new = self.rst_manager.get_y(i_iter)
        if np.any(y_new == None):
            return self._evaluate_x_new(x_next)
        else:
            return np.atleast_2d(x_next), np.atleast_1d(y_new)

    def _evaluate_x_new(self, x_new):
        """
        Evaluates user function at given location 'x_new'
        to get the observation scalar 'y_new'.
        Later also gradient 'ydnew' should be made possible.
        """
        # run user script to evaluate sample
        self.main_output.progress_msg(
            "Evaluating objective function at x ="
            + self.main_output.utils.oneDarray_line(x_new.flatten(), self.dim, float),
            1,
        )

        local_timer = Timer()
        x_new = np.atleast_2d(x_new)  # X-data expected to be 2d-array
        y_new = np.atleast_1d(self.f(x_new))  # call the user function
        # os.chdir(self.dir)  # in case the user function changed the dir
        self.main_output.progress_msg(
            "Objective function evaluated,"
            + " time [s] %s" % (local_timer.str_lapTime()),
            1,
        )
        return x_new, y_new

    def _optimize_model(self, i_iter):
        """
        Optimize the GP model or, if the next hyperparameters are contained in
        the rst-file, just use them.
        """
        if self.hmciters > 0:
            self.hmcsample = self.model.sample_unfixed_params(self.hmciters)

        n = self.model.get_unfixed_params().size
        theta = self.rst_manager.get_theta(i_iter, n)
        if np.any(theta == None):
            self.model.optimize(self.updaterestarts)
        else:
            self.model.set_unfixed_params(theta)

    def _add_convergence(self):
        """
        Updates self.convergence with a new row containing
        bestx, besty, xhat, muhat, nuhat (in this order).
        """
        # if self.model == None:
        #     conv = np.atleast_2d(np.repeat(np.nan, 5))
        # else:
        bestx, besty = self.model.get_best_xy()
        xhat, muhat, nuhat = self._min_model_prediction()
        conv = np.atleast_2d([bestx, besty, xhat, muhat, nuhat])
        self.convergence = np.vstack((self.convergence, conv))

    def _min_model_prediction(self):
        """
        Finds and returns the model global minimum prediction xhat
        and the model mean (muhat) and variance (nuhat) at that point.
        """
        gmin = Minimization.minimize(
            self.model.predict_mean_grad,
            self.bounds,
            self.kerntype,
            np.hstack([self.model.X, self.model.Y]),
            self.min_dist_acqs,
            accuracy=self.minzacc,
        )
        xhat = np.array(gmin[0])
        muhat, nuhat = self.model.predict(np.atleast_2d(xhat))
        return xhat, muhat[0][0], nuhat[0][0]
