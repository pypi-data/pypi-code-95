import pandas as pd
import os
from . import utils
from . import population
from datetime import datetime

crime_categories = {
    "crimes": ["Straftaten insgesamt"],
    "fraud": [
        "Betrug §§ 263, 263a, 264, 264a, 265, 265a, 265b StGB davon:", "Betrug §§ 263, 263a, 264, 264a, 265, 265a, 265b StGB",
        "Urkundenfälschung §§ 267-271, 273-279, 281 StGB", "Betrug §§ 263, 263a, 264, 264a, 265, 265a-e StGB"],
    "violence": ["Gefährliche und schwere Körperverletzung, Verstümmelung weiblicher Genitalien §§ 224, 226, 226a, 231 StGB",
                 "Vorsätzliche einfache Körperverletzung § 223 StGB",
                 "Gewaltkriminalität",
                 "Tätlicher Angriff auf Vollstreckungsbeamte und gleichstehende Personen §§ 114, 115 StGB",
                 "Vergewaltigung, sexuelle Nötigung und sexueller Übergriff im besonders schweren Fall einschl. mit Todesfolge §§ 177, 178 StGB",
                 "Mord, Totschlag und Tötung auf Verlangen"],
    "theft": ["Raub, räuberische Erpressung und räuberischer Angriff auf Kraftfahrer §§ 249-252, 255, 316a StGB", "Raub, räuberische Erpressung auf/gegen Geldinstitute, Postfilialen und -agenturen",
              "Raub, räuberische Erpressung auf/gegen sonstige Zahlstellen und Geschäfte",
              "Handtaschenraub",
              "Sonstige Raubüberfälle auf Straßen, Wegen oder Plätzen",
              "Raubüberfälle in Wohnungen",
              "Diebstahl ohne erschwerende Umstände §§ 242, 247, 248a-c StGB und zwar:",
              "Einfacher Ladendiebstahl",
              "Diebstahl unter erschwerenden Umständen §§ 243-244a StGB und zwar:",
              "Wohnungseinbruchdiebstahl §§ 244 Abs. 1 Nr. 3 und Abs. 4, 244a StGB",
              "Tageswohnungseinbruchdiebstahl §§ 244 Abs. 1 Nr. 3 und Abs. 4, 244a StGB",
              "Diebstahl insgesamt und zwar:",
              "Diebstahl insgesamt von Kraftwagen einschl. unbefugte Ingebrauchnahme",
              "Diebstahl insgesamt von Mopeds und Krafträdern einschl. unbefugte Ingebrauchnahme",
              "Diebstahl insgesamt von Fahrrädern einschl. unbefugte Ingebrauchnahme",
              "Diebstahl insgesamt an/aus Kraftfahrzeugen",
              "Taschendiebstahl insgesamt"
              ],
    "drug": ["Rauschgiftdelikte (soweit nicht bereits mit anderer Schlüsselzahl erfasst)"]
}


def crime_filter(df, categories, column="Straftat"):
    """Construct filter for crimes listed in [categories]

    Args:
        df ([type]): [description]
        column (str, optional): [description]. Defaults to "Straftat".

    Returns:
        [type]: [description]
    """
    filt = df[column] == categories[0]
    for cat in categories:
        filt = filt | (df[column] == cat)
    return filt


def year_to_path(year):
    """Compute path of data on crimes for the given year

    Args:
        year (int): year

    Returns:
        str: path to data file
    """
    data_path = os.path.join(utils.path_to_data_dir(), "raw", "crime")
    path = str(year)
    files = os.listdir(os.path.join(data_path, "bka", path))
    if len(files) > 0:
        return os.path.join(data_path, "bka", path, files[0])


def prep_data_2013():
    """Preprocess data on crimes in 2013

    Returns:
        DataFrame: data on crimes in 2013
    """
    df = pd.read_excel(year_to_path(2013), skiprows=6)[
        ["Unnamed: 1", "Unnamed: 2", "Fälle"]].dropna(subset=["Unnamed: 2"])
    df.rename(columns={
        "Unnamed: 1": "Straftat", "Unnamed: 2": "kreis_key", "Fälle": "crimes_2013"}, inplace=True)
    cats = df.Straftat.unique()

    df.kreis_key = utils.fix_key(df.kreis_key)

    df = df[["Straftat", "kreis_key", "crimes_2013"]]

    df_ges = pd.DataFrame()

    for cat in crime_categories:
        df_cat = df[crime_filter(df, crime_categories[cat])]
        df_cat = df_cat.groupby("kreis_key").sum().reset_index()
        df_cat = df_cat.rename(columns={"crimes_2013": f"{cat}_2013"})
        if not df_ges.empty:
            df_ges = df_ges.merge(df_cat, on="kreis_key", how="outer")
        else:
            df_ges = df_cat

        df_ges = utils.fix_goettingen(df_ges, f"{cat}_2013")

    df_ges = utils.fix_goettingen(df_ges, "crimes_2013")

    return df_ges, list(cats)


def prep_data_14_20(year):
    """Preprocess data on crimes in the specified year

    Args:
        year (int): year in the range 2014-2020

    Returns:
        DataFrame: data on crimes in the given year
    """
    crime_clm = f"crimes_{year}"

    df = pd.read_csv(year_to_path(year), encoding="ISO-8859-1",
                     delimiter=";", skiprows=1, thousands=",")
    cats = df.Straftat.unique()
    df.rename(columns={"Gemeindeschlüssel": "kreis_key", "Anzahl erfasste Faelle": crime_clm,
              "erfasste Fälle": crime_clm, "Gemeindeschluessel": "kreis_key", "erfasste Faelle": crime_clm}, inplace=True)
    df.kreis_key = utils.fix_key(df.kreis_key)

    df_ges = pd.DataFrame()

    for cat in crime_categories:
        df_cat = df[["kreis_key", "Straftat", crime_clm]
                    ][crime_filter(df, crime_categories[cat])]
        df_cat = df_cat.groupby("kreis_key").sum().reset_index()
        df_cat = df_cat.rename(columns={crime_clm: f"{cat}_{year}"})
        if not df_ges.empty:
            df_ges = df_ges.merge(df_cat, on="kreis_key")
        else:
            df_ges = df_cat
        if year <= 2016:
            df_ges = utils.fix_goettingen(df_ges, f"{cat}_{year}")

    return df_ges, list(cats)


def prep_data():
    """Preprocess crime data

    Returns:
        DataFrame: crime data in the years 2013-2020
    """
    df, cats = prep_data_2013()

    for i in range(2014, 2021):
        df2, cats2 = prep_data_14_20(i)
        df = df.merge(df2, on="kreis_key", how="outer")
        cats = cats + cats2
    cats_df = pd.DataFrame(pd.Series(cats).unique())
    cats_df.to_csv(os.path.join(utils.path_to_data_dir(),
                   "processed", "crime", "categories.csv"))

    # calculate crime rates

    df_population = population.load_data()

    df_crime_rates = df.merge(df_population, on="kreis_key")
    years = list(filter(lambda y: f"population_{y}" in df_crime_rates.columns and f"crimes_{y}" in df_crime_rates.columns, range(2000, datetime.today(
    ).year+2)))

    cols = ["kreis_key"]

    for cat in crime_categories:
        for year in years:
            df_crime_rates[f"{cat}_pp_{year}"] = df_crime_rates[f"{cat}_{year}"] / \
                df_crime_rates[f"population_{year}"]
        cols = cols + [f"{cat}_{year}" for year in years]
        cols = cols + [f"{cat}_pp_{year}" for year in years]

    df_crime_rates = df_crime_rates[cols]

    return df_crime_rates


def load_data():
    """Load crime data from csv

    Returns:
       DataFrame : data on crimes
    """
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed",
                                  "crime", "crime.csv"), index_col=0)
    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
