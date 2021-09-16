"""
This module contains the function which parses the json file
"""


def parse_json_by_keys(json_to_parse: dict, list_of_keys: list, is_recursive: bool = False):
    """
    Parses a json file to a new one which contains the given keys
    :param json_to_parse: The file to parse
    :param list_of_keys: the list of keys to search for
    :param is_recursive: if should search inside iterable values
    :return: a new json with the pairs which their keys are in the given list
    """
    parsed_json = {}

    # iterate over all the keys in the dict
    for key in json_to_parse:
        value = json_to_parse[key]

        # append the pair if the key is matches
        if key in list_of_keys:
            parsed_json[key] = value

        # if the value is dict call self with the value, to not miss any child
        elif type(value).__name__ in ['dict'] and is_recursive:
            parsed_json = parse_json_by_dict(json_to_parse, list_of_keys, key, parsed_json, parse_json_by_keys)

        # if the key does not match
        elif type(value).__name__ in ['list'] and is_recursive:
            parsed_json = parse_json_by_list(value, list_of_keys, key, parsed_json, parse_json_by_keys)

    return parsed_json


def parse_json_by_value_types(json_to_parse: dict, list_of_value_types: list, is_recursive: bool = False):
    """
    Parses a json file to a new one which contains the given value types
    :param json_to_parse: The file to parse
    :param list_of_value_types: The list of values the search for
    :param is_recursive: If should search nested values
    :return: A new json with the pairs which their value types matches the given list
    """
    parsed_json = {}

    # iterate over all the keys in the dict
    for key in json_to_parse:
        value = json_to_parse[key]

        if type(json_to_parse[key]).__name__ in list_of_value_types:
            parsed_json[key] = value

        # if the value is dict call self with the value, to not miss any child
        elif type(value).__name__ in ['dict'] and is_recursive:
            parsed_json = parse_json_by_dict(json_to_parse,
                                             list_of_value_types,
                                             key,
                                             parsed_json,
                                             parse_json_by_value_types)

        # if the key does not match
        elif type(value).__name__ in ['list'] and is_recursive:
            parsed_json = parse_json_by_list(value, list_of_value_types, key, parsed_json, parse_json_by_value_types)

    return parsed_json


def parse_json_by_values(json_to_parse: dict, list_of_values: list, is_recursive: bool = False):
    """
    Parses a json file to a new one which contains the given values
    :param json_to_parse: The File to parse
    :param list_of_values: The list of values to search for
    :param is_recursive: If should search nested values
    :return: A new json with the pairs which their values match the given list
    """
    parsed_json = {}

    # iterate over all the keys in the dict
    for key in json_to_parse:
        value = json_to_parse[key]

        if json_to_parse[key] in list_of_values:
            parsed_json[key] = value

        # if the value is dict call self with the value, to not miss any child
        elif type(value).__name__ in ['dict'] and is_recursive:
            parsed_json = parse_json_by_dict(json_to_parse,
                                             list_of_values,
                                             key,
                                             parsed_json,
                                             parse_json_by_values)

        elif type(value).__name__ in ['list'] and is_recursive:
            parsed_json = parse_json_by_list(value, list_of_values, key, parsed_json, parse_json_by_values)

    return parsed_json


def parse_json_by_dict(json_to_parse, list_of_keys, key, parsed_json, cb):
    """
    Receives an inner dict of the one to parse in continues to parse the dict
    :param cb: the function to call to keep parsing
    :param json_to_parse: the json object to parse
    :param list_of_keys: the keys to search for
    :param key: the current key to check
    :param parsed_json: the parsed json with the data which matches
    :return: The parsed json with the new matching values
    """
    # mix the current parsed json with the value returned from the inner search
    inner_child = cb(json_to_parse[key], list_of_keys, True)
    if inner_child:
        # add the new value with it's father, so the format will remain
        parsed_json[key] = {} if key not in list(parsed_json.keys()) else parsed_json[key]
        parsed_json[key] = {**parsed_json[key], **inner_child}

    return parsed_json


def parse_json_by_list(value, list_of_keys, key, parsed_json, cb):
    """
    Receives an inner list of the one to parse in continues to parse the dict
    :param cb: the function to call to keep parsing
    :param value: the list to iterate on
    :param list_of_keys: the keys list to search for
    :param key: the current key
    :param parsed_json: the current parsed json object
    :return: the parsed_json object with the new matches
    """
    # iterate over the list to find more dicts
    for item in value:
        if type(item).__name__ in ['dict']:

            # receive the values from the child of the current element
            inner_child = cb(item, list_of_keys, True)

            # if the child has data, append it to the current parsed dict
            if inner_child:
                parsed_json[key] = [] if key not in list(parsed_json.keys()) else parsed_json[key]
                parsed_json[key].append(inner_child)

    return parsed_json
