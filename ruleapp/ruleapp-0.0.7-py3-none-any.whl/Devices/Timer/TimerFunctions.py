from .TimerDTO import Timer
from datetime import datetime


class TimerFunction(object):
    def __init__(self, redis):
        self.r = redis

    def register(self, user_id):
        try:
            device_id = "timer-" + user_id
            if self.r.exists("device:" + device_id + ":name") == 0:
                key_pattern = "device:" + device_id
                self.r.set(key_pattern + ":name", "timer")
                self.r.set(key_pattern + ":user_id", user_id)
                return "true"
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device(self, device_id):
        try:
            dto = Timer()
            dto.device_id = device_id
            dto.name = self.r.get("device:" + device_id + ":name")
            if self.r.exists("device:" + device_id + ":rules") == 1:
                dto.rules = self.r.lrange("device:" + device_id + ":rules")
            dto.measure_time = datetime.now().strftime("%H:%M")
            dto.measure_day = str(datetime.today().weekday())
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def update_device(self, device_json):
        try:
            dto = Timer()
            dto.json_mapping(device_json)
            key_pattern = "device:" + dto.device_id
            self.r.set(key_pattern + ":name", dto.name)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"
