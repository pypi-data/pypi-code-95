import os

import requests
from urllib3.exceptions import InsecureRequestWarning

class BaseApi():
    def __init__(self):
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        self.login_api = os.getenv("HABU_LOGIN_API", "https://localhost:6042/moonraker")
        self.cleanroom_api = os.getenv("HABU_CR_API", "https://localhost:5018/unhygienix")

    def login(self):
        user = os.getenv("HABU_USER")
        password = os.getenv("HABU_PASSWORD")

        if not user or not password:
            raise Exception("User and Password must be defined in your environment. Please check documentation!")

        response = requests.post("%s/auth/login" % self.login_api, json={
            "email": user,
            "password": password
        }, verify=False)

        if response.status_code != 200:
            raise Exception("Unable to login to habu API. Check your environment and settings!")

        data = response.json()
        auth_token = data["authToken"]
        return auth_token

    def logout(self, auth_token):
        response = requests.post("%s/auth/logout" % self.login_api, verify=False,
                                 headers={'Authorization': auth_token})
        if response.status_code != 200:
            raise Exception("Unable to logout.")

    def post(self, key, url):
        auth_token = self.login()
        try:
            response = requests.post(url,
                                     verify=False,
                                     headers={'Authorization': auth_token})
            if response.status_code != 200:
                response.raise_for_status()
            return response.json()[key]
        finally:
            self.logout(auth_token)

    def get(self, key, url):
        auth_token = self.login()
        try:
            response = requests.get(url,
                                    verify=False,
                                    headers={'Authorization': auth_token})
            if response.status_code != 200:
                response.raise_for_status()
            return response.json()[key]
        finally:
            self.logout(auth_token)


class CleanRoom(BaseApi):
    def __init__(self):
        BaseApi.__init__(self)
        self.org_uuid = os.getenv("HABU_ORGANIZATION")
        if not self.org_uuid:
            raise Exception("Organization must be defined in your environment. Please check documentation!")

    def get_clean_rooms(self):
        return self.post("cleanRooms", "%s/organization/%s/clean-room/list" % (self.cleanroom_api, self.org_uuid))

    def get_clean_room_questions(self, cleanroom_uuid):
        return self.get("questions", "%s/organization/%s/clean-room/%s/question/list"
                        % (self.cleanroom_api, self.org_uuid, cleanroom_uuid))

    def get_question_runs(self, cleanroom_uuid, question_uuid):
        return self.get("runs", "%s/organization/%s/clean-room/%s/clean-room-question/%s/run/list"
                        % (self.cleanroom_api, self.org_uuid, cleanroom_uuid, question_uuid))

    def get_question_run_data(self, cleanroom_uuid, question_uuid, run_uuid):
        return self.post("data", "%s/organization/%s/clean-room/%s/clean-room-question/%s/run/%s/table"
                        % (self.cleanroom_api, self.org_uuid, cleanroom_uuid, question_uuid, run_uuid))