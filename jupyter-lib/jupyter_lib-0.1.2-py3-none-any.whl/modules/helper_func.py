import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np


def shift_s(s, shift_arr):
    df = []

    for shift in shift_arr:
        df.append(s.shift(shift).rename(s.name + "_" + str(shift)))

    df = pd.concat(df, axis=1)
    return df

