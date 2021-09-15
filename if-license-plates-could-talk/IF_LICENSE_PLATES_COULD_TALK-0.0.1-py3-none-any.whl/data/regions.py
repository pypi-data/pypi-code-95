import pandas as pd
import os
from . import utils
from . import license_plate


def prep_data():
    """Preprocess data on regions

    Returns:
        DataFrame: data on regions
    """
    df_plate = license_plate.load_data(with_kreis_name=True)
    df_regions = df_plate.drop(columns=["license_plate"])
    df_regions = df_regions[["kreis_key", "kreis_name"]].drop_duplicates()

    df_regions["bl_key"] = df_regions.kreis_key.str.slice(0, 2).astype(int)

    df_regions["east"] = df_regions.bl_key >= 12

    return df_regions[["kreis_key", "kreis_name", "east"]]


def load_data():
    """Load data on regions

    Returns:
        DataFrame: data on regions
    """
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed",
                                  "regions", "regions.csv"), index_col=0)
    df.east = df.east.astype(bool)
    df.kreis_key = utils.fix_key(df.kreis_key)

    return df
