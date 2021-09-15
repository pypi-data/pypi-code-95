from . import regions
from . import utils
from .. import geo
import os
import pandas as pd


def prep_data():
    """Preprocess data on border vicinity
    """
    print("This may take a while!")
    df = regions.load_data()
    df = df[["kreis_key"]]
    df.drop_duplicates()
    distance_calculator = geo.border_vicinity.DistanceCalculator()
    df["border_vic"] = df.kreis_key.apply(distance_calculator.distance)
    return df[["kreis_key", "border_vic"]]


def load_data():
    """Load data on border vicinity
    """
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed",
                     "border_vicinity", "border_vicinity.csv"), index_col=0)
    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
