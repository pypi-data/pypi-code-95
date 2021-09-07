import jwt
from cryptography.fernet import Fernet


class ProfileFunction(object):
    def __init__(self, redis, config):
        self.r = redis
        password_key = config.get("OAUTH", "password_key")
        self.fernet = Fernet(password_key)
        self.token_key = config.get("OAUTH", "token_key")

    def register(self, dto):
        try:
            key_pattern = "profile:" + dto.email
            if self.r.exists(key_pattern + ":name") == 0:
                user_id = str(self.r.incr("profile:counter"))
                self.r.set(key_pattern + ":name", dto.name)
                self.r.set(key_pattern + ":password", self.encrypt_password(dto.password))
                self.r.set(key_pattern + ":surname", dto.surname)
                self.r.set(key_pattern + ":user_id", user_id)
                dto.user_id = user_id
                token = self.create_token(dto)
                return token
        except Exception as error:
            print(repr(error))
            return "error"

    def login(self, dto):
        try:
            key_pattern = "profile:" + dto.email
            if self.r.exists(key_pattern + ":name") == 1:
                password = self.decrypt_password(self.r.get(key_pattern+":password"))
                if password == dto.password:
                    dto.name = self.r.get(key_pattern + ":name")
                    dto.surname = self.r.get(key_pattern + ":surname")
                    dto.user_id = self.r.get(key_pattern + ":user_id")
                    token = self.create_token(dto)
                    return token
        except Exception as error:
            print(repr(error))
            return "error"

    def create_token(self, dto):
        payload = dto.__dict__
        return jwt.encode(payload, self.token_key, algorithm="HS256")

    def encrypt_password(self, password):
        return self.fernet.encrypt(password)

    def decrypt_password(self, password):
        return self.fernet.decrypt(password)
