from datetime import datetime
import dateutil.parser
import dateutil.tz


class StaticUtils(object):
    @staticmethod
    def ParseDate(x):
        if x is None:
            return None
        return dateutil.parser.parse(x)

    @staticmethod
    def ReplaceTZ(dt, tz_name):
        tz_info = dateutil.tz.gettz(tz_name)
        return dt.replace(tzinfo=tz_info)

    @staticmethod
    def DateTimeToUTC(dt):
        return dt.astimezone(dateutil.tz.UTC)
