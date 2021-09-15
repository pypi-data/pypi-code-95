from searchdata import SearchdataSDK

class SearchdataGoogleMaps(SearchdataSDK):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.engine = 'google_maps'
        self.api_url = 'https://api.searchdata.io/v1'
        self.is_searchdata_api = True
    
    def set_q(self, value: str):
        """
        Set parameter q

        :param value: The terms that you are searching for (the query). 
        """
        self.params['q'] = value

    def set_device(self, value: str):
        """
        Set parameter device

        :param value: The device used for your google search. Must be a value from ["desktop","mobile","tablet"]
        """
        self.params['device'] = value

    def set_type(self, value: str):
        """
        Set parameter type

        :param value: The type of search. Must be a value from ["search","place"]
        """
        self.params['type'] = value

    def set_data(self, value: str):
        """
        Set parameter data

        :param value: This parameter is required only if type is set to place. It has to be constructed in the next sequence: !4m5!3m4!1s + data_id + !8m2!3d + latitude + !4d + longitude 
        """
        self.params['data'] = value

    def set_ll(self, value: str):
        """
        Set parameter ll

        :param value: Parameter defines GPS coordinates of location where you want your q (query) to be applied. It has to be constructed in the next sequence: @ + latitude + , + longitude + , + zoom 
        """
        self.params['ll'] = value

    def set_hl(self, value: str):
        """
        Set parameter hl

        :param value: The language you want to use for your google search. 
        """
        self.params['hl'] = value

    def set_google_domain(self, value: str):
        """
        Set parameter google_domain

        :param value: Represents the domain from google that you want to use for your search. 
        """
        self.params['google_domain'] = value

    def get_q(self) -> str:
        """
        Get parameter q

        :return: Returns parameter q
        """
        return self.params['q']

    def get_device(self) -> str:
        """
        Get parameter device

        :return: Returns parameter device
        """
        return self.params['device']

    def get_type(self) -> str:
        """
        Get parameter type

        :return: Returns parameter type
        """
        return self.params['type']

    def get_data(self) -> str:
        """
        Get parameter data

        :return: Returns parameter data
        """
        return self.params['data']

    def get_ll(self) -> str:
        """
        Get parameter ll

        :return: Returns parameter ll
        """
        return self.params['ll']

    def get_hl(self) -> str:
        """
        Get parameter hl

        :return: Returns parameter hl
        """
        return self.params['hl']

    def get_google_domain(self) -> str:
        """
        Get parameter google_domain

        :return: Returns parameter google_domain
        """
        return self.params['google_domain']