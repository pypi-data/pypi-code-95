"""
This module, together with Settings, implements a global keyword system for BOSS.
Here, the types and default values for all keywords are encoded and functions for
keyword I/O are implemented (these are used in the BOSS CLI).

Valid BOSS keywords are stored in a global keywords dict named categories.
The keywords are further divided into subcategories depending on their dimensionality
 and the element type. More specifically, each key in categories is a tuple (type, ndim)
where type is the element type and ndim is the dimensionality (as returned by np.ndim)
and the correspondig value is a dict that maps keywords that have this structure
to their default values.

Examples
--------
Single booleans have type bool and ndim=0 so all such keywords are grouped
under categories[(bool, 0)]. 
2D-arrays of floats have type float and ndim=2 so they are grouped
under categories[(float, 2)].

To add a new keyword to BOSS you simple need to make a new entry in the correct
subcategory below, the keywords will then be automatically available for use in the
code via the Settings object.
"""
import copy
import importlib
import os
import sys
from inspect import getfile
from pathlib import Path

import numpy as np


categories = {}
categories[(bool, 0)] = {
    "ygrads": False,
    "pp_models": False,
    "pp_acq_funcs": False,
    "pp_truef_at_xhats": False,
    "initupdate": True,
    "ynorm": False,
}
categories[(int, 0)] = {
    "initpts": 5,
    "verbosity": 1,
    "iterpts": None,
    "updatefreq": 1,
    "cores": 1,
    "updaterestarts": 2,
    "updateoffset": 0,
    "mep_precision": 25,
    "mep_rrtsteps": 10000,
    "mep_nebsteps": 20,
    "pp_truef_npts": None,
    "hmciters": 0,
    "minzacc": 15,
    "minfreq": 1,
    "userfn_arrdim": 2,
    "seed": None,
    "parallel_optims": 0,
}
categories[(int, 1)] = {
    "pp_iters": None,
    "pp_model_slice": None,
}
categories[(float, 0)] = {
    "noise": 1e-12,
    "acqtol": 0.001,
    "min_dist_acqs": None,
    "mep_maxe": None,
    "pp_local_minima": None,
}
categories[(float, 1)] = {
    "yrange": [-10.0, 10.0],
    "gm_tol": None,
    "periods": None,
    "acqfnpars": np.array([]),
    "pp_var_defaults": None,
    "thetainit": None,
}
categories[(float, 2)] = {"bounds": None, "thetapriorpar": None, "thetabounds": None}
categories[(str, 0)] = {
    "outfile": "boss.out",
    "ipfile": "boss.in",
    "rstfile": "boss.rst",
    "acqfn_name": "elcb",
    "inittype": "sobol",
    "thetaprior": "gamma",
    "userfn": None,
}
categories[(str, 1)] = {
    "kernel": ["rbf"],
}


def get_copied_categories():
    """Returns deep copies of all categories.

    Useful when setting default values using the category
    dicts and we want to avoid changing the default value
    contained in the category dict itself.
    """
    return [copy.deepcopy(cat) for cat in categories.values()]


def find_category(key):
    """Finds the category dict that contains a given key. """
    for cat, cat_dict in categories.items():
        if key in cat_dict:
            return cat
    raise KeyError(f"No category correspondig to keyword: {key}.")


def _eval_bool(x):
    """Converts string input to booleans.

    Boolean values can be specified in BOSS input files as
    0 / 1, [y]es / [n]o, [t]rue / [f]alse where all the words are
    case-insensitive. This function handles conversion from these strings
    to proper Python booleans.
    """
    truthy = bool(x == "1" or x.lower()[0] == "y" or x.lower()[0] == "t")
    falsey = bool(x == "0" or x.lower()[0] == "n" or x.lower()[0] == "f")
    return truthy and not falsey


def destringify(val_str, category):
    """Converts a string to an appropriate Python object.

    When a boss input file is parsed, each string containing the value of a keyword
    is passed to this function. Strings are evaluated according to the BOSS input
    ruleset (see BOSS documentation).

    Parameters
    ----------
    val_str : str
        An input string to be evaluated.
    category : Tuple[type, int]
        The target type and dimensionality of the string evaluation. For instance,
        a string 'True' with category (bool, 1) will be evaluated to [True].

    Returns
    ----------
    Any
        The result of the string evaluation.
    """
    cat_type, cat_dim = category[0], category[1]
    val_str = val_str.strip()
    if val_str.lower() == "none":
        val = None
    elif cat_dim == 0:
        if cat_type is bool:
            val = _eval_bool(val_str)
        else:
            val = cat_type(val_str)
    elif cat_dim == 1:
        val_split = val_str.split()
        if cat_type == bool:
            val = np.asarray([_eval_bool(x) for x in val_split])
        else:
            val = [cat_type(x) for x in val_split]
            if cat_type in [int, float]:
                val = np.asarray(val)
    elif cat_dim == 2:
        rows = val_str.split(";")
        val = np.asarray([np.fromstring(row, sep=" ") for row in rows])
    else:
        raise ValueError(f"Cannot convert '{val_str}' to {category}")
    return val


def stringify(val):
    """Convert a Python type to a BOSS-style string.

    Parameters
    ----------
    val : str
        Python object to stringify
    """
    val_ndim = np.ndim(val)
    if val_ndim == 0:
        if isinstance(val, bool):
            val_str = str(int(val))
        else:
            val_str = str(val)
    if val_ndim == 1:
        if len(val) == 0:
            val_str = None
        else:
            val_str = " ".join([str(x) for x in val])
    elif val_ndim >= 2:
        val = np.array(val)
        val_str = str(val)
        val_str = val_str.replace("\n", ";")
        val_str = val_str.replace("[", "")
        val_str = val_str.replace("]", "")
    return val_str


def func_from_keyword(func_str):
    """"""
    fsplit = func_str.split()
    if len(fsplit) == 2:
        func_name = fsplit[1]
    else:
        func_name = "f"
    func_path = Path(fsplit[0])
    sys.path.append(str(func_path.parent))
    func = getattr(importlib.import_module(func_path.stem), func_name)
    return func


def func_to_keyword(func):
    """
    The user function is either an ordinary function or a user defined,
    callable object. In the second case we must pass the type and not the
    object instance to inspect.getfile.
    """
    if type(func).__name__ == "function":
        func_path = getfile(func)
        func_name = func.__name__
    else:
        func_path = getfile(type(func))
        func_name = type(func).__name__
    path_str = f"{func_path} {func_name}"
    return path_str
