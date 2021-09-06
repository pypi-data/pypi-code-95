from hestia_earth.schema import IndicatorStatsDefinition, SiteSiteType
from hestia_earth.utils.lookup import download_lookup, _get_single_table_value, column_name, get_table_value
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import emission_value, get_site, get_region_id
from hestia_earth.models.utils.input import sum_input_impacts
from . import MODEL

TERM_ID = 'scarcityWeightedWaterUse'
AWARE_KEY = 'awareWaterBasinId'
IRRIGATED_SITE_TYPES = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.PERMANENT_PASTURE.value
]


def _indicator(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run(impact_assessment: dict, fresh_water: float, awarecf: float):
    cycle = impact_assessment.get('cycle', {})
    inputs_value = sum_input_impacts(cycle.get('inputs', []), TERM_ID)
    logger.debug('model=%s, term=%s, inputs value=%s', MODEL, TERM_ID, inputs_value)
    value = fresh_water * awarecf + inputs_value
    return _indicator(value) if value else None


def _get_factor_from_basinId(site: dict):
    aware_value = site.get(AWARE_KEY)
    lookup_col = 'YR_IRRI' if site.get('siteType') in IRRIGATED_SITE_TYPES else 'YR_NONIRRI'
    return safe_parse_float(
        _get_single_table_value(
            download_lookup(f"{AWARE_KEY}.csv", True), column_name(AWARE_KEY), int(aware_value), column_name(lookup_col)
        ), None
    ) if aware_value else None


def _get_factor_from_region(impact_assessment: dict, site: dict):
    region_id = get_region_id(impact_assessment)
    site_type = site.get('siteType')
    lookup = download_lookup('region-aware-factors.csv')
    lookup_suffix = 'unspecified' if not site_type else ('irri' if site_type in IRRIGATED_SITE_TYPES else 'non_irri')
    return safe_parse_float(get_table_value(lookup, 'termid', region_id, column_name(f"Agg_CF_{lookup_suffix}")), None)


def _should_run(impact_assessment: dict):
    fresh_water = emission_value(impact_assessment, 'freshwaterWithdrawals')
    site = get_site(impact_assessment)
    awarecf = _get_factor_from_basinId(site) or _get_factor_from_region(impact_assessment, site)

    debugRequirements(model=MODEL, term=TERM_ID,
                      fresh_water=fresh_water,
                      awarecf=awarecf)

    should_run = all([fresh_water, awarecf])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, fresh_water, awarecf


def run(impact_assessment: dict):
    should_run, fresh_water, awarecf = _should_run(impact_assessment)
    return _run(impact_assessment, fresh_water, awarecf) if should_run else None
