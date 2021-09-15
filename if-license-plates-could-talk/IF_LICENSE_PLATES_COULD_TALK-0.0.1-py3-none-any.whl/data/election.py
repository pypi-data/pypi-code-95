import pandas as pd
import os
from . import utils


def prep_data():
    """Preprocess data on the Europawahl 2019 / 2014
    """
    election_path = os.path.join(
        utils.path_to_data_dir(), "raw", "election", "ew19_kerg.csv")
    election = pd.read_csv(election_path, skiprows=[0, 1, 3, 4], delimiter=";")
    election.dropna(axis=1, inplace=True, how="all")

    general_columns = ["kreis_key",  "kreis_name", "bl_key", "ew_eli_2019", "ew_eli_2014", "ew_vot_2019", "ew_vot_2014",
                       "ew_invalid_2019", "ew_invalid_2014", "ew_valid_2019", "ew_valid_2014"]

    election.columns = general_columns + list(election.columns[11:])
    election.drop("kreis_name", axis=1, inplace=True)
    election.dropna(subset=["kreis_key"], inplace=True)

    general_columns.remove("kreis_name")

    df_partei = pd.DataFrame()

    new_columns = list(election.columns[:10])
    partei_key = ""
    partei_keys = []
    for i in range(10, len(election.columns)):
        clm = election.columns[i]
        if "Unnamed: " not in clm:
            partei_key = clm.lower()
            replacements = {
                " ": "_",
                "/": "_",
                ".": "_",
                "-": "_",
                "ä": "ae",
                "ö": "oe",
                "ü": "ue",
                "ß": "ss"
            }
            for rep in replacements:
                partei_key = partei_key.replace(rep, replacements[rep])

            df_partei = df_partei.append(
                {"partei_key": partei_key, "partei_name": clm}, ignore_index=True)
            partei_keys.append("")

            new_columns.append(f"ew_vot_abs_{partei_key}_2019")
        else:
            new_columns.append(f"ew_vot_abs_{partei_key}_2014")

    df_partei.to_csv(os.path.join(utils.path_to_data_dir(),
                     "processed", "election", "parties.csv"))

    election.columns = new_columns

    election = election[election.kreis_key > 99]

    election.kreis_key = utils.fix_key(election.kreis_key)

    election = election.fillna(0)

    interesting_parties = ["alternative_fuer_deutschland",
                           'sozialdemokratische_partei_deutschlands', 'buendnis_90_die_gruenen', 'christlich_demokratische_union_deutschlands', "freie_demokratische_partei", "die_linke"]

    # combine CDU / CSU

    for y in [2014, 2019]:
        election[f'ew_vot_abs_christlich_demokratische_union_deutschlands_{y}'] = election[f'ew_vot_abs_christlich_demokratische_union_deutschlands_{y}'] + \
            election[f'ew_vot_abs_christlich_soziale_union_in_bayern_e_v__{y}']
        for party in interesting_parties:
            election[f"ew_vot_rel_{party}_{y}"] = election[f'ew_vot_abs_{party}_{y}'] / \
                election[f"ew_vot_{y}"]
        party_vot_cols = [
            f"ew_vot_rel_{party}_{y}" for party in interesting_parties]

        election[f"ew_winner_{y}"] = election[party_vot_cols].idxmax(
            axis=1).str.slice(11, -5)

    cols_to_return = general_columns + \
        [f"ew_vot_{relabs}_{party}_{y}" for party in interesting_parties for relabs in [
            "rel", "abs"] for y in [2014, 2019]] + ["ew_winner_2014"] + ["ew_winner_2019"]

    return election[cols_to_return]


def load_data():
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(),
                     "processed", "election", "election.csv"), index_col=0)
    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
