import json

from alfa_sdk.common.session import Session


class BaseClient:
    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        if self.session is None:
            self.session = Session(**kwargs)

        self.team_id = kwargs.get("team_id")
        self.user = self.session.auth.user


class BaseResource(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data = kwargs.get("data", None)
        self.populate()

    def __str__(self):
        return json.dumps(self.__repr__())

    def __repr__(self):
        return self.get_data()

    #

    def _fetch_data(self):
        raise NotImplementedError

    def _fill_data(self):
        raise NotImplementedError

    def populate(self):
        if self._data is None:
            self._data = self._fetch_data()
        self._fill_data()

    def get_data(self):
        return self._data
