from unittest.mock import patch
import json

from tests.utils import (
    SOURCE, fixtures_path, fake_grouped_cycles, fake_grouped_impacts, fake_grouped_sites, start_year, end_year,
    fake_aggregated_version
)
from hestia_earth.aggregation.models.terms import aggregate

class_path = 'hestia_earth.aggregation.models.terms'


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
        AGGREGATION_KEYS, _update_cycle, _format_terms_results
    )

    with open(f"{fixtures_path}/cycle/terms/aggregated.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    cycles = fake_grouped_cycles()
    results = aggregate(AGGREGATION_KEYS, cycles)
    results = list(map(_format_terms_results, results))
    results = list(map(_update_cycle(None, start_year, end_year, SOURCE), results))
    assert results == expected
    assert len(results) == 2


@patch('hestia_earth.aggregation.impact_assessment.indicator._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.impact_assessment.utils._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.impact_assessment.utils._aggregated_node', side_effect=fake_aggregated_version)
def test_aggregate_impact(*args):
    from hestia_earth.aggregation.impact_assessment.utils import (
        AGGREGATION_KEY, _update_impact_assessment, _format_terms_results
    )

    with open(f"{fixtures_path}/impact-assessment/terms/aggregated.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    impacts = fake_grouped_impacts()
    results = aggregate(AGGREGATION_KEY, impacts)
    results = list(map(_format_terms_results, results))
    results = list(map(_update_impact_assessment(None, start_year, end_year, SOURCE), results))
    assert results == expected
    assert len(results) == 11


@patch('hestia_earth.aggregation.site.measurement._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.site.utils._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.site.utils._aggregated_node', side_effect=fake_aggregated_version)
def test_aggregate_site(*args):
    from hestia_earth.aggregation.site.utils import (
        AGGREGATION_KEY, _update_site, _format_results
    )

    with open(f"{fixtures_path}/site/terms/aggregated.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    impacts = fake_grouped_sites()
    results = aggregate(AGGREGATION_KEY, impacts)
    results = list(map(_format_results, results))
    results = list(map(_update_site(None, SOURCE), results))
    assert results == expected
    assert len(results) == 1
