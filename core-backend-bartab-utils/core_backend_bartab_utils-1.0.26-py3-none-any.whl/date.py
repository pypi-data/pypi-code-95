from django.conf import settings
from .paths import get_relative_path
from .json import JsonFile
import datetime
import pytz
import datetime


class TimeZoneData:

    TIME_ZONE_GENERATED_DATA_PATH = get_relative_path(
        '../data/generated/timezones.json', __file__)

    @staticmethod
    def data():
        timezone_data_file = JsonFile(
            TimeZoneData.TIME_ZONE_GENERATED_DATA_PATH)

        if not timezone_data_file.is_valid():
            TimeZoneData.__generate_timezone_data()

        return timezone_data_file.data()

    @staticmethod
    def __generate_timezone_data():
        timezones_by_offset_file = JsonFile(
            TimeZoneData.TIME_ZONE_GENERATED_DATA_PATH)

        timezone_data = {
            'timezones_by_offset': {},
            'offset_by_timezone_name': {},
            'us_time_zones_by_offset': {}
        }

        for timezone in pytz.common_timezones:
            timezone_now = datetime.datetime.now(pytz.timezone(timezone))
            offset_time_in_hours = timezone_now.utcoffset().total_seconds()/60/60

            if offset_time_in_hours in timezone_data['timezones_by_offset']:
                timezone_data['timezones_by_offset'][offset_time_in_hours].append(
                    timezone)
            else:
                timezone_data['timezones_by_offset'][offset_time_in_hours] = [
                    timezone]

            if 'US/' in timezone:
                timezone_data['us_time_zones_by_offset'][offset_time_in_hours] = timezone

            timezone_data['offset_by_timezone_name'][timezone] = offset_time_in_hours

        timezones_by_offset_file.set_json(timezone_data)


def is_same_day(date_time_one, date_time_two, date_time_format=None):
    if date_time_format == None:
        date_time_format = settings.DATETIME_FORMAT

    if isinstance(date_time_one, str):
        date_time_one = datetime.datetime.strptime(
            date_time_one, date_time_format)
    elif not isinstance(date_time_one, datetime.datetime):
        raise ValueError("Invalid date type")

    if isinstance(date_time_two, str):
        date_time_two = datetime.datetime.strptime(
            date_time_two, date_time_format)
    elif not isinstance(date_time_two, datetime.datetime):
        raise ValueError("Invalid date type")

    return date_time_one.date() == date_time_two.date()


def is_today(date_time, date_time_format=None):
    if date_time_format == None:
        date_time_format = settings.DATETIME_FORMAT
    
    return is_same_day(date_time, datetime.datetime.now(), date_time_format)


def is_future(date_time, date_time_format=None):
    if date_time_format == None:
        date_time_format = settings.DATETIME_FORMAT
    
    if isinstance(date_time, str):
        return datetime.datetime.now() < datetime.datetime.strptime(date_time, date_time_format)
    elif isinstance(date_time, datetime.datetime):
        return datetime.datetime.now() < date_time
    elif isinstance(date_time, datetime.date):
        return datetime.datetime.now() < datetime.combine(date_time, datetime.min.time())
    else:
        raise ValueError("Invalid date type")


def is_past(date_time, date_time_format=None):
    if date_time_format == None:
        date_time_format = settings.DATETIME_FORMAT
    
    return not is_future(date_time, date_time_format)
