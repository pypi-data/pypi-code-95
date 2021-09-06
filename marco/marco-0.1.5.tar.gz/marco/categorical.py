from typing import Any, Dict, List, Union

from pandas import DataFrame, Series


def categorical_table(data: Union[List, Dict]) -> DataFrame:
    mapped_data = data
    if isinstance(data, list):
        mapped_data = map_categorical_data(data)

    cumulative_absolute = Series(mapped_data.values()).cumsum()
    relative_frecuency = [v / sum(mapped_data.values()) for v in mapped_data.values()]
    cumulative_relative = Series(relative_frecuency).cumsum()
    percentage_frequency = [i * 100 for i in relative_frecuency]

    return DataFrame(
        {
            "ni": mapped_data.values(),
            "Ni": cumulative_absolute.tolist(),
            "hi": relative_frecuency,
            "Hi": cumulative_relative.tolist(),
            "%": percentage_frequency,
            "% acum": Series(percentage_frequency).cumsum().tolist(),
        },
        index=mapped_data.keys(),
    ).rename_axis("Clase", axis=1)


def map_categorical_data(data: List[Any]) -> Dict[Any, int]:
    mapped = dict()
    for element in data:
        mapped[element] = mapped.get(element, 0) + 1
    return mapped
