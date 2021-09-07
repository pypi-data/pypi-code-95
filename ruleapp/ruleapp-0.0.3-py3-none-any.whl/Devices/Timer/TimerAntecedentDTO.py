import json


class TimerAntecedent(object):
    def __init__(self):
        self.device_id = ""
        self.device_name = ""
        self.measure_time = ""
        self.measure_day = ""
        self.condition_time = "between"
        self.condition_day = "="
        self.day_start_value = []
        self.time_start_value = ""
        self.time_stop_value = ""
        self.evaluation = "false"
        self.order = ""
        self.check_time = "true"
        self.check_date = "true"

    def json_mapping(self, device_json):
        x = json.loads(device_json)
        if "device_id" in x.keys():
            self.device_id = x["device_id"]
        if "device_name" in x.keys():
            self.device_name = x["device_name"]
        if "condition_time" in x.keys():
            self.condition_time = x["condition_time"]
        if "condition_day" in x.keys():
            self.condition_day = x["condition_day"]
        if "check_time" in x.keys():
            self.check_time = x["check_time"]
        if "check_date" in x.keys():
            self.check_date = x["check_date"]
        if "day_start_value" in x.keys():
            self.day_start_value = x["day_start_value"]
        if "time_start_value" in x.keys():
            self.time_start_value = x["time_start_value"]
        if "time_stop_value" in x.keys():
            self.time_stop_value = x["time_stop_value"]
        if "order" in x.keys():
            self.order = x["order"]
