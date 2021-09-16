import miidl
from .methods import log2, loge, log2p, logep, zscore, median, mean, none

def normalize(df, method='log2p'):
    return getattr(miidl.normalization, method)(df)

call = {
    'log2': log2,
    'loge': loge,
    'log2p': log2p, 
    'logep': logep, 
    'zscore': zscore, 
    'median': median, 
    'mean': mean, 
    'none': none
}