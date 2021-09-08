import dateutil
from datetime import date, datetime, timezone as tz
import pandas as pd

def float_as_currency(val: float):
    return "${:,.2f}".format(round(val, 2))


def int_tryParse(value):
    try:
        return int(value)
    except:
        return None


def date_tryParse(value):
    return force_to_date_or_None(value)

def datestamp_tryParse(value, include_time: bool = True, include_ms: bool = True):
    try:
        val = force_to_datetime_or_None(value)

        if not include_time:
            val = datetime.combine(val, datetime.min.time())

        if not include_ms:
            val = val.replace(microsecond=0)

        return val
    except:
        return None

def force_to_date_or_None(val):
    my_datetime = force_to_datetime_or_None(val)
    if my_datetime is None:
        return None
    else:
        return my_datetime.date()

def force_to_datetime_or_None(val):
    try:
        if isinstance(val, datetime):
            return val
        elif isinstance(val, date):
            return datetime.combine(val, datetime.min.time())
        elif isinstance(val, pd.Timestamp):
            the_date = val.to_pydatetime().date()
            return datetime.combine(the_date, datetime.min.time())
        else:
            val = dateutil.parser.parse(val)
            return force_to_datetime_or_None(val)
    except:
        return None


if __name__ == "__main__":
    try_vals = [
        date.today(),
        '10.21.21',
        '10/21/21',
        None,
        datetime.today(),
        '2014-08-01 11:00:00+02:00'
    ]

    results = map(force_to_datetime_or_None, try_vals)

    print(list(results))

    results = map(lambda x: datestamp_tryParse(x, include_ms=False), try_vals)
    print(list(results))