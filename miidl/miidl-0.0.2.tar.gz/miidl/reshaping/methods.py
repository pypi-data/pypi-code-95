from math import sqrt, ceil
from warnings import warn
import numpy as np


def edge(n_feature, width=None, devide=4):
    if type(width) is int:
        if width**2 >= n_feature:
            if width % devide == 0:
                return width
            else:
                warn(f"Width of {width} seems not a good choice.", Warning)
                return width
        else:
            warn(f"Width of {width} seems a bad choice. Chenged to auto mode.", Warning)
            width = None

    if width is None:
        width = ceil(sqrt(n_feature))
        while True:
            if width % devide == 0:
                return width
            else:
                width += 1

def integrate(df, patch_len):
    for i in range(patch_len):
        df['patch_'+str(i)] = 0
    return df


def auto(df):
    df = df.fillna(0)
    n_feature = len(list(df))
    n_sample = len(df.index)
    width = edge(n_feature)
    patch = width**2 - n_feature
    df = integrate(df, patch)
    features = list(df)
    ndarr = df.to_numpy()
    ndarr = ndarr.reshape(n_sample, 1, width, width)
    return ndarr, features

# def custom(df, width):
#     n_feature = len(list(df))
#     n_sample = len(df.index)
#     width = edge(n_feature, width)
#     patch_len = width**2 - n_feature
#     df = integrate(df, patch_len)
#     features = list(df)
#     ndarr = df.to_numpy()
#     ndarr = ndarr.reshape(n_sample, 1, width, width)
#     return ndarr, features

def none(df):
    ndarr = df.to_numpy()
    features = list(df)
    return ndarr, features