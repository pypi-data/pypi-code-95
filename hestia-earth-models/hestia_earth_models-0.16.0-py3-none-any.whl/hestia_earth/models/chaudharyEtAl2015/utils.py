from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logger
from hestia_earth.models.utils.impact_assessment import get_site, get_region_id
from . import MODEL


def get_region_factor(impact_assessment: dict, factor: str):
    product = impact_assessment.get('product')
    region_id = get_region_id(impact_assessment)
    ecoregion = get_site(impact_assessment).get('ecoregion')
    lookup_name = 'ecoregion' if ecoregion else 'region-ecoregion-factors' if region_id else None
    col = 'ecoregion' if ecoregion else 'termid' if region_id else None
    try:
        grouping = get_table_value(
            download_lookup(f"{product.get('termType')}.csv", True), 'termid', product.get('@id'),
            column_name('cropGroupingFAO')
        )
        logger.debug('model=%s, factor=%s for product=%s with grouping=%s', MODEL, factor, product.get('@id'), grouping)
        return safe_parse_float(
            get_table_value(
                download_lookup(f"{lookup_name}.csv", True), col, ecoregion or region_id,
                column_name(f"{grouping}_TAXA_AGGREGATED_Median_{factor}")
            )
        ) if grouping and lookup_name else None
    except Exception:
        return None
