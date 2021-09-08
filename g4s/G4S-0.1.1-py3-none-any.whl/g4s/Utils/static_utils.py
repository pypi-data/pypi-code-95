import dateutil.parser
import dateutil.tz


class StaticUtils:
    @staticmethod
    def parse_date(datetime_string):
        if datetime_string is None:
            return None
        return dateutil.parser.parse(datetime_string)

    @staticmethod
    def replace_tz(datetime, tz_name):
        tz_info = dateutil.tz.gettz(tz_name)
        return datetime.replace(tzinfo=tz_info)

    @staticmethod
    def datetime_to_utc(datetime):
        return datetime.astimezone(dateutil.tz.UTC)
