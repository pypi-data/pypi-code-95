from javaman.connexio import JManCon


class Pobles:
    __slots__ = '_con'

    _url_pobles = '/pobles'

    def __init__(self, con: JManCon):
        self._con = con

    def list(self):
        res = self._con.get(url=self._url_pobles)
        return res.json()

    def get(self, poble_id: int):
        res = self._con.get(url=self._url_pobles + '/' + str(poble_id))
        return res.json()

    def crear(self, poble: dict):
        res = self._con.post(url=self._url_pobles, data=poble)
        return res.json()

    def troba(self, provincia_id: int, poble: str):
        tmp_url = self._url_pobles + '?poble_nom=' + poble + '&provincia_id=' + str(provincia_id)
        response = self._con.get(url=tmp_url)
        if response.status_code == 200:
            return response.json()
