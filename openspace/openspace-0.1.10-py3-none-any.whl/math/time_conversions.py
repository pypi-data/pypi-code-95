from math import fmod
import time
import datetime as dt
from openspace.math.measurements import Angle

SECONDS_IN_DAY = 86400
MINUTES_IN_DAY = 1440
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60
HOURS_IN_DAY = 24
JULIAN_DAYS_TO_AD = 1721424.5
MODIFIED_JULIAN_DATE = 2400000.5

def get_eci_to_ecef_gst_angle(epoch):
    j2000 = dt.datetime(2000, 1, 1, 12, 0)
    t = epoch.to_datetime() - j2000    

    degs = 360.9856123035484*(t.total_seconds()/SECONDS_IN_DAY)+280.46
    return Angle(degs, "degrees").to_unit("radians")

def tle_epoch_string_to_datetime(tle_epoch_str):
    yd, dd = tle_epoch_str.split(".")
    dd = float("." + dd)
    h, m, s = decimal_day_to_time(dd)
    hms = ":".join(["%02d" % h, "%02d" % m, "%02.6f" % s])

    return dt.datetime.strptime(" ".join([yd, hms]), "%y%j %H:%M:%S.%f")

def tle_epoch_string_to_timestamp(tle_epoch_str):
    tle_dt = tle_epoch_string_to_datetime(tle_epoch_str)
    return dt.datetime.timestamp(tle_dt)

def epoch_string_to_datetime(epoch_str, epoch_fmt):
    return dt.datetime.strptime(epoch_str, epoch_fmt)

def timestamp_to_datetime(tstamp):
    return dt.datetime.fromtimestamp(tstamp)

def epoch_string_to_timestamp(epoch_str, epoch_fmt):
    return time.mktime(dt.datetime.strptime(epoch_str, epoch_fmt).timetuple())

def timestamp_to_epoch_string(tstamp, epoch_fmt):
    return timestamp_to_datetime(tstamp).strftime(epoch_fmt)

def timestamp_to_julian_date(tstamp):
    
    input_datetime = dt.datetime.fromtimestamp(tstamp)
    days = input_datetime.toordinal() + JULIAN_DAYS_TO_AD
    dec_days = time_to_decimal_day(
        input_datetime.hour, 
        input_datetime.minute, 
        input_datetime.second
        )

    return days+dec_days

def timestamp_to_modified_julian_date(tstamp):
    return timestamp_to_julian_date(tstamp)-MODIFIED_JULIAN_DATE

def julian_date_to_epoch_string(jDate, epochFormat):
    tstamp = JulianDateToTimestamp(jDate)
    return timestamp_to_epoch_string(tstamp, epochFormat)

def JulianDateToTimestamp(jDate):
    pass

def time_to_decimal_day(hr, min, sec):
    day = sec/SECONDS_IN_DAY
    day += min/MINUTES_IN_DAY
    day += hr/HOURS_IN_DAY
    return day

def decimal_day_to_time(dec_day):
    hrs_dec = dec_day*HOURS_IN_DAY
    hrs = int(hrs_dec)
    if hrs > 0:
        min_dec = fmod(hrs_dec, hrs)*MINUTES_IN_HOUR
    else:
        min_dec = hrs_dec*MINUTES_IN_HOUR
    mins = int(min_dec)

    if mins > 0:
        sec = fmod(min_dec, mins)*SECONDS_IN_MINUTE
    else:
        sec = min_dec*SECONDS_IN_MINUTE
    return hrs, mins, sec
