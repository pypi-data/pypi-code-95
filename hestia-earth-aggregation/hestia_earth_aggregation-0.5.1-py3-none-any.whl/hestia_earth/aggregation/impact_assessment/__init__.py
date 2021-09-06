from hestia_earth.utils.tools import non_empty_list

from hestia_earth.aggregation.utils import _group_by_product
from hestia_earth.aggregation.models.terms import aggregate as aggregate_by_term
from hestia_earth.aggregation.models.countries import aggregate as aggregate_by_country
from hestia_earth.aggregation.models.world import aggregate as aggregate_world
from .utils import (
    AGGREGATION_KEY,
    _format_terms_results, _format_country_results, _format_world_results,
    _update_impact_assessment, _remove_duplicated_impact_assessments
)


def aggregate_country(country: dict, impacts: list, source: dict, start_year: int, end_year: int) -> list:
    # step 1: aggregate all impacts indexed on the platform
    impacts = _group_by_product(impacts, [AGGREGATION_KEY], True)
    aggregates = aggregate_by_term(AGGREGATION_KEY, impacts)
    impacts = non_empty_list(map(_format_terms_results, aggregates))
    impacts = list(map(_update_impact_assessment(country, start_year, end_year, source), impacts))

    # step 2: use aggregated impacts to calculate country-level impacts
    aggregates = aggregate_by_country(AGGREGATION_KEY, _group_by_product(impacts, [AGGREGATION_KEY], False))
    weight_impacts = non_empty_list(map(_format_country_results, aggregates))
    weight_impacts = list(map(_update_impact_assessment(country, start_year, end_year, source, False), weight_impacts))

    # step 3: remove duplicates for product without matrix organic/irrigated
    impacts = _remove_duplicated_impact_assessments(impacts + weight_impacts)

    return impacts


def aggregate_global(country: dict, impacts: list, source: dict, start_year: int, end_year: int) -> list:
    impacts = _group_by_product(impacts, [AGGREGATION_KEY], False)
    aggregates = aggregate_world(AGGREGATION_KEY, impacts)
    impacts = non_empty_list(map(_format_world_results, aggregates))
    impacts = list(map(_update_impact_assessment(country, start_year, end_year, source, False), impacts))
    return impacts
