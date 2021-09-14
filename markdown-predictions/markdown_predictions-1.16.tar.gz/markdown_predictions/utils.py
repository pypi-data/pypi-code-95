import numpy as np

def compute_rmse(y_pred, y_test):
    return ((y_pred - y_test) ** 2).mean() ** 0.5

def linearize_dates(date_vec, base_date=np.datetime64("2021-09-19")):
    return ((base_date - date_vec) / np.timedelta64(1, 'D')) / 7
