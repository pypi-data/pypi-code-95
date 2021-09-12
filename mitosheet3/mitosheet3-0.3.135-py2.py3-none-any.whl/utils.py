#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Contains helpful utility functions
"""
import json
import re
import uuid
from os.path import basename, normpath
from typing import Any, Dict, List, Match

import numpy as np
import pandas as pd

from mitosheet.column_headers import ColumnIDMap
from mitosheet.sheet_functions.types.utils import (get_datetime_columns,
                                                   get_float_columns,
                                                   get_timedelta_columns)


def get_first_unused_dataframe_name(existing_df_names: List[str], new_dataframe_name: str) -> str:
    """
    Appends _1, _2, .. to df name until it finds an unused 
    dataframe name. If no append is necessary, will just
    return the initial passed value.
    """
    if new_dataframe_name not in existing_df_names:
        return new_dataframe_name

    for i in range(len(existing_df_names) + 1):
        new_name = f'{new_dataframe_name}_{i + 1}'
        if new_name not in existing_df_names:
            return new_name


def get_valid_dataframe_name(existing_df_names: List[str], original_dataframe_name: str) -> str:
    """
    Given a string, turns it into a valid dataframe name.
    """
    # We get all the words from the original name, and append them with underscores
    dataframe_name = '_'.join([
        match.group() for match in re.finditer('\w+', original_dataframe_name)
    ])

    # A valid variable name cannot be empty, or start with a number
    if dataframe_name[0].isdecimal() or len(dataframe_name) == 0:
        return 'df_' + dataframe_name

    return get_first_unused_dataframe_name(existing_df_names, dataframe_name)


def get_valid_dataframe_names(existing_df_names: List[str], original_df_names: List[str]):
    """
    Helper function for taking a list of potential and turning them into valid
    names for dataframes, that do not overlap with the existing dataframe names.
    """

    final_names = []

    for original_df_name in original_df_names:
        new_names_final = get_valid_dataframe_name(
            existing_df_names + final_names,
            original_df_name
        )
        final_names.append(new_names_final)
    
    return final_names


def dfs_to_json(
        dfs: List[pd.DataFrame],
        column_ids: ColumnIDMap
    ) -> str:
    return json.dumps([
        df_to_json_dumpsable(df, column_ids.column_header_to_column_id[sheet_index]) 
        for sheet_index, df in enumerate(dfs)
    ])


def df_to_json_dumpsable(
        df: pd.DataFrame,
        column_headers_to_column_ids: Dict[Any, str],
        length_restriction=True # Used if we want to only return the first 2k rows of the dataframe
    ):
    """
    Returns a dataframe represented in a way that can be turned into a 
    JSON object with json.dumps
    """
    # First, if the length_restriction is True, we get the head, and then 
    # we make a copy (as we modify the df below)
    # NOTE: we get the head first for efficiency reasons.
    if length_restriction:
        df = df.head(n=2000).copy(deep=True) # we only show the first 2k rows!
    
    # Second, we figure out which of the columns contain dates, and we
    # convert them to string columns (for formatting reasons).
    # NOTE: we don't use date_format='iso' in df.to_json call as it appends seconds to the object, 
    # see here: https://stackoverflow.com/questions/52730953/pandas-to-json-output-date-format-in-specific-form
    date_columns = get_datetime_columns(df)
    for column_header in date_columns:
        df[column_header] = df[column_header].dt.strftime('%Y-%m-%d %X')

    # Third, we figure out which of the columns contain timedeltas, and 
    # we format the timedeltas as strings to make them readable
    timedelta_columns = get_timedelta_columns(df)
    for column_header in timedelta_columns:
        df[column_header] = df[column_header].apply(lambda x: str(x))

    # Then, we get all the float columns and actually make them 
    # look like floating point values, by converting them to strings
    float_columns = get_float_columns(df)
    for column_header in float_columns:
        # Convert the value to a string if it is a number, but leave it alone if its a NaN 
        # as to preserve the formatting of NaN values. 
        df[column_header] = df[column_header].apply(lambda x: x if np.isnan(x) else str(x))

    json_obj = json.loads(df.to_json(orient="split"))
    # Then, we go through and find all the null values (which are infinities),
    # and set them to 'NaN' for display in the frontend.
    for d in json_obj['data']:
        for idx, e in enumerate(d):
            if e is None:
                d[idx] = 'NaN'
    
    # Then, turn the column headers to their IDs, so that
    # the frontend can access them properly
    json_obj['columns'] = [
        column_headers_to_column_ids[column_header] for column_header in json_obj['columns']
    ]
    # And instead of having them be called columns, be clear they are columnIDs
    json_obj['columnIDs'] = json_obj['columns']
    del json_obj['columns']

    return json_obj


def get_random_id():
    """
    Creates a new random ID for the user, which for any given user,
    should only happen once.
    """
    return str(uuid.uuid1())

def get_new_id():
    return str(uuid.uuid4())


