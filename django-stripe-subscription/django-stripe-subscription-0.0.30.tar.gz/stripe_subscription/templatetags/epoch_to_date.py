from datetime import datetime, timezone
from django import template

register = template.Library()


@register.filter
def epoch_to_date(unix_epoch):
    """
    Returns datetime object for given unix epoch time.
    :param unix_epoch: int Unix epoch time
    :returns datetime.datetime:
    """

    date = datetime.fromtimestamp(unix_epoch, tz=timezone.utc)

    return date
