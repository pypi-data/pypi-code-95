import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np

def display_time(t_1, t_2):
    time = t_2-t_1
    if time >= 60 and time < 3600:
        print("Calculation time:", round(time/60, 1), "min")
    elif time >= 3600:
        print("Calculation time:", round(time/3600, 1),  "h")
    else:
        print("Calculation time:", round(time, 1), "s")

