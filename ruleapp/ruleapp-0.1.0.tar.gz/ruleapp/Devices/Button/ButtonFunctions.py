from .ButtonDTO import Button
from .ButtonAntecedentFunctions import ButtonAntecedentFunction
from ..DeviceEvaluationDTO import DeviceEvaluation
from datetime import datetime


class ButtonFunction(object):
    def __init__(self, redis):
        self.r = redis
        self.button_antecedent_functions = ButtonAntecedentFunction(redis)

    def register(self, user_id, device_id):
        try:
            if self.r.exists("device:" + device_id + ":name") == 0:
                key_pattern = "device:" + device_id
                device_id_keys = self.r.lrange("user:" + user_id + ":sensors")
                device_name = "WATERLEVEL " + str(len(device_id_keys))
                self.r.set(key_pattern + ":name", device_name)
                self.r.set(key_pattern + ":user_id", user_id)
                self.r.set(key_pattern + ":measure", "-")
                self.r.rpush("user:" + user_id + ":sensors", device_id)
                return "true"
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device(self, device_id):
        try:
            key_pattern = "device:" + device_id
            dto = Button()
            dto.device_id = device_id
            dto.name = self.r.get(key_pattern + ":name")
            if self.r.exists(key_pattern + ":rules") == 1:
                dto.rules = self.r.lrange(key_pattern + ":rules")
            if self.r.exists(key_pattern + ":measure") == 1:
                measure = self.r.get(key_pattern + ":measure")
                if measure == "-":
                    dto.measure = measure
                    dto.color = "yellow"
                    dto.status = "initialization"
                else:
                    dto.measure = measure
                    dto.color = "green"
                    dto.status = "connected"
            dto.max_measure = self.r.get(key_pattern + ":max_measure")
            dto.max_measure_time = self.r.get(key_pattern + ":max_measure_time")
            dto.min_measure = self.r.get(key_pattern + ":min_measure")
            dto.min_measure_time = self.r.get(key_pattern + ":min_measure_time")
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def update_device(self, device_json):
        try:
            dto = Button()
            dto.json_mapping(device_json)
            key_pattern = "device:" + dto.device_id
            self.r.set(key_pattern + ":name", dto.name)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_device(self, user_id, device_id):
        try:
            self.r.lrem("user:" + user_id + ":sensors", device_id)
            key_pattern = "device:" + device_id
            self.r.delete(key_pattern + ":name")
            self.r.delete(key_pattern + ":user_id")
            self.r.delete(key_pattern + ":measure")
            self.r.delete(key_pattern + ":last_time_on")
            self.r.delete(key_pattern + ":last_time_off")
            self.r.delete(key_pattern + ":last_date_on")
            self.r.delete(key_pattern + ":last_date_off")
            if self.r.exists(key_pattern + ":rules") == 1:
                rules = self.r.lrange(key_pattern + ":rules")
                for rule_id in rules:
                    self.button_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def measure_evaluation(self, device_id, measure):
        time_str = datetime.now().strftime("%H:%M:%S")
        date_str = datetime.now().strftime("%d/%m/%Y")
        key_pattern = "device:" + device_id
        if measure == "on":
            self.r.set(key_pattern + ":last_time_on", time_str)
            self.r.set(key_pattern + ":last_date_on", date_str)
        else:
            self.r.set(key_pattern + ":last_time_off", time_str)
            self.r.set(key_pattern + ":last_date_off", date_str)
        return measure

    def device_evaluation(self, device_id, measure):
        output = DeviceEvaluation()
        key_pattern = "device:" + device_id
        if self.r.exists(key_pattern + ":user_id") == 1:
            output.user_id = self.r.get("device:" + device_id + ":user_id")
            output.measure = self.measure_evaluation(device_id, measure)
            output.device_id = device_id
            output.type = "antecedent"
            if self.r.exists(key_pattern + ":rules"):
                output.rules = list(self.r.smembers(key_pattern + ":rules"))
        return output
