import pandas as pd  # type: ignore

from tktl.future.utils import JSONStructure


def series_deserialize(*, value: JSONStructure, sample: pd.Series) -> pd.Series:
    return pd.Series(value)


def series_serialize(*, value: pd.Series) -> str:
    return value.to_json(orient="records", date_format="iso")


def series_to_example(*, value: pd.Series) -> str:
    return value.iloc[[0]].to_json(orient="records", date_format="iso")
