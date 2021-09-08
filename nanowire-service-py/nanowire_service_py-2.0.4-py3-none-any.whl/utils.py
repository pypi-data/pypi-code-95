import json
from datetime import datetime, timezone


def find(xs, f):
    for x in xs:
        if f(x):
            return x
    return None


def path(path, obj):
    value = obj
    for part in path:
        if part in value:
            value = value[part]
        else:
            return None
    return value


# Handles datetime better
def safe_json(o):
    if isinstance(o, datetime):
        return o.__str__()


def safe_dump(d):
    return json.dumps(d, default=safe_json)


def now():
    return datetime.now(timezone.utc).isoformat()
