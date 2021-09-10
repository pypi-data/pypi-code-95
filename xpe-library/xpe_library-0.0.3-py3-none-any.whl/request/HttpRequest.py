import requests
from requests.auth import HTTPBasicAuth


class HttpRequest:
    """Class to do all http requests"""
    __TIMEOUT = 3.0
    __EXPECTED_RESPONSE_CODES = [200, 201, 202]

    def __init__(self, login: str, password: str):
        """
        :param login : Username to auth request
        :param password : Password to auth request
        """
        self.__login = login
        self.__password = password

    def change_auth(self, login: str, password: str) -> None:
        """Change auth credentials.

         :param login : Username to auth request
         :param password : Password to auth request
        """
        self.__login = login
        self.__password = password

    def get(self, url: str) -> (int, dict):
        """ Get request method

        :param url: url to get resource
        :return: :tuple: First value is code request and second is response data (JSON)
        """
        try:
            response: requests.Response = requests.get(url=url, auth=HTTPBasicAuth(self.__login, self.__password), timeout=self.__TIMEOUT)
            body: dict = None
            if response.status_code in self.__EXPECTED_RESPONSE_CODES:
                body = response.json()
            return response.status_code, body
        except requests.exceptions.RequestException as error:
            return 0, None

    def post(self, url: str, payload: dict = None) -> (int, dict):
        """Post request method

        :param url: url to post resource
        :param payload: A dictionary with the information to send
        :return: :tuple: First value is code request and second is response data (JSON)
        """
        try:
            response: requests.Response = requests.post(url=url, json=payload, auth=HTTPBasicAuth(self.__login, self.__password), timeout=self.__TIMEOUT)
            body: dict = None
            if response.status_code in self.__EXPECTED_RESPONSE_CODES:
                body = response.json()
            return response.status_code, body
        except requests.exceptions.RequestException as error:
            print(error)
            return 0, None
