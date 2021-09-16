# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta, time, tzinfo, timezone


def today():
    return datetime.today().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)


def last_tradeday():
    # 가장 최근 거래일
    t = today()
    # 주말 제외
    while t.weekday() in [5,6]:
        t = t - timedelta(days=1)
    # 법정공휴일 제외
    return t
