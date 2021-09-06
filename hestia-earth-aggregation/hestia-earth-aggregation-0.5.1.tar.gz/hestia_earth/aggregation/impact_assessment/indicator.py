from hestia_earth.schema import IndicatorJSONLD, IndicatorStatsDefinition
from hestia_earth.utils.model import linked_node

from hestia_earth.aggregation.utils import _aggregated_version


def _new_indicator(term: dict, value: float = None):
    node = IndicatorJSONLD().to_dict()
    node['term'] = linked_node(term)
    if value is not None:
        node['value'] = value
        node['statsDefinition'] = IndicatorStatsDefinition.IMPACTASSESSMENTS.value
    return _aggregated_version(node, 'term', 'statsDefinition', 'value')
