from hestia_earth.models.utils.impact_assessment import _get_impacts_dict, get_product, impact_value, get_region_id


def test_get_impacts_dict():
    impacts = _get_impacts_dict()
    assert len(impacts.keys()) > 0


def test_get_product():
    term_id = 'id'
    product = {
        'term': {'@id': term_id}
    }
    cycle = {'products': [product]}
    impact = {'product': {'@id': term_id}}

    # no product
    assert not get_product(impact)

    # with cycle and product
    impact['cycle'] = cycle
    assert get_product(impact) == product


def test_get_value():
    impact = {
        'emissionsResourceUse': [
            {
                'term': {
                    '@id': 'ch4ToAirSoil'
                },
                'value': 100
            }
        ]
    }
    # multiplies the emissionsResourceUse values with a coefficient
    assert impact_value(impact, 'co2EqGwp100ExcludingClimate-CarbonFeedbacksIpcc2013') == 2850


def test_get_region_id():
    impact = {'country': {'@id': ''}}

    impact['country']['@id'] = 'region-world'
    assert get_region_id(impact) == 'region-world'
    impact['country']['@id'] = 'GADM-AUS'
    assert get_region_id(impact) == 'GADM-AUS'
    impact['country']['@id'] = 'GADM-AUS.1_1'
    assert get_region_id(impact) == 'GADM-AUS.1_1'
    impact['country']['@id'] = 'GADM-AUS.1.2_1'
    assert get_region_id(impact) == 'GADM-AUS.1_1'
    impact['country']['@id'] = 'GADM-AUS.2.10_1'
    assert get_region_id(impact) == 'GADM-AUS.2_1'
