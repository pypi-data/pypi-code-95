import json


class Switch(object):
    def __init__(self):
        self.device_id = ""
        self.name = "switch"
        self.measure = "-"
        self.rules = []
        self.automatic = "true"
        self.manual_measure = "false"
        self.last_date_on = "-"
        self.last_date_off = "-"
        self.last_time_on = "-"
        self.last_time_off = "-"
        self.status = "disconnected"
        self.color = "red"
        self.expire_time = "10"

    def json_mapping(self, device_json):
        x = json.loads(device_json)
        if "device_id" in x.keys():
            self.device_id = x["device_id"]
        if "name" in x.keys():
            self.name = x["name"]
        if "rules" in x.keys():
            self.rules = x["rules"]
        if "automatic" in x.keys():
            self.automatic = x["automatic"]
        if "manual_measure" in x.keys():
            self.manual_measure = x["manual_measure"]
