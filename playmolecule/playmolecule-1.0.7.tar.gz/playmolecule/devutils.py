# Utilities necessary inside PM apps
import os


def tarFolder(folder, outtar=None, arcname=""):
    import tarfile

    folder = os.path.abspath(folder)
    parentdir = os.path.dirname(folder)
    foldername = os.path.basename(folder)

    if outtar is None:
        outtar = os.path.join(parentdir, f"{foldername}.tar.gz")

    with tarfile.open(outtar, "w:gz") as tar:
        tar.add(folder, arcname=arcname)

    return outtar


def getJobId(configpath):
    """
    Returns the job id stored in the config file

    Parameters
    ----------
    configpath: str
        The file path for the config file

    Returns
    -------
    jobid: str
        The id of the job
    """
    import json

    jobId = json.load(open(configpath, "r"))["execid"]
    return jobId


def setAsCompleted(outdir):
    """
    Writes the sentinel for the complete job.

    Parameters
    ----------
    outdir: str
        The location where to write the sentinel file
    """
    writeSentinel("pmwsjob.done", outdir)


def setAsError(outdir):
    """
    Writes the sentinel for the error job.

    Parameters
    ----------
    outdir: str
        The location where to write the sentinel file
    """
    writeSentinel("pmwsjob.err", outdir)


def setAsSleep(outdir):
    """
    Writes the sentinel for the complete job.

    Parameters
    ----------
    outdir: str
        The location where to write the sentinel file
    """
    writeSentinel("pmwsjob.sleep", outdir)


def writeSentinel(fname, outfolder, message=None):
    """
    Writes a sentinel file. A message can be written in the file

    Parameters
    ----------
    fname: str
        The sentinel file name
    outfolder: str
        The location where to write the sentinel file
    message: str
        The text to write in the sentinel file

    """
    import yaml

    fout = os.path.join(outfolder, fname)

    f = open(fout, "w")
    if message is not None:
        if isinstance(message, dict):
            yaml.dump(message, f, default_flow_style=True)
        else:
            f.write("{}\n".format(message))
    f.close()


def basenameInputs(parser, args, prefix="."):
    """
    Returns the basename of the value for the file arguments

    Parameters
    ----------
    parser: argparse.ArgumentParser
        The argparse parser
    args: dict
        The dictionary of the arguments to inspect
    prefix: str
        The path prefix to apply to the basename
    Returns
    -------
    args: dict
        The dictionary of the arguments with the basename value (for files)
    """
    for action in parser._actions:
        if (
            action.metavar == "FILE"
        ):  # For DIRECTORY should not use basename but the equivalent
            value = args[action.dest]
            if value is None or value == "":
                continue
            if isinstance(value, list):
                tmp_args = []
                for v in value:
                    if v == "":
                        continue
                    bname = os.path.basename(v)
                    oname = os.path.join(prefix, bname)
                    tmp_args.append(oname)
                args[action.dest] = tmp_args
            else:
                bname = os.path.basename(value)
                tmponame = (
                    bname if bname != "" else os.path.normpath(value).split("/")[-1]
                )
                oname = os.path.join(prefix, tmponame)
                args[action.dest] = oname
    return args


def writeInputsOptionsLog(path, parser, varset, debug=False):
    """
    Writes a log file, in yml format file, reporting all the options used for the current simulations.

    Parameters
    ----------
    parser: argparse.ArgumentParser
        The argparse parser
    path: str
        The folder destination where to write the log
    varset: Namespace
        The namespace that contains all the options used
    debug: bool
        Set as True if you want to write the debug value
    """
    import yaml

    fname = os.path.join(path, "inopt.yml")
    options = {k: ("" if v is None else v) for k, v in vars(varset).items()}
    if options["outdir"].startswith("/data/out"):
        del options["outdir"]
    if options["scratchdir"].startswith("/data/scratch"):
        del options["scratchdir"]
    if not debug:
        del options["debug"]
    options = basenameInputs(parser, options, prefix="")

    with open(fname, "w") as outfile:
        yaml.dump(options, outfile, default_flow_style=False)


def zipdir(path, ziph):
    """
    Adds all the tree files of the folder passed into the zip file
    Parameters
    ----------
    path: str
        The path to add to the zip file
    ziph: zipfile.ZipFile
        The zipfile object
    """
    # ziph is zipfile handle
    for root, _, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file), os.path.join(path, "..")),
            )


def zipit(dir_list, zip_name):
    """
    Creates the zip file with all the files and folder passed

    Parameters
    ----------
    dir_list: list
        The list of files and folders to zip
    zip_name: str
        The name of the zipfile
    """
    import zipfile

    zipf = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)
    for dir in dir_list:
        if os.path.isdir(dir):
            zipdir(dir, zipf)
        else:
            zipf.write(dir, os.path.basename(dir))
    zipf.close()


def unzipit(z, tmpdir="./tmp", overwrite=False, outdir=None):
    """
    Returns a list with the files in the zip file (when a zip). In alternative, a list with the passed file/folder

    Paramteres
    ----------
    z: str
        The path file

    Returns
    -------
    inps: list
        A list of the file in zip or the file/folder as unique item list
    """
    import zipfile
    import shutil
    from glob import glob

    if not zipfile.is_zipfile(z):
        return [z]
    tmpdir = os.path.normpath(tmpdir)
    os.makedirs(tmpdir, exist_ok=True)

    with zipfile.ZipFile(z, "r") as zip_file:
        zip_file.extractall(tmpdir)

    tmpinps = glob(tmpdir + "/*")
    if outdir is None:
        outdir = os.getcwd()

    inps = []
    for f in tmpinps:
        b = os.path.basename(f)
        o = os.path.join(outdir, b)
        if os.path.exists(o) and not overwrite:
            continue
        if os.path.exists(o) and overwrite and os.path.isdir(o):
            shutil.rmtree(o)
        if os.path.exists(o) and overwrite and os.path.isfile(o):
            os.remove(o)
        shutil.move(f, o)
        inps.append(o)
    shutil.rmtree(tmpdir)

    return inps


def pmtryexcept(arg1, arg2, arg3):
    """
    The decorator that handles the try/except by redirecting the sys.stderr and sys.stdout to a log file.
    Two boolean arguments can trigger the usage of the log file: arg1 refers to standalone mode; arg2 refers to
    debug mode. For writing to the log file the arg1 needs to be False or the arg2 needs to be True.

    """
    import sys
    import traceback

    def wrap(f):
        def wrapped_f(self, *args, **kwargs):
            standalone = getattr(self, arg1)
            debug = getattr(self, arg2)
            pmwsjob = getattr(self, arg3)

            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                err_detail = "\nError detailed:\n\t{}: {}\n".format(type(e).__name__, e)
                tb = repr(traceback.extract_tb(e.__traceback__, limit=-1))
                _fr = tb.split()
                _file = _fr[_fr.index("file") + 1]
                _line = _fr[_fr.index("line") + 1]
                eType, eValue, eTraceback = sys.exc_info()
                summary_error = (
                    "Error raised from:\n\tfile: {}\n\tline: {}\n\ttype: {}\n\tvalue: {}\n\t"
                    "traceback {}\n".format(_file, _line, eType, eValue, eTraceback)
                )

                log = "" if standalone else "LOG"
                h1 = "# ERROR {}\n".format(log)
                h2 = "\n# Error summary (dev)\n"
                h3 = "\n# Error Traceback (dev)\n"
                spacer = "_" * 40

                if standalone and not debug:
                    text = [h2, summary_error, spacer, h3]
                    print("".join(text))
                    traceback.print_tb(e.__traceback__)
                    text = ["\n", spacer, "\n", h1, err_detail]
                    print("".join(text))
                else:
                    error_log = (
                        "/data/out/outerror.log" if not debug else "outerror.log"
                    )
                    flog = open(error_log, "w")
                    text = [h1, err_detail, spacer, h2, summary_error, spacer, h3]
                    flog.write("".join(text))
                    traceback.print_tb(e.__traceback__, file=flog)

                    flog.close()
                    if pmwsjob is not None:
                        setAsError("/data/out/")
                        # pmwsjob.setError()
                    print("Error !!!")
                sys.exit(0)

        return wrapped_f

    return wrap


########### New devutils for function-based singularity apps ##############
def _pm_try_except(func, SESSION, JOB, standalone, debug, vars):
    import traceback
    import sys

    try:
        func(SESSION, JOB, vars.outdir, vars.scratchdir, vars)
    except Exception as e:
        err_detail = f"\nError detailed:\n\t{type(e).__name__}: {e}\n"
        tb = repr(traceback.extract_tb(e.__traceback__, limit=-1))
        _fr = tb.split()
        _file = _fr[_fr.index("file") + 1]
        _line = _fr[_fr.index("line") + 1]
        eType, eValue, eTraceback = sys.exc_info()
        summary_error = f"Error raised from:\n\tfile: {_file}\n\tline: {_line}\n\ttype: {eType}\n\tvalue: {eValue}\n\t traceback {eTraceback}\n"

        h1 = f"# ERROR LOG\n"
        h2 = "\n# Error summary (dev)\n"
        h3 = "\n# Error Traceback (dev)\n"
        spacer = "_" * 40

        if standalone and not debug:
            text = [h2, summary_error, spacer, h3]
            print("".join(text))
            traceback.print_tb(e.__traceback__)
            text = ["\n", spacer, "\n", h1, err_detail]
            print("".join(text))
        else:
            error_log = os.path.join(vars.outdir, "outerror.log")
            with open(error_log, "w") as flog:
                text = [h1, err_detail, spacer, h2, summary_error, spacer, h3]
                flog.write("".join(text))
                traceback.print_tb(e.__traceback__, file=flog)

            if JOB is not None:
                setAsError("/data/out/")
            print(f"Error !!! Check {error_log} for more details.")
        sys.exit(0)


def app_wrapper(args, parser, func):
    from playmolecule import Session
    import argparse

    standalone = True
    debug = args["debug"]
    SESSION = None
    JOB = None

    if debug:
        standalone = False

    if len(args["token"]) > 0:
        SESSION = Session(token=args["token"])
        JOB = SESSION.get_job(execid=getJobId("/data/in/config"))
        standalone = False

    for arg, value in args.items():
        if value == "":
            args[arg] = None

    vars = argparse.Namespace(**args)
    writeInputsOptionsLog(vars.outdir, parser, vars, debug)

    _pm_try_except(func, SESSION, JOB, standalone, debug, vars)

    if not standalone:
        ### set the complete status of the job
        setAsCompleted(vars.outdir)


def app_arg_parser(description):
    import argparse

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-token",
        dest="token",
        action="store",
        type=str,
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-outdir",
        dest="outdir",
        action="store",
        type=str,
        default=".",
        help="The output folder where to write the results",
    )
    parser.add_argument(
        "-scratchdir",
        dest="scratchdir",
        action="store",
        type=str,
        default="scratch",
        help="The scratch folder where to write the temporary data",
    )
    parser.add_argument(
        "--debug", dest="debug", action="store_true", help=argparse.SUPPRESS
    )
    return parser
