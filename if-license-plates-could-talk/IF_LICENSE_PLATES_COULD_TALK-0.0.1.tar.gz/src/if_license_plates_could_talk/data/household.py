import pandas as pd
import os
from . import utils


def prep_data():
    path = os.path.join(utils.path_to_data_dir(),
                        "raw", "household", "12111-31-01-4.csv")
    df_raw = pd.read_csv(path, encoding="ISO-8859-1",
                         skiprows=9, delimiter=";")

    df_raw.columns = ["kreis_key", "kreis_name", "hh_ges",
                      "hh_1", "hh_2", "hh_3", "hh_4", "hh_5", "hh_6"]

    df_raw = df_raw[df_raw.kreis_key != "DG"]

    # Change in regions since 2011:

    region_replace = {
        "13001": "13075",
        "13002": "13071",
        "13005": "13073",
        "13006": "13074",
        "13051": "13072",
        "13052": "13071",
        "13053": "13072",
        "13054": "13076",
        "13055": "13071",
        "13057": "13073",
        "13058": "13074",
        "13059": "13075",
        "13060": "13076",
        "13061": "13073",
        "13062": "13075",
        "03152": "03159",  # GÖTTTINGEN
        "03156": "03159"
    }

    df_raw.kreis_key.replace(region_replace, inplace=True)

    df_raw.kreis_key.replace(
        {"02": "02000", "11": "11000"}, inplace=True)  # Berlin, Hamburg

    df_raw = df_raw[[len(i) == 5 for i in df_raw.kreis_key]]

    df_raw = utils.to_numeric(df_raw)

    df_raw = df_raw.groupby("kreis_key").sum().reset_index()
    df_raw = df_raw.set_index("kreis_key")
    df_raw = df_raw.reset_index()

    df_raw["hh_avg"] = (df_raw["hh_1"] + 2*df_raw["hh_2"] + 3*df_raw["hh_3"] + 4 *
                        df_raw["hh_4"] + 5*df_raw["hh_5"] + 6*df_raw["hh_6"]) / df_raw["hh_ges"]

    return df_raw[["kreis_key", "hh_ges", "hh_avg"]]


def load_data():
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(),
                     "processed", "household", "household.csv"), index_col=0)
    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
