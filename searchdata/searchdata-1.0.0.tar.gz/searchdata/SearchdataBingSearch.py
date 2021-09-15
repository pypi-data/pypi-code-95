from searchdata import SearchdataSDK

class SearchdataBingSearch(SearchdataSDK):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.engine = 'bing'
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

    def set_cc(self, value: str):
        """
        Set parameter cc

        :param value: The country code from where you want to perform the search. 
        """
        self.params['cc'] = value

    def set_setLang(self, value: str):
        """
        Set parameter setLang

        :param value: The user interface language. 
        """
        self.params['setLang'] = value

    def set_offset(self, value: int):
        """
        Set parameter offset

        :param value: The offset of the bing search results. Represents the number of results that you want to skip. 
        """
        self.params['offset'] = value

    def set_mkt(self, value: str):
        """
        Set parameter mkt

        :param value: The market where the results come from. 
        """
        self.params['mkt'] = value

    def set_safeSearch(self, value: str):
        """
        Set parameter safeSearch

        :param value: It's used to filter adult content. Must be a value from ["off","moderate","strict"]
        """
        self.params['safeSearch'] = value

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

    def get_cc(self) -> str:
        """
        Get parameter cc

        :return: Returns parameter cc
        """
        return self.params['cc']

    def get_setLang(self) -> str:
        """
        Get parameter setLang

        :return: Returns parameter setLang
        """
        return self.params['setLang']

    def get_offset(self) -> int:
        """
        Get parameter offset

        :return: Returns parameter offset
        """
        return self.params['offset']

    def get_mkt(self) -> str:
        """
        Get parameter mkt

        :return: Returns parameter mkt
        """
        return self.params['mkt']

    def get_safeSearch(self) -> str:
        """
        Get parameter safeSearch

        :return: Returns parameter safeSearch
        """
        return self.params['safeSearch']

    def get_location(self) -> str:
        """
        Get parameter location

        :return: Returns parameter location
        """
        return self.params['location']