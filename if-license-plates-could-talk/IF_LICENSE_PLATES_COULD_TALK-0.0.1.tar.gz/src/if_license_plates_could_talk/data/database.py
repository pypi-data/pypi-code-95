import sqlite3
import os
import pandas as pd

from . import household
from . import border_vicinity
from . import license_plate
from . import population
from . import income
from . import crime
from . import regions
from . import utils
from . import education
from . import election

FEATURE_LIST = [
    "license_plate", "income", "regions", "border_vicinity", "education", "election", "household", "population", "crime"]


class DataBase:
    """Interface to sqlite database stored in data/sqlite"""

    def __init__(self):
        """Initializing database, connecting to db, ..."""
        path = os.path.join(utils.path_to_data_dir(), "sqlite", "database.db")
        self.con = sqlite3.connect(path)

    def populate_db(self):
        """Populate database with processed data"""

        def load_data(feature):
            df = globals()[feature].load_data()
            df.to_sql(feature, self.con, if_exists="replace")
            return df

        for feature in FEATURE_LIST:
            load_data(feature)

    def query(self, sql_query):
        """Execute a query.

        Args:
            sql_query (str): sql  query

        Returns:
            DataFrame: Result of query
        """
        df = pd.read_sql(sql_query, self.con, index_col="index")
        return df

    def get_data(self):
        """Load data from db. For details on columns, see data/processed/data_desc.csv

        Returns:
            DataFrame: Data on regions, income, crime and population
        """

        df_merged = pd.DataFrame(columns=["kreis_key"])

        for feature in FEATURE_LIST:
            df_feat = self.query(f"SELECT * FROM {feature}")
            df_merged = df_merged.merge(df_feat, on="kreis_key", how="outer")

        # No Boolean data type in sqlite

        df_merged.east = df_merged.east.astype(bool)
        df_merged = df_merged.dropna(subset=["kreis_name"])
        df_merged.to_csv(os.path.join(
            utils.path_to_data_dir(), "processed", "merged.csv"))

        return df_merged
