from .AlertDTO import Alert


class AlertFunction(object):
    def __init__(self, redis):
        self.r = redis

    def register(self, user_id, email):
        try:
            device_id = "alert-" + user_id
            key_pattern = "device:" + device_id
            if self.r.exists(key_pattern + ":name") == 0:
                self.r.set(key_pattern + ":name", "alert")
                self.r.set(key_pattern + ":user_id", user_id)
                self.r.rpush(key_pattern + ":email_list", email)
                return "true"
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device(self, user_id):
        try:
            device_id = "alert-" + user_id
            key_pattern = "device:" + device_id
            dto = Alert()
            dto.device_id = device_id
            dto.name = self.r.get(key_pattern + ":name")
            dto.email_list = self.r.lrange(key_pattern + ":email_list")
            dto.rules = self.r.lrange(key_pattern + ":rules")
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_all_email(self, user_id):
        device_id = "alert-" + user_id
        key_pattern = "device:" + device_id
        if self.r.exists(key_pattern + ":email_list"):
            email_list = self.r.lrange(key_pattern + ":email_list")
            if len(email_list) > 0:
                for email in email_list:
                    self.r.lrem(key_pattern + ":email_list", email)

    def update_device(self, device_json):
        try:
            dto = Alert()
            dto.json_mapping(device_json)
            key_pattern = "device:" + dto.device_id
            self.r.set(key_pattern + ":name", dto.name)
            self.delete_all_email(dto.device_id)
            if len(dto.email_list) > 0:
                for email in dto.email_list:
                    self.r.rpush(key_pattern + ":email_list", email)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def add_alert_email(self, user_id):
        try:
            alert_id = "alert-" + user_id
            self.r.rpush("device:" + alert_id + ":email_list", "")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "added"

    def delete_alert_email(self, user_id, index):
        try:
            alert_id = "alert-" + user_id
            email_list = self.r.lrange("device:" + alert_id + ":email_list")
            email = email_list[index]
            self.r.lrem("device:" + alert_id + ":email_list", email)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "deleted"

    def modify_alert_email(self, user_id, email, idx):
        try:
            alert_id = "alert-" + user_id
            self.r.lset("device:" + alert_id + ":email_list", idx, email)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "deleted"
