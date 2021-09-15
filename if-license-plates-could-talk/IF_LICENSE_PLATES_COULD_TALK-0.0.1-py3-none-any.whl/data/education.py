import pandas as pd
import os
from . import utils


def prep_data():
    path = os.path.join(utils.path_to_data_dir(),
                        "raw", "education", "AI-N-06.csv")
    df_raw = pd.read_csv(path, encoding="ISO-8859-1",
                         skiprows=4, delimiter=";")
    df_raw.columns = ["year", "kreis_key",
                      "kreis_name", "prop_abitur", "prop_no_haupt"]

    df_raw.prop_abitur = pd.to_numeric(
        df_raw.prop_abitur.str.replace(",", "."), errors="coerce")
    df_raw.prop_no_haupt = pd.to_numeric(
        df_raw.prop_no_haupt.str.replace(",", "."), errors="coerce")

    df_raw = df_raw.dropna(subset=["kreis_key"])

    df_raw = df_raw[df_raw.kreis_key != "DG"]
    df_raw.kreis_key.replace(
        {"02": "02000", "11": "11000"}, inplace=True)  # Berlin, Hamburg

    df_raw = df_raw[[len(i) == 5 for i in df_raw.kreis_key]]

    # Pivot Data
    df_piv = df_raw.pivot(
        index="kreis_key", columns="year", values=["prop_abitur", "prop_no_haupt"])

    df_piv.columns = df_piv.columns.droplevel(0)
    df_piv = df_piv.reset_index()
    df_piv.columns = ["kreis_key"] + [f"prop_abitur_{i}" for i in df_raw.year.unique()] + [
        f"prop_no_haupt_{i}" for i in df_raw.year.unique()]

    for year in range(2013, 2017):
        df_piv = utils.fix_goettingen(
            df_piv, f"prop_abitur_{year}", proportional=True)
        df_piv = utils.fix_goettingen(
            df_piv, f"prop_no_haupt_{year}", proportional=True)

    # No data for Landkreis Bamberg and Schweinfurt

    df_piv = df_piv.fillna(df_piv.mean())

    return df_piv


def load_data():
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed",
                                  "education", "education.csv"), index_col=0)
    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
