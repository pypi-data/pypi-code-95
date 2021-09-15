from searchdata import SearchdataSDK

class SearchdataGoogleScholarProfiles(SearchdataSDK):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.engine = 'google_scholar_profiles'
        self.api_url = 'https://api.searchdata.io/v1'
        self.is_searchdata_api = True

    def set_mauthors(self, value: str):
        """
        Set parameter mauthors

        :param value: The terms that you are searching for (the query). 
        """
        self.params['mauthors'] = value

    def set_after_author(self, value: str):
        """
        Set parameter after_author

        :param value: Defines the next page token and must preceed the value of before_author. 
        """
        self.params['after_author'] = value

    def set_before_author(self, value: str):
        """
        Set parameter before_author

        :param value: Defines the previous page token. 
        """
        self.params['before_author'] = value

    def set_hl(self, value: str):
        """
        Set parameter hl

        :param value: The language you want to use for your google search. 
        """
        self.params['hl'] = value

    def get_mauthors(self) -> str:
        """
        Get parameter mauthors

        :return: Returns parameter mauthors
        """
        return self.params['mauthors']

    def get_after_author(self) -> str:
        """
        Get parameter after_author

        :return: Returns parameter after_author
        """
        return self.params['after_author']

    def get_before_author(self) -> str:
        """
        Get parameter before_author

        :return: Returns parameter before_author
        """
        return self.params['before_author']

    def get_hl(self) -> str:
        """
        Get parameter hl

        :return: Returns parameter hl
        """
        return self.params['hl']