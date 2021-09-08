from typing import Union

import sklearn.decomposition
from .corpca import CorPCA


def PCA(criterion: str, *args, **kargs) -> Union[sklearn.decomposition.PCA, CorPCA]:
    if criterion == 'variance':
        return sklearn.decomposition.PCA(*args, **kargs)
    elif criterion == 'mse':
        return CorPCA(*args, **kargs)
    else:
        raise ValueError('criterion must be "variance" or "mse";'
                         f'instead of {criterion}')
