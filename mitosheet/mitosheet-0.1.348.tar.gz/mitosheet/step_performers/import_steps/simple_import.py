#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

import csv
import json
from os.path import normpath, basename
from mitosheet.utils import get_valid_dataframe_names
import os
from copy import copy
from typing import Any, Dict, List, Optional

import chardet
import pandas as pd
from mitosheet.errors import make_is_directory_error
from mitosheet.state import DATAFRAME_SOURCE_IMPORTED, State
from mitosheet.step_performers.step_performer import StepPerformer


class SimpleImportStepPerformer(StepPerformer):
    """
    A simple import, which allows you to import dataframes 
    with the given file_names, while detecting the correct
    way to import them.
    """

    @classmethod
    def step_version(cls) -> int:
        return 2

    @classmethod
    def step_type(cls) -> str:
        return 'simple_import'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Imported CSV Files'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'simple_import_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        file_names: List[str],
        use_deprecated_id_algorithm: bool=False,
        **params
    ) -> State:
        # If any of the files are directories, we throw an error to let
        # the user know
        for file_name in file_names:
            if os.path.isdir(file_name):
                raise make_is_directory_error(file_name)

        # Create a new step
        post_state = copy(prev_state)

        file_delimeters = []
        file_encodings = []

        just_final_file_names = [basename(normpath(file_name)) for file_name in file_names]

        for file_name, df_name in zip(file_names, get_valid_dataframe_names(post_state.df_names, just_final_file_names)):

            df, delimeter, encoding = read_csv_get_delimeter_and_encoding(file_name)

            # Save the delimeter and encodings for transpiling
            file_delimeters.append(delimeter)
            file_encodings.append(encoding)
            
            post_state.add_df_to_state(
                df, 
                DATAFRAME_SOURCE_IMPORTED, 
                df_name=df_name,
                use_deprecated_id_algorithm=use_deprecated_id_algorithm
            )   
 
        # Save the renames that have occured in the step, for transpilation reasons
        # and also save the seperator that we used for each file
        return post_state, {
            'file_delimeters': file_delimeters,
            'file_encodings': file_encodings
        }

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        file_names: List[str],
        use_deprecated_id_algorithm: bool=False,
    ) -> List[str]:
        code = ['import pandas as pd']

        index = 0
        for file_name, df_name in zip(file_names, post_state.df_names[len(post_state.df_names) - len(file_names):]):

            delimeter = execution_data['file_delimeters'][index]
            encoding = execution_data['file_encodings'][index]

            code.append(
                generate_read_csv_code(file_name, df_name, delimeter, encoding)
            )
            
            index += 1

        return code

    @classmethod
    def describe(
        cls,
        file_names: List[str],
        use_deprecated_id_algorithm: bool=False,
        df_names=None,
        **params
    ) -> str:
        return f'Imported {", ".join(file_names)}'


def generate_read_csv_code(file_name, df_name, delimeter, encoding):
    """
    Helper function for generating minimal read_csv code 
    depending on the delimeter and the encoding of a file
    """
    if encoding != 'default' and delimeter != ',':
        # If there is a non comma delimieter and an encoding, we use both.
        # NOTE: we add a r in front of the string so that it is a raw string
        # and file slashes are not interpreted as a unicode sequence
        return f'{df_name} = pd.read_csv(r\'{file_name}\', sep=\'{delimeter}\', encoding=\'{encoding}\')'
    elif encoding != 'default':
        # If there is a comma delimieter and an encoding, we set the encoding
        return f'{df_name} = pd.read_csv(r\'{file_name}\', encoding=\'{encoding}\')'
    elif delimeter != ',':
        # If there is a delimeter for this file, we use it
        return f'{df_name} = pd.read_csv(r\'{file_name}\', sep=\'{delimeter}\')'
    else:
        # We don't add or encoding if they are the default.
        return f'{df_name} = pd.read_csv(r\'{file_name}\')'


def read_csv_get_delimeter_and_encoding(file_name: str):
    """
    Given a file_name, will read in the file as a CSV, and
    return the df, delimeter, and encoding of the file
    """
    # We use 'default' instead of None to ensure that we log the encoding even when we don't need to set one.
    encoding = 'default'
    # Also set a default delemeter
    delimeter = ','
    try:
        # First attempt to read csv without specifying an encoding, just with a delimeter
        delimeter = guess_delimeter(file_name)
        df = pd.read_csv(file_name, sep=delimeter)
    except UnicodeDecodeError:
        # If we have an encoding error, try and get the encoding
        encoding = guess_encoding(file_name)
        delimeter = guess_delimeter(file_name, encoding=encoding)

        # Read the file as dataframe 
        df = pd.read_csv(file_name, sep=delimeter, encoding=encoding)
    
    return df, delimeter, encoding


def guess_delimeter(file_name: str, encoding=None):
    """
    Given a path to a file that is assumed to exist and be a CSV, this
    function guesses the delimeter that is used by that file
    """
    s = csv.Sniffer()
    with open(file_name, 'r', encoding=encoding) as f:
        return s.sniff(f.readline()).delimiter

def guess_encoding(file_name: str) -> str:
    """
    Uses chardet to guess the encoding of the the file
    at the given file_name
    """
    # Attempt to determine the encoding and try again. 
    with open(file_name, 'rb') as f:
        result = chardet.detect(f.readline())
        return result['encoding']
