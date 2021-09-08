import logging
import json
import pickle
import os
import pandas as pd


logger = logging.getLogger(__name__)

__all__=['one_hot_encoding','read_config_file','drop_columns','import_dictionary','convert_date']


def import_dictionary (path,file):
    with open( os.path.join( path, file ), 'rb' ) as f:
        logging.info( f'reading input dict from {path}' )
        dict = pickle.load( f )
        return dict


def drop_columns(df, columns):
    """Drops the selected columns

    Args:
        df ([dataframe]): [leads dataframe]
        columns ([list]): [list columns to drop]

    Returns:
        [df]: [leads dataframe]
    """
    for column in columns:
        if column in df:
            logging.info(f'dropping column : {column}')
            df = df.drop(column, axis=1)
    return df


def one_hot_encoding(df):
    """Generate one hot encoded dataset
    WARNING:
        Only encodes colums with category

    Args:
        df ([dataframe]): [dataframe]

    Returns:
        df[dataframe]: [dataframe with categorical variables one hot encoded]
    """
    # These variables must not be categories
    if 'campaign_bulk_date' in df.columns:
        df['campaign_bulk_date'] = df['campaign_bulk_date'].astype('object')
    if 'IDEmailStatus' in df.columns:
        df['IDEmailStatus'] = df['IDEmailStatus'].astype('object')
    logging.info("Data Types before encoding:")
    logging.info(f"{df.dtypes}")
    df = pd.get_dummies(data=df,
                        columns=df.select_dtypes(include=['category']).columns.tolist())
    logging.info("Data Types after encoding:")
    logging.info(f"{df.dtypes}")
    return df

def convert_date(df):
    # Convert date
    if 'campaign_bulk_date' in df.columns:
        df['campaign_bulk_date'] = df['campaign_bulk_date'].astype('object')
        df['campaign_bulk_date'] = pd.to_datetime(df['campaign_bulk_date'])
        df['campaign_bulk_date'] = df['campaign_bulk_date'].dt.date
    else:
        raise Exception('campaign_bulk_date not present! unable to perform dataset split')
    return df

def read_config_file(path, campaign_id):
    try:
        logging.info(f'reading config from {path}')
        with open( path ) as file:
            data = file.read()
        data = dict(json.loads( data ))
        logging.info(f'accessing {campaign_id}')
        config = data[campaign_id]

    except Exception as exception:
        config = None
        error_message = f"Read config file - {repr( exception )}"
        logging.info( error_message )
    return config
