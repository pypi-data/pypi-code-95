from hestia_earth.schema import MeasurementStatsDefinition

from hestia_earth.models.log import logger
from hestia_earth.models.utils.measurement import _new_measurement
from .utils import download, find_existing_measurement, has_geospatial_data, _site_gadm_id
from . import MODEL

TERM_ID = 'soilPh'
EE_PARAMS = {
    'collection': 'T_PH_H2O',
    'type': 'raster',
    'reducer': 'mean'
}
BIBLIO_TITLE = 'The harmonized world soil database. verson 1.0'


def _measurement(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    measurement = _new_measurement(TERM_ID, MODEL, BIBLIO_TITLE)
    measurement['value'] = [value]
    measurement['depthUpper'] = 0
    measurement['depthLower'] = 30
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    return measurement


def _download(site: dict):
    value = download(
        collection=EE_PARAMS['collection'],
        ee_type=EE_PARAMS['type'],
        reducer=EE_PARAMS['reducer'],
        fields=EE_PARAMS['reducer'],
        latitude=site.get('latitude'),
        longitude=site.get('longitude'),
        gadm_id=_site_gadm_id(site),
        boundary=site.get('boundary')
    ).get(EE_PARAMS['reducer'], None)
    return None if value is None else round(value, 1)


def _run(site: dict):
    value = find_existing_measurement(TERM_ID, site) or _download(site)
    return [] if value is None else [_measurement(value)]


def _should_run(site: dict):
    should_run = has_geospatial_data(site)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
