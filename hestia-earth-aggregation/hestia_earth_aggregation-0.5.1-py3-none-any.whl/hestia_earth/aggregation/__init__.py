from concurrent.futures import ThreadPoolExecutor
from pkgutil import extend_path
from hestia_earth.utils.tools import current_time_ms, flatten
from hestia_earth.schema import NodeType

from .log import logger
from .utils import get_time_ranges
from .utils.queries import earliest_date, find_nodes
from .utils.term import DEFAULT_COUNTRY_NAME, _is_global, _fetch_default_country, _fetch_single
from .utils.source import _get_source
from . import cycle
from . import impact_assessment
from . import site

__path__ = extend_path(__path__, __name__)


AGGREGATE = {
    NodeType.CYCLE.value: cycle,
    NodeType.IMPACTASSESSMENT.value: impact_assessment,
    NodeType.SITE.value: site
}


def _call_aggregate_by_type(node_type: str, country: dict, *args):
    aggregation = AGGREGATE[node_type]
    is_global = _is_global(country.get('name'))
    return aggregation.aggregate_global(country, *args) if is_global else aggregation.aggregate_country(country, *args)


def _aggregate_by_timerange(node_type: str, country: dict, source: dict):
    def aggregate(time_range: tuple):
        start_year, end_year = time_range
        nodes = find_nodes(node_type, start_year, end_year, country.get('name'))
        return _call_aggregate_by_type(node_type, country, nodes, source, start_year, end_year)
    return aggregate


def aggregate(type: NodeType, country_name=DEFAULT_COUNTRY_NAME):
    """
    Aggregates data from Hestia.
    Produced data will be aggregated by country or globally if no `country_name` is provided.

    Parameters
    ----------
    type: NodeType
        The type of Node to aggregate. Can be either: `NodeType.IMPACTASSESSMENT`, `NodeType.CYCLE`.
    country_name : str
        Optional - the country Name as found in the glossary to restrict the results by country.
        Returns aggregations for the world by default if not provided.

    Returns
    -------
    list
        A list of aggregations.
        Example: `[<impact_assesment1>, <impact_assesment2>, <cycle1>, <cycle2>]`
    """
    now = current_time_ms()

    node_type = type if isinstance(type, str) else type.value
    earliest_year = earliest_date(node_type, country_name)
    time_ranges = get_time_ranges(earliest_year) if earliest_year else []

    country = _fetch_default_country() if _is_global(country_name) else _fetch_single(country_name)
    if country is None:
        raise Exception('Country not found: ' + country_name)

    source = _get_source()
    if source is None:
        raise Exception('Source not found')

    with ThreadPoolExecutor() as executor:
        aggregations = flatten(executor.map(_aggregate_by_timerange(node_type, country, source), time_ranges))

    logger.info('time=%s, unit=ms', current_time_ms() - now)

    return aggregations
