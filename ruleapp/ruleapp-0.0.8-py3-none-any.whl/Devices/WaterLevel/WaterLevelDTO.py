import json


class WaterLevel(object):
    def __init__(self):
        self.device_id = ""
        self.name = "WATERLEVEL"
        self.measure = "-"
        self.absolute_measure = "-"
        self.setting_error = "0"
        self.setting_max = "100"
        self.setting_unit_measure = "cm"
        self.rules = []
        self.status = "disconnected"
        self.color = "red"
        self.unit_measure = "%"
        self.max_measure = "-"
        self.max_measure_time = "-"
        self.max_measure_date = "-"
        self.min_measure = "-"
        self.min_measure_time = "-"
        self.min_measure_date = "-"

    def json_mapping(self, device_json):
        x = json.loads(device_json)
        if "device_id" in x.keys():
            self.device_id = x["device_id"]
        if "name" in x.keys():
            self.name = x["name"]
        if "setting_error" in x.keys():
            self.setting_error = x["setting_error"]
        if "setting_max" in x.keys():
            self.setting_max = x["setting_max"]
        if "setting_unit_measure" in x.keys():
            self.setting_unit_measure = x["setting_unit_measure"]
        if "expiration" in x.keys():
            self.expiration = x["expiration"]
        if "rules" in x.keys():
            self.rules = x["rules"]