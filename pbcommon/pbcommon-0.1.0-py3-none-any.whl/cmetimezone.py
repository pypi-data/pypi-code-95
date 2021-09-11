from datetime import datetime, timedelta

import pytz

# CME TIMEZONE Config
CME_TIMEZONE = 'US/Central'
_CME_TZ = pytz.timezone(CME_TIMEZONE)


def cme_now(offset_days: int = 0) -> datetime:
    return datetime.now(_CME_TZ) + timedelta(days=-offset_days)