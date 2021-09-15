from searchdata import SearchdataSDK

class SearchdataGoogleMapsReviews(SearchdataSDK):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.engine = 'google_maps_reviews'
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

    def set_location(self, value: str):
        """
        Set parameter location

        :param value: Defines where do you want the search to originate from. Please use SearchdataLocations to obtain a location. 
        """
        self.params['location'] = value

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

    def get_location(self) -> str:
        """
        Get parameter location

        :return: Returns parameter location
        """
        return self.params['location']