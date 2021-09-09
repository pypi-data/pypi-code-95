import requests
from .base import base


class user(base):

    def __init__(self, token, app_secret=None):
        super().__init__(token, app_secret)

    def get(self):
        api_name = "game/getUser"
        return self.request(api_name)

    def getGold(self):
        return self.get().get("gold")

    def signIn(self):
        api_name = "game/addNewUserSignin"
        return self.request(api_name)

    def signInOld(self):
        api_name = "game/addUserSignin"
        return self.request(api_name)

    def activate(self, cdkey):
        # 激活
        api_name = "game/activateEnterpriseAcc"
        data = {}
        data["cdkey"] = cdkey
        return self.request(api_name)

    def updatePassword(self, oldPassword, newPassword):
        # 激活
        api_name = "auth/updateUserPassword"
        data = {}
        data["oldPassword"] = oldPassword
        data["newPassword"] = newPassword
        return self.request(api_name)
