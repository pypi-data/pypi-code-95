from searchdata import SearchdataSDK

class SearchdataYandexSearch(SearchdataSDK):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.engine = 'yandex'
        self.api_url = 'https://api.searchdata.io/v1'
        self.is_searchdata_api = True
    
    def set_text(self, value: str):
        """
        Set parameter text

        :param value: The terms that you are searching for (the query). 
        """
        self.params['text'] = value

    def set_device(self, value: str):
        """
        Set parameter device

        :param value: The device used for your google search. Must be a value from ["desktop","mobile","tablet"]
        """
        self.params['device'] = value

    def set_lang(self, value: str):
        """
        Set parameter lang

        :param value: The language to use for the search. 
        """
        self.params['lang'] = value

    def set_location(self, value: str):
        """
        Set parameter location

        :param value: Defines where do you want the search to originate from. Please use SearchdataLocations to obtain a location. 
        """
        self.params['location'] = value

    def set_lr(self, value: str):
        """
        Set parameter lr

        :param value: ID of the country or region to search. Determines the rules for ranking documents. 
        """
        self.params['lr'] = value

    def set_p(self, value: int):
        """
        Set parameter p

        :param value: The page number. Count starts from 0. 
        """
        self.params['p'] = value

    def set_yandex_domain(self, value: str):
        """
        Set parameter yandex_domain

        :param value: The yandex domain from where the search is performed. 
        """
        self.params['yandex_domain'] = value

    def get_text(self) -> str:
        """
        Get parameter text

        :return: Returns parameter text
        """
        return self.params['text']

    def get_device(self) -> str:
        """
        Get parameter device

        :return: Returns parameter device
        """
        return self.params['device']

    def get_lang(self) -> str:
        """
        Get parameter lang

        :return: Returns parameter lang
        """
        return self.params['lang']

    def get_location(self) -> str:
        """
        Get parameter location

        :return: Returns parameter location
        """
        return self.params['location']

    def get_lr(self) -> str:
        """
        Get parameter lr

        :return: Returns parameter lr
        """
        return self.params['lr']

    def get_p(self) -> int:
        """
        Get parameter p

        :return: Returns parameter p
        """
        return self.params['p']

    def get_yandex_domain(self) -> str:
        """
        Get parameter yandex_domain

        :return: Returns parameter yandex_domain
        """
        return self.params['yandex_domain']