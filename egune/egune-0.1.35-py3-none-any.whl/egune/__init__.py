from egune.requests import (  # noqa: 401
    ButtonQuestion,
    YesNoQuestion,
    OpenQuestion,
    Fail,
    Success,
    Tell,
    TellCustom,
    TellPreparedMessage,
    Do,
    MultiSelectQuestion,
    CheckboxQuestion,
    Form,
    FormQuestionTypes,
    ActorMessage,
    ActionServerRequest
)
from egune.response_manager import ResponseManager
from datetime import datetime
from cachetools import TTLCache
import requests

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class Egune:
    def __init__(self, egune_host, egune_port, api_token, response_manager_config, is_test=False):
        self.egune_home = f"http://{egune_host}:{egune_port}/"
        self.api_token = api_token
        self.is_test = is_test
        self.cache = TTLCache(9999, 60)
        self.response_manager = ResponseManager(response_manager_config, is_test)

    def tell_user_now(self, message: ActorMessage):
        request = TellCustom()
        request.variables = {"msg": message.to_dict()}
        self.send_request_now(TellCustom())

    def send_request_now(self, request: ActionServerRequest):
        request_dict = request.publish()
        request_dict["app_id"] = self.api_token
        request_dict["operation"] = "process"
        if self.is_test:
            print("EGUNE SENT MESSAGE:", request_dict)
        else:
            requests.post(
                self.egune_home + "app",
                json=request_dict
            )

    def create_ontime_event(self, user_id, timestamp: datetime, name="on time single event", data={}):
        event = {
            "type": "on-time",
            "user_id": user_id,
            "app_id": self.api_token,
            "time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "data": data,
            "operation": "add_event"
        }
        if self.is_test:
            print("EGUNE EVENT:", event)
        else:
            requests.post(
                self.egune_home + "app",
                json=event
            )

    def create_weekly_event(self, user_id, weekday, hour, minute, name="weekly repeating event", data={}):
        event = {
            "type": "weekly",
            "user_id": user_id,
            "app_id": self.api_token,
            "hour": hour,
            "minute": minute,
            "name": name,
            "weekday": weekday,
            "data": data,
            "operation": "add_event"
        }
        if self.is_test:
            print("EGUNE EVENT:", event)
        else:
            requests.post(
                self.egune_home + "app",
                json=event
            )

    def create_monthly_event(self, user_id, day, hour, minute, name="monthly repeating event", data={}):
        event = {
            "type": "monthly",
            "user_id": user_id,
            "app_id": self.api_token,
            "hour": hour,
            "minute": minute,
            "name": name,
            "day": day,
            "data": data,
            "operation": "add_event"
        }
        if self.is_test:
            print("EGUNE EVENT:", event)
        else:
            requests.post(
                self.egune_home + "app",
                json=event
            )

    def save_state(self, user_id, vals):
        self.cache[user_id] = vals

    def get_state(self, user_id):
        return self.cache.get(user_id, None)

    def add_data(self, app_id, train, test):
        request = {
            "operation": "add_data",
            "train": train,
            "test": test,
            "app_id": app_id
        }
        requests.post(self.egune_home + "app", json=request)
