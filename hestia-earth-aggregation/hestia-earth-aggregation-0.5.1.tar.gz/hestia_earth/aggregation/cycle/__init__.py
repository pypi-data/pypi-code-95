from hestia_earth.utils.tools import non_empty_list

from hestia_earth.aggregation.utils import _group_by_product
from hestia_earth.aggregation.models.terms import aggregate as aggregate_by_term
from hestia_earth.aggregation.models.countries import aggregate as aggregate_by_country
from hestia_earth.aggregation.models.world import aggregate as aggregate_world
from .utils import (
    AGGREGATION_KEYS,
    _format_for_grouping, _format_terms_results, _format_country_results, _format_world_results,
    _update_cycle, _remove_duplicated_cycles
)


def aggregate_country(country: dict, cycles: list, source: dict, start_year: int, end_year: int) -> list:
    # step 1: aggregate all cycles indexed on the platform
    cycles = _format_for_grouping(cycles)
    cycles = _group_by_product(cycles, AGGREGATION_KEYS, True)
    aggregates = aggregate_by_term(AGGREGATION_KEYS, cycles)
    cycles = non_empty_list(map(_format_terms_results, aggregates))
    cycles = list(map(_update_cycle(country, start_year, end_year, source), cycles))

    # step 2: use aggregated cycles to calculate country-level cycles
    country_cycles = _group_by_product(_format_for_grouping(cycles), AGGREGATION_KEYS, False)
    aggregates = aggregate_by_country(AGGREGATION_KEYS, country_cycles)
    country_cycles = non_empty_list(map(_format_country_results, aggregates))
    country_cycles = list(map(_update_cycle(country, start_year, end_year, source, False), country_cycles))

    # step 3: remove duplicates for product without matrix organic/irrigated
    cycles = _remove_duplicated_cycles(cycles + country_cycles)

    return cycles


def aggregate_global(country: dict, cycles: list, source: dict, start_year: int, end_year: int) -> list:
    cycles = _format_for_grouping(cycles)
    cycles = _group_by_product(cycles, AGGREGATION_KEYS, False)
    aggregates = aggregate_world(AGGREGATION_KEYS, cycles)
    cycles = non_empty_list(map(_format_world_results, aggregates))
    cycles = list(map(_update_cycle(country, start_year, end_year, source, False), cycles))
    return cycles
