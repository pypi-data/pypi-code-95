# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 17:07:39 2021

@author: xndm
"""
from tqdm import tqdm
from glob import glob
import numpy as np
import pandas as pd
from .evaluate import timmer
import warnings
warnings.filterwarnings("ignore")


@timmer
def read_part_csv(file_path, parse_dates=None, sep=','):
    csv_files = sorted(glob(file_path))
    frames = (pd.read_csv(file, parse_dates=parse_dates, sep=sep) for file in tqdm(csv_files))
    concat_df = pd.concat(frames)
    concat_df.reset_index(drop=True, inplace=True)
    print('read data done ...')
    return concat_df



def reduce_mem_usage_num(df, verbose=True, deep=True, except_cols=()):
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    start_mem = df.memory_usage(deep=deep).sum() / 1024**2
#     for col in df.columns:
    for col in [col for col in df.columns if col not in except_cols]:
        col_type = df[col].dtypes
        if col_type in numerics:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)    # ！！！
#                     df[col] = df[col].astype(np.float32)    ##  np.float16 在pandas里是没有的。在这改成32
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
    end_mem = df.memory_usage(deep=deep).sum() / 1024**2
    if verbose:
        print(f'{start_mem:.2f} Mb =>> {end_mem:.2f} Mb  compression ratio: {end_mem/start_mem:.2f}')
    return df


def reduce_mem_usage_cate(df, verbose=True, deep=True, except_cols=()):
    start_mem = df.memory_usage(deep=deep).sum() / 1024**2
    for c in [col for col in df.columns if col not in except_cols]:
        # col_type = df[c].dtypes
        mem_before = df[c].memory_usage(deep=True) / 1e6  #
        mem_cate = df[c].astype('category').memory_usage(deep=True) / 1e6  #
        c_type = df[c].dtype
        compress_rate = mem_before/mem_cate
        if compress_rate > 1:
            print(c, ' ', c_type, ':', f'{compress_rate:.2f}')
            df[c] = df[c].astype('category')
    end_mem = df.memory_usage(deep=deep).sum() / 1024**2
    if verbose:
        print('='*20)
        print(f'{start_mem:.2f} Mb =>> {end_mem:.2f} Mb  compression ratio: {end_mem/start_mem:.2f}')
    return df
