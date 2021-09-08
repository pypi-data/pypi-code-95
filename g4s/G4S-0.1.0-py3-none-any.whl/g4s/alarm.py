import json

from g4s.utils.api import API
from g4s.utils.alarm_status import AlarmStatus


class Alarm:
    def __init__(self, username, password):
        self.usernam = username
        self.password = password
        self.api = API(self.usernam, self.password)
        self.status = None
        self.users = None
        self.state = None
        self.last_state_change = None
        self.last_state_change_by = None
        self.sensors = None
        self.panel_settings = None
        self.update_status()

    def update_status(self):
        self.status = AlarmStatus(self.api.get_state(), self.api)
        self.panel_settings = self.status.panel_settings
        self.users = self.status.users
        self.state = self.status.system_state.arm_type
        self.sensors = self.status.state_devices
        self.last_state_change = self.status.system_state.arm_type_changed_time
        events = json.loads(self.api.get_events(date=self.last_state_change)["Events"])
        matching_events = [
            x
            for x in events
            if self.panel_settings.time_zone.date_time_as_utc(
                x["Events"][0]["Header"]["LocalTime"].replace('"', "")
            )
            == self.last_state_change
            and x["Events"][0]["UserId"] is not None
        ]
        if len(matching_events) > 0:
            user_id = matching_events[0]["Events"][0]["UserId"]
            self.last_state_change_by = [x for x in self.users if x.Id == user_id][0]
        self.panel_settings.default_temperature_device = [
            x
            for x in self.sensors
            if x.Id == self.panel_settings.default_temperature_device_id
        ][0]

    def arm(self):
        self.api.arm_alarm()
        self.update_status()

    def night_arm(self):
        self.api.night_arm_alarm()
        self.update_status()

    def disarm(self):
        self.api.disarm_alarm()
        self.update_status()

    def __str__(self) -> str:
        return str(self.state)

    def __repr__(self) -> str:
        return str(self)
