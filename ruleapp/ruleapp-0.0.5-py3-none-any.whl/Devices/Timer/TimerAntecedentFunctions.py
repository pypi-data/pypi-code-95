from .TimerAntecedentDTO import TimerAntecedent
from datetime import datetime


class TimerAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_antecedent(self, user_id, rule_id, device_id):
        try:
            antecedent = TimerAntecedent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            antecedent.device_id = device_id
            antecedent.device_name = self.r.get(key_pattern + ":device_name")
            antecedent.day_start_value = self.r.lrange(key_pattern + ":day_start_value")
            antecedent.time_start_value = self.r.get(key_pattern + ":time_start_value")
            antecedent.time_stop_value = self.r.get(key_pattern + ":time_stop_value")
            antecedent.check_time = self.r.get(key_pattern + ":check_time")
            antecedent.check_date = self.r.get(key_pattern + ":check_date")
            antecedent.evaluation = self.r.get(key_pattern + ":evaluation")
            antecedent.order = self.r.get(key_pattern + ":order")
            antecedent.measure_time = datetime.now().strftime("%H:%M")
            antecedent.measure_day = str(datetime.today().weekday())
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_antecedent_slim(self, user_id, rule_id, device_id):
        try:
            antecedent = TimerAntecedent()
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
            if self.r.exists(key_pattern + ":day_start_value") == 1:
                days = self.r.lrange(key_pattern + ":day_start_value")
                for day in days:
                    self.r.lrem(key_pattern + ":day_start_value", day)
            self.r.delete(key_pattern + ":device_name")
            self.r.delete(key_pattern + ":time_start_value")
            self.r.delete(key_pattern + ":time_stop_value")
            self.r.delete(key_pattern + ":check_time")
            self.r.delete(key_pattern + ":check_date")
            self.r.delete(key_pattern + ":evaluation")
            self.r.delete(key_pattern + ":order")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def set_antecedent(self, user_id, rule_id, antecedent_json):
        try:
            antecedent = TimerAntecedent()
            antecedent.json_mapping(antecedent_json)
            self.r.rpush("device:" + antecedent.device_id + ":rules", rule_id)
            self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", antecedent.device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + antecedent.device_id
            if self.r.exists(key_pattern + ":day_start_value") == 1:
                days = self.r.lrange(key_pattern + ":day_start_value")
                for day in days:
                    self.r.lrem(key_pattern + ":day_start_value", day)
            if len(antecedent.day_start_value) > 0:
                for day in antecedent.day_start_value:
                    self.r.rpush(key_pattern + ":day_start_value", day)
            self.r.set(key_pattern + ":device_name", antecedent.device_name)
            self.r.set(key_pattern + ":evaluation", antecedent.evaluation)
            self.r.set(key_pattern + ":time_start_value", antecedent.time_start_value)
            self.r.set(key_pattern + ":time_stop_value", antecedent.time_stop_value)
            self.r.set(key_pattern + ":check_time", antecedent.check_time)
            self.r.set(key_pattern + ":check_date", antecedent.check_date)
            self.r.set(key_pattern + ":order", antecedent.order)
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def evaluate_antecedent(self, user_id, rule_id, device_id):
        try:
            time_evaluation = self.evaluate_time(user_id, rule_id, device_id)
            date_evaluation = self.evaluate_date(user_id, rule_id, device_id)
            evaluation = "false"
            if time_evaluation == "true" and date_evaluation == "true":
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

    def evaluate_time(self, user_id, rule_id, device_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            check_time = self.r.get(key_pattern + ":check_time")
            evaluation = "true"
            if check_time == "true":
                current_time_str = datetime.now().strftime("%H:%M")
                current_time = datetime.strptime(current_time_str, '%H:%M').time()
                time_start_value_str = self.r.get(key_pattern + ":time_start_value")
                time_stop_value_str = self.r.get(key_pattern + ":time_stop_value")
                time_start_value = datetime.strptime(time_start_value_str, '%H:%M').time()
                time_stop_value = datetime.strptime(time_stop_value_str, '%H:%M').time()
                evaluation = "false"
                if time_start_value <= current_time < time_stop_value:
                    evaluation = "true"
            return evaluation
        except Exception as error:
            print(repr(error))
            return "error"

    def evaluate_date(self, user_id, rule_id, device_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            check_date = self.r.get(key_pattern + ":check_date")
            evaluation = "true"
            if check_date == "true":
                current_day = str(datetime.today().weekday())
                day_start_value = self.r.lrange(key_pattern + ":day_start_value")
                evaluation = "false"
                if current_day in day_start_value:
                    evaluation = "true"
            return evaluation
        except Exception as error:
            print(repr(error))
            return "error"
