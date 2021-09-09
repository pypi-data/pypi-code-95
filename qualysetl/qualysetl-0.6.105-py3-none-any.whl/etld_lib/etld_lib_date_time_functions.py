from datetime import datetime, timedelta
import re


def get_utc_date_minus_days(days=1):
    d = datetime.utcnow() - timedelta(days=days)
    td = f"{d.year}-{d.month:02d}-{d.day:02d}T00:00:00Z"
    return td


def get_utc_date_plus_days(days=1):
    d = datetime.utcnow() + timedelta(days=days)
    td = f"{d.year}-{d.month:02d}-{d.day:02d}T00:00:00Z"
    return td


def get_utc_date_minus_hours(hours=1):
    d = datetime.utcnow() - timedelta(hours=hours)
    td = f"{d.year}-{d.month:02d}-{d.day:02d}T{d.hour:02d}:{d.minute:02d}:00Z"
    return td


def get_utc_date_plus_hours(hours=1):
    d = datetime.utcnow() + timedelta(hours=hours)
    td = f"{d.year}-{d.month:02d}-{d.day:02d}T{d.hour:02d}:{d.minute:02d}:00Z"
    return td


def get_utc_date_minus_mins(mins=30):
    d = datetime.utcnow() - timedelta(minutes=mins)
    td = f"{d.year}-{d.month:02d}-{d.day:02d}T{d.hour:02d}:{d.minute:02d}:00Z"
    return td


def get_utc_date_plus_mins(mins=30):
    d = datetime.utcnow() + timedelta(minutes=mins)
    td = f"{d.year}-{d.month:02d}-{d.day:02d}T{d.hour:02d}:{d.minute:02d}:00Z"
    return td


def get_utc_date():
    d = datetime.utcnow()
    td = f"{d.year}-{d.month:02d}-{d.day:02d}T{d.hour:02d}:{d.minute:02d}:{d.second:02d}Z"
    return td


def get_local_date():
    d = datetime.now()
    td = f"{d.year}-{d.month:02d}-{d.day:02d} {d.hour:02d}:{d.minute:02d}:{d.second:02d}"
    return td


def is_valid_qualys_datetime_format(qualys_datetime_format=None):
    # Light validation for YYYY-MM-DDThh:mm:ssZ format.
    p_match = re.fullmatch(r"(^(19[7-9][0-9]|202[0-9])-"
                           r"(0[1-9]|1[0-2])-"
                           r"(0[1-9]|1[0-9]|2[0-9]|3[0-1])T"
                           r"(0[0-9]|1[0-9]|2[0-3]):"
                           r"[0-5][0-9]:"
                           r"[0-5][0-9]Z$)", qualys_datetime_format)
    if p_match is not None:
        return True
    else:
        return False


def main():
    print(f"NOW UTC DATE       - get_utc_date                = {get_utc_date()}")
    print(f"5 Days UTC Ago     - get_utc_date_minus_days(5)  = {get_utc_date_minus_days(5)}")
    print(f"5 Days UTC Future  - get_utc_date_plus_days(5)   = {get_utc_date_plus_days(5)}")
    print(f"5 Hours UTC Ago    - get_utc_date_minus_hours(5) = {get_utc_date_minus_hours(5)}")
    print(f"5 Hours UTC Future - get_utc_date_plus_hours(5)  = {get_utc_date_plus_hours(5)}")
    print(f"5 Min   UTC Ago    - get_utc_date_minus_mins(5)  = {get_utc_date_minus_mins(5)}")
    print(f"5 Min   UTC Future - get_utc_date_plus_mins(5)   = {get_utc_date_plus_mins(5)}")


if __name__ == '__main__':
    main()
