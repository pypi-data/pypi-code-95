from .ButtonAntecedentDTO import ButtonAntecedent
from datetime import datetime


class ButtonAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_antecedent(self, user_id, rule_id, device_id):
        try:
            antecedent = ButtonAntecedent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            antecedent.device_id = device_id
            antecedent.device_name = self.r.get(key_pattern + ":device_name")
            antecedent.measure = self.r.get(key_pattern + ":measure")
            antecedent.evaluation = self.r.get(key_pattern + ":evaluation")
            antecedent.last_time_on = self.r.get(key_pattern + ":last_time_on")
            antecedent.last_time_off = self.r.get(key_pattern + ":last_time_off")
            antecedent.last_date_on = self.r.get(key_pattern + ":last_date_on")
            antecedent.last_date_off = self.r.get(key_pattern + ":last_date_off")
            antecedent.order = self.r.get(key_pattern + ":order")
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_antecedent_slim(self, user_id, rule_id, device_id):
        try:
            antecedent = ButtonAntecedent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            antecedent.device_id = device_id
            antecedent.device_name = self.r.get(key_pattern + ":device_name")
            antecedent.evaluation = self.r.get(key_pattern + ":evaluation")
            antecedent.order = self.r.get(key_pattern + ":order")
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_antecedent(self, user_id, rule_id, device_id):
        try:
            self.r.lrem("device:" + device_id + ":rules", rule_id)
            self.r.lrem("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            self.r.delete(key_pattern + ":device_name")
            self.r.delete(key_pattern + ":measure")
            self.r.delete(key_pattern + ":evaluation")
            self.r.delete(key_pattern + ":last_time_on")
            self.r.delete(key_pattern + ":last_time_off")
            self.r.delete(key_pattern + ":last_date_on")
            self.r.delete(key_pattern + ":last_date_off")
            self.r.delete(key_pattern + ":order")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def set_antecedent(self, user_id, rule_id, antecedent_json):
        try:
            antecedent = ButtonAntecedent()
            antecedent.json_mapping(antecedent_json)
            self.r.rpush("device:" + antecedent.device_id + ":rules", rule_id)
            self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", antecedent.device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + antecedent.device_id
            self.r.set(key_pattern + ":device_name", antecedent.device_name)
            self.r.set(key_pattern + ":order", antecedent.order)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def antecedent_evaluation(self, user_id, rule_id, device_id, measure):
        try:
            measure_evaluation = self.evaluate_measure(measure)
            evaluation = "false"
            if measure_evaluation == "true":
                evaluation = "true"
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            old_evaluation = self.r.get(key_pattern + ":evaluation")
            trigger = "false"
            if evaluation != old_evaluation:
                self.r.set(key_pattern + ":evaluation", evaluation)
                trigger = "true"
            return trigger
        except Exception as error:
            print(repr(error))
            return "error"

    def evaluate_measure(self, measure):
        try:
            evaluation = "false"
            if measure == "on":
                evaluation = "true"
            return evaluation
        except Exception as error:
            print(repr(error))
            return "error"

