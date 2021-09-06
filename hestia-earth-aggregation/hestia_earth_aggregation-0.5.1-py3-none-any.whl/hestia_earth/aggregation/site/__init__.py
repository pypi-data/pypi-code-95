from hestia_earth.utils.tools import non_empty_list

from hestia_earth.aggregation.models.terms import aggregate as aggregate_by_term
from .utils import (
    AGGREGATION_KEY,
    _format_results, _update_site, _group_by_siteType
)


def aggregate_country(country: dict, sites: list, source: dict, *args) -> list:
    sites = _group_by_siteType(sites)
    aggregates = aggregate_by_term(AGGREGATION_KEY, sites)
    sites = non_empty_list(map(_format_results, aggregates))
    sites = list(map(_update_site(country, source), sites))
    return sites


def aggregate_global(*args): return aggregate_country(*args)
