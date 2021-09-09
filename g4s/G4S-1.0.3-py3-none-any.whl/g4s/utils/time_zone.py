from g4s.utils.static_utils import StaticUtils
from datetime import datetime
from typing import Any, Optional, Dict


class TimeZone:
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        self.country_code: str = input_dict["CountryCode"]
        self.time_zone_id: int = input_dict["TimeZoneId"]
        self.olson_name: str = input_dict["OlsonName"]
        self.is_enabled: bool = input_dict["IsEnabled"]
        self.name: str = input_dict["Name"]

    def date_time_as_utc(self, string_date: Optional[str]) -> Optional[datetime]:
        date_time: Optional[datetime] = StaticUtils.parse_date(string_date)
        if date_time is None:
            return None
        date_time = StaticUtils.replace_tz(date_time, self.olson_name)
        date_time = StaticUtils.datetime_to_utc(date_time)
        return date_time
