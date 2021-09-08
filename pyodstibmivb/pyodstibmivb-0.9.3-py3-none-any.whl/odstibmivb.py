"""
interact async with the opendata api of the Belgian STIB MIVB public transport company
"""

import csv
import re
from io import StringIO

import aiohttp
import yarl

from .routes import LINE_CSV_FILE, TRANSLATIONS_CSV_FILE

URL = "https://opendata-api.stib-mivb.be/"  # pragma: no mutate
ROUTES_URL = (
    "https://openmobilitydata.org/p/societe-des-transports-"  # pragma: no mutate
    "intercommunaux-de-bruxelles/527/latest/download/routes.txt"  # pragma: no mutate
)  # pragma: no mutate
TRANSLATIONS_URL = (
    "https://openmobilitydata.org/p/societe-des-transports-"  # pragma: no mutate
    "intercommunaux-de-bruxelles/527/latest/download/translations.txt"  # pragma: no mutate
)  # pragma: no mutate


def base_url():
    """return the base url for the api"""
    return URL + "{}/{}"


METHODS = {
    "vehicle_position": "OperationMonitoring/4.0/VehiclePositionByLine",
    "waiting_time": "OperationMonitoring/4.0/PassingTimeByPoint",
    "message_by_line": "OperationMonitoring/4.0/MessageByLine",
    "stops_by_line": "NetworkDescription/1.0/PointByLine",
    "point_detail": "NetworkDescription/1.0/PointDetail",
}


class ODStibMivb:
    """Interface with Stib-Mivb Open Data API"""

    def __init__(self, access_token, session=None):
        self.access_token = access_token
        self._session = session
        self._gtfs_line_data = None
        self._gtfs_translation_data = None

    @property
    def access_token(self):
        """The access code to acces the api"""
        return self.__access_token

    @access_token.setter
    def access_token(self, value):
        value = value.lower()
        if re.fullmatch("[a-f0-9]{32}", value):
            # pylint: disable=W0201
            self.__access_token = value
            self.__header = {"Authorization": "Bearer " + self.access_token}
        else:
            raise ValueError("invalid format for access token")

    @property
    def header(self):
        """http header in which te access code will be set"""
        return self.__header

    async def get_gtfs_line_data(self, id_):
        """get data from gtfs data file"""
        if self._gtfs_line_data is None:
            self._gtfs_line_data = await self.set_gtfs_line_data()
        try:
            return self._gtfs_line_data[str(id_)]
        except KeyError:
            raise ValueError("unknown line id")

    async def get_gtfs_translation_data(self, trans_id):
        """get data from gtfs translation file"""
        if self._gtfs_translation_data is None:
            self._gtfs_translation_data = await self.set_gtfs_translation_data()
        try:
            return self._gtfs_translation_data[trans_id]
        except KeyError:
            try:
                parts = trans_id[0].split(" - ")
                translated_parts = [
                    self._gtfs_translation_data[(part, trans_id[1])] for part in parts
                ]
                return " - ".join(translated_parts)
            except KeyError:
                raise ValueError("unknown translation id")

    async def set_gtfs_translation_data(self):
        """
        get the gtfs data. Either from the server
        or from the embedded csv file if that fails
        """
        try:
            if self._session is None:
                async with aiohttp.ClientSession() as session:
                    data = await self.get_gtfs_response(
                        session, TRANSLATIONS_URL
                    )  # pragma: no mutate
            else:
                data = await self.get_gtfs_response(self._session, TRANSLATIONS_URL)
            return extract_gtfs_translation_data(data.decode())
        except HttpException:
            return extract_gtfs_translation_data(TRANSLATIONS_CSV_FILE)

    async def set_gtfs_line_data(self):
        """
        get the gtfs data. Either from the server
        or from the embedded csv file if that fails
        """
        try:
            if self._session is None:
                async with aiohttp.ClientSession() as session:
                    data = await self.get_gtfs_response(
                        session, ROUTES_URL
                    )  # pragma: no mutate
            else:
                data = await self.get_gtfs_response(self._session, ROUTES_URL)
            return extract_gtfs_line_data(data.decode())
        except HttpException:
            return extract_gtfs_line_data(LINE_CSV_FILE)

    async def get_gtfs_response(self, session, url):
        """
        get the gtfs data from the remote server
        """
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.content.read()
            else:
                code = response.status  # pragma: no mutate
                message = f"Unexpected status code {code}."  # pragma: no mutate
                raise HttpException(message, await response.text(), response.status)
            return data

    async def do_request(self, method, id_, *ids):
        """
        Create a session if needed and do the API request
        """
        if method not in METHODS:
            raise ValueError("this method does not exist")

        if self._session is None:
            async with aiohttp.ClientSession() as session:
                return await self.get_response_unlimited(session, method, id_, *ids)
        else:
            return await self.get_response_unlimited(self._session, method, id_, *ids)

    async def get_response_unlimited(self, session, method, *ids):
        """
        if needed split up the api request in multiple 10 argument requests
        """
        response_unlimited = {}
        i = 0
        while i < len(ids):
            url = yarl.URL(
                base_url().format(
                    METHODS[method], "%2C".join(str(e) for e in ids[i : i + 10])
                ),
                # we need this here, but doesn't make a difference with our mock app
                # so mutmut complains :(
                encoded=True,  # pragma: no mutate
            )

            response = await self.get_response(session, url)
            assert len(response.keys()) == 1
            for key in response.keys():
                if key in response_unlimited.keys():
                    response_unlimited[key].extend(response[key])
                else:
                    response_unlimited[key] = response[key]
            i = i + 10
        return response_unlimited

    async def get_response(self, session, url):
        """
        Do the actual api request
        """
        async with session.get(url, headers=self.header) as response:
            if response.status == 200:
                try:
                    json_data = await response.json()
                except ValueError as exception:
                    message = "Server gave incorrect data"
                    raise Exception(message) from exception

            elif response.status == 401:
                message = "401: Acces token might be incorrect or expired"
                raise HttpException(message, await response.text(), response.status)

            elif response.status == 403:
                message = "403: incorrect API request"
                raise HttpException(message, await response.text(), response.status)

            else:
                message = f"Unexpected status code {response.status}."
                raise HttpException(message, await response.text(), response.status)

            return json_data

    async def get_vehicle_position(self, id_, *ids):
        """do the vehicle position api request"""
        return await self.do_request("vehicle_position", id_, *ids)

    async def get_waiting_time(self, id_, *ids):
        """do the waiting time api request"""
        return await self.do_request("waiting_time", id_, *ids)

    async def get_message_by_line(self, id_, *ids):
        """do the message by line api request"""
        return await self.do_request("message_by_line", id_, *ids)

    async def get_message_by_line_with_point_detail(self, id_, *ids):
        """
        do the message by line api request,
        and get the point id of the mentioned stops in the response
        """
        response = await self.do_request("message_by_line", id_, *ids)
        for line in response["messages"]:
            point_ids = [id_["id"] for id_ in line["points"]]
            point_details = await self.get_point_detail(*point_ids)
            line["points"] = point_details["points"]
        return response

    async def get_stops_by_line(self, id_, *ids):
        """do the stops by line api request"""
        return await self.do_request("stops_by_line", id_, *ids)

    async def get_point_detail(self, id_, *ids):
        """do the point detail api request"""
        return await self.do_request("point_detail", id_, *ids)

    async def get_line_long_name(self, id_):
        """get the long name from the static gtfs file"""
        tmp = await self.get_gtfs_line_data(str(id_))
        return tmp[0]

    async def get_line_type(self, id_):
        """get the route type from the static gtfs file"""
        tmp = await self.get_gtfs_line_data(str(id_))
        return tmp[1]

    async def get_line_color(self, id_):
        """get the route color from the static gtfs file"""
        tmp = await self.get_gtfs_line_data(str(id_))
        return tmp[2]

    async def get_line_text_color(self, id_):
        """get the route text color from the static gtfs file"""
        tmp = await self.get_gtfs_line_data(str(id_))
        return tmp[3]

    async def get_translation_fr(self, trans_id):
        """get the route text color from the static gtfs file"""
        return await self.get_gtfs_translation_data((trans_id, "fr"))

    async def get_translation_nl(self, trans_id):
        """get the route text color from the static gtfs file"""
        return await self.get_gtfs_translation_data((trans_id, "nl"))


def extract_gtfs_line_data(data):
    """extract the gtfs line csv file and put it in a dict"""
    gtfs_line_data = {}
    buffer = StringIO(data)
    reader = csv.DictReader(buffer, delimiter=",")
    for row in reader:
        gtfs_line_data[row["route_short_name"]] = (
            row["route_long_name"],
            row["route_type"],
            row["route_color"],
            row["route_text_color"],
        )
    return gtfs_line_data


def extract_gtfs_translation_data(data):
    """extract the gtfs translation csv file and put it in a dict"""
    gtfs_translation_data = {}
    buffer = StringIO(data)
    reader = csv.DictReader(buffer, delimiter=",")
    for row in reader:
        gtfs_translation_data[(row["trans_id"], row["lang"])] = row["translation"]
    return gtfs_translation_data


class HttpException(Exception):
    """HTTP exception class with message text, and status code"""

    def __init__(self, message, text, status_code):

        super().__init__(message)

        self.status_code = status_code
        self.text = text
