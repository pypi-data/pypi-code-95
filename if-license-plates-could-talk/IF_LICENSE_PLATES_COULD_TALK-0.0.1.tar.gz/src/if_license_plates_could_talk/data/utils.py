import os
import pandas as pd


def fix_key(ser):
    """Transform int to 5-digit str, padded with zeros. Ex: 101 -> 00101

    Args:
        ser (Series): Series of ints 

    Returns:
        Series: Series of strings, 5 digits + padded with zeros
    """
    return ser.astype(int).astype(str).str.zfill(5)


def to_numeric(df, except_=["kreis_key"]):
    """Convert all columns to numeric, except the columns passed via except_

    Args:
        df (pd.DataFrame): Target dataframe.
        except_ (list): List of columns not to convert. Optional, defaults to ["kreis_key"]. 

    Returns:
        pd.DataFrame: Dataframe with converted columns
    """
    df = df.copy()

    for col in df.columns:
        if col not in except_:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def path_to_data_dir():
    """Path to Data directory

    Returns:
        str: Absolute path to data directory
    """
    return os.path.join(os.path.dirname(__file__), "data_files")


def fix_goettingen(df, col, proportional=False):
    """In 2016, regions 3152 and 3156 merged to become Göttingen, 3159

    Args:
        df (DataFrame): [description]
        col (str): [description]

    Returns:
        [type]: [description]
    """
    df.kreis_key = pd.to_numeric(df.kreis_key)
    df = df.set_index("kreis_key")
    if proportional:  # relative features should not be added naively
        # Rough approximation using the bigger county
        df.loc[3159, col] = pd.to_numeric(df.loc[3156, col], errors="coerce")
    else:  # absolute features can be added
        df.loc[3159, col] = pd.to_numeric(
            df.loc[3152, col], errors="coerce") + pd.to_numeric(df.loc[3156, col], errors="coerce")
    df = df.reset_index()
    df.kreis_key = fix_key(df.kreis_key)
    return df
