from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.model import find_primary_product

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.ecoClimateZone import get_ecoClimateZone_lookup_value
from hestia_earth.models.utils.cycle import calculate_land_occupation
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

TERM_ID = 'n2OToAirOrganicSoilCultivationDirect'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(histosol: float, organic_soil_factor: float, land_occupation: float):
    value = land_occupation * histosol / 100 * organic_soil_factor * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])

    def _get_measurement_content(term_id: str):
        return most_relevant_measurement_value(measurements, term_id, end_date)

    histosol = _get_measurement_content('histosol')
    eco_climate_zone = _get_measurement_content('ecoClimateZone')
    organic_soil_factor = get_ecoClimateZone_lookup_value(
        eco_climate_zone, 'IPCC_2006_ORGANIC_SOILS_KG_N2O-N_HECTARE') / 10000 if eco_climate_zone else 0
    primary_product = find_primary_product(cycle) or {}
    land_occupation = calculate_land_occupation(cycle, site, primary_product)

    debugRequirements(model=MODEL, term=TERM_ID,
                      organic_soil_factor=organic_soil_factor,
                      land_occupation=land_occupation,
                      histosol=histosol)

    should_run = all([valid_site_type(cycle, True), organic_soil_factor, land_occupation, histosol])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, histosol, organic_soil_factor, land_occupation


def run(cycle: dict):
    should_run, histosol, organic_soil_factor, land_occupation = _should_run(cycle)
    return _run(histosol, organic_soil_factor, land_occupation) if should_run else []
