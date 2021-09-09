from hestia_earth.orchestrator.log import logger


def should_run(_data: dict, model: dict):
    logger.info('model=%s, key=%s, value=%s, should_run=True', model.get('model'), model.get('key'), model.get('value'))
    return True
