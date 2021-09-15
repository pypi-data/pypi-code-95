from searchdata import SearchdataSDK

class SearchdataGoogleScholar(SearchdataSDK):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.engine = 'google_scholar'
        self.api_url = 'https://api.searchdata.io/v1'
        self.is_searchdata_api = True   

    def set_q(self, value: str):
        """
        Set parameter q

        :param value: The terms that you are searching for (the query). 
        """
        self.params['q'] = value

    def set_cites(self, value: str):
        """
        Set parameter cites

        :param value: Parameter defines unique ID for an article to trigger Cited By searches. 
        """
        self.params['cites'] = value

    def set_as_ylo(self, value: str):
        """
        Set parameter as_ylo

        :param value: The parameter defines the year from when you want the results to be included. 
        """
        self.params['as_ylo'] = value

    def set_as_yhi(self, value: str):
        """
        Set parameter as_yhi

        :param value: The parameter defines the year until which you want the results to be included. 
        """
        self.params['as_yhi'] = value

    def set_scisbd(self, value: int):
        """
        Set parameter scisbd

        :param value: Represents if it should include only abstract results (set on 1) or all the results (set on 0). Must be a value from [0,1]
        """
        self.params['scisbd'] = value

    def set_as_vis(self, value: str):
        """
        Set parameter as_vis

        :param value: Represents if you would like to include citations or not. Set it to 1 to exclude citations or 0 otherwise. Must be a value from [0,1]
        """
        self.params['as_vis'] = value

    def set_lr(self, value: str):
        """
        Set parameter lr

        :param value: The languages as a list separated through |. For example: lang_en|lang_ar .
        """
        self.params['lr'] = value

    def set_hl(self, value: str):
        """
        Set parameter hl

        :param value: The language you want to use for your google search. 
        """
        self.params['hl'] = value

    def set_start(self, value: int):
        """
        Set parameter start

        :param value: The offset of the google search results. Represents the number of results that you want to skip. 
        """
        self.params['start'] = value

    def set_num(self, value: int):
        """
        Set parameter num

        :param value: The number of results returned on each page. 
        """
        self.params['num'] = value

    def set_safe(self, value: str):
        """
        Set parameter safe

        :param value: This parameter allows you to filter or not the adult content. Must be a value from ["active","off"]
        """
        self.params['safe'] = value

    def get_q(self) -> str:
        """
        Get parameter q

        :return: Returns parameter q
        """
        return self.params['q']

    def get_cites(self) -> str:
        """
        Get parameter cites

        :return: Returns parameter cites
        """
        return self.params['cites']

    def get_as_ylo(self) -> str:
        """
        Get parameter as_ylo

        :return: Returns parameter as_ylo
        """
        return self.params['as_ylo']

    def get_as_yhi(self) -> str:
        """
        Get parameter as_yhi

        :return: Returns parameter as_yhi
        """
        return self.params['as_yhi']

    def get_scisbd(self) -> int:
        """
        Get parameter scisbd

        :return: Returns parameter scisbd
        """
        return self.params['scisbd']

    def get_as_vis(self) -> str:
        """
        Get parameter as_vis

        :return: Returns parameter as_vis
        """
        return self.params['as_vis']

    def get_lr(self) -> str:
        """
        Get parameter lr

        :return: Returns parameter lr
        """
        return self.params['lr']

    def get_hl(self) -> str:
        """
        Get parameter hl

        :return: Returns parameter hl
        """
        return self.params['hl']

    def get_start(self) -> int:
        """
        Get parameter start

        :return: Returns parameter start
        """
        return self.params['start']

    def get_num(self) -> int:
        """
        Get parameter num

        :return: Returns parameter num
        """
        return self.params['num']

    def get_safe(self) -> str:
        """
        Get parameter safe

        :return: Returns parameter safe
        """
        return self.params['safe']