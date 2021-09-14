"""
lay_and_temp_manager.py

Functions which deal with layouts and templates
"""

from copy import deepcopy
from yaml import safe_load
from pkg_resources import resource_listdir, resource_string
from arnica.utils.string_manager import (string_minus_string,
                                         replace_stars_in_string)

__all__ = ["fetch_avbp_layouts", "fetch_avbp_templates", "decompact_template"]


def fetch_avbp_layouts():
    """It returns all the avbp layouts in a dictionary

    Output:
    -------
    avbp_layouts : nested object
    """

    avbp_layouts = {}
    layouts_files_list = resource_listdir('pyavbp.visu', 'avbp_layouts')

    for layout_file_name in layouts_files_list:
        layout_string = resource_string('pyavbp.visu', ("avbp_layouts/"
                                                        + layout_file_name))
        layout = safe_load(layout_string)
        avbp_layouts[layout["title"]] = layout

    return avbp_layouts


def fetch_avbp_templates():
    """It returns all the avbp templates in a dictionary

    Output:
    -------
    avbp_templates : nested object
    """

    avbp_templates = {}
    templates_files_list = resource_listdir('pyavbp.visu', 'avbp_templates')

    for template_file_name in templates_files_list:
        template_string = resource_string('pyavbp.visu', ("avbp_templates/"
                                                          + template_file_name))
        template = safe_load(template_string)
        avbp_templates[template["title"]] = template

    return avbp_templates


def decompact_template(template, data):
    """It decompacts the provided template in function of the provided
    data which are in the form of a key-value object and returns it

    Input:
    ------
    template : nested object
    data : key-value object

    Output:
    -------
    layout : nested object
    """

    layout = deepcopy(template)
    layout['graphs'] = []

    for graph_template in template['graphs']:
        layout['graphs'] += decompact_graph_template(graph_template,
                                                     data)

    return layout


def decompact_graph_template(graph_template, dataframe):
    """It returns the layouts of graphs associated to the provided
    template in function of the provided data frame

    Input:
    ------
    graph_template : nested object
    dataframe : pandas data frame

    Output:
    -------
    layouts_of_graphs : nested object
    """

    layouts_of_graphs = []
    curve_dyn_var = None

    for curve_template in graph_template["curves"]:
        if "*" in curve_template["var"]:
            curve_dyn_var = curve_template["var"]
            break

    if not curve_dyn_var:
        graph_layout = deepcopy(graph_template)
        layouts_of_graphs.append(graph_layout)
    else:
        for data_name in dataframe.keys():
            curve_dyn_var_without_star = curve_dyn_var.replace("*", "")
            data_name_spec = string_minus_string(curve_dyn_var_without_star,
                                                 data_name)
            graph_layout = replace_stars_in_graph_template(graph_template,
                                                           data_name_spec,
                                                           dataframe)
            if graph_layout:
                layouts_of_graphs.append(graph_layout)

    return layouts_of_graphs


def replace_stars_in_graph_template(graph_template, data_name_spec, dataframe):
    """It tries to replace the stars in the provided graph template
    by the provided data name specification and thanks to the
    provided data frame

    If it fails, it returns "None"
    Otherwise, it returns the graph layout resulting of the provided
    graph template and the provided data name specification

    Input:
    ------
    graph_template : nested object
    data_name_spec : list of strings
    dataframe : pandas data frame

    Output:
    -------
    graph_layout : nested object
    """

    graph_template_cp = deepcopy(graph_template)
    graph_layout = None

    for curve_template in graph_template_cp["curves"]:
        success = replace_stars_in_curve_template(curve_template,
                                                  data_name_spec,
                                                  dataframe)
        if not success:
            break
        if curve_template is graph_template_cp["curves"][-1]:
            if (graph_template != graph_template_cp and
                    "title" in graph_template_cp and
                    "*" in graph_template_cp["title"] and
                    graph_template_cp["title"].count("*") == len(data_name_spec)):
                graph_template_cp["title"] = replace_stars_in_string(graph_template_cp["title"],
                                                                     data_name_spec)
            graph_layout = graph_template_cp

    return graph_layout


def replace_stars_in_curve_template(curve_template, data_name_spec, dataframe):
    """It tries to replace the stars in the provided curve template
    by the provided data name specification and thanks to the
    provided data frame

    If it fails, it returns "False"
    Otherwise, it returns "True"

    Input:
    ------
    curve_template : dictionary
    data_name_spec : list of strings
    dataframe : pandas data frame

    Output:
    -------
    success : boolean
    """

    success = True

    if "*" in curve_template["var"]:
        if curve_template["var"].count("*") == len(data_name_spec):
            curve_template["var"] = replace_stars_in_string(curve_template["var"],
                                                            data_name_spec)
            if curve_template["var"] in dataframe.keys():
                if ("legend" in curve_template and
                        "*" in curve_template["legend"]
                        and curve_template["legend"].count("*") == len(data_name_spec)):
                    curve_template["legend"] = replace_stars_in_string(curve_template["legend"],
                                                                       data_name_spec)
            else:
                success = False
        else:
            success = False

    return success
