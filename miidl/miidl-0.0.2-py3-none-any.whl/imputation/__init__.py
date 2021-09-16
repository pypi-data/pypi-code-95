import miidl
from .methods import knn, minimum, median, mean, none

def impute(df, method='none'):
    return getattr(miidl.imputation, method)(df)

call = {
    'knn': knn, 
    'minimum': minimum, 
    'median': median, 
    'mean': mean,
    'none': none
}