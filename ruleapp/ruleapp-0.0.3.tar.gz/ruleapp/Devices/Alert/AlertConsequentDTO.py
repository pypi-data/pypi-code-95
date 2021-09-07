import json


class AlertConsequent(object):
    def __init__(self):
        self.device_id = ""
        self.device_name = ""
        self.message = ""
        self.if_value = "on"
        self.else_value = "off"
        self.delay = "0"
        self.delay_unit_measure = "seconds"
        self.order = ""

    def json_mapping(self, device_json):
        x = json.loads(device_json)
        if "device_id" in x.keys():
            self.device_name = x["device_id"]
        if "device_name" in x.keys():
            self.device_name = x["device_name"]
        if "message" in x.keys():
            self.device_name = x["message"]
        if "delay" in x.keys():
            self.delay = x["delay"]
        if "order" in x.keys():
            self.order = x["order"]
