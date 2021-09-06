import json
from pathlib import Path
from operator import itemgetter

from django.conf import settings


fixtures = Path(__file__).parent / 'fixtures'

HONG_KONG_ISO_CODE = 'HK'

UNITED_KINGDOM_ISO_CODE = 'GB'

UAE_TERRITORIES_ISO_CODES = ['AE-AZ', 'AE-AJ', 'AE-DU', 'AE-FU', 'AE-RK', 'AE-SH', 'AE-UQ']


# UrlString is just a convenience wrapper around a string for making it easy to build url strings.
# It borrows the `/` syntax from `pathlib` to allow for the building of natural looking urls.
#
# eg home = UrlString('https://example.com')
# new_url = home / 'foo' / 'bar'
#
# which returns 'https://example.com/foo/bar/'
class UrlString(str):
    def __truediv__(self, other):
        base = self.strip('/')
        path = other.strip('/')
        return UrlString(f'{base}/{path}/')


def get_url(url_name, default):
    return UrlString(getattr(settings, url_name, None) or default)


# from https://data.trade.gov.uk/catalogue/reference-data-sets/reference/countries-and-territories
with (fixtures / 'countries-and-territories.json').open('r') as f:
    countries_and_territories_data = []
    for item in json.loads(f.read()):
        if not item['End date']:
            countries_and_territories_data.append(item)


def build_country_choices(
    exclude_all_territories=False,
    include=[],
    exclude=[]
):
    country_list = []
    exclude = UAE_TERRITORIES_ISO_CODES + exclude
    for country_item in countries_and_territories_data:
        if country_item['Key'] in include:
            country_list.append((country_item['Key'], country_item['Name']))
        elif country_item['Key'] in exclude or (exclude_all_territories and country_item['Type'] == 'Territory'):
            continue
        else:
            country_list.append((country_item['Key'], country_item['Name']))
    country_list.sort(key=itemgetter(1))
    return country_list


def build_country_region_choices(
    exclude_all_territories=False,
    include=[],
    exclude=[]
):

    country_list = []
    exclude = UAE_TERRITORIES_ISO_CODES + exclude
    with (fixtures / 'countryorterritory.region.type.json').open('r') as f:
        countries_and_territories_data = []
        for item in json.loads(f.read()):
            iso2 = item.get('Country or Territory: ISO 2 code')
            if (iso2 in include) or not (iso2 in exclude or (exclude_all_territories and item['Type'] == 'Territory')):
                country_list.append({
                    'id': iso2,
                    'name': item.get('Country or Territory: Name'),
                    'region': item.get('HMTC overseas region: Overseas regions name'),
                    'type': item.get('Type')
                })

    return country_list
