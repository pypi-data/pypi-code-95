import datetime, pytz


def now_aware():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

def now_as_string():
    return now_aware().strftime("%Y-%m-%dT%H:%M:%S%z")