import numpy as np
import pandas as pd

from typing import Union, Iterable, Dict

from ..mlutils import MultiColumnLabelEncoderDecoder


def generate_combinatorial_dataset(names: Dict[str, Union[np.ndarray, list]], variables: Iterable[str] = None):
    """
        Generate the combinatorial dataset for a list of variables

        names : a dictionary
            names.key = name of the variable
            names.value = values that the variable can assume
        variables :  the iterables with the list of variables/columns for which to generate the dataset
            If variables = None, all the names.keys() will be used

        Returns
        -----------------------
        pd.DataFrame

        A dataframe with the combinatorial dataset
    """
    variables = np.array(variables) if variables is not None else np.array(list(names.keys()))
    generator = [names[node] for node in variables]
    return pd.DataFrame(np.array(np.meshgrid(*generator)).T.reshape(-1, len(variables)), columns=variables)


def number_of_combinations_encoder(encdec: MultiColumnLabelEncoderDecoder, variables: Iterable = None):
    if variables is None:
        variables = encdec.get_encoder().keys()

    combs = 1
    for var in variables:
        combs *= len(encdec.get_encoder()[var])
    return combs


def random_combinatorial_sample(encdec: MultiColumnLabelEncoderDecoder, size: int, variables: Iterable = None, replace=True):
    if variables is None:
        variables = encdec.get_encoder().keys()
    if not replace:
        size = min(size, number_of_combinations_encoder(encdec, variables))
    sample = pd.DataFrame()
    while len(sample) < size:
        tempsample = pd.DataFrame()
        for var in variables:
            var_bowl = np.array(list(encdec.get_encoder()[var].keys()))
            tempsample[var] = np.random.choice(var_bowl, size - len(sample), replace=True)
        sample = pd.concat([sample, tempsample], axis=0)
        if not replace:
            sample.drop_duplicates(inplace=True)
    sample.reset_index(inplace=True, drop=True)
    return sample


def get_features_encodings(X: pd.DataFrame):
    """
        Return the uniques values for each feature
    """
    feature_encodings = {}
    for f in X.columns:
        u = X[f].unique()
        feature_encodings[f] = sorted(u)
    return feature_encodings


def number_of_combinations_categorical(X: [pd.DataFrame, MultiColumnLabelEncoderDecoder]):
    """
        Return the number of combinations of inputs
    """
    combs = 1
    feature_encodings = get_features_encodings(X)
    for f, encods in feature_encodings.items():
        combs *= len(encods)
    return combs