from dataclasses import dataclass, field as dcf
from datetime import datetime
from typing import List, Union

from manparams.io import dump, load, to_record


@dataclass
class Params:
    """Simulation params"""

    ff: float = 0.
    ii: int = 1
    ll: List[int] = dcf(default_factory=list)
    tt: datetime = None
    uu: Union[int, datetime] = 1


def test_load_fill_params_values():
    params = load(Params, {'ff': 10, 'ii': 3, 'll': [1, 2], 'tt': "2020-01-03T10:00", 'uu': "2020-01-03T10:00"})

    assert params.ff == 10
    assert type(params.ff) == float
    assert params.ii == 3
    assert type(params.ii) == int
    assert params.ll == [1, 2]
    assert type(params.ll) == list
    assert params.tt == datetime(2020, 1, 3, 10)
    assert type(params.tt) == datetime
    assert params.uu == datetime(2020, 1, 3, 10)
    assert type(params.uu) == datetime


def test_dump_converts_to_native_python_objects():
    params = Params(ff=10., ii=3, ll=[4, 5], tt=datetime(2020, 1, 1, 13), uu=1)

    assert dump(params) == {'ff': 10., 'ii': 3, 'll': [4, 5], 'tt': params.tt.isoformat(), 'uu': 1}


def test_to_record_preserve_types():
    data = dict(ff=10., ii=3, ll=[4, 5], tt=datetime(2020, 1, 1, 13), uu=1)
    params = Params(**data)

    assert to_record(params) == data
