class UserFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_sensors(self, user_id):
        try:
            return self.r.lrange("user:" + user_id + ":sensors")
        except Exception as error:
            print(repr(error))
            return "error"

    def get_switches(self, user_id):
        try:
            return self.r.lrange("user:" + user_id + ":switches")
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rules(self, user_id):
        try:
            return self.r.lrange("user:" + user_id + ":rules")
        except Exception as error:
            print(repr(error))
            return "error"

    def get_folders(self, user_id):
        try:
            return self.r.lrange("user:" + user_id + ":folders")
        except Exception as error:
            print(repr(error))
            return "error"


