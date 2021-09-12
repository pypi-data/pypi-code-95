import os
import shutil
import warnings

import numpy as np
from scipy.spatial.distance import euclidean

import boss.io.dump as dump
import boss.io.ioutils as ioutils
import boss.io.parse as parse
import boss.pp.plot as plot
from boss.bo.bo_main import BOMain
from boss.bo.model import Model
from boss.io.main_output import MainOutput
from boss.settings import Settings
from boss.utils.minimization import Minimization
from boss.bo.rstmanager import split_rst_data

warnings.filterwarnings("ignore")  # ignore warnings


def recreate_bo(settings, acqs, par):
    """Loads given data and parameters to a given model object. """
    dim = settings.dim
    X = acqs[:, :dim]
    Y = acqs[:, dim : dim + 1]
    bo = BOMain.from_settings(settings)
    bo.add_xy_list(X, Y)
    bo.model.set_unfixed_params(par)
    return bo


def _find_index(array, npts):
    if array.size == 0:
        return None
    else:
        ind = np.where(array[:, 0] == npts)[0]
        if ind.size == 0:
            return None
        else:
            return ind[-1]


class PPMain:
    """Performs the automated post-processing of a BOSS run. """

    def __init__(
        self,
        bo_results,
        pp_iters=None,
        pp_acq_funcs=None,
        pp_models=None,
        pp_model_slice=None,
        pp_var_defaults=None,
        pp_truef_at_xhats=None,
        pp_truef_npts=None,
        pp_local_minima=None,
    ):
        pp_settings = {
            "pp_iters": pp_iters,
            "pp_acq_funcs": pp_acq_funcs,
            "pp_models": pp_models,
            "pp_model_slice": pp_model_slice,
            "pp_var_defaults": pp_var_defaults,
            "pp_truef_at_xhats": pp_truef_at_xhats,
            "pp_truef_npts": pp_truef_npts,
            "pp_local_minima": pp_local_minima,
        }
        bo_results.settings.update(
            {k: v for k, v in pp_settings.items() if v is not None}
        )
        bo_results.settings.correct()

        self.bo_results = bo_results
        self.settings = bo_results.settings
        self.rstfile = self.settings["rstfile"]
        self.outfile = self.settings["outfile"]
        self.main_output = None
        self._setup()

    @classmethod
    def from_file(cls, rstfile, outfile, main_output=None):
        self = cls.__new__(cls)
        self.bo_results = None
        self.settings = Settings.from_file(rstfile)
        self.rstfile = rstfile
        self.outfile = outfile
        self.main_output = main_output
        cls._setup(self)
        return self

    @classmethod
    def from_settings(cls, settings, main_output=None):
        self = cls.__new__(cls)
        self.bo_results = None
        self.settings = settings
        self.rstfile = settings["rstfile"]
        self.outfile = settings["outfile"]
        self.main_output = main_output
        cls._setup(self)
        return self

    def _setup(self):
        """Common setup for all factory methods. """

        # User-specified model slices are interpreted as being indexed
        # from 1, so we convert to 0-based indexing here.
        self.settings["pp_model_slice"][:2] -= 1

        if not getattr(self, "main_output", None):
            self.main_output = MainOutput(self.settings)

        # Store paths to all PP-related files.
        self.files = {
            "acqs": "postprocessing/acquisitions.dat",
            "min_preds": "postprocessing/minimum_predictions.dat",
            "conv_meas": "postprocessing/convergence_measures.dat",
            "hypers": "postprocessing/hyperparameters.dat",
            "truehat": "postprocessing/true_f_at_x_hat.dat",
        }

        # Define a dict to hold all data structures used to generate the PP output.
        # The fundamental items are acqs, mod_par and min_preds: these must be extracted
        # from a BOMain object or read from file and can the be used to generate
        # xnexts, est_yranges and conv_meas.
        self.data = {
            "acqs": None,
            "mod_par": None,
            "min_preds": None,
            "xnexts": None,
            "est_yranges": None,
            "conv_meas": None,
        }

        # create needed directories
        if os.path.isdir("postprocessing"):
            print("warning: overwriting directory 'postprocessing'")

        shutil.rmtree("postprocessing", ignore_errors=True)
        os.makedirs("postprocessing", exist_ok=True)

        if self.settings["pp_models"]:
            os.makedirs("postprocessing/data_models", exist_ok=True)
            os.makedirs("postprocessing/graphs_models", exist_ok=True)
        if self.settings["pp_acq_funcs"]:
            os.makedirs("postprocessing/data_acqfns", exist_ok=True)
            os.makedirs("postprocessing/graphs_acqfns", exist_ok=True)
        if self.settings["pp_local_minima"] is not None:
            os.makedirs("postprocessing/data_local_minima", exist_ok=True)

    @property
    def slc_dim(self):
        sts = self.settings
        _slc_dim = 1 if sts["pp_model_slice"][0] == sts["pp_model_slice"][1] else 2
        return _slc_dim

    def run(self):
        self.load_data()
        self.dump_data()
        self.plot()

    def load_data(self):
        sts = self.settings
        dim = sts.dim
        initpts = sts["initpts"]
        iterpts = sts["iterpts"]
        minfreq = sts["minfreq"]
        totalpts = initpts + iterpts
        bo_results = self.bo_results

        # Obtain the basic output data: acqs, mod_bar, min_preds from BoMain,
        # or from boss out and rst files.
        if bo_results is not None:
            acqs = np.c_[np.arange(1, totalpts + 1), bo_results.X, bo_results.Y]

            mod_par = np.c_[np.arange(initpts, totalpts + 1), bo_results.hyperparams]

            # Determine loop indices for which convergence data was calculated.
            if 0 < minfreq < totalpts:
                imins = np.arange(initpts, totalpts, minfreq)
                imins = np.append(imins, totalpts)
            else:
                imins = np.array([totalpts])

            min_preds = np.c_[
                imins,
                np.array(list(bo_results.convergence[:, 2]), dtype=np.float64),
                bo_results.convergence[:, 3:],
            ]

        else:
            input_data = parse.parse_input_file(self.rstfile, skip="keywords")
            acqs, mod_par = split_rst_data(input_data["rst_data"], sts.dim)
            min_preds = parse.parse_min_preds(self.settings, self.outfile)

        # Generate the derived output data: xnexts, conv_meas and est_yranges.
        xnexts = []
        for i in range(len(acqs) - 1):
            xnexts.append([])
            xnexts[-1].append(acqs[i, 0])
            for n in range(dim):
                xnexts[-1].append(acqs[i + 1, 1 + n])
        xnexts = np.array(xnexts)

        est_yranges = np.array(
            [
                [acqs[i - 1, 0], max(acqs[:i, -1]) - min(acqs[:i, -1])]
                for i in range(1, len(acqs) + 1)
            ]
        )

        conv_meas = None
        if min_preds is not None:
            conv_meas = np.array(
                [
                    [
                        min_preds[i, 0],
                        euclidean(
                            min_preds[i - 1, 2 : dim + 2],
                            min_preds[i, 2 : dim + 2],
                        ),
                        abs(min_preds[i - 1, -2] - min_preds[i, -2])
                        / est_yranges[
                            _find_index(est_yranges, int(min_preds[i, 0])), -1
                        ],
                    ]
                    for i in range(1, len(min_preds))
                ]
            )

        self.data.update(
            {
                "conv_meas": conv_meas,
                "est_yranges": est_yranges,
                "xnexts": xnexts,
                "acqs": acqs,
                "mod_par": mod_par,
                "min_preds": min_preds,
            }
        )

    def dump_data(self):
        """Dump standard data. """
        acqs = self.data["acqs"]
        mod_par = self.data["mod_par"]
        min_preds = self.data["min_preds"]
        conv_meas = self.data["conv_meas"]
        totalpts = self.settings["initpts"] + self.settings["iterpts"]

        # Initialize dump files
        # 1. acquisitions
        ioutils.overwrite(
            self.files["acqs"],
            "# Data acquisitions " + "by iteration (iter npts x y)\n",
        )
        # 2. Minimum predictions
        if min_preds is not None:
            ioutils.overwrite(
                self.files["min_preds"],
                "# Global minimum predictions by iteration"
                + " (iter npts x_hat mu_hat nu_hat)\n",
            )

        # 3. Convergence measures
        if conv_meas is not None:
            ioutils.overwrite(
                self.files["conv_meas"],
                "# Convergence measures by iteration"
                + " (iter npts dx_hat abs(dmu_hat)/yrange)\n",
            )

        # 4. Hyperparameters
        ioutils.overwrite(
            self.files["hypers"],
            "# Model hyperparameter values by iteration"
            + " (iter npts parameters)\n",
        )
        # 5. True function values at xhats
        if self.settings["pp_truef_at_xhats"] and min_preds is not None:
            ioutils.overwrite(
                self.files["truehat"],
                "# True function value at x_hat locations"
                + " by iteration (iter npts f(x_hat) "
                + "f(x_hat)-mu_hat)\n",
            )

        for npts in range(1, totalpts + 1):
            it = npts - self.settings["initpts"]

            # acquisitions
            ind_acqs = _find_index(acqs, npts)
            if ind_acqs is not None:
                ioutils.append_write(
                    self.files["acqs"],
                    ioutils.data_line([it, npts], acqs[ind_acqs, 1:], fstr="%18.10E"),
                )

            # hyperparameters
            ind_par = _find_index(mod_par, npts)
            if ind_par is not None:
                ioutils.append_write(
                    self.files["hypers"],
                    ioutils.data_line([it, npts], mod_par[ind_par, 1:], fstr="%18.10E"),
                )

            # global minimum predictions
            ind_mp = None
            if min_preds is not None:
                ind_mp = _find_index(min_preds, npts)
                if ind_mp is not None:
                    ioutils.append_write(
                        self.files["min_preds"],
                        ioutils.data_line(
                            [it, npts], min_preds[ind_mp, 1:], fstr="%18.10E"
                        ),
                    )

            # convergence measures
            if conv_meas is not None:
                ind_cm = _find_index(conv_meas, npts)
                if ind_cm is not None:
                    ioutils.append_write(
                        self.files["conv_meas"],
                        ioutils.data_line(
                            [
                                it,
                                npts,
                                conv_meas[ind_cm, -2],
                                conv_meas[ind_cm, -1],
                            ],
                            fstr="%18.10E",
                        ),
                    )

            # true function at xhat
            if (
                self.settings["pp_truef_at_xhats"]
                and min_preds is not None
                and ind_mp is not None
            ):
                self.main_output.progress_msg("Evaluating true function at x_hat", 2)
                tfhat = self.settings.f(
                    np.atleast_2d(min_preds[ind_mp, 1 : self.settings.dim + 1])
                )
                muhat = min_preds[ind_mp, -2]
                ioutils.append_write(
                    self.files["truehat"],
                    ioutils.data_line([it, npts, tfhat, tfhat - muhat], fstr="%18.10E"),
                )

    def plot(self, target="all"):
        if target in ["hyperparameters", "all"]:
            self._plot_hypers()

        # Check that minimum predictions are present in the data, otherwise
        # we cannot plot any of the targets below.
        # TODO: Should implement post-run generation of min preds.
        # if self.data['min_preds'] is None:
        #     print(f'BOSS must be run with minfreq > 0 to plot target: {target}')
        #     return

        if target in ["acquisitions", "all"]:
            self._plot_acqs()

        if target in ["convergence", "all"]:
            self._plot_conv()

        if target in ["model", "all"]:
            self._plot_model()

        if target in ["truef", "all"]:
            self._plot_truef()

    def _plot_hypers(self):
        # plot standard data dumps
        hypers = np.atleast_2d(np.loadtxt(self.files["hypers"], skiprows=1))
        if len(hypers) > 1:
            plot.plot_hyperparameters(
                self.settings, "postprocessing/hyperparameters.png", hypers
            )

    def _plot_acqs(self):
        minp = np.atleast_2d(np.loadtxt(self.files["min_preds"], skiprows=1))

        if len(minp[0]) == 0:
            raise ValueError("No minimal points found in out-file.")
        acqs_data = np.atleast_2d(np.loadtxt(self.files["acqs"], skiprows=1))

        if len(acqs_data) > 1:
            plot.plot_data_acquisitions(
                self.settings,
                "postprocessing/acquisition" + "_locations.png",
                acqs_data,
                minp,
            )

    def _plot_conv(self):
        minp = np.atleast_2d(np.loadtxt(self.files["min_preds"], skiprows=1))

        if len(minp[0]) == 0:
            raise ValueError("No minimal points found in out-file.")

        conv_meas = np.atleast_2d(np.loadtxt(self.files["conv_meas"], skiprows=1))
        if len(conv_meas) > 1:
            plot.plot_conv_measures(
                self.settings, "postprocessing/convergence_measures.png", conv_meas
            )

        if self.settings["pp_truef_at_xhats"]:
            truef_hats = np.atleast_2d(np.loadtxt(self.files["truehat"], skiprows=1))
            if len(truef_hats) > 1:
                plot.plot_truef_hat(
                    self.settings,
                    "postprocessing/true_function" + "_at_xhats.png",
                    truef_hats,
                )

    def _plot_model(self):
        acqs = self.data["acqs"]
        mod_par = self.data["mod_par"]
        conv_meas = self.data["conv_meas"]
        min_preds = self.data["min_preds"]
        xnexts = self.data["xnexts"]
        sts = self.settings
        slc_dim = self.slc_dim

        # recreate snapshots of model in a loop for all pp_iters
        curr_xhat = None

        for it in sts["pp_iters"]:

            npts = sts["initpts"] + it
            ind_acqs = _find_index(acqs, npts)
            ind_par = _find_index(mod_par, npts)

            if ind_acqs is None or ind_par is None:
                self.main_output.progress_msg(
                    "Could not find data or "
                    + " parameters to recreate model at iteration %i," % (it)
                    + " skipping post-processing for that iteration.",
                    0,
                )
                continue

            self.main_output.progress_msg("Post-processing iteration %i" % (it), 1)
            bo = recreate_bo(sts, acqs[: ind_acqs + 1, 1:], mod_par[ind_par, 1:])
            assert npts == bo.model.X.shape[0], "Model recreate fail!"

            # find current xhat
            ind_mp = _find_index(min_preds, npts)
            if ind_mp is not None:
                curr_xhat = min_preds[ind_mp, 1 : sts.dim + 1]
            ind_cm = _find_index(conv_meas, npts)

            # Local minima
            if sts["pp_local_minima"] is not None:
                self.main_output.progress_msg("Finding model local minima", 2)
                mins = Minimization.minimize(
                    bo.model.predict_mean_grad,
                    sts["bounds"],
                    sts["kernel"],
                    np.hstack([bo.get_x(), bo.get_y()]),
                    sts["min_dist_acqs"],
                    accuracy=sts["pp_local_minima"],
                    args=(),
                    lowest_min_only=False,
                )

                mins = sorted(mins, key=lambda x: (x[1]))
                minima_data = [[]] * (sts.dim + 2)
                for m in mins:
                    p = []
                    for i in range(sts.dim):
                        p.append(m[0][i])
                    p.append(bo.get_mu(m[0]))
                    p.append(bo.get_nu(m[0]))
                    minima_data = np.insert(minima_data, len(minima_data[0]), p, axis=1)

                titleLine = "# Local minima (x mu nu) - model data ensemble size %i" % (
                    npts
                )
                ioutils.write_cols(
                    "postprocessing/data_local_minima/"
                    "it%.4i_npts%.4i.dat" % (it, npts),
                    minima_data,
                    titleLine=titleLine,
                )
            # Model (cross-sections)
            if sts["pp_models"]:
                dump.dump_model(
                    sts,
                    "postprocessing/data_models/it%.4i_npts%.4i.dat" % (it, npts),
                    bo,
                    bo.model.get_all_params(),
                    curr_xhat,
                )
                mdata = np.loadtxt(
                    "postprocessing/data_models/" + "it%.4i_npts%.4i.dat" % (it, npts),
                    skiprows=2,
                )
                if ind_mp is not None:
                    xhat = min_preds[ind_mp, 1 : sts.dim + 1]
                else:
                    xhat = None
                macqs = acqs[: ind_acqs + 1, 1:]
                if slc_dim < sts.dim and slc_dim == 1:
                    macqs = None

                ind_xnext = _find_index(xnexts, npts)
                if ind_xnext is not None:
                    xnext = xnexts[ind_xnext, 1:]
                else:
                    xnext = None

                if sts["pp_local_minima"] is not None and slc_dim == sts.dim:
                    minima = np.atleast_2d(np.array(minima_data)).T
                else:
                    minima = None

                plot.plot_model(
                    sts,
                    "postprocessing/graphs_models/it%.4i_npts%.4i" ".png" % (it, npts),
                    mdata,
                    xhat,
                    macqs,
                    xnext,
                    minima,
                )

            # acquisition function (cross-sections)
            if sts["pp_acq_funcs"] and it >= 0:
                ind_xnext = _find_index(xnexts, npts)
                if ind_xnext is not None:
                    defs = xnexts[ind_xnext, 1:]
                else:
                    defs = curr_xhat
                xn, acqfn = bo._acqnext(it)
                dump.dump_acqfn(
                    sts,
                    "postprocessing/data_acqfns/it%.4i_npts%.4i.dat" % (it, npts),
                    bo,
                    acqfn,
                    defs,
                )
                acqfn_data = np.loadtxt(
                    "postprocessing/data_acqfns/" + "it%.4i_npts%.4i.dat" % (it, npts),
                    skiprows=1,
                )
                if ind_mp is not None and slc_dim == sts.dim:
                    xhat = min_preds[ind_mp, 1 : sts.dim + 1]
                else:
                    xhat = None
                macqs = acqs[: ind_acqs + 1, 1:] if slc_dim == 2 else None
                ind_xnext = _find_index(xnexts, npts)
                if ind_xnext is not None:
                    xnext = xnexts[ind_xnext, 1:]
                else:
                    xnext = None

                plot.plot_acq_func(
                    sts,
                    "postprocessing/graphs_acqfns/" "it%.4i_npts%.4i.png" % (it, npts),
                    acqfn_data,
                    macqs,
                    xhat,
                    xnext,
                )

    def _plot_truef(self):
        """Dump and plot true function (cross-section). """

        sts = self.settings
        min_preds = self.data["min_preds"]
        acqs = self.data["acqs"]
        xnexts = self.data["xnexts"]
        slc_dim = self.slc_dim

        if sts["pp_truef_npts"] is None:
            # print("BOSS must be run with pp_truef_npts to plot the true function. ")
            return

        self.main_output.progress_msg("Dumping and plotting true function", 1)

        # if curr_xhat is None:
        curr_xhat = min_preds[-1, 1 : sts.dim + 1]

        dump.dump_truef(sts, "postprocessing/true_func.dat", curr_xhat)
        truef_data = np.loadtxt("postprocessing" + "/true_func.dat", skiprows=1)
        plot.plot_truef(sts, "postprocessing/true_func.png", truef_data)
        ind = np.where(min_preds[:, 1 : sts.dim + 1] == curr_xhat)[0][0]
        truef_slc_xhat_npts = int(min_preds[ind, 0])

        # replot 1D models with truef if it is now available
        if not (
            sts["pp_model_slice"][0] == sts["pp_model_slice"][1] and sts["pp_models"]
        ):
            print(
                "Replotting of 1D models with the true function requires pp_models and pp_model_slice[0]==pp_model_slice[1]"
            )
            return

        self.main_output.progress_msg("Replotting 1D models with true" + " function", 1)
        for mdat_file in os.listdir("postprocessing/data_models"):

            # find it and and npts from naming it%.4i_npts%.4i.dat
            negit = True if mdat_file[2] == "-" else False
            it = int(mdat_file[2:6]) if not negit else int(mdat_file[2:7])
            npts = int(mdat_file[-8:-4])
            mdata = np.loadtxt(
                "postprocessing/data_models/" + "it%.4i_npts%.4i.dat" % (it, npts),
                skiprows=2,
            )
            ind_mp = _find_index(min_preds, npts)
            if ind_mp is not None:
                xhat = min_preds[ind_mp, 1 : sts.dim + 1]
            else:
                xhat = None
            ind_acqs = _find_index(acqs, npts)
            macqs = acqs[: ind_acqs + 1, 1:]
            if slc_dim < sts.dim and slc_dim == 1:
                macqs = None
            ind_xnext = _find_index(xnexts, npts)
            if ind_xnext is not None and slc_dim == sts.dim:
                xnext = xnexts[ind_xnext, 1:]
            else:
                xnext = None

            if sts["pp_local_minima"] is not None and slc_dim == sts.dim:
                minima = np.loadtxt(
                    "postprocessing/data_local_"
                    + "minima/it%.4i_npts%.4i.dat" % (it, npts),
                    skiprows=1,
                )
                minima = np.atleast_2d(minima)
            else:
                minima = None

            if npts != truef_slc_xhat_npts and slc_dim < sts.dim:
                truef_d = None
            else:
                truef_d = truef_data

            plot.plot_model(
                sts,
                "postprocessing/graphs_models/" + "it%.4i_npts%.4i.png" % (it, npts),
                mdata,
                xhat,
                macqs,
                xnext,
                minima,
                truef_d,
            )
