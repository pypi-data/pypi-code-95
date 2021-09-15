from searchdata import SearchdataSDK

class SearchdataGoogleSearch(SearchdataSDK):
    def __init__(self, api_key: str):
        """
        SearchdataGoogleSearch constructor

        :param api_key: The api_key from https://app.searchdata.io 
        """
        super().__init__(api_key)
        self.engine = 'google'
        self.api_url = 'https://api.searchdata.io/v1'
        self.is_searchdata_api = True
        
    def set_q(self, value: str):
        """
        Set parameter q

        :param value: The terms that you are searching for (the query). 
        """
        self.params['q'] = value

    def set_flatten_results(self, value: int):
        """
        Set parameter flatten_results

        :param value: Whether or not to flatten the results. It can be set to 1 (to flatten results) or 0. Must be a value from [0,1]
        """
        self.params['flatten_results'] = value

    def set_device(self, value: str):
        """
        Set parameter device

        :param value: The device used for your google search. Must be a value from ["desktop","mobile","tablet"]
        """
        self.params['device'] = value

    def set_cookie(self, value: str):
        """
        Set parameter cookie

        :param value: Set cookies for your google search. The string must be url encoded.
        """
        self.params['cookie'] = value

    def set_empty_results(self, value: int):
        """
        Set parameter empty_results

        :param value: Can be set to 0 (to hide empty results) or 1 (to display empty results)Must be a value from [0,1]
        """
        self.params['empty_results'] = value

    def set_time_period(self, value: str):
        """
        Set parameter time_period

        :param value: The period of time for the results. Must be a value from ["last_hour","last_day","last_week","last_month","last_year","custom"]
        """
        self.params['time_period'] = value

    def set_time_period_min(self, value: str):
        """
        Set parameter time_period_min

        :param value: The minimum value for time period when the time_period parameter is set to custom. 
        """
        self.params['time_period_min'] = value

    def set_time_period_max(self, value: str):
        """
        Set parameter time_period_max

        :param value: The maximum value for time period when the time_period parameter is set to custom. 
        """
        self.params['time_period_max'] = value

    def set_sort_by(self, value: str):
        """
        Set parameter sort_by

        :param value: Sorts the results. Must be a value from ["relevance","date"]
        """
        self.params['sort_by'] = value

    def set_location(self, value: str):
        """
        Set parameter location

        :param value: Defines where do you want the search to originate from. Please use SearchdataLocations to obtain a location. 
        """
        self.params['location'] = value

    def set_uule(self, value: str):
        """
        Set parameter uule

        :param value: The google encoded location that you want to use for your search. 
        """
        self.params['uule'] = value

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

    def set_gl(self, value: str):
        """
        Set parameter gl

        :param value: The country you want to use for your google search. 
        """
        self.params['gl'] = value

    def set_google_domain(self, value: str):
        """
        Set parameter google_domain

        :param value: Represents the domain from google that you want to use for your search. 
        """
        self.params['google_domain'] = value

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

    def set_ijn(self, value: int):
        """
        Set parameter ijn

        :param value: Parameter defines the page number for Google Images. There are 100 images per page. This parameter is equivalent to start (offset) = ijn * 100. 
        """
        self.params['ijn'] = value

    def set_safe(self, value: str):
        """
        Set parameter safe

        :param value: This parameter allows you to filter or not the adult content. Must be a value from ["active","off"]
        """
        self.params['safe'] = value

    def set_filter(self, value: int):
        """
        Set parameter filter

        :param value: Defines if the filters for similar results and omitted results are on (set to 1) or off (set to 0). Must be a value from [0,1]
        """
        self.params['filter'] = value

    def set_nfpr(self, value: int):
        """
        Set parameter nfpr

        :param value: Defines if it should exclude or not the auto-corrected query. Can have the value 1 to exclude results or 0 otherwise. Must be a value from [0,1]
        """
        self.params['nfpr'] = value

    def set_tbs(self, value: str):
        """
        Set parameter tbs

        :param value: The parameter defines advanced search parameters that aren't possible in the regular query field. (e.g., advanced search for patents, dates, news, videos, images, apps, or text contents). 
        """
        self.params['tbs'] = value

    def set_ludocid(self, value: str):
        """
        Set parameter ludocid

        :param value: Defines the id (CID) of the Google My Business listing you want to scrape. Also known as Google Place ID. 
        """
        self.params['ludocid'] = value

    def set_lsig(self, value: str):
        """
        Set parameter lsig

        :param value: Parameter that you might have to use to force the knowledge graph map view to show up. 
        """
        self.params['lsig'] = value

    def set_tbm(self, value: str):
        """
        Set parameter tbm

        :param value: The parameter defines the type of search you want to do. It can be isch for images, vid for videos, nws for news or shop for shoping. If left unset it will continue with the regular search. Must be a value from ["isch","vid","nws","shop"]
        """
        self.params['tbm'] = value

    def get_q(self) -> str:
        """
        Get parameter q

        :return: Returns parameter q
        """
        return self.params['q']

    def get_flatten_results(self) -> int:
        """
        Get parameter flatten_results

        :return: Returns parameter flatten_results
        """
        return self.params['flatten_results']

    def get_device(self) -> str:
        """
        Get parameter device

        :return: Returns parameter device
        """
        return self.params['device']

    def get_cookie(self) -> str:
        """
        Get parameter cookie

        :return: Returns parameter cookie
        """
        return self.params['cookie']

    def get_empty_results(self) -> int:
        """
        Get parameter empty_results

        :return: Returns parameter empty_results
        """
        return self.params['empty_results']

    def get_time_period(self) -> str:
        """
        Get parameter time_period

        :return: Returns parameter time_period
        """
        return self.params['time_period']

    def get_time_period_min(self) -> str:
        """
        Get parameter time_period_min

        :return: Returns parameter time_period_min
        """
        return self.params['time_period_min']

    def get_time_period_max(self) -> str:
        """
        Get parameter time_period_max

        :return: Returns parameter time_period_max
        """
        return self.params['time_period_max']

    def get_sort_by(self) -> str:
        """
        Get parameter sort_by

        :return: Returns parameter sort_by
        """
        return self.params['sort_by']

    def get_location(self) -> str:
        """
        Get parameter location

        :return: Returns parameter location
        """
        return self.params['location']

    def get_uule(self) -> str:
        """
        Get parameter uule

        :return: Returns parameter uule
        """
        return self.params['uule']

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

    def get_gl(self) -> str:
        """
        Get parameter gl

        :return: Returns parameter gl
        """
        return self.params['gl']

    def get_google_domain(self) -> str:
        """
        Get parameter google_domain

        :return: Returns parameter google_domain
        """
        return self.params['google_domain']

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

    def get_ijn(self) -> int:
        """
        Get parameter ijn

        :return: Returns parameter ijn
        """
        return self.params['ijn']

    def get_safe(self) -> str:
        """
        Get parameter safe

        :return: Returns parameter safe
        """
        return self.params['safe']

    def get_filter(self) -> int:
        """
        Get parameter filter

        :return: Returns parameter filter
        """
        return self.params['filter']

    def get_nfpr(self) -> int:
        """
        Get parameter nfpr

        :return: Returns parameter nfpr
        """
        return self.params['nfpr']

    def get_tbs(self) -> str:
        """
        Get parameter tbs

        :return: Returns parameter tbs
        """
        return self.params['tbs']

    def get_ludocid(self) -> str:
        """
        Get parameter ludocid

        :return: Returns parameter ludocid
        """
        return self.params['ludocid']

    def get_lsig(self) -> str:
        """
        Get parameter lsig

        :return: Returns parameter lsig
        """
        return self.params['lsig']

    def get_tbm(self) -> str:
        """
        Get parameter tbm

        :return: Returns parameter tbm
        """
        return self.params['tbm']