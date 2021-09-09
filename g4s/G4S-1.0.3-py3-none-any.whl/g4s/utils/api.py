from datetime import datetime, timedelta
import requests
from typing import Any, Optional, Dict, List


class API:
    def __init__(self, username: str, password: str) -> None:
        self.username: str = username
        self.password: str = password
        self.base_url: str = "https://mit.g4severhome.dk/ESI.API/API"
        self.status_url_part: str = "systemstatus/getState"
        self.command_url_part: str = "Commands/invokeAPI"
        self.panel_id: Optional[int] = None
        self.get_state()

    def get_state(self) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.status_url_part}"
        body: Dict[str, Any] = {"username": self.username, "password": self.password}
        if self.panel_id is not None:
            body["panel_id"] = self.panel_id
        req = requests.post(url, json=body)
        req.raise_for_status()
        return_value = req.json()
        if return_value["Response"] != 0:
            raise Exception(return_value["ResponseDescription"])
        if self.panel_id is None:
            self.panel_id = return_value["panelInfo"]["PanelId"]
        return return_value

    def arm_alarm(self) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.command_url_part}"
        body = {
            "email": self.username,
            "password": self.password,
            "methodToInvoke": "Arm",
            "panelId": self.panel_id,
            "partition": 0,
        }
        req = requests.post(url, json=body)
        return req.json()

    def night_arm_alarm(self) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.command_url_part}"
        body = {
            "email": self.username,
            "password": self.password,
            "methodToInvoke": "Arm",
            "partition": 2,
            "panelId": self.panel_id,
        }
        req = requests.post(url, json=body)
        return req.json()

    def day_arm_alarm(self) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.command_url_part}"
        body = {
            "email": self.username,
            "password": self.password,
            "methodToInvoke": "Arm",
            "partition": 1,
            "panelId": self.panel_id,
        }
        req = requests.post(url, json=body)
        return req.json()

    def disarm_alarm(self) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.command_url_part}"
        body = {
            "email": self.username,
            "password": self.password,
            "methodToInvoke": "Disarm",
            "panelId": self.panel_id,
        }
        req = requests.post(url, json=body)
        return req.json()

    def change_user_panel_pin(self, user_id: int, access_code: str) -> Dict[str, Any]:
        url = f"{self.base_url}/users/SetTr5AccessCode"
        body = {
            "panelId": self.panel_id,
            "userName": self.username,
            "password": self.password,
            "accessCode": access_code,
            "userId": user_id,
        }
        req = requests.post(url, json=body)
        req.raise_for_status()
        return req.json()

    def get_events(
        self,
        event_type_list: Optional[list[str]] = None,
        count: int = 100,
        date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/Events/InvokeApi"
        body = {
            "email": self.username,
            "password": self.password,
            "methodToInvoke": "GetEventsHistory",
            "panelId": self.panel_id,
            "eventTypeList": "314,56,57,51,58,59,1,2,5,153,155,3,156,8,9,1010,39,40,203,211,212,215,216,222,223,411,412,506,510,511,513,514,515,516,904,906,907,909,910,912,913,915,916,918,919,921,104,106,105,101,103,102,150,152,151,204,1201,1207,1253,706,705,220,221,107,109,112,113,114,418,1258,1259,1260,1875,1876,1205,1208,1602,1601,1604,1610,1611,1640,1641,1612,1613,1614,1615,1616,927,928,930,931,933,901,903,108,810,811,812,813,814,927,815,1617,1618,1810,1811,1891,1892,1893,1894,1895,1896,30,1812,1879,1883,1884,1899,1900,1901,1902,1903",
            "numberOfEvents": count,
        }
        if event_type_list is not None:
            body["eventTypeList"] = ",".join(event_type_list)

        if date is not None:
            body["fromDate"] = date.strftime("%Y-%m-%d")
            body["toDate"] = (date + timedelta(days=1)).strftime("%Y-%m-%d")
        req = requests.post(url, json=body)
        req.raise_for_status()
        return req.json()
