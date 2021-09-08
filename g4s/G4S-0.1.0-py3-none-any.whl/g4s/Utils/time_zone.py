from g4s.utils.static_utils import StaticUtils


class TimeZone:
    def __init__(self, input_dict):
        self.country_code = input_dict.get("CountryCode")
        self.time_zone_id = input_dict.get("TimeZoneId")
        self.olson_name = input_dict.get("OlsonName")
        self.is_enabled = input_dict.get("IsEnabled")
        self.name = input_dict.get("Name")

    def date_time_as_utc(self, string_date):
        if string_date is None:
            return None
        date_time = StaticUtils.parse_date(string_date)
        date_time = StaticUtils.replace_tz(date_time, self.olson_name)
        date_time = StaticUtils.datetime_to_utc(date_time)
        return date_time
