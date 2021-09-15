from searchdata import SearchdataSDK

class SearchdataGoogleScholarAuthor(SearchdataSDK):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.engine = 'google_scholar_author'
        self.api_url = 'https://api.searchdata.io/v1'
        self.is_searchdata_api = True

    def set_device(self, value: str):
        """
        Set parameter device

        :param value: The device used for your google search. Must be a value from ["desktop","mobile","tablet"]
        """
        self.params['device'] = value

    def set_author_id(self, value: str):
        """
        Set parameter author_id

        :param value: Represents the id of the author. 
        """
        self.params['author_id'] = value

    def set_view_op(self, value: str):
        """
        Set parameter view_op

        :param value: Is used to view specific parts of the page. Must be a value from ["view_citation","list_colleagues"]
        """
        self.params['view_op'] = value

    def set_sort(self, value: str):
        """
        Set parameter sort

        :param value: Sorts the results. Can be set as title to sort by title or pubdate to sort by published date. Must be a value from ["title","pubdate"]
        """
        self.params['sort'] = value

    def set_citation_id(self, value: str):
        """
        Set parameter citation_id

        :param value: It's used to retrieve a specific citation. It is required when view_op is set on view_citation. 
        """
        self.params['citation_id'] = value

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

    def get_device(self) -> str:
        """
        Get parameter device

        :return: Returns parameter device
        """
        return self.params['device']

    def get_author_id(self) -> str:
        """
        Get parameter author_id

        :return: Returns parameter author_id
        """
        return self.params['author_id']

    def get_view_op(self) -> str:
        """
        Get parameter view_op

        :return: Returns parameter view_op
        """
        return self.params['view_op']

    def get_sort(self) -> str:
        """
        Get parameter sort

        :return: Returns parameter sort
        """
        return self.params['sort']

    def get_citation_id(self) -> str:
        """
        Get parameter citation_id

        :return: Returns parameter citation_id
        """
        return self.params['citation_id']

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