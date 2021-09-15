from requests import request, Response
from urllib.parse import urlencode

class SearchdataSDK:    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.params = {}   
        
    def execute(self) -> Response:
        """
        Executes the request formed on the object

        :return: Returns a Response
        """ 
        if self.is_searchdata_api:
            if not self.engine:
                raise Exception('Missing "engine" parameter')
            if not self.api_key:
                raise Exception('Missing "api_key" parameter')
        return self.request(self.params)
    
    def executeRaw(self, params: dict = {}) -> Response:
        """
        Executes the request formed on the params parameter

        :param params: The params dict
        :return: Returns a Response
        """
        if self.is_searchdata_api:
            if not self.engine:
                raise Exception('Missing "engine" parameter')
            if not self.api_key:
                raise Exception('Missing "api_key" parameter')
        return self.request(params)
        
    def request(self, params: dict) -> Response:
        """
        Executes the final request

        :param params: The params dict
        :return: Returns a Response
        """
        if self.is_searchdata_api:
            params['api_key'] = self.api_key
            params['engine'] = self.engine

        full_api_url = self.api_url + '?' + urlencode(params)
        
        return request("GET", full_api_url)