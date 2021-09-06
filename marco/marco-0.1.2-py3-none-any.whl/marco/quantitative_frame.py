from typing import List, Tuple
from numbers import Real
from pandas import DataFrame, Series


class QuantitativeFrame:
    def __init__(self, data: List[Real], dataframe: DataFrame, interval: int) -> None:
        self.data = data
        self.dataframe = dataframe
        self.interval = interval
        self.__median_index: int = None
        self.__trend_index: int = None

    def __find_median_row(self) -> Tuple[int, Series]:
        n_2 = len(self.data) / 2
        return next((i, row) for i, row in self.dataframe.iterrows() if row["Ni"] > n_2)

    def __find_trend_row(self) -> Tuple[int, Series]:
        index = self.__trend_index = self.dataframe["ni"].argmax()
        return (index, self.dataframe.iloc[self.__trend_index])

    def arithmetic_mean(self) -> Real:
        return sum(self.dataframe["mi x ni"]) / len(self.data)

    def median(self) -> Real:
        (self.__median_index, median_row) = self.__find_median_row()
        Fi = self.dataframe.iloc[self.__median_index - 1]["Ni"]
        fi = median_row["ni"]
        Linf = median_row["Clase"][0]
        A = self.interval
        n_2 = len(self.data) / 2

        return Linf + A * ((n_2 - Fi) / fi)

    def trend(self) -> Real:
        (index, row) = self.__find_trend_row()
        Linf = row["Clase"][0]
        A = self.interval
        fi = row["ni"]
        Fi = self.dataframe.iloc[index - 1]["ni"]
        fi_1 = self.dataframe.iloc[index + 1]["ni"]

        return Linf + A * (fi - Fi) / ((fi - Fi) + (fi - fi_1))

    def median_row(self) -> DataFrame:
        if self.__median_index is None:
            (self.__median_index, _) = self.__find_median_row()
        return self.dataframe.iloc[[self.__median_index]]

    def trend_row(self) -> DataFrame:
        (index, _) = self.__find_trend_row()
        return self.dataframe.iloc[[index]]
