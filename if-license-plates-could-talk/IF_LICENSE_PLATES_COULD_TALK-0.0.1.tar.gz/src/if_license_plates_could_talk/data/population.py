import pandas as pd
import os
from . import utils
from .. import geo


def prep_data():
    """Preprocess population data. Reads data in data/raw/population, outputs processed data in data/processed/population"""
    path = os.path.join(utils.path_to_data_dir(),
                        "raw", "population", "12411-05-01-4.csv")
    path_density = os.path.join(
        utils.path_to_data_dir(), "raw", "population", "AI002-1.csv")
    df_raw = pd.read_csv(path, encoding="ISO-8859-1",
                         skiprows=6, delimiter=";")

    df_dens = pd.read_csv(path_density, encoding="ISO-8859-1",
                          delimiter=";", skiprows=4)

    # clean data

    df_raw.rename(columns={"Unnamed: 0": "year", "Unnamed: 1": "kreis_key",
                  "Unnamed: 2": "kreis_name", "Insgesamt": "population"}, inplace=True)
    df_raw = df_raw.dropna(subset=["kreis_key"])
    df_raw = df_raw[df_raw.kreis_key != "DG"]
    df_raw.kreis_key.replace(
        {"02": "02000", "11": "11000"}, inplace=True)  # Berlin, Hamburg

    df_dens = df_dens.iloc[:, :4]
    df_dens.columns = ["year", "kreis_key", "kreis_name", "population_density"]
    df_dens = df_dens[["year", "kreis_key", "population_density"]]
    df_dens = df_dens.dropna(subset=["kreis_key"])
    df_dens.kreis_key.replace(
        {"02": "02000", "11": "11000"}, inplace=True)  # Berlin, Hamburg
    df_dens.population_density = pd.to_numeric(
        df_dens.population_density.str.replace(",", "."), errors="coerce")

    df_raw = df_raw.merge(df_dens, on=["kreis_key", "year"])

    # Pivot Data
    df_piv = df_raw.pivot(
        index="kreis_key", columns="year", values=["population", "population_density"])

    df_piv.columns = [f"{desc}_{year}" for desc, year in df_piv.columns]

    df_piv = df_piv.reset_index()

    df = df_piv[[len(i) == 5 for i in df_piv.kreis_key]].copy()

    for year in range(2013, 2016):
        df = utils.fix_goettingen(df, f"population_{year}")
        df = utils.fix_goettingen(
            df, f"population_density_{year}", proportional=True)

    df = df.dropna(subset=["kreis_key"])

    return df


def load_data():
    """Load data from csv stored in data/processed"""
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed",
                                  "population", "population.csv"), index_col=0)
    df = utils.to_numeric(df)
    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
