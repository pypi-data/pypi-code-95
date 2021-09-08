import jsonpickle
from datetime import datetime


class DatetimeHandler(jsonpickle.handlers.BaseHandler):
    _datetime_format = "%Y-%m-%d %H:%M:%S.%f"

    def flatten(self, obj, data):
        return DatetimeHandler.to_json(obj)

    @staticmethod
    def to_json(obj):
        data = obj.strftime(DatetimeHandler._datetime_format)
        return data

    @staticmethod
    def from_json(data):
        if isinstance(data, str):
            obj = datetime.strptime(data, DatetimeHandler._datetime_format)
            return obj
        return data
