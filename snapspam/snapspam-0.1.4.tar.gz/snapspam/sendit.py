"""Functions to spam a sendit message."""
import json
import requests
import secrets


class Sendit:
    """Initialize the Sendit class

    Args:
        link_or_id (str): The sendit URL or the ID portion of the URL
        message (str): The message to send
        delay (int, optional): The delay before sending the message
            (part of the sendit API). Defaults to 0.
        proxies (dict, optional): Proxies to use for requests
    """

    def __init__(self,
                 link_or_id: str,
                 message: str,
                 delay: int = 0,
                 proxies: dict = {}):
        self._sendit_id = self._link_to_id(link_or_id)
        self._message = message
        self._delay = delay
        self._s = requests.Session()
        self._headers = {
            'App-Id': 'c2ad997f-1bf2-4f2c-b5fd-83926e8f3c65',
            'App-Version': '1.0',
            'Content-Type': 'application/json',
        }
        self._proxies = proxies

    def post(self):
        """Send a message to the API

        Returns:
            requests.Response: The response from the POST
        """
        info = self._get_recipient_info()
        if info['status'] != 'success':
            print(f'Sticker info request failed. Response:\n{info}')
            exit(1)

        author = info['payload']['sticker']['author']['id']
        shadow_token = f'{secrets.token_hex(4)}-{secrets.token_hex(2)}-{secrets.token_hex(2)}-{secrets.token_hex(2)}-{secrets.token_hex(6)}'
        msg = json.dumps(self._make_message(author, shadow_token),
                         separators=(',', ':'))

        return self._post_message(msg)

    def _link_to_id(self, link: str) -> str:
        """Convert a sendit link to just the hex ID

        Args:
            link (str): The sendit link

        Returns:
            str: The ID from the link
        """
        return link.split('/')[-1][:36]

    def _get_recipient_info(self) -> dict:
        """Gets info about the recipient required to send the message

        Returns:
            dict: The parsed response body
        """
        request_url = f'https://api.getsendit.com/v1/stickers/{self._sendit_id}?user=null&shadowToken='
        self._s.options(
            request_url,
            headers=self._headers,
            proxies=self._proxies,
        )
        r = self._s.get(
            request_url,
            headers=self._headers,
            proxies=self._proxies,
        )
        return json.loads(r.content)

    def _make_message(self, author_id: str, author_shadow_token: str) -> dict:
        """Makes a dict to POST to the sendit API to send the message

        Args:
            author_id (str): The ID of the author returned by the sendit API
            author_shadow_token (str): Identifies the message sender.
              Can be randomly generated.

        Returns:
            dict: The dict to stringify and POST to the API
        """
        return {
            'recipient_identity': {
                'type': 'id',
                'value': author_id,
            },
            'type': 'sendit.post-type:question-and-answer-v1',
            'data': {
                'question': self._message,
            },
            'ext_data': {
                'sticker_id': self._sendit_id,
                'author_shadow_token': author_shadow_token,
                'browser_language': 'en',
            },
            'timer': self._delay,
        }

    def _post_message(self, msg: str) -> requests.Response:
        """POST the message to the sendit API

        Args:
            msg (dict): Stringified message returned by Sendit._make_message
        
        Returns:
            requests.Response: The response from the POST
        """
        request_url = 'https://api.getsendit.com/v1/posts'
        self._s.options(
            request_url,
            headers=self._headers,
            proxies=self._proxies,
        )
        return self._s.post(
            request_url,
            data=msg,
            headers=self._headers,
            proxies=self._proxies,
        )
