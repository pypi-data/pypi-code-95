##############################################################################
# Institute for the Design of Advanced Energy Systems Process Systems
# Engineering Framework (IDAES PSE Framework) Copyright (c) 2018-2020, by the
# software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia
# University Research Corporation, et al. All rights reserved.
#
# Please see the files COPYRIGHT.txt and LICENSE.txt for full copyright and
# license information, respectively. Both files are also available online
# at the URL "https://github.com/IDAES/idaes-pse".
##############################################################################
"""
Main file of ALAMOpy; a shell that calls other alm functions.
"""
import os

import almopts as almopts
import almwrite as almwrite
import almexec as almexec
import almread as almread


def doalamo(xdata=None, zdata=None, noutputs=None, xmin=None, xmax=None,
            simulator=None, **kwargs):
    """
    Main function. Accept user input, write an alm file, call alamo, parse the
    resulting lst file, and return the result to the user.

    Args:
    xdata: A two-dimensional array of size m*n denoting m data points in the
            n-dimensional space. Or, alternatively, a one-dimensional array to
            denote one point in the n-dimensional space. These are the x (input)
            data points.
    zdata: The same requirements as xdata, although the dimensionality needs
            not be the same. These are the z (output) data points. The number of
            z data points should be equal to the number of x data points.
        noutputs: The number of dimensions for each output data point.
        xmin: The minimum value that any x data point can take.
        xmax: The maximum value that any x data point can take.
        simulator: Path to an executable, "simulator", that can be used to provide
                additional data points on-demand. See the ALAMO manual for
                requirements for this executable.
        kwargs: Various other options that can be used to control ALAMO and
                ALAMOpy. See almopts.py for a complete documentation.
    """

    # Preparing and updating options with user-supplied values
    opts = almopts.prepare_default_opts()
    for key, value in kwargs.items():
        opts[key] = value
    opts["xdata"] = xdata
    opts["zdata"] = zdata
    opts["noutputs"] = noutputs
    opts["xmin"] = xmin
    opts["xmax"] = xmax
    opts["simulator"] = simulator
    almopts.validate_opts(opts)
    almopts.complete_opts(opts)

    # Writing alm file
    almwrite.write_alm_file(opts)

    # Running ALAMO
    almexec.exec_alamo(opts)

    # Reading lst file
    almread.read_lst_file(opts)

    # Cleaning up
    if not opts["keep_alm_file"] and os.path.isfile(opts["alm_file_name"]):
        os.remove(opts["alm_file_name"])
    if not opts["keep_lst_file"] and os.path.isfile(opts["lst_file_name"]):
        os.remove(opts["lst_file_name"])

    # Returning to the user
    return opts["return"]
