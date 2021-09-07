from .FolderDTO import FolderDto


class FolderFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_folder(self, user_id, folder_id):
        try:
            folder = FolderDto()
            key_pattern = "user:" + user_id + ":folder:" + folder_id
            folder.folder_id = folder_id
            folder.folder_name = self.r.get(key_pattern+":name")
            folder.rules = self.r.lrange(key_pattern+":rules")
            return folder
        except Exception as error:
            print(repr(error))
            return "error"

    def create_folder(self, user_id, folder_name):
        try:
            folder_id = str(self.r.incr("user:" + user_id + ":folder:counter"))
            self.r.rpush("user:" + user_id + ":folders", folder_id)
            self.r.set("user:" + user_id + ":folder:" + folder_id + ":name", folder_name)
            folder = FolderDto()
            folder.folder_id = folder_id
            folder.folder_name = folder_name
            return folder
        except Exception as error:
            print(repr(error))
            return "error"

    def update_folder(self, user_id, folder):
        try:
            key_pattern = "user:" + user_id + ":folder:" + folder.folder_id
            self.r.set(key_pattern+":name", folder.name)
            rules = self.r.lrange(key_pattern+":rules")
            for rule in rules:
                self.r.lrem(key_pattern+":rules", rule)
            for rule in folder.rules:
                self.r.rpush(key_pattern+":rules", rule)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_folder(self, user_id, folder_id):
        try:
            self.r.lrem("user:" + user_id + ":folders", folder_id)
            self.r.delete("user:" + user_id + ":folder:" + folder_id + ":name")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def add_rule(self, user_id, folder_id, rule_id):
        try:
            self.r.rpush("user:"+user_id+":folder:"+folder_id+":rules", rule_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_rule(self, user_id, folder_id, rule_id):
        try:
            self.r.lrem("user:"+user_id+":folder:"+folder_id+":rules", rule_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"
