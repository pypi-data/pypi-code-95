import pytz
from datetime import datetime
from pydantic import BaseModel


class TimeSpanConfiguration(BaseModel):
    timezone: str
    start: str
    end: str

    @staticmethod
    def _convert(hour_string):
        return datetime.strptime(hour_string, '%H:%M:%S')

    def is_in_timespan(self):
        now = datetime.utcnow()

        tz = pytz.timezone(self.timezone)
        local_now = now.replace(tzinfo=pytz.utc).astimezone(tz)

        hour_string = datetime.strftime(local_now, '%H:%M:%S')
        now_hour = self._convert(hour_string)
        start = self._convert(self.start)
        end = self._convert(self.end)

        return start < now_hour < end
