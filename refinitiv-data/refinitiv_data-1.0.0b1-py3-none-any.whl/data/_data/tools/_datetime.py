from datetime import timedelta, datetime, date
from typing import Union, Tuple

import dateutil.parser
from dateutil import tz


def to_datetime(
    date_value: Union[str, timedelta, Tuple[datetime, date]]
) -> Union[tuple, datetime, None]:
    if date_value is None:
        return None

    if isinstance(date_value, timedelta):
        return datetime.now(tz.tzlocal()) + date_value

    if isinstance(date_value, (datetime, date)):
        return date_value

    try:
        return dateutil.parser.parse(date_value)
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(e)


def _to_utc(datetime_value):
    if datetime_value is None:
        return None
    _value = to_datetime(datetime_value)
    UTC = tz.gettz("UTC")
    _value = _value.astimezone(UTC).replace(tzinfo=None)
    return _value


def to_utc_datetime(datetime_value):
    datetime_value = _to_utc(datetime_value)
    if datetime_value is None:
        return None
    return datetime_value  # .strftime("%Y-%m-%d %H:%M:%S")


def to_utc_date(date_value):
    date_value = _to_utc(date_value)
    if date_value is None:
        return None
    return date_value.date()


def to_utc_datetime_isofmt(datetime_value):
    datetime_value = _to_utc(datetime_value)
    if datetime_value is None:
        return None
    datetime_value = datetime_value.isoformat(timespec="microseconds") + "000Z"
    return datetime_value


def get_date_from_today(days_count):
    if type(days_count) != int:
        raise ValueError(
            "The parameter {} should be an integer, found {}".format(
                days_count, type(days_count)
            )
        )
    return datetime.now(tz.tzlocal()) + timedelta(days=-days_count)


def convert_to_datetime(value, add=None):
    utc = tz.gettz("UTC")

    if value is None:
        return None
    elif isinstance(value, datetime):
        pass
    elif isinstance(value, timedelta):
        value = datetime.now(tz.tzlocal()).astimezone(utc) + value
    elif isinstance(value, date):
        value = datetime.combine(value, datetime.min.time())
    else:
        try:
            value = dateutil.parser.parse(value)
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(e)
    if add:
        value = value + add
    return value


class Converter:
    def convert(self, value):
        return convert_to_datetime(value)


class Formatter:
    def to_str(self, date_time_value):
        return date_time_value.isoformat(timespec="microseconds")


class CFSFormatter:
    def to_str(self, date_time_value):
        return date_time_value.strftime("%Y-%m-%dT%H:%M:%SZ")


class NanosecondsFormatter:
    NANOSECOND_LENGTH = 9

    def to_str(self, date_time):
        s = date_time.isoformat(timespec="microseconds")
        # s => '2021-08-03T10:33:35.554103+00:00000Z'
        s, *_ = s.split("+", maxsplit=1)
        # s => '2021-08-03T10:33:35.554103'
        s, microseconds = s.split(".", maxsplit=1)
        # microseconds => '554103'
        diff = self.NANOSECOND_LENGTH - len(microseconds)
        # nanoseconds => '554103000'
        nanoseconds = f"{microseconds}{diff * '0'}"
        # return => '2021-08-03T10:33:35.554103000Z'
        return f"{s}.{nanoseconds}Z"


class DateTimeAdapter:
    def __init__(self, converter_, formatter_):
        self.converter = converter_
        self.formatter = formatter_

    def convert(self, value):
        return self.converter.convert(value)

    def get_str(self, value):
        return self.formatter.to_str(self.convert(value))


_nanoseconds_formatter = NanosecondsFormatter()
_converter = Converter()

_z_ends_date_time_adapter = DateTimeAdapter(_converter, _nanoseconds_formatter)
hp_datetime_adapter = _z_ends_date_time_adapter
tds_datetime_adapter = _z_ends_date_time_adapter
cfs_datetime_adapter = DateTimeAdapter(_converter, CFSFormatter())
