from so4gp import *
import pandas as pd

df = pd.read_csv('DATASET.csv', sep=' ')
gps = run_genetic_algorithm(df, max_iteration=20)
print(gps)
