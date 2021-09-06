#!/usr/bin/env python3
"""
    Generates a pdf report from google's supplier data. The report is attached
    to an email message and sent.
"""
import os
from datetime import date
from it_automation import reports
from it_automation import emails


def read_data(description_directory):
    """ Reads data from a directory containing descriptions of fruit. Returns
        two list with the name and weight of each fruit.

        The data being read is in files with the following format
        Fruit name
        Fruit weight
        Fruit descriptions

    Args:
        description_directory(string): Path to directory containing supplier
        data descriptions.

    Returns:
        name_list(list): A list of fruit names from files in
        description_directory.

        weight_list(list): A list of fruit weights from files
        description_directory.
    """
    name_list = []
    weight_list = []
    for root, dirs, files in os.walk(description_directory):
        # Ignoring hidden files and directories
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            file_path = os.path.join(root,file)
            with open(file_path, 'r') as f:
                lines = f.readlines()
                name_list.append( lines[0].strip())
                weight_list.append( lines[1].strip())
    return name_list, weight_list


def summary_data(name_list, weight_list):
    """ Reads the names and weights of fruits in two list and puts them in a
        string format to be written into a pdf file.

        name: Fruit names
        weight: Fruit Weight lbs

    Args:
        name_list(list): list of fruit names.
        weight_list(list): list of the weight of each fruit.

    Returns:
        summary(string): A string with the name and wight of each fruit on each
        line.
    """
    summary = ""
    for i in range(len(name_list)):
        summary += 'name: {} <br /> weight: {} <br /><br />'.format(name_list[i],
                                                                weight_list[i])
    return summary