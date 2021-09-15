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
A layer that compassionates with the legacy IDAES interface.
"""

import almain as almain
import almutils as almutils


def pre_process(xdata, zdata, **kwargs):
    """
    Pre-process the arguments and update kwargs.
    """
    if xdata is not None:
        kwargs["xdata"] = xdata
    if zdata is not None:
        kwargs["zdata"] = zdata
    if "showalm" in kwargs.keys():
        kwargs["print_alm_output"] = (kwargs["showalm"] == 1)
    if "almname" in kwargs.keys():
        kwargs["alm_file_name"] = kwargs["almname"]
    if "savescratch" in kwargs.keys():
        kwargs["keep_alm_file"] = (kwargs["savescratch"] == 1)
        kwargs["keep_lst_file"] = (kwargs["savescratch"] == 1)


def post_process(result):
    """
    Post-process the results and update result.
    """
    result["version"] = almutils.get_alamo_version()
    if "XLABELS" in result["in"].keys():
        result["xlabels"] = result["in"]["XLABELS"]
    if "ZLABELS" in result["in"].keys():
        result["zlabels"] = result["in"]["ZLABELS"]
    if "bases" in result["in"].keys():
        result["nbas"] = len(result["in"]["bases"])
    if "NINPUTS" in result["in"].keys():
        result["ninputs"] = result["in"]["NINPUTS"]
    if "time" in result["other"].keys():
        result["olrtime"] = result["other"]["time"]["OLR"]
        result["miptime"] = result["other"]["time"]["MIP"]
        result["othertime"] = result["other"]["time"]["other"]
        result["totaltime"] = result["other"]["time"]["total"]
    if len(result["out"].keys()) > 0:
        var_name = list(result["out"].keys())[0]
        var_dict = result["out"][var_name]
        result["R2"] = var_dict["R2"]
        result["f(model)"] = var_dict["model_fun"]
        result["madp"] = var_dict["MADp"]
        result["model"] = var_name + " = " + var_dict["model_str"]
        result["rmse"] = var_dict["RMSE"]
        result["ssr"] = var_dict["SSE"]


def alamo(xdata=None, zdata=None, **kwargs):
    """
    The alamo() function that compassionates with the legacy IDAES interface.
    """
    pre_process(xdata, zdata, **kwargs)
    result = almain.doalamo(xdata, zdata, kwargs["ninputs"], kwargs["xmin"],
                            kwargs["xmax"], kwargs["simulator"], **kwargs)
    post_process(result)
    return result
