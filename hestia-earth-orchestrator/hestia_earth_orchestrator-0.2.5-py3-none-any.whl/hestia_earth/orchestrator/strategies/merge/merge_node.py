import pydash

from hestia_earth.orchestrator.log import logger
from hestia_earth.orchestrator.utils import update_node_version, _average

METHOD_TIER_ORDER = [
    'tier 1',
    'tier 2',
    'tier 3',
    'measured',
    'background'
]


def _has_threshold_diff(source: dict, dest: dict, key: str, threshold: float):
    source_value = _average(source.get(key), None)
    dest_value = _average(dest.get(key), 0)
    delta = None if source_value is None else (
        abs(source_value - dest_value) / (1 if source_value == 0 else source_value)
    )
    term_id = dest.get('term', {}).get('@id', dest.get('@id'))
    # skip replace if new value is 0 (means some inputs were missing)
    should_merge = source_value is None or (dest_value > 0 and delta > threshold)
    logger.debug('merge %s for %s with threshold=%s, delta=%s: %s', key, term_id, threshold, delta, should_merge)
    return should_merge


def _should_merge_threshold(source: dict, dest: dict, args: dict):
    [key, threshold] = args.get('replaceThreshold', [None, 0])
    return True if key is None else _has_threshold_diff(source, dest, key, threshold)


def _should_merge_lower_tier(source: dict, dest: dict, args: dict):
    source_tier = METHOD_TIER_ORDER.index(source.get('methodTier', METHOD_TIER_ORDER[0]))
    dest_tier = METHOD_TIER_ORDER.index(dest.get('methodTier', METHOD_TIER_ORDER[-1]))
    term_id = dest.get('term', {}).get('@id', dest.get('@id'))
    should_merge = args.get('replaceLowerTier', False) or dest_tier >= source_tier
    logger.debug('merge for %s with original tier=%s, new tier=%s: %s',
                 term_id, source.get('methodTier'), dest.get('methodTier'), should_merge)
    return should_merge


_MERGE_FROM_ARGS = {
    'replaceThreshold': _should_merge_threshold,
    'replaceLowerTier': _should_merge_lower_tier
}


def _should_merge_args(source: dict, dest: dict, args: dict):
    return all([func(source, dest, args) for func in _MERGE_FROM_ARGS.values()])


def merge(source: dict, dest: dict, version: str, args={}):
    should_merge = source is None or _should_merge_args(source, dest, args)
    return update_node_version(version, pydash.objects.merge({}, source, dest), source) if should_merge else source
