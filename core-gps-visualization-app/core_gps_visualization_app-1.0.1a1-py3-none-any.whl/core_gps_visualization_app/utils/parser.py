"""Visualization utils parser"""

import copy
import re
import core_gps_visualization_app.data_config as config
from datetime import datetime, timedelta
import statistics


def parse_date(date_string):
    """

    Args:
        date_string: YYYY-mm-ddTHH:MM:SS

    Returns: datetime

    """
    try:
        year = date_string[:4]
        month = date_string[5:7]
        day = date_string[8:10]
        hours = date_string[11:13]
        mins = date_string[14:16]
        secs = date_string[17:19]
        parsed_date = datetime(int(year), int(month), int(day), int(hours), int(mins), int(secs))

    except ValueError:
        parsed_date = False
    except TypeError:
        parsed_date = False

    return parsed_date


def parse_value_by_path(dict_content, path, ids_list_of_dicts=None):
    """ Check if path is not None or a List. If it is a list,
    only a single element of it will bring back a value from the dict_content

    Args:
        dict_content:
        path:
        ids_list_of_dicts:

    Returns:

    """
    if ids_list_of_dicts is None:
        ids_list_of_dicts = []

    if path is None:
        return None

    value = None

    if isinstance(path, list):
        path_index = 0
        while value is None and path_index < len(path):
            value = get_value_by_path(dict_content, path[path_index], ids_list_of_dicts)
            path_index += 1
    else:
        value = get_value_by_path(dict_content, path, ids_list_of_dicts)

    if is_number(value):
        value = float(value)
    else:
        is_date = parse_date(value)
        if is_date:
            value = parse_date(value)

    return value


def get_ids_values_by_paths(dict_content, ids_paths_list_of_tuples):
    """ Create unique lists of dicts and insert them in a single list of lists of dicts
    Each unique sublist contains a number of dicts equals to the length of the
    ids_paths_list_of_tuples, they all have the same keys but they are unique in their values
    combinations

    Args:
        dict_content:
        ids_paths_list_of_tuples: [('name1', 'path1'), ('name2', 'path2'),..]

    Returns: ids_list_of_dicts = [[{name1: value1a, name2: value2a}, {name1: value1a, name2: value2b}],..]

    """
    ids_list_of_lists_of_dicts = []
    common_dicts = []
    unique_dicts = []

    for id_path_tuple in ids_paths_list_of_tuples:
        id_name = id_path_tuple[0]
        id_path = id_path_tuple[1]
        # Add ids common to whole XML (one key, one value) to common_dicts
        if '/' not in id_path:
            id_value = parse_value_by_path(dict_content, id_path)
            common_dicts.append({id_name: id_value})
        # Add other ids to a separate list (one key, many values) unique_dicts
        else:
            dict_content_ids_list = get_value_by_path(dict_content, id_path.split('/')[0])
            if dict_content_ids_list is not None:
                for dict_content_id in dict_content_ids_list:
                    id_value = get_value_by_path(dict_content_id, id_path.split('/')[1])
                    unique_dicts.append({id_name: id_value})
            #else:
                #return ids_list_of_lists_of_dicts

    # Each element of unique_dicts (same key, different values) combined the list of common ids
    # To create a unique list_of_dicts
    for unique_dict in unique_dicts:
        list_of_dicts = copy.deepcopy(common_dicts)
        list_of_dicts.append(unique_dict)
        ids_list_of_lists_of_dicts.append(list_of_dicts)

    if len(ids_list_of_lists_of_dicts) == 0:
        ids_list_of_lists_of_dicts = [None]

    return ids_list_of_lists_of_dicts


def get_value_by_path(dict_content, path, ids_list_of_dicts=None):
    """ Recursive method to get a value inside a dict from a path.
    '.' defines a layer in the dict and '/' defines start of a list

    Args:
        dict_content:
        path:
        ids_list_of_dicts

    Returns:

    """
    if ids_list_of_dicts is None:
        ids_list_of_dicts = []

    path_list = path.split('.')

    if dict_content:
        # In the specific case just below, dict_content is a list
        if isinstance(dict_content, list):
            # In this case, the third argument should be present
            # If different values from a same key are found in a same document
            # Some ID needs to be there to identify and group those values
            if len(ids_list_of_dicts) != 0:
                # dict_content should be a list of dicts in this case
                for dict_elt in dict_content:
                    # dict_elt contains only one key, value
                    dict_elt_key = list(dict_elt.keys())[0]
                    id_path_list_of_dicts = get_ids_path_by_name(ids_list_of_dicts, config.config_ids)
                    for id_path_dict in id_path_list_of_dicts:
                        if dict_elt_key in id_path_dict:
                            if dict_elt[dict_elt_key] == id_path_dict[dict_elt_key]:
                                return get_value_by_path(dict_elt, path)

        if '/' in path_list[0] and path_list[0].startswith('/') is False:
            substr_length = len(path_list[0])
            new_path = '/'.join(path_list[0].split('/')[1:]) + path[substr_length:]
            return get_value_by_path(dict_content[path_list[0].split('/')[0]], new_path, ids_list_of_dicts)

        if len(path_list) == 1 and '/' not in path_list[0]:
            return dict_content[path]

        else:
            substr_length = len(path_list[0]) + 1  # +1 to substring the point
            if path_list[0] not in dict_content:
                return None
            else:
                return get_value_by_path(dict_content[path_list[0]], path[substr_length:], ids_list_of_dicts)

    return None


def get_path_by_name(list_of_dicts, key, value, path_key):
    """ Return path_value of a specific dict from a list, by using a key / value as identifier

    Args:
        list_of_dicts:
        key: key from a dict
        value: value associated to the key
        path_key: used to bring the path_value from dict where key / value matches

    Returns:

    """
    path_value = None
    for elt_dict in list_of_dicts:
        if key in elt_dict:
            if elt_dict[key] == value:
                path_value = elt_dict[path_key]

    return path_value


def get_elements_by_union(list_of_dicts, id_1, id_2, union_point):
    """ Union of two lists that share a same key in a list of dicts. Identification
    is made through 2 ids that belong to the dicts

    Args:
        list_of_dicts: list of dicts
        id_1: a value of a dict (unique)
        id_2: a value of another dict (unique)
        union_point: a common key whose value is a list

    Returns: union_list

    """
    list_1, list_2 = [], []

    for elt_dict in list_of_dicts:
        if id_1 in elt_dict.values():
            list_1 = elt_dict[union_point]
        if id_2 in elt_dict.values():
            list_2 = elt_dict[union_point]

    union_list = list_1
    for elt in list_2:
        if elt not in union_list:
            union_list.append(elt)

    return union_list


def add_or_update_charts(chart_dict, list_of_charts):
    """ Add chart_dict to the list_of_charts if no element of the list_of_charts has the same 'ids' values than
    chart_dict for a unique 'x' and 'y' combination. Otherwise, replace the list_of_charts element with chart_dict

    Args:
        chart_dict:
        list_of_charts:

    Returns:

    """
    chart_ids = chart_dict['ids']
    x_tuple = chart_dict['x']
    y_tuple = chart_dict['y']
    new_chart = True
    chart_index = 0
    while new_chart and chart_index < len(list_of_charts):
        if list_of_charts[chart_index]['ids'] == chart_ids:
            if list_of_charts[chart_index]['x'] == x_tuple and list_of_charts[chart_index]['y'] == y_tuple:
                new_chart = False
        if new_chart:
            chart_index += 1
    if new_chart:
        list_of_charts.append(chart_dict)
    else:
        list_of_charts[chart_index] = chart_dict

    return list_of_charts


def get_chart_dict_by_ids(x_tuple, y_tuple, ids_list, list_of_charts):
    """ Get a specific dict (chart) from a list of dicts (charts) using an ids_list.
    'ids' list is unique for each 'x' and 'y' combination.
    This corresponds to the partially parsed charts, not the config_charts.

    Args:
        x_tuple:
        y_tuple:
        ids_list:
        list_of_charts:

    Returns:

    """
    chart_found = False
    chart_index = 0
    while not chart_found and chart_index < len(list_of_charts):
        if list_of_charts[chart_index]['ids'] == ids_list:
            if list_of_charts[chart_index]['x'] == x_tuple and list_of_charts[chart_index]['y'] == y_tuple:
                chart_found = True
        if not chart_found:
            chart_index += 1
    if chart_found:
        return list_of_charts[chart_index]

    return None


def get_ids_path_by_name(ids_list_of_dicts, config_ids):
    """ Get the last element of a config_ids 'parameterPath' using a 'parameterName'

    Args:
        ids_list_of_dicts:
        config_ids:

    Returns: id_path_list_of_dicts

    """
    id_path_list_of_dicts = []
    for id_dict in ids_list_of_dicts:
        id_name = list(id_dict.keys())[0]
        id_value = list(id_dict.values())[0]
        for parameter in config_ids:
            if parameter['idName'] == id_name:
                id_path = parameter['idPath']
                id_path_name = re.split('[./]', id_path)[-1]
                id_path_list_of_dicts.append({id_path_name: id_value})

    return id_path_list_of_dicts


def is_number(value):
    """ Check if value is a number

    Args:
        value:

    Returns:

    """
    try:
        float(value)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def stringify(string):
    """ Build a readable string from an argument

    Args:
        string:

    Returns:

    """
    if string is None:
        return ''
    if isinstance(string, list):
        parsed_string = ''
        for elt in string:
            parsed_string += stringify(elt)
        return parsed_string
    else:
        return str(string)


def unit_stringify(unit_label):
    """ Build a label

    Args:
        unit_label:

    Returns:

    """
    if stringify(unit_label) != '':
        label = " (" + stringify(unit_label) + ")"
    else:
        label = ''
    return label


def parse_time_range_data(list_of_tuples_data, time_range):
    """
    Args:
        list_of_tuples_data:
        time_range:

    Returns:

    """
    x_data = []
    y_data = []
    sub_x_data = [list_of_tuples_data[0][0]]
    sub_y_data = [list_of_tuples_data[0][1]]

    for tuple_data in list_of_tuples_data[1:]:
        time_range_reached = False

        if time_range == "Seconds":
            if tuple_data[0].second != sub_x_data[0].second:
                time_range_reached = True
        if time_range == "Minutes":
            if tuple_data[0].minute != sub_x_data[0].minute:
                time_range_reached = True
        if time_range == "Hours":
            if tuple_data[0].hour != sub_x_data[0].hour:
                time_range_reached = True
        if time_range == "Days":
            if tuple_data[0].day != sub_x_data[0].day:
                time_range_reached = True

        if time_range_reached:
            x_data.append(sub_x_data)
            y_data.append(sub_y_data)
            sub_x_data = [tuple_data[0]]
            sub_y_data = [tuple_data[1]]
        else:
            sub_x_data.append(tuple_data[0])
            sub_y_data.append(tuple_data[1])
            if list_of_tuples_data.index(tuple_data) == len(list_of_tuples_data) - 1:
                x_data.append(sub_x_data)
                y_data.append(sub_y_data)

    updated_data = []

    for i in range(0, len(x_data)):
        time = x_data[i][0]
        if time_range == "Seconds":
            x = datetime(time.year, time.month, time.day, time.hour, time.minute, time.second)
        if time_range == "Minutes":
            x = datetime(time.year, time.month, time.day, time.hour, time.minute)
        if time_range == "Hours":
            x = datetime(time.year, time.month, time.day, time.hour)
        if time_range == "Days":
            x = datetime(time.year, time.month, time.day)

        y = statistics.median(y_data[i])
        updated_data.append((x, y))

    return updated_data
