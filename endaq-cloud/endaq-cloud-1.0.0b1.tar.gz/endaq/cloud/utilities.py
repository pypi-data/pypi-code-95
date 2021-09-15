import numpy as np
import pandas as pd

import json
import re


def convert_file_data_to_dataframe(files_data):
    """
    Produces a pandas dataframe from a list of dictionaries of data as given by cloud API

    :param files_data: A list of data dictionaries containing all the data about the files as given by
     using the direct cloud API.  (this is how the cloud visualizations `files` variable is given)
    :return: If files_data is length 0 it will return an empty pandas dataframe if not it will return a
     pandas dataframe of attributes, with the index being the file names, and columns corresponding to the
     attributes present in the given files_data
    """
    """
    NOTES:
     - This code was originally written with the idea that complex short code is better than more readable code
      that goes on for a while, as it was intended to be a section in example visualization scripts to be 'ignored'.

    TODO:
     - Check that this doesn't produce problems when multiple files have the same name (I'm now thinking it will)
    """
    if len(files_data) == 0:
        return pd.DataFrame()
    else:
        df = pd.DataFrame(files_data)
        df['attributes'] = df['attributes'].map(lambda x: {attribs['name']: attribs for attribs in x})

        unique_attributes_and_types = df['attributes'].map(lambda x: [(k, v['type']) for k, v in x.items()]).values
        unique_attributes_and_types = set(pair for file_info in unique_attributes_and_types for pair in file_info)

        for attrib_name, attrib_type_str in unique_attributes_and_types:
            if attrib_type_str == 'float':
                df[attrib_name] = df['attributes'].map(
                    lambda x: None if len(x) == 0 or attrib_name not in x else float(x[attrib_name]['value']))
            elif attrib_type_str == 'string':
                try:  # Try and parse the JSON string into an array of floats
                    df[attrib_name] = df['attributes'].map(
                        lambda x: [] if len(x) == 0 or attrib_name not in x else np.array(
                            json.loads(re.sub(r'\bnan\b', 'NaN', x[attrib_name]['value'])), dtype=np.float32))
                except json.JSONDecodeError:  # Save it as a String if it can't be converted to a float array
                    df[attrib_name] = df['attributes'].map(
                        lambda x: "" if len(x) == 0 or attrib_name not in x else x[attrib_name]['value'])

        # Convert the columns which represent times to pandas datetime type
        for time_col_name in ['recording_ts', 'created_ts', 'modified_ts', 'archived_ts']:
            df[time_col_name] = pd.to_datetime(df[time_col_name], unit='s')

        # Add the GPS coordinates as 2 seperate latitude and longitude columns
        gps_coord_series = df['gpsLocationFull'].map(
            lambda x: np.array(x.split(','), dtype=np.float32) if len(x) else np.array(2 * [np.nan], dtype=np.float32))

        df['latitudes'] = gps_coord_series.map(lambda x: x[0])
        df['longitudes'] = gps_coord_series.map(lambda x: x[1])

        df = df.set_index('file_name')

        return df
