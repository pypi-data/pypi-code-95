"""
Base Module
-----------
This module contains an abstract class of the dataset objects.
All dataset objects in MAICA inherits the abstract class of this module.
"""


import numpy
import pandas
import warnings
from abc import ABC


# Ignore unnecessary user-defined warnings.
warnings.filterwarnings(action='ignore', category=UserWarning)


class Dataset(ABC):
    """
    An abstract class for the Dataset classes in MAICA.
    """
    pass


def read_data_file(path_data_file: str):
    """
    Read data file form the given ``path_data_file``.
    Only the :obj:`.xlsx` and :obj:`.csv` extensions are acceptable.

    :param path_data_file: (*str*) A path of the data file.
    :return: Pandas and NumPy array objects of the data file.
    """

    # Get the file extension of the data file.
    ext = path_data_file.split('.')[-1]

    # Read dataset file according to the file extension.
    if ext == 'xlsx':
        data_file = pandas.read_excel(path_data_file)
        data_obj = numpy.array(data_file)
    elif ext == 'csv':
        data_file = pandas.read_csv(path_data_file)
        data_obj = numpy.array(data_file)
    else:
        raise AssertionError('Only .xlsx and .csv extensions are available,' +
                             'but unknown file extension was given {}.'.format(ext))

    return data_file, data_obj
