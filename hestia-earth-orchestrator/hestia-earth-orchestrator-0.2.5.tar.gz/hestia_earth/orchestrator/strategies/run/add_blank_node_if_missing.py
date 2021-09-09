from hestia_earth.orchestrator.log import logger
from hestia_earth.orchestrator.utils import get_required_model_param, find_term_match

_RUN_FROM_ARGS = {
    'runNonReliable': lambda node: node.get('reliability', 1) >= 3,
    'runNonAddedTerm': lambda node: 'term' not in node.get('added', []),
    'runNonMeasured': lambda node: node.get('methodTier') != 'measured'
}


def _run_args(node: dict, args: dict):
    keys = list(filter(lambda key: args[key] is True, args.keys()))
    return len(keys) > 0 and all([_RUN_FROM_ARGS[key](node) for key in keys])


def should_run(data: dict, model: dict):
    key = get_required_model_param(model, 'key')
    term_id = get_required_model_param(model, 'value')
    args = model.get('runArgs', {})
    node = find_term_match(data.get(key, []), term_id, None)
    run = node is None or _run_args(node, args)
    logger.info('model=%s, key=%s, value=%s, should_run=%s', model.get('model'), key, term_id, run)
    return run
