from searchdata import SearchdataSDK

class SearchdataGoogleAutocomplete(SearchdataSDK):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.engine = 'google_autocomplete'
        self.api_url = 'https://api.searchdata.io/v1'
        self.is_searchdata_api = True
        
    def set_q(self, value: str):
        """
        Set parameter q

        :param value: The terms that you are searching for (the query). 
        """
        self.params['q'] = value

    def get_q(self) -> str:
        """
        Get parameter q

        :return: Returns parameter q
        """
        return self.params['q']