from math import floor
from numbers import Real

from pandas import DataFrame
from pandas.core.series import Series

from marco.quantitative_frame import QuantitativeFrame


class UngroupedFrame(QuantitativeFrame):
    """
    """

    def arithmetic_mean(self) -> Real:
        return sum(self.data) / len(self.data)

    def median(self) -> Real:
        classes = self.dataframe["Clase"]
        n = len(classes)
        middle = floor(n / 2)
        if n % 2 == 0:
            return (classes[middle - 1] + classes[middle]) / 2
        return classes[middle]

    def trend(self) -> Real:
        (_, row) = self._find_trend_row()
        return row["Clase"]

    def median_row(self) -> Series:
        middle = self.median()
        index = floor(len(self.dataframe) / 2)
        if len(self.dataframe) % 2 != 0:
            index = next(i for i, row in self.dataframe.iterrows() if row["Clase"] == middle)
        return self.dataframe.iloc[[index]]

    def trend_row(self) -> DataFrame:
        (index, _) = self._find_trend_row()
        return self.dataframe.iloc[[index]]
