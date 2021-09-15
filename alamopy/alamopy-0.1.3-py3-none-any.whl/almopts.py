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
Prepare and process options and globals for ALAMOpy

To add a new user option to ALAMO:
    If the user input for this new option will be either a scalar, a string, or
        a 1D vector, append the option name to default_opts["entry_names"] in
        prepare_default_opts. When the user passes in arguments by this option
        name, it will automatically get written onto the alm file.
    If the user input for this new option will be a 2D vector section just like
        xpredata, append the section name to default_opts["section_names"] in
        prepare_default_opts. When the user passes in arguments by this section
        name, this section will automatically get written onto the alm file
        with formatting.
    If the new option will entail some new corelation between one option and
        another, such as the one between npredata and xpredata, add an auto-
        inference routine in complete_opts.
    If the new option necessitates a security check, such as the check that
        alm_file_name cannot exceed 1000 characters, add that check in
        validate_opts.
"""
import almutils as almutils


def prepare_default_opts():
    """
    Prepare a dictionary containing default options for write_alm_file.
    This dictionary WILL be the returned value after ALAMO is done 
    running. Note that this dictionary contains ALL the possible options,
    either necessary or optional. It also contains the data file the
    client passes in, and the lst_file produced from ALAMO with the stats.
    """
    default_opts = {}

    # Python opts
    default_opts["alm_file_name"] = "temp.alm"
    default_opts["lst_file_name"] = None
    default_opts["keep_alm_file"] = False
    default_opts["keep_lst_file"] = False
    default_opts["print_alm_output"] = False

    # ALAMO opts
    # Contains options both necessary and optional that client can execute

    default_opts["entry_names"] = ["ninputs", "noutputs", "xmin", "xmax",
                                   "ndata", "npredata", "nsample", "nvalsets",
                                   "nvaldata", "nvalsample", "maxsim",
                                   "maxpoints", "xfactor", "xscaling",
                                   "scalez", "xlabels", "zlabels", "mono",
                                   "multi2", "multi3", "ratios", "expfcns",
                                   "linfcns", "logfcns", "sinfcns", "cosfcns",
                                   "constant", "ncustombas", "grbfcns",
                                   "rbfparam", "trace", "tracefname",
                                   "modeler", "builder", "backstepper",
                                   "convpen", "screener", "ncvf", "sismult",
                                   "initializer", "sampler", "simulator",
                                   "preset", "maxtime", "maxiter",
                                   "datalimitterms", "maxterms", "minterms",
                                   "numlimitbasis", "exclude", "ignore",
                                   "xisint", "zisint", "tolrelmetric",
                                   "tolabsmetric", "tolmeanerror",
                                   "tolmaxerror", "tolsse", "mipoptca",
                                   "mipoptcr", "linearerror", "simin",
                                   "simout", "gams", "gamssolver", "solvemip",
                                   "print_to_file", "print_to_screen",
                                   "funform", "ntrans", "monomialpower",
                                   "multi2power", "multi3power", "ratiopower",
                                   "zmin", "zmax", "extrapxmin", "extrapxmax",
                                   "printextrap", "crncustom", "crtol",
                                   "crninitial", "crmaxiter", "crnviol",
                                   "crntrials", "ngroups"]
    # The sections of data are also initialized
    default_opts["section_names"] = ["data", "xpredata", "valdata",
                                     "custombas", "transforms", "customcon",
                                     "groups", "groupcon"]
    for entry_name in default_opts["entry_names"]:
        default_opts[entry_name] = None
    for section_name in default_opts["section_names"]:
        default_opts[section_name] = None
    default_opts["xdata"] = None
    default_opts["zdata"] = None

    # Return opts
    default_opts["return"] = {}
    default_opts["return"]["in"] = {}
    default_opts["return"]["out"] = {}
    default_opts["return"]["other"] = {}

    return default_opts


def complete_opts(opts):
    """
    Infers the value of some options from other options. Indicates
    that some essential inputs for ALAMO does not have to be provided
    by the client in order to be "found". Note this function infers
    validate_opts is true.
    """

    # Infer lst_file_name from alm_file_name
    opts["lst_file_name"] = almutils.alm2lst(opts["alm_file_name"])

    # User passes in x and z data arrays
    if opts["xdata"] is not None and opts["zdata"] is not None:
        # Make xdata and zdata 2D
        opts["zdata"] = almutils.vector_2d(opts["zdata"])
        opts["xdata"] = almutils.vector_2d(opts["xdata"])
        # Infer ninputs from xdata
        if opts["ninputs"] is None:
            opts["ninputs"] = almutils.datadim(opts["xdata"])
        # Infer noutputs from zdata
        if opts["noutputs"] is None:
            opts["noutputs"] = almutils.datadim(opts["zdata"])
        # Infer ndata from xdata
        if opts["ndata"] is None:
            opts["ndata"] = len(opts["xdata"])
        # Infer xmin from xdata
        if opts["xmin"] is None:
            opts["xmin"] = almutils.data2min(opts["xdata"])
        # Infer xmax from xdata
        if opts["xmax"] is None:
            opts["xmax"] = almutils.data2max(opts["xdata"])
        # Make data array from xdata and zdata
        if opts["data"] is None:
            opts["data"] = almutils.zip_2d_lists(opts["xdata"], opts["zdata"])

    # User passes in simulator, xmin, xmax, and noutputs
    if (opts["xmin"] is not None and opts["xmax"] is not None and
            opts["noutputs"] is not None and opts["simulator"] is not None):
        # Infer ninputs from xmin
        if opts["ninputs"] is None:
            opts["ninputs"] = len(opts["xmin"])


'''
error checking for two different scenarios:
1) xdata AND zdata OR xmin, xmax, noutputs, simulator not inputted
2) file passed in by client has a name longer than 1000 characters
'''


def validate_opts(opts):
    """
    Error-check the opts and raise RuntimeError if needed
    """
    # Either (xdata and zdata) are passed in, or (xmin, xmax, noutputs,
    # simulator) are passed in.
    case_1 = opts["xdata"] is not None and opts["zdata"] is not None
    case_2 = (opts["xmin"] is not None and opts["xmax"] is not None and
              opts["noutputs"] is not None and opts["simulator"] is not None)
    if not case_1 and not case_2:
        raise RuntimeError("Inadequate input options. ALAMO needs either \
                           (xdata and zdata), or (xmin, xmax, noutputs, \
                           and simulator).")

    # File path and name should not exceed 1000 characters in length
    if len(opts["alm_file_name"]) > 1000:
        raise RuntimeError("File name should not exceed 1000 "
                           "characters in length.")
