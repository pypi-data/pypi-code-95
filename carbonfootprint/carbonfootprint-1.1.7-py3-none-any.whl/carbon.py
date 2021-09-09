import pandas as pd
import numpy as np
import carbonemisison.fuelmix
import os
from carbonemisison.NamedLists import column_list_Mwh, column_list_carbon, column_list_power


class Carbon:

    def __init__(self):
        """Return a dataframe about carbon emission.

            Contains the following fields:
                index          68 non-null int64
                fuel name      68 non-null object
                carbon content 68 non-null object
            ... (docstring truncated) ...
        """
        dirname = os.path.dirname(__file__)
        filname = os.path.join(dirname, 'dataset/carbon4.csv')
        self.df_carbon = pd.read_csv(filname)

    def calculate_carbonemission(self, df):
        for col in df[np.array(column_list_power)].columns:
            for j, carbon in self.df_carbon.iterrows():
                if carbon[0] in col:
                    # print("Match between two tables for "+col+ " and "+ carbon[0] +" - "+ str(carbon[1]))
                    df['carbon_' + col.replace("(W)", "(kgeCO2)")] = df[col] * carbon[
                        2] * 0.001  # Wh * gCO2eq/Wh * 0.001 = eqKgCo2
        df["carbon_total(kgeCO2)"] = df[np.array(column_list_carbon)].sum(axis=1)
        return df
