from typing import Union
import numpy as np
import pandas as pd

from ..utils import np_sample


def sample_data(X: Union[pd.DataFrame, np.ndarray],
                n=None,
                frac=None,
                random_state=None,
                replace=False,
                **kwargs) -> Union[pd.DataFrame, np.ndarray]:
    assert frac is None or n is None, "Cannot specify both `n` and `frac`"
    assert not (frac is None and n is None), "One of `n` or `frac` must be passed."

    input_is_pd = isinstance(X, pd.DataFrame)

    if not input_is_pd:
        X = pd.DataFrame(X)

    sample = X.sample(
        n=n,
        frac=frac,
        random_state=random_state,
        replace=replace,
        **kwargs,
    )

    if not input_is_pd:
        return sample.values
    else:
        return sample
