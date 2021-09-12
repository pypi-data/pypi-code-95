"""
The format of the input file is a set of space-separated keyword value pairs:

    # comment
    key1 val1
    key2 val2  # comment2

Keyword values are evaluated according to the ruleset:

    foo               -> str
    3                 -> int
    1.0               -> float
    foo bar           -> List[str]
    3 10              -> np.ndarray(shape(1, 2), dtype=np.int64)
    5.0 7.0           -> np.ndarray(shape(1, 2), dtype=np.float64)
    1.0 2.0 ; 3.0 4.0 -> np.ndarray(shape=(2,2), dtype=np.float64)
"""
import time
import importlib
import inspect
import os
import sys
from pathlib import Path
import boss.keywords as bkw
import itertools

import numpy as np


def parse_input_file(file_path, skip=None):
    """Parses a boss input file.

    Parses the contents of the file and organizes keywords and their
    values into a dictionary. If present, restart data present under
    the optional results header is also parsed.

    Parameters
    ----------
    input_file : Optional[Union[str, Path]]
        Input file path.

    skip: Optional[str] = None
        Skip parsing part of the input, can be either 'keywords' or 'results'.

    Returns
    ----------
    input_data: dict
        A dictionary containing the parsed input data. Can contain
        the following items:

        is_rst : bool
            Whether rst data was present in the input_file or not

        rst_data: np.ndarray
            Array containing rst data, each row is composed of the X, y data
            followed by the model parameters. Rows containing the initial
            points and/or missing y-data are padded with np.nan.
    """
    input_data = {"is_rst": False}
    with open(file_path, "r") as fd:
        text = fd.read()

    # The strategy is to split the text around the results header
    # and then parse the two parts seprately.
    text_split = text.split("RESULTS:")

    # The first part of the split contains all boss keywords.
    input_data["keywords"] = {}
    if skip != "keywords":
        keywords = input_data["keywords"]
        kw_text = text_split[0].strip()
        kw_lines = kw_text.splitlines()
        for ln in kw_lines:
            ln = ln.split("#", maxsplit=1)[0].rstrip()
            if len(ln) > 0:
                key, val_str = ln.split(maxsplit=1)
                category = bkw.find_category(key)
                keywords[key] = bkw.destringify(val_str, category)

    # The second part of the split contains the restart data.
    if len(text_split) == 2:
        input_data["is_rst"] = True
        if skip != "results":
            rst_text = text_split[1].strip()
            rst_lines = rst_text.splitlines()

            # If no actual rst data is present we return early.
            if len(rst_lines) == 0:
                return input_data

            arrs = []
            for ln in rst_lines:
                ln = ln.split("#", maxsplit=1)[0].rstrip()
                if len(ln) > 0:
                    arrs.append(np.fromstring(ln, dtype=float, sep=" "))

            totalpts = len(arrs)
            max_len = max([len(a) for a in arrs])
            rst_data = np.full((totalpts, max_len), np.nan)
            for i, arr in enumerate(arrs):
                rst_data[i, : len(arr)] = arr

            input_data["rst_data"] = rst_data
    return input_data


def parse_config():
    """Parses a config file for BOSS keywords to use as new defaults.

    The name of the config file must be .bossrc or bossrc. BOSS will search
    for a config file under the following directories, in order:

    $PWD > $HOME > $HOME/.config/boss

    Only the first file encountered will be parsed.

    Returns
    ----------
    keywords: dict
        BOSS keywords parsed from the config file.
    """
    parents = [Path.cwd(), Path.home(), Path.home() / ".config/boss"]
    stems = [".bossrc", "bossrc"]
    keywords = {}
    for parent, stem in itertools.product(parents, stems):
        path = parent / stem
        if path.is_file():
            keywords = parse_input_file(path)["keywords"]
            break
    return keywords


def parse_min_preds(settings, outfile):
    """
    Extracts xhat, muhat and nuhat from all bo iterations in the output
    file. Returns a numpy array where each row is [npts, xhat, muhat,
    nuhat]. Works on output files with all verbosity levels.
    """
    data = []
    npts = None

    with open(outfile, "r") as f:
        line = f.readline()
        while len(line) > 0:
            if line.find("Total ensemble size") != -1:
                npts = int(line.split()[-1])
            elif line.find("Global minimum prediction") != -1:
                line = f.readline()
                line = line.split()
                data.append(np.concatenate([[npts], line[: settings.dim + 2]]))
            line = f.readline()

    return np.array(data).astype(float)


def parse_acqs(settings, outfile):
    """
    Extracts data acquisitions from all bo iterations in the output file.
    Returns a numpy array where each element is [npts, x, y].
    Note that there may be several acquisitions on the same iteration -
    especially the initial points at the 0th iteration.
    Works on output files with all verbosity levels.
    """
    acq = []
    npts = 0

    with open(outfile, "r") as f:
        line = f.readline()
        while len(line) > 0:
            if line.find("Data point added to dataset") != -1:
                line = f.readline()
                while len(line.split()) == settings.dim + 1 and line.find(".") != -1:
                    line = line.split()
                    npts += 1
                    acq.append(np.concatenate([[npts], line[: settings.dim + 1]]))
                    line = f.readline()
            else:
                line = f.readline()

    return np.array(acq).astype(float)


def parse_best_acqs(settings, outfile):
    """
    Extracts xbest and ybest from all bo iterations in the output file.
    Returns a numpy array where each element is [npts, xbest, ybest].
    Works only on output files with verbosity levels of at least 1.
    """
    data = []
    npts = None

    with open(outfile, "r") as f:
        line = f.readline()
        while len(line) > 0:
            if line.find("Total ensemble size") != -1:
                npts = int(line.split()[-1])
            elif line.find("Best acquisition") != -1:
                line = f.readline()
                line = line.split()
                data.append(np.concatenate([[npts], line[: settings.dim + 1]]))
            line = f.readline()

    return np.array(data).astype(float)


def parse_conv_measures(settings, outfile):
    """
    Extracts dx_hat and dmu_hat from all bo iterations in the output
    file. Returns a numpy array where each element is
    [npts, dxhat, dmuhat].
    Works only on output files with verbosity levels of at least 1.
    """
    data = []
    npts = None

    with open(outfile, "r") as f:
        line = f.readline()
        while len(line) > 0:
            if line.find("Total ensemble size") != -1:
                npts = int(line.split()[-1])
            elif line.find("Global minimum convergence") != -1:
                line = f.readline()
                line = line.split()
                if "none" in line:
                    pass
                else:
                    data.append(np.concatenate([[npts], line]))
            line = f.readline()

    return np.array(data).astype(float)


def parse_mod_params(outfile):
    """
    Extracts unfixed GP model hyperparameters from all bo iterations in the
    output file. Returns a numpy array where each element is
    [npts, unfixed model parameters].
    Works only on output files with verbosity levels of at least 2.
    """
    hpar = []
    npts = None

    with open(outfile, "r") as f:
        line = f.readline()
        while len(line) > 0:
            if line.find("Total ensemble size") != -1:
                npts = int(line.split()[-1])
            elif line.find("GP model hyperparameters") != -1:
                line = f.readline()
                line = line.split()
                hpar.append(np.concatenate([[npts], line]))
            line = f.readline()

    return np.array(hpar).astype(float)


def parse_xnexts(outfile):
    """
    Extracts xnext locations from all bo iterations in the output file.
    Returns a numpy array where each element is [npts, xnext].
    Note that this means that the location 'xnext' is to be evaluated
    in the next iteration 'iter+1'.
    Works only on output files with verbosity levels of at least 2.
    """
    try:
        data = []
        with open(outfile) as f:
            data = []
            line = f.readline()
            npts = None
            while len(line) > 0:
                if line.find("Total ensemble size") != -1:
                    npts = int(line.split()[-1])
                elif line.find("Next sampling location") != -1:
                    line = f.readline()
                    line = line.split()
                    data.append(np.concatenate([[npts], line]))
                line = f.readline()
            return np.array(data).astype(float)
    except:
        raise OSError("Error trying to read file '" + outfile + "'")


def parse_minima(outfile):
    """
    Extract local minima
    """
    try:
        f = open(outfile)
        line = f.readline()
        if line[:14] == "# Local minima":
            ok = True
        else:
            ok = False
        f.close()
    except:
        raise OSError("Error trying to read file '" + outfile + "'")

    if not ok:
        raise Exception("'" + outfile + "' not recognized as " + "a minima file.")

    try:
        f = open(outfile)
        line = f.readline()
        line = f.readline()
        minima = np.array(line.split())
        line = f.readline()
        while len(line) > 0:
            minima = np.vstack((minima, line.split()))
            line = f.readline()
        f.close()
        return minima.astype(float)

    except:
        raise OSError("Error trying to read file '" + outfile + "'")
