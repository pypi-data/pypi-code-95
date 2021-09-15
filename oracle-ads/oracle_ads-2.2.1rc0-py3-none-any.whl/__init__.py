#!/usr/bin/env python
# -*- coding: utf-8 -*--

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from __future__ import print_function, division, absolute_import
import os
import logging
import sys

import IPython
from IPython import get_ipython
from IPython.core.error import UsageError

from ads.common import utils

# from ads.environment import ads_inspect
import matplotlib.font_manager  # causes matplotlib to regenerate its fonts
import json

import ocifs

os.environ["GIT_PYTHON_REFRESH"] = "quiet"

__version__ = ""
with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ads_version.json")
) as version_file:
    __version__ = json.load(version_file)["version"]

debug_mode = os.environ.get("DEBUG_MODE", True)
documentation_mode = os.environ.get("DOCUMENTATION_MODE", "False") == "True"
test_mode = os.environ.get("TEST_MODE", False)
resource_principal_mode = bool(os.environ.get("RESOURCE_PRINCIPAL_MODE", False))


def set_auth(auth="api_key"):
    """
    Enable/disable resource principal identity or keypair identity in a notebook session.

    Parameters
    ----------

    auth: {'api_key', 'resource_principal'}, default 'api_key'
         Enable/disable resource principal identity or keypair identity in a notebook session

    """
    global resource_principal_mode
    if auth == "api_key":
        resource_principal_mode = False
    if auth == "resource_principal":
        resource_principal_mode = True


try:
    from ads.environment import ml_runtime

    # import ocifs
except ImportError as e:
    raise ImportError(str(e) + "\n\n" + "ads is not installed")

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# All warnings are logged by default
logging.captureWarnings(True)


def set_debug_mode(mode=True):
    """
    Enable/disable printing stack traces on notebook.

    Parameters
    ----------

    mode: bool (default True)
         Enable/disable print stack traces on notebook

    """
    global debug_mode
    debug_mode = mode
    if debug_mode:
        IPython.core.interactiveshell.InteractiveShell.showtraceback = (
            orig_ipython_traceback
        )
    else:
        IPython.core.interactiveshell.InteractiveShell.showtraceback = _log_traceback


def set_documentation_mode(mode=False):
    """
        Enable/disable printing user tips on notebook.

        Parameters
    ads//common/utils.py:572:        return TqdmProgressBar(max_progress, description=description, verbose=is_debug_mode())    ----------

        mode: bool (default False)
             Enable/disable print user tips on notebook
    """

    global documentation_mode
    documentation_mode = mode


def set_expert_mode():
    """
    Enables the debug and documentation mode for expert users all in one method.
    """
    set_debug_mode(True)
    set_documentation_mode(False)


#
# ***FOR TESTING PURPOSE ONLY***
#
def _set_test_mode(mode=False):
    """
    Enable/disable intercept the automl call and rewrite it to always use the two algorithms (LogisticRegression for classification and LinearRegression for regression).
    Enable only during tests to reduce nb convert notebook tests run time.

    Parameters
    ----------

    mode: bool (default False)
         Enable/disable the ability to intercept automl call

    """
    global test_mode
    test_mode = mode


def runtime():
    """
    get the compute runtime (Dask client object).
    """
    from ads.environment import ml_runtime

    return ml_runtime.compute_accelerator()


def hello():
    """
    Imports Dask, Pandas, sets the documentation mode, and prints a fancy "Hello".
    """
    import dask, pandas

    global documentation_mode
    global debug_mode

    print(
        f"""

  O  o-o   o-o
 / \\ |  \\ |
o---o|   O o-o
|   ||  /     |
o   oo-o  o--o

ADS SDK version: {__version__}
Dask version: {dask.__version__} ({ads.runtime().status})
Pandas version: {pandas.__version__}
Debug mode: {debug_mode}
"""
    )


def _log_traceback(self, exc_tuple=None, **kwargs):
    try:
        etype, value, tb = self._get_exc_info(exc_tuple)
    except ValueError:
        print("No traceback available to show.", file=sys.stderr)
        return
    msg = etype.__name__, str(value)
    logger.error("ADS Exception", exc_info=(etype, value, tb))
    sys.stderr.write("{0}: {1}".format(*msg))


if IPython.core.interactiveshell.InteractiveShell.showtraceback != _log_traceback:
    orig_ipython_traceback = (
        IPython.core.interactiveshell.InteractiveShell.showtraceback
    )

# Override the default showtraceback behavior of ipython, to show only the error message and log the stacktrace
IPython.core.interactiveshell.InteractiveShell.showtraceback = _log_traceback

ipy = get_ipython()
if ipy is not None:
    try:
        # show matplotlib plots inline
        ipy.run_line_magic("matplotlib", "inline")
    except UsageError:
        #  ignore error and use the default matplotlib mode
        pass
else:
    import matplotlib as mpl

    mpl.rcParams["backend"] = "agg"
    import matplotlib.pyplot as plt

    plt.switch_backend("agg")

# start dask client at the time of import
client = ml_runtime.compute_accelerator()
