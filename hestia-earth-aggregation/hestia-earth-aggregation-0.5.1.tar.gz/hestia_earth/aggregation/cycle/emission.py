from hestia_earth.schema import EmissionJSONLD, EmissionMethodTier, EmissionStatsDefinition, NodeType
from hestia_earth.utils.model import linked_node

from hestia_earth.aggregation.utils import _aggregated_version

MODEL = 'aggregatedModels'


def _new_emission(term: dict, value: float = None):
    node = EmissionJSONLD().to_dict()
    node['term'] = linked_node(term)
    if value is not None:
        node['value'] = [value]
        node['statsDefinition'] = EmissionStatsDefinition.CYCLES.value
    node['methodModel'] = {'@type': NodeType.TERM.value, '@id': MODEL}
    node['methodTier'] = EmissionMethodTier.TIER_1.value
    return _aggregated_version(node, 'term', 'statsDefinition', 'value', 'methodModel', 'methodTier')
