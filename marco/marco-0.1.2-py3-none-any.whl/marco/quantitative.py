from typing import List, Dict, Tuple
from pandas import DataFrame, Series
from enum import Enum, auto
from numbers import Real
from numpy import arange
from math import ceil, log10
from src.marco.quantitative_frame import QuantitativeFrame


class QuantitativeType(Enum):
    DISCRETE = auto()
    CONTINUOUS = auto()


QuantitativeClass = List[Tuple[Real, Real]]


def quantitative_table(
    data: List[Real], type=QuantitativeType.CONTINUOUS
) -> QuantitativeFrame:
    Ro = range_set(data)
    class_n = class_amount(len(data))
    fixed_data = apply_range_fix(data, Ro)
    interval_value = interval(Ro, class_n)
    q_class = quantitative_class(fixed_data, interval_value, class_n)
    mi = class_mark(q_class)
    ni = quantitative_absolute_frecuency(sorted(data), q_class)
    mi_x_ni = [a * b for a, b in zip(mi, ni.values())]

    return QuantitativeFrame(
        data,
        DataFrame(
            {
                "Clase": q_class,
                "mi": mi,
                "ni": ni.values(),
                "Ni": Series(ni.values()).cumsum().tolist(),
                "mi x ni": mi_x_ni,
            },
        ),
        interval_value,
    )


def range_set(data: List[Real]) -> Real:
    return max(data) - min(data)


def class_amount(data_amount: int) -> int:
    return ceil(1 + 3.3 * log10(data_amount))


def interval(range_interval: Real, class_amount: int) -> int:
    return ceil(range_interval / class_amount)


def quantitative_class(
    data: List[Real], interval: int, class_amount: int
) -> QuantitativeClass:
    tuples_list = []
    lower_limit = data[0]
    for _ in range(class_amount):
        upper_limit = lower_limit + interval
        tuples_list.append((lower_limit, upper_limit))
        lower_limit += interval

    return tuples_list


def class_mark(quantitative_class: QuantitativeClass) -> List[Real]:
    return [(q[0] + q[1]) / 2 for q in quantitative_class]


def fix_range(class_amount: int, interval: int, range_interval: Real) -> Real:
    return class_amount * interval - range_interval


def apply_range_fix(data: List[Real], range_interval: Real) -> List[Real]:
    sorted_data = sorted(data)
    class_n = class_amount(len(data))
    interval_value = interval(range_interval, class_n)
    range_fix = fix_range(class_n, interval_value, range_interval) / 2
    sorted_data[0] -= range_fix
    sorted_data[-1] += range_fix
    return sorted_data


def quantitative_absolute_frecuency(
    data: List[Real], q_class: QuantitativeClass
) -> Dict[str, int]:
    mapped = dict()
    i = j = 0
    while i < len(data):
        if data[i] in arange(q_class[j][0], q_class[j][1], 0.5):
            mapped[str(q_class[j])] = mapped.get(str(q_class[j]), 0) + 1
            i += 1
        else:
            if j < len(q_class) - 1:
                j += 1
    return mapped
