import requests
from urllib.parse import urljoin

from .cycle import Cycle


class Session:

    def get_headers(self):
        return {
            'Authorization': 'Bearer ' + self.token
        }

    def get_url(self, path):
        return urljoin(self.url, path)

    def __init__(self, url, username, password):
        self.url = urljoin(url, '/api/')
        login_res = requests.post(
            self.get_url('login'),
            json={
                'name': username,
                'password': password
            }
        )

        login_res.raise_for_status()
        login_data = login_res.json()
        self.token = login_data.get('token')
        user = login_data.get('user')
        self.username = user.get('name')
        self.roles = [x.get('name') for x in user.get('roles')]

        info_res = requests.get(
            self.get_url('info'),
            headers=self.get_headers()
        )

        info_res.raise_for_status()
        info_data = info_res.json()
        info = info_data.get('info')
        self.version = info.get('version')
        self.byteorder = info.get('byteorder')

        pumps_res = requests.get(
            self.get_url('pump/exec'),
            headers=self.get_headers()
        )

        pumps_res.raise_for_status()
        pumps_data = pumps_res.json()
        pumps = pumps_data.get('pumps')
        self.pumps = [x.get('name') for x in pumps]

    def open(self, pump):
        if pump not in self.pumps:
            raise Exception('Invalid pump name.')

        open_res = requests.post(
            self.get_url('cycle'),
            headers=self.get_headers(),
            json={
                'cycle': {
                    'pump_name': pump
                }
            }
        )
        open_res.raise_for_status()
        open_data = open_res.json()
        return Cycle(self, open_data)
