from typing import Dict, Callable
from ..eta import Eta
from crostab import Crostab
from collections import namedtuple
from veho.matrix import iso as iso_matrix
from veho.columns import mapper as map_columns
from aryth.math import round_d2

LapseAndResult = namedtuple('Lapse_Result', 'lapse result')


def strategies(
        repeat: int,
        candidates: Dict[str, any],
        methods: Dict[str, Callable],
        show_average: bool = True,
        show_params: bool = False,
        param_type: type = None
) -> LapseAndResult(Crostab, Crostab):
    eta = Eta(log=False)
    param_labels = list(candidates.keys())
    method_labels = list(methods.keys())
    (h, w) = (len(param_labels), len(method_labels))
    crostab_lapse = Crostab(side=param_labels[:], head=method_labels[:], rows=iso_matrix(h, w, None))
    crostab_result = Crostab(side=param_labels[:], head=method_labels[:], rows=iso_matrix(h, w, None))
    for param_label, param in candidates.items():
        for method_label, method in methods.items():
            eta.lap_milli()
            result = None
            if param_type == tuple:
                for i in range(repeat): result = method(*param)
            elif param_type == dict:
                for i in range(repeat): result = method(**param)
            else:
                for i in range(repeat): result = method(param)
            lapse = eta.lap_milli() * 1000
            print(f"[lap] +{lapse :0.4f}ms [#] {repeat} [param] {param_label} [method] {method_label}")
            crostab_lapse[param_label, method_label] = lapse
            crostab_result[param_label, method_label] = result
    if show_average:
        averages = map_columns(crostab_lapse.rows, lambda col: sum(col) / len(col))
        crostab_lapse.unshift_row('average', averages)
    crostab_lapse.mutate(round_d2)
    if show_params:
        params = list(candidates.values())
        crostab_result.unshift_column('param', params)
    return LapseAndResult(crostab_lapse, crostab_result)
