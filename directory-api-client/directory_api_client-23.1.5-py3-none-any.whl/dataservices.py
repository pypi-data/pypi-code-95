from directory_api_client.base import AbstractAPIClient

url_country_data_by_country = 'dataservices/country-data/'
url_cia_world_factbook_data = 'dataservices/cia-factbook-data/'
url_population_data = 'dataservices/population-data/'
url_population_data_by_country = 'dataservices/population-data-by-country/'
url_society_data_by_country = 'dataservices/society-data-by-country/'
url_last_year_import_data_by_country = 'dataservices/lastyearimportdatabycountry/'
url_suggested_countries = '/dataservices/suggested-countries/'
url_trading_blocs_by_country = '/dataservices/trading-blocs/'
url_trade_barriers = '/dataservices/trade-barriers/'


class DataServicesAPIClient(AbstractAPIClient):
    def get_country_data_by_country(self, countries, fields):
        return self.get(url=url_country_data_by_country, params={'countries': countries, 'fields': fields})

    def get_cia_world_factbook_data(self, country, data_key):
        return self.get(
            url=url_cia_world_factbook_data, params={'country': country, 'data_key': data_key}, use_fallback_cache=True
        )

    def get_population_data(self, country, target_ages):
        return self.get(
            url=url_population_data, params={'country': country, 'target_ages': target_ages}, use_fallback_cache=True
        )

    def get_population_data_by_country(self, countries: list):
        return self.get(url=url_population_data_by_country, params={'countries': countries}, use_fallback_cache=True)

    def get_society_data_by_country(self, countries: list):
        return self.get(url=url_society_data_by_country, params={'countries': countries}, use_fallback_cache=True)

    def get_last_year_import_data_by_country(self, commodity_code, countries: list):
        return self.get(
            url=url_last_year_import_data_by_country, params={'commodity_code': commodity_code, 'countries': countries}
        )

    def suggested_countries_by_hs_code(self, hs_code):
        return self.get(
            url=url_suggested_countries,
            params={
                'hs_code': hs_code,
            },
        )

    def trading_blocs_by_country(self, iso2):
        return self.get(
            url=url_trading_blocs_by_country,
            params={
                'iso2': iso2,
            },
        )

    def get_trade_barriers(self, sectors: list, countries: list):
        return self.get(url=url_trade_barriers, params={'sectors': sectors, 'countries': countries})
