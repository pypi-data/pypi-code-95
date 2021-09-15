from requests import Response
from searchdata import SearchdataSDK

class SearchdataLocations(SearchdataSDK):
    def __init__(self):
        super().__init__()
        self.api_url = 'https://locations.searchdata.io/'
        self.is_searchdata_api = False
        
    def execute(self, q: str = None, limit: int = None) -> Response:
        """
        Executes the request formed on the object

        :param q: The query for the location.
        :param limit: The limit of results.
        :return: Returns a Response
        """
        if q is not None:
            self.set_q(q)
        if limit is not None:
            self.set_limit(limit)
        if 'q' not in self.params or not self.params['q']:
            raise Exception('Missing "q" parameter')
        if 'limit' not in self.params or not self.params['limit']:
            raise Exception('Missing "limit" parameter')
        response = super().execute()
        return response
    
    def executeRaw(self, params: dict = {}) -> Response:
        """
        Executes the request formed on the params parameter

        :param params: The params dict
        :return: Returns a Response
        """
        if 'q' not in params or not params['q']:
            raise Exception('Missing "q" parameter')
        if 'limit' not in params or not params['limit']:
            raise Exception('Missing "limit" parameter')
        response = super().executeRaw(params)
        return response;
    
    def set_q(self, value: str):
        """
        Set parameter q

        :param value: The query for the location
        """
        self.params['q'] = value

    def set_limit(self, value: int):
        """
        Set parameter limit

        :param value: The limit of results
        """
        self.params['limit'] = value
        
    def get_q(self) -> str:
        """
        Get parameter q

        :return: Returns parameter q
        """
        return self.params['q']

    def get_limit(self) -> int:
        """
        Get parameter limit

        :return: Returns parameter limit
        """
        return self.params['limit']
    
    def process_location(self, location: dict = {}) -> Response:
        """
        Returns the concatenated location string that needs to be sent to the searchdata API

        :param location: One given location dictionary from the results
        :return: Returns the concatenated location string that needs to be sent to the searchdata API
        """
        return '"' + location['Criteria ID'] + '","' + location['Name'] + '","' + location['Canonical Name'] + '","' + location['Parent ID'] + '","' + location['Country Code'] + '","' + location['Target Type'] + '",' + location['Status']