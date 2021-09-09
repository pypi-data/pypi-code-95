import dateutil.parser
import dateutil.tz
from datetime import datetime
from typing import Optional



class StaticUtils:
    @staticmethod
    def parse_date(datetime_string: Optional[str]) -> Optional[datetime]:
        if datetime_string is None:
            return None
        return dateutil.parser.parse(datetime_string)

    @staticmethod
    def replace_tz(datetime: datetime, tz_name: str) -> datetime:
        tz_info = dateutil.tz.gettz(tz_name)
        return datetime.replace(tzinfo=tz_info)

    @staticmethod
    def datetime_to_utc(datetime: datetime) -> datetime:
        return datetime.astimezone(dateutil.tz.UTC)
