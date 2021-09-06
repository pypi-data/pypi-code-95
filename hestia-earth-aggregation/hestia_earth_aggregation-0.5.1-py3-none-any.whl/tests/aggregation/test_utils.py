from tests.utils import IMPACTS
from hestia_earth.aggregation.utils import get_time_ranges, _group_by_product


def test_get_time_ranges():
    assert get_time_ranges('1996') == [(1990, 1999), (2000, 2009), (2010, 2019), (2020, 2029)]
    assert get_time_ranges('2000') == [(2000, 2009), (2010, 2019), (2020, 2029)]


def test_group_impacts_by_product():
    results = _group_by_product(IMPACTS, ['emissionsResourceUse'], True)
    assert len(results.keys()) == 11

    # non-including organic/irrigated matrix
    results = _group_by_product(IMPACTS, ['emissionsResourceUse'], False)
    assert len(results.keys()) == 6
