import datetime


__ALL__ = ["dt2yyyymmddhhmmss", "yyyymmddhhmmss2dt"]


def dt2yyyymmddhhmmss() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def yyyymmddhhmmss2dt(string: str) -> datetime.datetime:
    return datetime.datetime.strptime(string, "%Y-%m-%d %H-%M-%S")

