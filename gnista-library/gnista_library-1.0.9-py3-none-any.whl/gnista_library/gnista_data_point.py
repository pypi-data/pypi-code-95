import json

import pandas as pd
from pandas import DataFrame
from structlog import get_logger

from data_point_client import AuthenticatedClient
from data_point_client.api.data_point import data_point_get_data
from data_point_client.models import GetSeriesResponse, GetSeriesResponseCurve

from .gnista_connetion import GnistaConnection

log = get_logger()


class GnistaDataPoint:
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    DATE_NAME = "Date"
    VALUE_NAME = "Value"

    def __init__(self, connection: GnistaConnection, data_point_id: str, name: str = None):
        self.connection = connection
        self.name = name
        self.data_point_id = data_point_id

    def __str__(self):
        return "GnistaDataPoint " + self.data_point_id + " with name " + self.name

    def get_data_point_data(self, window_hours: int = 0) -> DataFrame:
        token = self.connection.get_access_token()
        client = AuthenticatedClient(base_url=self.connection.base_url + "/datapoint", token=token)

        byte_content = data_point_get_data.sync_detailed(
            client=client, data_point_id=self.data_point_id, window_hours=window_hours
        ).content
        log.debug("Received Response from gnista.io", content=byte_content)

        content_text = byte_content.decode("utf-8")
        jscon_content = json.loads(content_text)
        series_response = GetSeriesResponse.from_dict(jscon_content)
        if isinstance(series_response.curve, GetSeriesResponseCurve):
            curve: GetSeriesResponseCurve = series_response.curve
            return self._from_time_frames(time_frames=curve.to_dict())

        return None

    def _from_time_frames(self, time_frames: dict, date_format: str = DATE_FORMAT) -> DataFrame:

        if not isinstance(time_frames, dict):
            raise TypeError

        log.debug("Reading data as Pandas DataFrame")

        data_record = []
        for date in time_frames:
            value = time_frames[date]
            data_record.append({self.DATE_NAME: date, self.VALUE_NAME: value})

        data_frame = pd.DataFrame.from_records(data_record, columns=[self.DATE_NAME, self.VALUE_NAME])

        data_frame[self.DATE_NAME] = pd.to_datetime(data_frame[self.DATE_NAME], format=date_format)

        data_frame[self.VALUE_NAME] = pd.to_numeric(data_frame[self.VALUE_NAME])

        data_frame = data_frame.set_index(data_frame[self.DATE_NAME])
        data_frame = data_frame.drop([self.DATE_NAME], axis=1)

        return data_frame
