from datetime import datetime


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


def get_client_ip(scope):
    headers = dict(scope['headers'])
    if b'x-real-ip' in headers:
        return headers[b'x-real-ip'].decode("utf8")
    return 'Unknown'
