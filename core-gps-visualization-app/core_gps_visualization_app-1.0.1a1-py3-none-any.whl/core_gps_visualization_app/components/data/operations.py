"""Visualization Data Operations"""

from core_main_app.system import api as system_api
from core_gps_visualization_app import data_config
from core_gps_visualization_app.utils import parser as utils


def get_all_data():
    """ Get all data as is from the DB under JSON format (data follow the structure defined by a schema)

    Returns: dict

    """
    templates = system_api.get_all_templates()

    # Each data in the list contains a XML file content accessible through its dict_content attribute
    all_data = system_api.get_all_by_list_template(templates)

    return all_data


def parse_all_data(all_data, config_charts=data_config.config_charts, config_parameters=data_config.config_parameters,
                   config_ids=data_config.config_ids):
    """ Parse all data from the DB that follow a schema structure meant to organize data in way that models a system
    into a structure strictly adapted to quick visualizations that are based on the data_config file

    Args:
        all_data: List of all XML documents (under JSON format)
        config_charts:
        config_parameters:
        config_ids:

    Returns: List of dicts that each represent one plot (check tests for more details)

    """
    # Instantiate list to return
    list_of_charts = []

    # Each XML file contains potentially all parameters defined in the schema
    # We only look for the ones from the data_config file
    for chart_info in config_charts:

        # Get information from data config chart
        x_name = chart_info['xName']
        y_name = chart_info['yName']
        try:
            ids_names = chart_info['idsNames']
        except KeyError:
            # if no ids defined
            ids_names = None

        # Use the information above to get details from the data config parameters involved into chart
        x_path = utils.get_path_by_name(config_parameters, 'parameterName', x_name, 'parameterPath')
        x_unit_path = utils.get_path_by_name(config_parameters, 'parameterName', x_name, 'unitPath')
        y_path = utils.get_path_by_name(config_parameters, 'parameterName', y_name, 'parameterPath')
        y_unit_path = utils.get_path_by_name(config_parameters, 'parameterName', y_name, 'unitPath')

        # Instantiate the dict to add to the list to return
        chart_dict = {
            'data': []
        }

        # Loop to consider 1 XML file content at the time
        for parameters_data in all_data:
            dict_content = parameters_data['dict_content']

            # Default IDs list is the union in between 'x' parameter idsNames and 'y' parameter idsNames
            # Occurs when 'idsNames' not in config_charts element
            if ids_names is None:
                ids_names = utils.get_elements_by_union(config_parameters, x_name, y_name, 'idsNames')

            # Create IDs list that identify a parameter
            # This is needed to group the data to plot
            ids_paths_list_of_tuples = []
            for id_name in ids_names:
                id_path = utils.get_path_by_name(config_ids, 'idName', id_name, 'idPath')
                ids_paths_list_of_tuples.append((id_name, id_path))

            # Find all combination of ids values possible and add them in a list
            ids_list_of_lists_of_dicts = utils.get_ids_values_by_paths(dict_content, ids_paths_list_of_tuples)

            for ids_list_of_dicts in ids_list_of_lists_of_dicts:
                # Parse the JSON from the DB using variables instantiated using the data_config
                # Load parsed data in variables
                x_value = utils.parse_value_by_path(dict_content, x_path, ids_list_of_dicts)
                y_value = utils.parse_value_by_path(dict_content, y_path, ids_list_of_dicts)
                x_unit = utils.parse_value_by_path(dict_content, x_unit_path, ids_list_of_dicts)
                y_unit = utils.parse_value_by_path(dict_content, y_unit_path, ids_list_of_dicts)

                if 'ids' not in chart_dict:
                    chart_dict['ids'] = ids_list_of_dicts

                # Worth adding only if x and y have actual values
                if x_value is not None and y_value is not None:
                    # If chart in list_of_charts with same everything but 'data', we get it
                    chart_dict = utils.get_chart_dict_by_ids((x_name, x_unit), (y_name, y_unit), ids_list_of_dicts,
                                                             list_of_charts)
                    # Otherwise, chart_dict is None and we create a new element
                    if chart_dict is None:
                        chart_dict = {
                            'x': (x_name, x_unit),
                            'y': (y_name, y_unit),
                            'ids': ids_list_of_dicts,
                            'data': [(x_value, y_value)]
                        }
                    # If it already existed, we just add the new data tuple to its data
                    else:
                        chart_dict['data'].append((x_value, y_value))
                    # Finally, we update the list_of_charts
                    list_of_charts = utils.add_or_update_charts(chart_dict, list_of_charts)

    for chart in list_of_charts:
        chart['data'].sort()

    return list_of_charts
