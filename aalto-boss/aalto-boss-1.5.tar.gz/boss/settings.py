import importlib
import inspect
import os
import sys
from pathlib import Path
import copy

import numpy as np

import boss.keywords as bkw
import boss.io.parse as parse
import boss.io.dump as dump
from boss.bo.acq.ei import ei
from boss.bo.acq.elcb import elcb
from boss.bo.acq.exploit import exploit
from boss.bo.acq.explore import explore
from boss.bo.acq.lcb import lcb
from boss.io.main_output import MainOutput
from boss.utils.distributions import Distributions


def standardize_signature(f, xdim):
    """Standardizes the signature of the user-function.

    Internally, 2d np.ndarray are passed to the user function,
    thus user-functions with different signatures must first
    be converted to this format.

    Parameters
    ----------
    f: Callable
        User-function that takes an arbitary number
        of type-identical arguments,
    xdim: int
        The dimension, as returned by np.ndim, of the individual arguments to f.

    Returns
    -------
    Callable
        A wrapped (if necessary) version of f that takes a single
        1d np.ndarray as input.
    """
    sig = inspect.signature(f)
    nargs = len(sig.parameters)
    if xdim == 0:
        def fnew(x):
            return f(*x[0])
    elif xdim == 1:
        if nargs == 1:
            def fnew(x):
                return f(x[0])
        else:
            def fnew(x):
                return f(*np.hsplit(x[0], nargs))
    elif xdim == 2:
        if nargs == 1:
            fnew = f
        else:
            def fnew(x):
                return f(*np.hsplit(x, nargs))
    else:
        raise ValueError
    return fnew


class Settings(dict):
    """Reads, interprets and defines the code internal settings based on input.
    """

    def __init__(self, keywords, f=None):
        super().__init__()

        # Non-keyword attributes.
        self.is_rst = False

        self.dir = os.getcwd()
        self.acqfn = None

        # Before any other keywords are set, we assign values to all keywords
        # with independent defaults.
        self.set_independent_defaults(only_missing=False)

        # Update with keywords from config files
        self.update(parse.parse_config())

        # Update with BOSS keywords passed to init
        self.update(keywords)
        if keywords.get("bounds") is None:
            raise ValueError(
                "Keyword 'bounds' has to be defined by the user"
            )

        # Handle the user function: if a function is passed directly we take that,
        # otherwise fall back to the function specified by the userfn keyword.
        if f is None:
            if self["userfn"] is not None:
                f_user = bkw.func_from_keyword(self["userfn"])
                f = standardize_signature(f_user, self["userfn_arrdim"])
            self.f = f
        else:
            self["userfn"] = bkw.func_to_keyword(f)
            self.f = standardize_signature(f, self["userfn_arrdim"])

        # Set default values for dependent keywords if they
        # have not yet been specified.
        self.set_acqfn(self["acqfn_name"])
        self.correct()
        self.set_dependent_defaults(only_missing=True)

        # Set RNG seed if specified.
        # TODO: Propagate this seed to GPy to eliminate all randomness.
        if self["seed"] is not None:
            np.random.seed(self["seed"])

    @classmethod
    def from_file(cls, file_path):
        """Factory method for Constructing a Settings object from a boss input file.

        Parameters
        -----------
        file_path: str, Path
            Path to the input file.

        Returns
        -------
        Settings
            Settings object generated using the input file.
        """
        input_data = parse.parse_input_file(file_path, skip="results")
        settings = cls(input_data['keywords'])
        settings.is_rst = input_data['is_rst']
        return settings

    def copy(self):
        return copy.deepcopy(self)

    def set_independent_defaults(self, only_missing=True):
        """Sets default values for independent keywords. """
        if not only_missing:
            for cat in bkw.get_copied_categories():
                self.update(cat)
        else:
            for cat in bkw.get_copied_categories():
                for key, val in cat.items():
                    if self.get(key) is None:
                        self[key] = val

    def set_dependent_defaults(self, only_missing=True):
        """Sets default values for keywords that depend on other keywords.
        """
        should_update = lambda key: self.get(key) is None or only_missing is False

        if should_update("periods"):
            self["periods"] = self["bounds"][:, 1] - self["bounds"][:, 0]
        if should_update("iterpts"):
            self["iterpts"] = int(15 * self.dim ** 1.5)
        if should_update("pp_iters"):
            self["pp_iters"] = list(range(self["iterpts"] + 1))
            self["pp_iters"] = np.arange(0, self['iterpts'] + 1)
        if should_update("min_dist_acqs"):
            self["min_dist_acqs"] = 0.01 * min(self["periods"])

        # Default initial hyperparameters.
        if should_update("thetainit"):
            if self["ynorm"]:
                diff = 1.0 # when observations are range normalised
            else:
                diff = self["yrange"][1] - self["yrange"][0]
            self["thetainit"] = [0.5 * diff]  # sig
            for i in range(self.dim):  # lengthscales
                if self["kernel"][i] == "stdp":  # pbc
                    self["thetainit"].append(np.pi / 10)
                else:  # nonpbc
                    self["thetainit"].append(self["periods"][i] / 20)

        # Default hyperparameter constraints.
        if self["thetaprior"] is not None:
            if should_update("thetabounds"):
                self["thetabounds"] = [
                    [self["thetainit"][0] / 1000.0, self["thetainit"][0] * 1000.0]
                ]  # variance
                for i in range(self.dim):  # lengthscale
                    self["thetabounds"].append(
                        [
                            self["thetainit"][i + 1] / 100.0,
                            self["thetainit"][i + 1] * 100.0,
                        ]
                    )
                self["thetabounds"] = np.array(self["thetabounds"])

            # Default hyperparameter priors.
            if should_update("thetapriorpar"):
                if self["ynorm"]:
                    diff = 1.0 # when observations are range normalised
                else:
                    diff = self["yrange"][1] - self["yrange"][0]    
                if self["thetaprior"] == "gamma":

                    # Ulpu's heuristic prior
                    shape = 2.00
                    rate = 2.0/(diff/2.0)**2

                    # Original solution, to be tested further
                    #shape, rate = Distributions.gammaparams(
                    #    (diff/4)**2, (10*diff/4)**2, 0.5, 0.99)
                    #shape = 1.0    # NORMALIZATION
                    #rate = 1.5     # NORMALIZATION
                    self["thetapriorpar"] = [[shape, rate]]

                    for i in range(self.dim):
                        if self["kernel"][i] == "stdp":  # pbc
                            shape = 3.3678
                            rate = 9.0204
                        else:  # nonpbc
                            shape, rate = Distributions.gammaparams(
                                self["periods"][i] / 20, self["periods"][i] / 2
                            )
                        self["thetapriorpar"].append([shape, rate])
                    self["thetapriorpar"] = np.asarray(self["thetapriorpar"])
                else:
                    raise TypeError(
                        f"Unknown options set for thetaprior: {self['thetaprior']}."
                    )

        # Model slice and number of points.
        if should_update("pp_model_slice"):
            if self.dim == 1:
                self["pp_model_slice"] = np.array([1, 1, 50])
            else:
                self["pp_model_slice"] = np.array([1, 2, 25])

    @property
    def dim(self):
        """The dimensionality of the user-supplied objective.

        The number of dimensions is a read-only propery that is
        derived from the bounds provided by the user.

        Returns
        -------
        int
            The dimensionality of the objective.

        """
        return len(self["bounds"])

    @dim.setter
    def dim(self, val):
        raise AttributeError("Cannot modify read-only attribute: dim")

    def set_acqfn(self, name):
        if name == "elcb":
            self.acqfn = elcb
        elif name == "lcb":
            self.acqfn = lcb
            if len(self["acqfnpars"]) < 1:
                self["acqfnpars"] = np.array([2.0])  # explr_weight
        elif name == "explore":
            self.acqfn = explore
        elif name == "exploit":
            self.acqfn = exploit
        elif name == "ei":
            self.acqfn = ei
        else:
            raise TypeError(f"ERROR: Unknown acquisition function selected: {name}")

    def dump(self, file_path):
        """Writes the current settings to a boss input file.

        Parameters
        ----------
        fname : Union[str, path]
            Path to the destination file.
        """
        dump.dump_input_file(file_path, self)

    def correct(self):
        """Corrects the type and value of certain keywords.

        The user is allowed to be lazy in defining certain keywords,
        e.g., by providing lists instead of np.arrays, and we correct
        for this laziness here.
        """
        if self["pp_acq_funcs"] and self["verbosity"] < 2:
            self["verbosity"] = 2  # to have xnexts printed

        # Make sure int and float arrays are np and not python sequences.
        # and have the correct dtype
        for key, val in self.items():
            cat = bkw.find_category(key)
            cat_type, cat_dim = cat[0], cat[1]

            if cat_dim > 0 and cat_type != str and val is not None:
                if cat_type == int:
                    self[key] = np.asarray(val, dtype=np.int64)
                elif cat_type == float:
                    self[key] = np.asarray(val, dtype=np.float64)

        bounds = self['bounds']
        if bounds.ndim == 1:
            self['bounds'] = np.atleast_2d(bounds)

        kernel = self["kernel"]
        if isinstance(kernel, str):
            self["kernel"] = [kernel]

        if len(self["kernel"]) == 1:
            self["kernel"] *= self.dim

        # Exception to the above rule: gm_tol is a mixed list [float, int]
        # TODO: break gm_tol into two keywords in a future release
        gm_tol = self["gm_tol"]
        if gm_tol is not None:
            self["gm_tol"] = [float(gm_tol[0]), int(gm_tol[1])]
