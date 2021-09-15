import pandas as pd
import os
from . import utils


def prep_data():
    """Preprocess data on income

    Returns:
        DataFrame: data on income
    """
    path = os.path.join(utils.path_to_data_dir(),
                        "raw", "income", "82411-01-03-4.csv")
    df_raw = pd.read_csv(path, encoding="ISO-8859-1",
                         skiprows=6, delimiter=";")

    df_raw = df_raw.rename(columns={"Unnamed: 0": "year", "Unnamed: 1": "kreis_key",
                           "Unnamed: 2": "kreis_name", "Tsd. EUR": "income", "EUR": "income_pp"})
    df_raw = df_raw.dropna(subset=["kreis_key"])
    df_raw = df_raw[df_raw.kreis_key != "DG"]
    df_raw.kreis_key.replace(
        {"02": "02000", "11": "11000"}, inplace=True)  # Berlin, Hamburg

    df_piv = df_raw.pivot(index="kreis_key", columns="year",
                          values=["income_pp", "income"])

    df_piv.columns = [f"{s1}_{s2}" for (s1, s2) in df_piv.columns.tolist()]

    df_piv.reset_index(inplace=True)

    # drop rows that are not on "Kreis"-level
    df = df_piv[[len(i) == 5 for i in df_piv.kreis_key]]

    return df


def load_data():
    """Load data from csv stored in data/processed"""
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed",
                     "income", "income.csv"), index_col=0)

    df = utils.to_numeric(df)

    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
