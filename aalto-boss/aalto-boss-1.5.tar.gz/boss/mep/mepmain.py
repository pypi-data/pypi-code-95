import os
import shutil

from boss.mep.mep import MEP
from boss.mep.space import Space
import boss.io.dump as dump
import boss.io.ioutils as ioutils
import boss.io.parse as parse
from boss.pp.pp_main import recreate_bo
import boss.pp.plot as plot


class MEPMain:
    def __init__(self, settings, ipt_rstfile, minimafile, main_output):
        # create needed directories
        if os.path.isdir("mep"):
            print("warning: overwriting directory 'mep'")
        shutil.rmtree("mep", ignore_errors=True)
        os.makedirs("mep", exist_ok=True)

        # recreate model and read local minima
        self.get_model(settings, ipt_rstfile, main_output)
        self.get_minima(minimafile, main_output)
        self.get_space(settings)

        # initialize and run
        mep = MEP(
            self.bo,
            self.space,
            self.minima,
            settings["mep_precision"],
            settings["mep_rrtsteps"],
            settings["mep_nebsteps"],
            settings["mep_maxe"],
        )
        mep.run_mep(main_output)

        # write to file
        for path in mep.fullpaths:
            dump.dump_mep(path)

        # plot
        if self.minima.shape[1] == 2:
            self.plot2D(settings, mep)

    def get_model(self, settings, ipt_rstfile, main_output):
        acqs, mod_par = parse.parse_rst(settings, ipt_rstfile)
        self.bo = recreate_bo(
            settings,
            acqs[:, 1:],
            mod_par[mod_par.shape[0] - 1, 1:],
            main_output,
        )

    def get_minima(self, minimafile, main_output):
        self.minima = parse.parse_minima(minimafile)
        self.minima = self.minima[:, :-2]

    def get_space(self, settings):
        bounds = np.transpose(settings["bounds"])
        pbc = np.array(settings["kernel"]) == "stdp"
        if not np.all(settings["periods"] == (bounds[1, :] - bounds[0, :])):
            print("warning: MEP currently assumes periods to match " + "boundlength")
        self.space = Space(bounds, pbc)

    def plot2D(self, settings, mep):
        it = np.max(settings["pp_iters"])
        npts = settings["initpts"] + it
        fname = "postprocessing/data_models/" + "it%.4i_npts%.4i.dat" % (it, npts)
        if not files_ok([fname]):
            print(
                "Model data of the last iteration is required for "
                + "automatic 2D plotting, check\nthe 'pp_models' "
                + "and 'pp_iters' options, then try rerunning postprocessing."
            )
            return
        mdata = ioutils.read_cols(fname, skiprows=2)
        xhat = None
        xnext = None
        minima = self.minima
        truef = None

        plot.model(
            settings,
            "mep/minpaths.png",
            mdata,
            minima=self.minima,
            incl_uncert=False,
            paths=mep.fullpaths,
        )


def files_ok(filenames):
    """
    Checks that the given files exist and can be opened.
    """
    for fname in filenames:
        try:
            f = open(fname, "r")
            f.close()
        except FileNotFoundError:
            print("Could not find file '" + fname + "'")
            return False
    return True
