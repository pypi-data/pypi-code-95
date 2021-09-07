from .RuleDTO import Rule
from ..Devices.Timer.TimerAntecedentFunctions import TimerAntecedentFunction
from ..Devices.Alert.AlertConsequentFunctions import AlertConsequentFunction
from ..Devices.WaterLevel.WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from ..Devices.Switch.SwitchConsequentFunctions import SwitchConsequentFunction
from ..Devices.Button.ButtonAntecedentFunctions import ButtonAntecedentFunction


class RuleFunction(object):
    def __init__(self, redis):
        self.r = redis
        self.timer_antecedent_functions = TimerAntecedentFunction(redis)
        self.alert_consequent_functions = AlertConsequentFunction(redis)
        self.waterlevel_antecedent_functions = WaterLevelAntecedentFunction(redis)
        self.switch_consequent_functions = SwitchConsequentFunction(redis)
        self.button_antecedent_functions = ButtonAntecedentFunction(redis)

    def create_rule(self, user_id, rule_name):
        try:
            rule_id = str(self.r.incr("user:" + user_id + ":rule:counter"))
            key_pattern = "user:"+user_id+":rule:"+rule_id
            self.r.rpush("user:"+user_id+":rules", rule_id)
            self.r.set(key_pattern+":rule_name", rule_name)
            self.r.set(key_pattern+":evaluation", "false")
            return rule_id
        except Exception as error:
            print(repr(error))
            return "error"

    def get_user_rules(self, user_id):
        try:
            rules_id_list = self.r.lrange("user:" + user_id + "rules")
            output = []
            rule = Rule()
            for rule_id in rules_id_list:
                key_pattern = "user:" + user_id + ":rule:" + rule_id
                if self.r.exists(key_pattern + ":name") == 1:
                    rule.rule_name = self.r.get(key_pattern + ":name")
                    rule.rule_id = rule_id
                    rule.evaluation = self.r.get(key_pattern + ":evaluation")
                    output.append(rule)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule(self, user_id, rule_id):
        try:
            key_pattern = "user:"+user_id+":rule:"+rule_id
            rule = Rule()
            rule.rule_id = rule_id
            rule.rule_name = self.r.get(key_pattern+":rule_name")
            rule.last_time_on = self.r.get(key_pattern+":last_time_on")
            rule.last_time_off = self.r.get(key_pattern+":last_time_off")
            rule.last_date_on = self.r.get(key_pattern+":last_date_on")
            rule.last_date_off = self.r.get(key_pattern+":last_date_off")
            rule.device_antecedents = self.r.lrange(key_pattern+":device_antecedents")
            rule.device_consequents = self.r.lrange(key_pattern+":device_consequents")
            rule.evaluation = self.r.get(key_pattern+":evaluation")
            rule.rule_antecedents = self.get_rule_antecedents(user_id, rule_id)
            rule.rule_consequents = self.get_rules_consequents(user_id, rule_id)
            return rule
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedents(self, user_id, rule_id):
        try:
            key_pattern = "user:"+user_id+":rule:"+rule_id
            device_antecedents = self.r.lrange(key_pattern+":device_antecedents")
            rule_antecedents = []
            for device_id in device_antecedents:
                antecedent = self.get_rule_antecedent_slim(user_id, rule_id, device_id)
                if antecedent != "error":
                    rule_antecedents.append(antecedent)
                else:
                    raise Exception("error retrieving antecedent")
            return rule_antecedents
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedent(self, user_id, rule_id, device_id):
        try:
            antecedent = {}
            if "timer" in device_id:
                antecedent = self.timer_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            elif "WATERLEVEL" in device_id:
                antecedent = self.waterlevel_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            elif "BUTTON" in device_id:
                antecedent = self.button_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedent_slim(self, user_id, rule_id, device_id):
        try:
            antecedent = {}
            if "timer" in device_id:
                antecedent = self.timer_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            elif "WATERLEVEL" in device_id:
                antecedent = self.waterlevel_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            elif "BUTTON" in device_id:
                antecedent = self.button_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_consequents(self, user_id, rule_id):
        key_pattern = "user:"+user_id+":rule:"+rule_id
        device_consequents = self.r.lrange(key_pattern+":device_consequents")
        rule_consequents = []
        for device_id in device_consequents:
            consequent = self.get_rule_consequent_slim(user_id, rule_id, device_id)
            if consequent != "error":
                rule_consequents.append(consequent)
            else:
                raise Exception("error retrieving consequent")
        return rule_consequents

    def get_rule_consequent(self, user_id, rule_id, device_id):
        try:
            consequent = {}
            if "alert" in device_id:
                consequent = self.alert_consequent_functions.get_consequent(user_id, rule_id, device_id)
            elif "SWITCH" in device_id:
                consequent = self.switch_consequent_functions.get_consequent(user_id, rule_id, device_id)
            return consequent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_consequent_slim(self, user_id, rule_id, device_id):
        try:
            consequent = {}
            if "alert" in device_id:
                consequent = self.alert_consequent_functions.get_consequent_slim(user_id, rule_id, device_id)
            elif "SWITCH" in device_id:
                consequent = self.switch_consequent_functions.get_consequent_slim(user_id, rule_id, device_id)
            return consequent
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_rule(self, user_id, rule_id):
        key_pattern = "user:"+user_id+":rule:"+rule_id
        self.r.lrem("user:"+user_id+":rules", rule_id)
        self.r.delete(key_pattern+":rule_name")
        self.r.delete(key_pattern+":last_time_on")
        self.r.delete(key_pattern+":last_time_off")
        self.r.delete(key_pattern+":last_date_on")
        self.r.delete(key_pattern+":last_date_off")
        device_antecedents = self.r.lrange(key_pattern+":device_antecedents")
        for device_id in device_antecedents:
            self.delete_rule_antecedent(user_id, rule_id, device_id)
        device_consequents = self.r.lrange(key_pattern+":device_consequents")
        for device_id in device_consequents:
            self.delete_rule_consequent(user_id, rule_id, device_id)

    def delete_rule_antecedent(self, user_id, rule_id, device_id):
        try:
            key_pattern = "user:"+user_id+":rule:"+rule_id
            self.r.lrem(key_pattern+":device_antecedents", device_id)
            if "timer" in device_id:
                return self.timer_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            elif "WATERLEVEL" in device_id:
                return self.waterlevel_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            elif "BUTTON" in device_id:
                return self.button_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_rule_consequent(self, user_id, rule_id, device_id):
        try:
            key_pattern = "user:"+user_id+":rule:"+rule_id
            self.r.lrem(key_pattern+":device_consequents", device_id)
            if "alert" in device_id:
                return self.alert_consequent_functions.delete_consequent(user_id, rule_id, device_id)
            elif "SWITCH" in device_id:
                return self.switch_consequent_functions.delete_consequent(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def update_rule_name(self, user_id, rule_id, rule_name):
        try:
            key_pattern = "user:"+user_id+":rule:"+rule_id
            self.r.set(key_pattern+":rule_name", rule_name)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def add_rule_antecedent(self, user_id, rule_id, device_id, antecedent_json):
        try:
            key_pattern = "user:"+user_id+":rule:"+rule_id
            self.r.rpush(key_pattern+":device_antecedents", device_id)
            return self.update_rule_antecedent(user_id, rule_id, device_id, antecedent_json)
        except Exception as error:
            print(repr(error))
            return "error"

    def add_rule_consequent(self, user_id, rule_id, device_id, consequent_json):
        try:
            key_pattern = "user:"+user_id+":rule:"+rule_id
            self.r.rpush(key_pattern+":device_consequents", device_id)
            return self.update_rule_consequent(user_id, rule_id, device_id, consequent_json)
        except Exception as error:
            print(repr(error))
            return "error"

    def update_rule_antecedent(self, user_id, rule_id, device_id, antecedent_json):
        try:
            antecedent = {}
            if "timer" in device_id:
                antecedent = self.timer_antecedent_functions.set_antecedent(user_id, rule_id, antecedent_json)
            elif "WATERLEVEL" in device_id:
                antecedent = self.waterlevel_antecedent_functions.set_antecedent(user_id, rule_id, antecedent_json)
            elif "BUTTON" in device_id:
                antecedent = self.button_antecedent_functions.set_antecedent(user_id, rule_id, antecedent_json)
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def update_rule_consequent(self, user_id, rule_id, device_id, consequent_json):
        try:
            if "alert" in device_id:
                self.alert_consequent_functions.set_consequent(user_id, rule_id, consequent_json)
            elif "SWITCH" in device_id:
                self.switch_consequent_functions.set_consequent(user_id, rule_id, consequent_json)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"



