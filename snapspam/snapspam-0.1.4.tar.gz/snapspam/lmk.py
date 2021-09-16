"""Functions to spam an LMK message."""
from bs4 import BeautifulSoup
from dataclasses import dataclass
import json
import random
import requests
import string
from typing import List
from urllib.parse import quote, unquote, urlencode


@dataclass(frozen=True)
class Choice:
    """A choice on an LMK poll

    Args:
        cid (str): The ID of the choice to send to the API
        contents (str): The display contents of the choice
    """
    cid: str
    contents: str


class LMK:
    """Initialize the LMK class

    Args:
        link_or_id (str): The LMK URL or the ID portion of the URL
        proxies (dict, optional): Proxies to use for requests
    """

    def __init__(self, link_or_id: str, proxies: dict = {}):
        self._lmk_id = self._link_to_id(link_or_id)
        self._headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        self._proxies = proxies

    def get_choices(self) -> List[Choice]:
        """Get a list of the choices on the poll along with their IDs

        Returns:
            List[Choice]: The list of choices
        """
        request_url = f'https://www.onlmk.com/question/{quote(self._lmk_id)}'
        r = requests.get(request_url, proxies=self._proxies)
        soup = BeautifulSoup(r.content, 'html.parser')

        if r.status_code != 200:
            print(f'Failed to get choices. Code: {r.status_code}')
            print(r.content)
            exit(1)

        choices_div = soup.find('div', {'class': 'btnPanelRounded'})
        choices_children = choices_div.findChildren('div', recursive=False)

        choices = []

        for choice in choices_children:
            cid = choice.get('data-uid')
            contents = choice.find('td').contents[0]
            choices.append(Choice(cid, contents))

        return choices

    def post(self, choice: str) -> requests.Response:
        """Send a message to the API

        Args:
            choice (str): The ID of the choice to send

        Returns:
            requests.Response: The response from the POST
        """
        self._choice = choice
        uid = ''.join(
            random.choice(string.ascii_lowercase + string.digits)
            for i in range(22))
        msg = urlencode(self._make_message(uid))

        return self._post_message(msg)

    def _link_to_id(self, link: str):
        """Convert a sendit link to just the hex ID

        Args:
            link (str): The sendit link

        Returns:
            str: The ID from the link
        """
        encoded = link.split('/')[-1]
        return unquote(encoded)

    def _make_message(self, uid: str) -> dict:
        """Makes a dict to POST to the LMK API to send the message

        Args:
            uid (str): An ID to identify the sender. Can be randomly generated.

        Returns:
            dict: The dict to stringify and POST to the API
        """
        return {
            "content": json.dumps({"q": self._choice}, separators=(',', ':')),
            "questionUserToken": self._lmk_id,
            "uid": uid,
        }

    def _post_message(self, msg: str) -> requests.Response:
        """POST the message to the LMK API

        Args:
            msg (dict): Stringified message returned by LMK._make_message

        Returns:
            requests.Response: The response from the POST
        """
        request_url = 'https://www.onlmk.com/api/v4/questionResults'
        return requests.post(
            request_url,
            data=msg,
            headers=self._headers,
            proxies=self._proxies,
        )
