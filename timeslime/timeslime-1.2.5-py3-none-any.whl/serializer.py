from json import loads
from datetime import datetime
from uuid import UUID

from timeslime.model import Timespan

class TimespanSerializer():
    def deserialize(self, json_string: str) -> Timespan:
        if type(json_string) is str:
            timespan_object = loads(json_string)
        else:
            timespan_object = json_string

        timespan = Timespan()

        if 'id' in timespan_object:
            timespan.id = UUID(timespan_object['id'])

        timespan.start_time = datetime.strptime(timespan_object['start_time'], '%Y-%m-%d %H:%M:%S.%f')

        if 'stop_time' in timespan_object:
            if timespan_object['stop_time'] == 'None':
                return timespan
            timespan.stop_time = datetime.strptime(timespan_object['stop_time'], '%Y-%m-%d %H:%M:%S.%f')
        return timespan

    def serialize(self, timespan: Timespan) -> str:
        return '{"id": "%s", "start_time": "%s", "stop_time": "%s"}' % (str(timespan.id), str(timespan.start_time), str(timespan.stop_time))
