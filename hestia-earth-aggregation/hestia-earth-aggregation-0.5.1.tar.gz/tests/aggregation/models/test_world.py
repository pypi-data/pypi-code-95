from unittest.mock import patch
import json

from tests.utils import SOURCE, WORLD, fixtures_path, start_year, end_year, fake_aggregated_version
from hestia_earth.aggregation.utils import _group_by_product
from hestia_earth.aggregation.models.world import aggregate

class_path = 'hestia_earth.aggregation.models.world'


@patch('hestia_earth.aggregation.cycle.emission._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.cycle.input._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.cycle.product._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.cycle.utils._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.cycle.utils._aggregated_node', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.site.measurement._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.site.utils._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.site.utils._aggregated_node', side_effect=fake_aggregated_version)
def test_aggregate_cycle(*args):
    from hestia_earth.aggregation.cycle.utils import (
        AGGREGATION_KEYS, _format_for_grouping, _update_cycle, _remove_duplicated_cycles, _format_world_results
    )

    with open(f"{fixtures_path}/cycle/terms/aggregated.jsonld", encoding='utf-8') as f:
        terms = json.load(f)
    with open(f"{fixtures_path}/cycle/countries/aggregated.jsonld", encoding='utf-8') as f:
        countries = json.load(f)
    with open(f"{fixtures_path}/cycle/world/aggregated.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    cycles = _remove_duplicated_cycles(terms + countries)
    cycles = _format_for_grouping(cycles)
    results = aggregate(AGGREGATION_KEYS, _group_by_product(cycles, AGGREGATION_KEYS, False))
    results = list(map(_format_world_results, results))
    results = list(map(_update_cycle(WORLD, start_year, end_year, SOURCE, False), results))
    assert results == expected
    assert len(results) == 2


@patch('hestia_earth.aggregation.impact_assessment.indicator._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.impact_assessment.utils._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.impact_assessment.utils._aggregated_node', side_effect=fake_aggregated_version)
def test_aggregate_impact(*args):
    from hestia_earth.aggregation.impact_assessment.utils import (
        AGGREGATION_KEY, _update_impact_assessment, _remove_duplicated_impact_assessments, _format_world_results
    )

    with open(f"{fixtures_path}/impact-assessment/terms/aggregated.jsonld", encoding='utf-8') as f:
        terms = json.load(f)
    with open(f"{fixtures_path}/impact-assessment/countries/aggregated.jsonld", encoding='utf-8') as f:
        countries = json.load(f)
    with open(f"{fixtures_path}/impact-assessment/world/aggregated.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    impacts = _remove_duplicated_impact_assessments(terms + countries)
    results = aggregate(AGGREGATION_KEY, _group_by_product(impacts, [AGGREGATION_KEY], False))
    results = list(map(_format_world_results, results))
    results = list(map(_update_impact_assessment(WORLD, start_year, end_year, SOURCE, False), results))
    assert results == expected
    assert len(results) == 6
