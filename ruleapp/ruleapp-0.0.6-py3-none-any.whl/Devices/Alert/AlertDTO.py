import json


class Alert(object):
    def __init__(self):
        self.device_id = ""
        self.name = "alert"
        self.email_list = []
        self.rules = []
        self.status = "connected"
        self.color = "green"
        self.expire_time = "10"

    def json_mapping(self, device_json):
        x = json.loads(device_json)
        if "device_id" in x.keys():
            self.device_id = x["device_id"]
        if "name" in x.keys():
            self.name = x["name"]
        if "rules" in x.keys():
            self.rules = x["rules"]
        if "email_list" in x.keys():
            self.email_list = x["email_list"]
