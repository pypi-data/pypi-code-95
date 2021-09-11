from datetime import datetime, timedelta

import pytz

# CME TIMEZONE Config
CME_TIMEZONE = 'US/Central'
CME_TZ = pytz.timezone(CME_TIMEZONE)


def cme_now(offset_days: int = 0) -> datetime:
    return datetime.now(CME_TZ) + timedelta(days=-offset_days)