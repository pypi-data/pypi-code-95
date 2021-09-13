from psu_base.models.downtime import Downtime
from psu_base.classes.Log import Log
from datetime import datetime, timedelta

log = Log()


def get_next_downtime():
    """Get the next (includes current active) downtime"""
    log.trace()
    now = datetime.now()
    cutoff = now + timedelta(minutes=20)
    downtimes = (
        Downtime.objects.filter(from_date__lte=cutoff)
        .exclude(until_date__lte=now)
        .order_by("from_date")
    )
    if downtimes:
        return downtimes[0]
    return None
