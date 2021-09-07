
class ProfileDto(object):
    def __init__(self):
        self.email = ""
        self.name = ""
        self.surname = ""
        self.password = ""
        self.user_id = ""

    def constructor(self, email, name, surname, password):
        self.email = email
        self.name = name
        self.surname = surname
        self.password = password

    def constructor_map(self, profile_map):
        if "email" in profile_map.keys:
            self.email = profile_map["email"]
        if "name" in profile_map.keys:
            self.name = profile_map["name"]
        if "surname" in profile_map.keys:
            self.surname = profile_map["surname"]
        if "password" in profile_map.keys:
            self.password = profile_map["password"]


