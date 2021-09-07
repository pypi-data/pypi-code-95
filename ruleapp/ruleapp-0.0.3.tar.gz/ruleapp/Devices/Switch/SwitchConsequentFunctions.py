from .SwitchConsequentDTO import SwitchConsequent


class SwitchConsequentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_consequent(self, user_id, rule_id, device_id):
        try:
            dto = SwitchConsequent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            dto.device_name = self.r.get(key_pattern + ":device_name")
            dto.delay = self.r.get(key_pattern + ":delay")
            dto.order = self.r.get(key_pattern + ":order")
            dto.automatic = self.r.get("device:" + device_id + ":automatic")
        except Exception as error:
            print(repr(error))
            return "error"

    def get_consequent_slim(self, user_id, rule_id, device_id):
        try:
            dto = SwitchConsequent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            dto.device_name = self.r.get(key_pattern + ":device_name")
            dto.order = self.r.get(key_pattern + ":order")
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_consequent(self, user_id, rule_id, device_id):
        try:
            self.r.lrem("device:" + device_id + ":rules", rule_id)
            self.r.lrem("user:" + user_id + ":rule:" + rule_id + ":device_consequents", device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            self.r.delete(key_pattern + ":delay")
            self.r.delete(key_pattern + ":order")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def set_consequent(self, user_id, rule_id, consequent_json):
        try:
            consequent = SwitchConsequent()
            consequent.json_mapping(consequent_json)
            self.r.rpush("device:" + consequent.device_id + ":rules", rule_id)
            self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_consequents", consequent.device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + consequent.device_id
            self.r.set(key_pattern + ":device_name", consequent.device_name)
            self.r.set(key_pattern + ":delay", consequent.delay)
            self.r.set(key_pattern + ":order", consequent.order)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

