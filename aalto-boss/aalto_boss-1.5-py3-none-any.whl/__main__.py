import sys

from boss import __version__
from boss.bo.bo_main import BOMain
from boss.settings import Settings
from boss.io.main_output import MainOutput
from boss.mep.mepmain import MEPMain
from boss.pp.pp_main import PPMain
from boss.bo.rstmanager import RstManager
from boss.utils.timer import Timer
from boss.io.parse import parse_input_file


def main(args=None):
    """The main routine."""
    # start timers
    local_timer = Timer()

    if args is None:
        args = sys.argv[1:]

    if not args_ok(args):  # Exit immediately if one or more args are invalid.
        print(
            "BOSS version "
            + str(__version__)
            + "\n"
            + "Usage:\n"
            + "   boss op <inputfile or rst-file>\n"
            + "   boss o <inputfile or rst-file>\n"
            + "   boss p <rst-file> <out-file>\n"
            + "   boss m <rst-file> <minima-file>\n"
            + "See the documentation for further instructions."
        )
        return

    if not files_ok(args[1:]):  # Exit immediately if input file doesn't open.
        return

    input_data = parse_input_file(args[1])
    settings = Settings(input_data["keywords"])

    # Don't overwrite an optimization run's outfile.
    if len(args) == 3:
        ipt_outfile = args[2]
        if "m" in args[0]:
            settings["outfile"] = settings["outfile"][:-4] + "_mep.out"
        else:
            settings["outfile"] = settings["outfile"][:-4] + "_pp.out"

    main_output = None

    # 1. Run bayesian optimization. Note: if we run an optimization we let BOMain
    # handle the MainOutput
    if "o" in args[0] and (settings["initpts"] + settings["iterpts"]) > 0:
        local_timer.startLap()

        rst_data = input_data.get("rst_data", None)
        bo = BOMain.from_settings(settings, rst_data)
        main_output = bo.main_output
        bo.run()

        main_output.progress_msg(
            "| Bayesian optimization completed, "
            + "time [s] %s" % (local_timer.str_lapTime()),
            1,
            True,
            True,
        )

    # If no optmization was run, we need to initialize the MainOutput and
    # start a new file manually
    if not main_output:
        main_output = MainOutput(settings)
        main_output.new_file()

    # 2. Run post-processing.
    if "p" in args[0] and len(settings["pp_iters"]) > 0:
        local_timer.startLap()
        main_output.progress_msg("Starting post-processing...", 1, True)
        main_output.section_header("POST-PROCESSING")

        ipt_rstfile = settings["rstfile"] if "o" in args[0] else args[1]
        if len(args) != 3:
            ipt_outfile = settings["outfile"]

        settings["rstfile"] = ipt_rstfile
        settings["outfile"] = ipt_outfile

        pp_main = PPMain.from_settings(settings, main_output)
        pp_main.run()

        main_output.progress_msg(
            "Post-processing completed, " + "time [s] %s" % (local_timer.str_lapTime()),
            1,
        )

    # 3. Find minimum energy paths.
    if "m" == args[0]:
        local_timer.startLap()
        main_output.progress_msg("Finding minimum energy paths...", 1, True)
        main_output.section_header("MINIMUM ENERGY PATHS")

        MEPMain(settings, args[1], args[2], main_output)
        main_output.progress_msg(
            "Finding minimum energy paths completed, "
            + "time [s] %s" % (local_timer.str_lapTime()),
            1,
        )

    main_output.footer(local_timer.str_totalTime())


def args_ok(args):
    """
    Checks that the user has called BOSS properly by examining the arguments
    given, number of files and filename extensions. BOSS should be called with
    one of the following:
        boss o options/.rst-file
        boss op options/.rst-file
        boss p .rst-file .out-file
        boss m .rst-file local_minima.dat
    """
    # TODO prevent calling boss pm
    some_args = len(args) > 0
    if some_args:
        optim_ok = "o" in args[0] and len(args) == 2
        justpp_arg_ok = "o" not in args[0] and "p" in args[0] and len(args) == 3
        mep_arg_ok = "o" not in args[0] and "m" in args[0] and len(args) == 3
        rst_incl = len(args) >= 2 and ".rst" in args[1]
        out_incl = len(args) == 3 and ".out" in args[2]
        dat_incl = len(args) == 3 and ".dat" in args[2]
        justpp_ok = justpp_arg_ok and rst_incl and out_incl
        mep_ok = mep_arg_ok and rst_incl and dat_incl
    return some_args and (optim_ok or justpp_ok or mep_ok)


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


# Start BOSS
if __name__ == "__main__":
    main()
