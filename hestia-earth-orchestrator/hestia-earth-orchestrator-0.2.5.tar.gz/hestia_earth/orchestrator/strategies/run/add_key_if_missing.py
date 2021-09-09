from hestia_earth.orchestrator.log import logger
from hestia_earth.orchestrator.utils import get_required_model_param


def should_run(data: dict, model: dict):
    key = get_required_model_param(model, 'key')
    run = data.get(key) is None
    logger.info('model=%s, key=%s, value=%s, should_run=%s', model.get('model'), key, model.get('value'), run)
    return run
