from datetime import datetime

from django.core.mail import mail_admins as django_mail_admins


def serializable(obj):
    if isinstance(obj, dict):
        ret = {}
        for k, v in obj.items():
            ret[serializable(k)] = serializable(v)
        return ret
    elif isinstance(obj, datetime):
        sr = obj.isoformat()
        if obj.microsecond:
            sr = sr[:23] + sr[26:]
        if sr.endswith('+00:00'):
            sr = sr[:-6] + 'Z'
        return sr
    elif isinstance(obj, list):
        return [serializable(x) for x in obj]
    else:
        return obj


async def mail_admins(loop, subj, msg):
    """
    Send error message to settings.ADMINS
    :param loop: asyncio loop
    :param subj: email subject
    :param msg: email msg
    """

    def send():
        django_mail_admins(subj, msg)

    await loop.run_in_executor(None, send)