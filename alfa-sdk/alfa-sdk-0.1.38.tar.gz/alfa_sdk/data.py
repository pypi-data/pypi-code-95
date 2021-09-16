import requests

from alfa_sdk.common.base import BaseClient


class DataClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch_data_file(self, data_file_id):
        url = self.session.request(
            "get", "data", "/api/Storages/download/{}".format(data_file_id)
        )

        res = requests.get(url["downloadLink"], allow_redirects=True)
        return res.content

    def list_data_files(self, prefix="", skip=0, limit=100, order="name ASC"):
        return self.session.request(
            "get",
            "data",
            "/api/Storages/list",
            params={
                "prefix": prefix,
                "skip": skip,
                "limit": limit,
                "order": order,
                "teamId": self.team_id,
            },
        )

    def update_data_file(self, data_file_id, changes):
        return self.session.request(
            "put",
            "data",
            "/api/Storages/update/{}".format(data_file_id),
            json={"updates": changes},
        )
