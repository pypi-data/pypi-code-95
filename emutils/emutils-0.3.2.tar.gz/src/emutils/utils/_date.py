import datetime

__all__ = ['timestamp']


def timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H %M %S')
