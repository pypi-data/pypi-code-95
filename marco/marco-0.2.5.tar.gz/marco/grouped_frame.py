from numbers import Real
from typing import List, Tuple

from pandas import DataFrame, Series
from marco.quantitative_frame import QuantitativeFrame


class GroupedFrame(QuantitativeFrame):
    def __init__(self, data: List[Real], dataframe: DataFrame, interval: int) -> None:
        self.interval = interval
        super().__init__(data, dataframe)

    def __find_median_row(self) -> Tuple[int, Series]:
        n_2 = len(self.data) / 2
        return next((i, row) for i, row in self.dataframe.iterrows() if row["Ni"] > n_2)

    def arithmetic_mean(self) -> Real:
        return sum(self.dataframe["mi x ni"]) / len(self.data)

    def median(self) -> Real:
        (self._median_index, median_row) = self.__find_median_row()
        Fi = self.dataframe.iloc[self._median_index - 1]["Ni"]
        fi = median_row["ni"]
        Linf = median_row["Clase"][0]
        A = self.interval
        n_2 = len(self.data) / 2

        return Linf + A * ((n_2 - Fi) / fi)

    def trend(self) -> Real:
        (index, row) = self._find_trend_row()
        Linf = row["Clase"][0]
        A = self.interval
        fi = row["ni"]
        Fi = self.dataframe.iloc[index - 1]["ni"]
        fi_1 = self.dataframe.iloc[index + 1]["ni"]

        return Linf + A * (fi - Fi) / ((fi - Fi) + (fi - fi_1))

    def median_row(self) -> DataFrame:
        if self._median_index is None:
            (self._median_index, _) = self.__find_median_row()
        return self.dataframe.iloc[[self._median_index]]

    def trend_row(self) -> DataFrame:
        (index, _) = self._find_trend_row()
        return self.dataframe.iloc[[index]]
