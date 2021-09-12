import datetime
import os

import numpy as np

import boss.io.ioutils as io
import boss.keywords as bkw
from boss import __version__


class MainOutput:
    """
    Functionality to write to the main output (*.out) file.
    """

    def __init__(self, settings):
        self.ipfile = settings["ipfile"]
        self.outfile = settings["outfile"]
        self.verbosity = settings["verbosity"]
        self.utils = io
        self.settings = settings

    def new_file(self):
        """Intializes a new main output file with header, input file and settings. """
        if os.path.isfile(self.outfile):
            print("warning: overwriting file '" + self.outfile + "'")

        self.header()
        if os.path.isfile(self.ipfile):
            self.ipfile_repeat(self.settings)

        self.add_settings(self.settings)

    def header(self):
        """
        Writes a header to main output file overwriting a possibly existing
        old output file at the same filepath.
        """
        s = (
            "\n-----------------------------   Welcome to ....   ----------"
            + "--------------------\n"
            + "                      _______  _______ _______ _______ \n"
            + "                     |   _   \|   _   |   _   |   _   |\n"
            + "                     |.  1   /|.  |   |   1___|   1___|\n"
            + "                     |.  _   \|.  |   |____   |____   |\n"
            + "                     |:  1    |:  1   |:  1   |:  1   |\n"
            + "                     |::.. .  |::.. . |::.. . |::.. . |\n"
            + "                     `-------'`-------`-------`-------'\n\n"
            + "{:^80s}\n".format("Version " + str(__version__))
            + "{:^80s}\n".format(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
            + "------------------------------------------------------------"
            + "--------------------\n\n"
        )
        with open(self.outfile, "w") as fd:
            fd.write(s)

    def footer(self, totaltime):
        """
        Writes a footer to main output file
        """
        text = "BOSS is done! Have a nice day :)"
        s = (
            "\n\n--------------------------------------------------------"
            + "------------------------\n"
        )
        s += "{:^80s}\n\n".format(text)
        s += "{:^40s}".format(
            datetime.datetime.now().strftime("Datetime %d-%m-%Y %H:%M:%S")
        )
        s += "{:^40s}".format("Total time [s] %s" % (totaltime))  # code total time
        s += (
            "\n---------------------------------------------------------"
            + "-----------------------\n"
        )
        with open(self.outfile, "a") as fd:
            fd.write(s)

    def ipfile_repeat(self, is_rst):
        """
        Repeats the input file near the beggining of the main output file.
        """
        if self.verbosity > 0:
            self.progress_msg("Reading BOSS input file from: " + self.ipfile, 0)
            self.progress_msg("Initializing...\n", 0)
            self.section_header("INPUT FILE")
            s = ""
            with open(self.ipfile, "r") as f:
                line = f.readline()
                while len(line) > 0:
                    s += line
                    line = f.readline()

            with open(self.outfile, "a") as fd:
                fd.write(s)

    def add_settings(self, settings):
        """
        Outputs the interpreted code variable settings to main output file.
        """
        if self.verbosity > 0:
            self.section_header("SIMULATION OPTIONS")
            s = "|| File input/output \n"
            s += "ipfile         %s\n" % (settings["ipfile"])
            s += "userfn         %s\n" % (bkw.stringify(settings["userfn"]))
            s += "outfile        %s\n" % (settings["outfile"])
            s += "rstfile        %s\n\n" % (settings["rstfile"])

            s += "|| Key settings \n"
            s += (
                "bounds        "
                + io.twoDfloatarray_line(settings["bounds"], settings.dim, 2)
                + "\n"
            )
            s += (
                "kerntype      "
                + io.oneDarray_line(settings["kernel"], settings.dim, str)
                + "\n"
            )
            if np.any(settings["kernel"] == "stdp"):
                s += (
                    "periods      "
                    + io.oneDarray_line(settings["periods"], settings.dim, float)
                    + "\n"
                )
            s += (
                "yrange        "
                + io.oneDarray_line(settings["yrange"], 2, float)
                + "\n"
            )
            s += "noise          %8.3E\n" % (settings["noise"])
            if not settings.is_rst:
                s += "inittype       %s\n" % (settings["inittype"])
            s += "initpts   %i    iterpts   %i\n" % (
                settings["initpts"],
                settings["iterpts"],
            )
            if settings["gm_tol"] is not None:
                s += "gm_tol         %8.3E   %i\n" % (
                    settings["gm_tol"][0],
                    settings["gm_tol"][1],
                )
            else:
                s += "gm_tol         none\n"
            s += "verbosity      %i\n\n" % (settings["verbosity"])

            s += "|| Data acquisition \n"
            s += "acqfn                %s\n" % (settings["acqfn_name"])
            s += "acqtol               "
            if settings["acqtol"] is None:
                s += "none\n"
            else:
                s += "%8.3E\n" % (settings["acqtol"])
            s += "\n"

            s += "|| GP hyperparameters \n"
            s += (
                "thetainit      "
                + io.oneDarray_line(settings["thetainit"], settings.dim, float)
                + "\n"
            )
            s += (
                "thetabounds    "
                + io.twoDfloatarray_line(settings["thetabounds"], settings.dim + 1, 2)
                + "\n"
            )
            s += "thetaprior      %s\n" % (settings["thetaprior"])
            s += (
                "thetapriorpar  "
                + io.twoDfloatarray_line(settings["thetapriorpar"], settings.dim + 1, 2)
                + "\n\n"
            )

            s += "|| Hyperparameter optimization\n"
            s += "updatefreq   %i  initupdate      %s\n" % (
                settings["updatefreq"],
                str(settings["initupdate"]),
            )
            s += "updateoffset %i  updaterestarts  %i\n\n" % (
                settings["updateoffset"],
                settings["updaterestarts"],
            )

            if len(settings["pp_iters"]) > 0:
                s += "| postprocessing\n"
                # s += "pp_iters          ="
                # s += io.oneDarray_line(settings["pp_iters"],len(settings["pp_iters"]),int)+"\n"
                s += "pp_models         = %s\n" % (settings["pp_models"])
                s += "pp_acq_funcs      = %s\n" % (settings["pp_acq_funcs"])
                s += "pp_truef_npts     = "
                if settings["pp_truef_npts"] is None:
                    s += "none\n"
                else:
                    s += "%i\n" % (settings["pp_truef_npts"])
                s += "pp_model_slice        ="
                s += (
                    io.oneDarray_line(
                        settings["pp_model_slice"], len(settings["pp_model_slice"]), int
                    )
                    + "\n"
                )
                if settings["pp_var_defaults"] is not None:
                    s += "pp_var_defaults   ="
                    s += (
                        io.oneDarray_line(
                            settings["pp_var_defaults"],
                            len(settings["pp_var_defaults"]),
                            float,
                        )
                        + "\n"
                    )
                s += "pp_truef_at_xhats = %s\n" % (settings["pp_truef_at_xhats"])
                s += "pp_local_minima   = "
                if settings["pp_local_minima"] is None:
                    s += "none\n\n"
                else:
                    s += "%i\n\n" % (settings["pp_local_minima"])
            with open(self.outfile, "a") as fd:
                fd.write(s)

    def progress_msg(self, msg, priority, preceding_bl=False, nospace=False):
        """
        Announce progress message to main output file depending on verbosity.
        """
        m = ""
        if self.verbosity >= priority:
            if preceding_bl:
                m = m + "\n"
            m = m + "|"
            if not nospace:
                m = m + " "
            m = m + msg + "\n"

        with open(self.outfile, "a") as fd:
            fd.write(m)

    def convergence_stop(self):
        """
        Announces BO stop due to global minimum convergence
        """
        msg = "Stopped BO due to global minimum prediction convergence"
        self.progress_msg(msg, 0, True)

    def iteration_start(self, i_iter):
        """
        Output section header for the new iteration.
        """
        initpts = self.settings["initpts"]
        if i_iter <= initpts:
            text = "INITIAL DATAPOINT " + str(i_iter)
        else:
            text = "BO ITERATION " + str(i_iter - initpts)
        s = (
            "\n--------------------------------------------------------"
            + "------------------------\n"
        )
        s += "{:^80}".format(text)
        s += (
            "\n---------------------------------------------------------"
            + "-----------------------\n"
        )
        with open(self.outfile, "a") as fd:
            fd.write(s)

    def iteration_summary(
        self,
        i_iter,
        datasize,
        newXs,
        newYs,
        convergence,
        xnext,
        est_yrange,
        model_params,
        timer,
    ):
        """
        Outputs info about one BO iteration to main output file
        """
        sts = self.settings
        initpts = sts["initpts"]
        iterpts = sts["iterpts"]
        totalpts = initpts + iterpts
        minfreq = sts["minfreq"]

        iconv = i_iter - initpts + 1
        write_conv = iconv >= 0 and (
            iconv == iterpts or (minfreq > 0 and (iconv % minfreq == 0))
        )

        if write_conv:
            xbest, ybest, xhat, muhat, nuhat = convergence[-1, :]
            d_xhat, d_muhat = np.nan, np.nan
            if convergence.shape[0] > 1:
                prev_xhat, prev_muhat = convergence[-2, [2, 3]]
                d_xhat = np.linalg.norm(xhat - prev_xhat)
                d_muhat = np.linalg.norm(muhat - prev_muhat) / est_yrange

        # self.progress_msg("-Iteration summary-", 0, True)
        s = "| Data point added to dataset (x y): \n"
        newXs = np.atleast_2d(newXs)
        newYs = np.atleast_1d(newYs)

        for i in range(len(newYs)):
            s += io.data_line(newXs[i], [newYs[i]], fstr="%18.10E")
        s += "\n| Total ensemble size: %i\n" % datasize

        # Model
        if not np.any(model_params == None):  # Only BO iterations
            if write_conv:
                if self.verbosity > 0:
                    s += "| Best acquisition, x_best y_best:\n"
                    s += io.data_line(xbest.flatten(), ybest.flatten(), fstr="%18.10E")
                s += "| Global minimum prediction, x_hat mu_hat +- nu_hat:\n"
                s += io.data_line(xhat.flatten(), [muhat, nuhat], fstr="%18.10E")
                # Convergence
                if self.verbosity > 1 and not np.any(np.isnan([d_xhat, d_muhat])):
                    s += "| Global minimum convergence, d_xhat d_muhat:\n"
                    s += io.data_line([d_xhat, d_muhat], fstr="%18.10E")

            if self.verbosity > 1:
                s += "\n| GP model hyperparameters:\n"
                s += io.data_line(model_params, fstr="%18.10E")
        if self.verbosity > 1:
            s += "| Next sampling location x_next:\n"
            s += io.data_line(xnext.flatten(), fstr="%18.10E")
        s += "\nIteration time [s]: %8.3f" % (timer.getLapTime())
        s += "        Total time [s]: %8.3f" % (timer.getTotalTime())
        with open(self.outfile, "a") as fd:
            fd.write(s + "\n")

    def section_header(self, text):
        """
        Writes a section header to main output file.
        """
        s = (
            "--------------------------------------------------------"
            + "------------------------\n"
        )
        s += "{:^80s}\n".format(text)
        s += (
            "---------------------------------------------------------"
            + "-----------------------\n"
        )
        with open(self.outfile, "a") as fd:
            fd.write(s)

    def mep_start(self, mep):
        """
        Writes MEP options and local minima
        """
        s = ""
        s += "|| MEP options\n"
        s += "precision %8d    maxE      %8.3E\n" % (mep.precision, mep.maxE)
        s += "rrtsteps  %8d    nebsteps   %8d\n" % (mep.rrtsteps, mep.nebsteps)
        s += "\n"
        s += "Energy threshold starting at %8.3E, stepsize %8.3E.\n" % (
            mep.e_start,
            mep.stepsize,
        )
        s += "\n"

        s += "|| Minima\n"
        s += "(pt index, coordinates)\n"
        for i in range(mep.min_points.shape[0]):
            s += str(i)
            for j in range(mep.min_points.shape[1]):
                s += " " + str(mep.min_points[i, j])
            s += "\n"
        s += "\n"

        with open(self.outfile, "a") as fd:
            fd.write(s)

    def mep_result(self, mep):
        """
        Writes the results of MEP
        """
        s = "\n"
        s += "|| MEP results\n"
        s += "(pt index, pt index, highest energy on the minimum energy path)\n"
        l = mep.min_points.shape[0]
        e = np.zeros((l, l))
        for path in mep.fullpaths:
            e[path.mi, path.mj] = path.maxe

        for i in range(l):
            for j in range(l):
                if i < j:
                    s += "%d %d %8.3E\n" % (i, j, e[i, j])

        s += "\n"
        with open(self.outfile, "a") as fd:
            fd.write(s)
