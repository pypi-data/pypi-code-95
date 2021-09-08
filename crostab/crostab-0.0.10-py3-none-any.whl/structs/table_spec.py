import json
from typing import List, Dict, Callable

from aryth import stat
from crostab import Aggreg, Crit


class TableSpec:
    side: str
    head: str
    filters: List[Crit]
    aggregs: List[Aggreg]
    calc: Callable[[Dict[str, List[float]]], float]

    def __init__(self,
                 side: str,
                 head: str,
                 filters: List[Crit],
                 aggregs: List[Aggreg],
                 calc: Callable[[Dict[str, List[float]]], float]):
        self.side = side
        self.head = head
        self.filters = filters
        self.aggregs = aggregs
        self.calc = calc
        for aggreg in self.aggregs:
            aggreg.stat = sum if aggreg.stat is not None else aggreg.stat

    @property
    def filters_count(self):
        return len(self.filters)

    @property
    def aggregs_count(self):
        return len(self.aggregs)

    @property
    def filter_labels(self):
        return [f.field for f in self.filters]

    @property
    def aggreg_labels(self):
        return [ag.field for ag in self.aggregs]

    @property
    def aggreg_stats(self):
        return [ag.stat or sum for ag in self.aggregs]

    def aggreg_exec(self, accums):
        lex = {ag.field: ag.stat(accums[i])
               for i, ag in enumerate(self.aggregs)}
        return lex

    def calc_exec(self, accums):
        lex = {ag.field: ag.stat(accums[i])
               for i, ag in enumerate(self.aggregs)}
        return self.calc(lex)

    def to_json(self):
        lex = {
            'side': self.side,
            'head': self.head,
            'filters': self.filters,
            'aggregs': self.aggregs,
            'calc': self.calc
        }
        return json.dumps(lex)
