import pandas as pd
from . import data
import os


def prep_data():
    """Preprocess the raw data in data/raw.

    Returns:
        DataFrame: data indexed by license plate codes
    """

    features = ["income", "population", "license_plate", "regions",
                "education", "crime", "household",  "election", "border_vicinity"]

    def prep_feature(feature):
        print(feature)
        df = getattr(data, feature).prep_data()
        df.to_csv(os.path.join(data.utils.path_to_data_dir(),
                  "processed", feature, f"{feature}.csv"))
        return df

    for feature in features:
        prep_feature(feature)
