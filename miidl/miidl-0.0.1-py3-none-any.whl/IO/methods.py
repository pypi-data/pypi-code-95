import pandas as pd

def read(fname, sep='\t', index_col=0):
    return pd.read_csv(fname, sep=sep, index_col=index_col)

def write(path, df, sep='\t', index=True, header=True, index_label=''):
    df.to_csv(path, sep=sep, index=index, header=header, index_label=index_label)
    return path