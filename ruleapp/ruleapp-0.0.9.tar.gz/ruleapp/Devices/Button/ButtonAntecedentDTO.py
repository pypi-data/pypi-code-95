import json


class ButtonAntecedent(object):
    def __init__(self):
        self.device_id = ""
        self.device_name = ""
        self.measure = ""
        self.condition_measure = "="
        self.start_value = "on"
        self.stop_value = "off"
        self.last_time_on = "-"
        self.last_time_off = "-"
        self.last_date_on = "-"
        self.last_date_off = "-"
        self.evaluation = "false"
        self.order = ""

    def json_mapping(self, device_json):
        x = json.loads(device_json)
        if "device_id" in x.keys():
            self.device_id = x["device_id"]
        if "device_name" in x.keys():
            self.device_name = x["device_name"]
        if "condition_measure" in x.keys():
            self.condition_measure = x["condition_measure"]
        if "start_value" in x.keys():
            self.start_value = x["start_value"]
        if "stop_value" in x.keys():
            self.stop_value = x["stop_value"]
        if "order" in x.keys():
            self.order = x["order"]
