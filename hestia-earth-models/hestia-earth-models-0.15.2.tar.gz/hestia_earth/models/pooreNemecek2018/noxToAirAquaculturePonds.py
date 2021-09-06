from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import total_excreta_n, total_excreta_tan
from hestia_earth.models.utils.practice import is_model_enabled
from . import MODEL

EF_Aqua = {'NH3N_NON': 0.0018, 'OtherN_NON': 0.0005}
TERM_ID = 'noxToAirAquaculturePonds'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(excr_tan: float, excr_n: float):
    value = EF_Aqua['NH3N_NON'] * excr_tan + (EF_Aqua['OtherN_NON'] * (excr_n - excr_tan) if excr_n else 0)
    value = value * get_atomic_conversion(Units.KG_NOX, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    inputs = cycle.get('inputs', [])
    excr_n = total_excreta_n(inputs)
    excr_tan = total_excreta_tan(inputs)
    model_enabled = is_model_enabled(MODEL, TERM_ID, cycle.get('practices', [None])[0])

    debugRequirements(model=MODEL, term=TERM_ID,
                      model_enabled=model_enabled,
                      excr_n=excr_n,
                      excr_tan=excr_tan)

    should_run = model_enabled and (excr_n > 0 or excr_tan > 0)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, excr_tan, excr_n


def run(cycle: dict):
    should_run, excr_tan, excr_n = _should_run(cycle)
    return _run(excr_tan, excr_n) if should_run else []
