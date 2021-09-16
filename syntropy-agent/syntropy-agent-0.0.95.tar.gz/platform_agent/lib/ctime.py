import datetime

DEFAULT_FORMAT = "%Y-%m-%dT%H:%M:%S%zZ"


def now() -> str:
    """ Returns current timestamp in default app format """
    return datetime.datetime.now().isoformat()
