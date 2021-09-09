import datetime
import json

from inspect import istraceback
import traceback


class _JsonEncoder(json.JSONEncoder):
    """
    A custom encoder extending the default JSONEncoder
    """

    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.time, datetime.datetime)):
            return obj.isoformat()

        elif istraceback(obj):  # pragma: nocover
            return ''.join(traceback.format_tb(obj)).strip()

        elif type(obj) == Exception \
                or isinstance(obj, Exception) \
                or type(obj) == type:
            return str(obj)

        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            try:
                return str(obj)
            except Exception:
                return None
