from datetime import time, datetime, timedelta
from django.conf import settings
from .date import TimeZoneData
import pytz
from .paths import get_relative_path
from .json import RequiredJsonFile
import time as pure_time

def current_milli_time():
    return round(pure_time.time() * 1000)


def get_hours_offset_from_float(float_number):
    return abs(int(float_number))


def get_minutes_offset_from_float(float_number: float) -> int:
    positive_modifier = 1 if float_number > 0 else -1

    hour_offset = get_hours_offset_from_float(float_number)

    float_minutes_str = str(abs(
        round(float_number - (hour_offset * positive_modifier), 2)))

    decimal_minutes_map_path = get_relative_path(
        './data/decimal_minutes_map.json', __file__)

    decimal_minutes_to_minutes_map = RequiredJsonFile(
        decimal_minutes_map_path).data()

    if float_minutes_str in decimal_minutes_to_minutes_map.keys():
        return decimal_minutes_to_minutes_map[float_minutes_str]
    else:
        raise ValueError(
            f"Minute decimal value: {float_minutes_str} not found ")


def get_offset_hours_from_float(float_number: float) -> str:
    hours = get_hours_offset_from_float(float_number)
    minutes = get_minutes_offset_from_float(float_number)

    sign = "+" if float_number >= 0 else '-'

    hours_display = hours if hours > 9 else "0{}".format(hours)
    minutes_display = minutes if minutes > 9 else "0{}".format(minutes)

    return "{sign}{h}{m}".format(sign=sign, h=hours_display, m=minutes_display)


def convert_datetime_to_time(date_time, date_time_format: str = None) -> time:
    if date_time_format == None:
        date_time_format = settings.DATETIME_FORMAT
    
    if isinstance(date_time, time):
        return date_time
    elif isinstance(date_time, str):
        date_time = datetime.strptime(date_time, date_time_format)
        return time(date_time.hour, date_time.minute)
    elif isinstance(date_time, datetime):
        return time(date_time.hour, date_time.minute)
    else:
        raise ValueError("Invalid date time format")


def time_in_range(begin_time, end_time, check_time=None) -> bool:
    check_time = datetime.utcnow().time() if check_time == None else convert_datetime_to_time(
        check_time)

    begin_time = convert_datetime_to_time(begin_time)
    end_time = convert_datetime_to_time(end_time)

    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def offset_hour(hour: int, hour_offset: int) -> int:
    # if adding time
    if hour_offset > 0:
        total = hour + hour_offset
        return total if total < 23 else total - 24
    # if removing time
    else:
        total = hour + hour_offset
        return total if total >= 0 else total + 24


def offset_minutes(minute: int, minutes_offset: int) -> int:
    total = minute + minutes_offset

    if total < 0:
        return total + 60
    elif total < 60:
        return total
    else:
        return total - 60


def convert_datetime_timezone(date_time: datetime, timezone: pytz.timezone) -> datetime:
    timezone_data = TimeZoneData.data()
    if str(date_time.tzinfo) in timezone_data['offset_by_timezone_name']:
        offset_float = float(
            timezone_data['offset_by_timezone_name'][str(date_time.tzinfo)]) * float(-1)
    else:
        offset_float = float(0.0) * float(-1)

    offset_h = get_hours_offset_from_float(offset_float)
    offset_min = get_minutes_offset_from_float(offset_float)

    utc_t = date_time + timedelta(hours=offset_h, minutes=offset_min)

    utc_time = datetime(utc_t.year, utc_t.month, utc_t.day,
                        utc_t.hour, utc_t.minute, utc_t.second, tzinfo=pytz.UTC)

    return utc_time.astimezone(timezone)
