#!/usr/bin/env python3
""" Functions for reading a directory and then making post request with the
    data.

    This is used for google's IT automation class project. Reads a directory
    with files containing information on fruits and then makes a post request
    to the class website to show the data.
"""
import os
import requests


def read_description_directory(description_directory):
    """ Reads a directory with files describing each fruit. Returns a list of
        dictionaries. Each dictionary contains information from each file read.

        The data being read is in files with the following format
        Fruit name
        Fruit weight
        Fruit descriptions

        Each dictionary in the returned list will look like this
        {
            'name': fruit_name,
            weight: 'fruit_weight',
            'description': fruit description,
            'image_name': filename.jpeg
        }

    Args:
        description_directory(string): Directory containing discriptions for
        each fruit.

    Returns:
        data_list(list): List of dictionaries containing information for each
        fruit
    """
    data_list = []
    separator = " "
    for root, dirs, files in os.walk(description_directory):
        # Ignoring hidden files and directories
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            fruit_dictionary = {}
            file_path = os.path.join(root,file)
            filename, extension = os.path.splitext(file)
            with open(file_path) as f:
                fruit_dictionary['name'] = separator.join(
                                                f.readline()
                                                .splitlines()
                                            )
                fruit_dictionary['weight'] = int(f.readline().split(' ')[0])
                fruit_dictionary['description'] = separator.join(
                                                    f.read().
                                                    splitlines()
                                                )
                fruit_dictionary['image_name'] = filename + '.jpeg'
                data_list.append(fruit_dictionary)
    return data_list


def post_description(url, data_list):
    """ Makes a post request to google's class website expecting json objects
        with information on fruits.

    Args():
        url(string): url for post request
        data_list(string): list of dictionaries for json post request

    Returns():
        None:
    """
    for data in data_list:
        request = requests.post(url, json=data)
        if request.status_code != 201:
            raise Exception('POST error status={}'.format(request.status_code))
