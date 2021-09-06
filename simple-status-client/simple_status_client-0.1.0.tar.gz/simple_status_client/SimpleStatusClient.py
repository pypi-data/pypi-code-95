import hashlib
import json
from datetime import datetime

import requests
import yarl

from simple_status_client.models import ConfigIn, StatusIn
from simple_status_client import Colors


class APIClient():

    def __init__(self, url):
        self.url = yarl.URL(url)
        response = requests.get(url=self.url / "ping")
        assert b"pong" in response.content

    def set_config_base(self,
                        component_key: int,
                        name: str,
                        details: str,
                        timeout_min: int,
                        timeout_color: Colors,
                        parent_key: int = 0,
                        ):
        """
        Base methods have full capability, but there may be an easier implementation for you to use.
        This method will set a config for a given a component using it's component_key to identify it.  The
        component_key must be unique, an easy way to do this is to pick a unqiue name and hash it
        :param component_key: a unique identifier for your component, non unique values will result in overwriting
        the config
        :param name: The name of your component
        :param parent_key: a key for your parent component, results in your
        :param details: Any further information about your component you wish to convey
        :param timeout_min: the number of minutes your status should remain valid for
        :param timeout_color: the color your status should change to once it times out, will never "improve" the
        color of your status
        :return:
        """
        config = ConfigIn(name=name, parent_key=parent_key, details=details, timeout_min=timeout_min,
                          timeout_color=timeout_color)
        url = self.url / "components" / str(component_key) / "config"
        response = self.send_it(config, url)
        return response

    def set_config(self,
                   name: str,
                   details: str,
                   timeout_min: int,
                   timeout_color: Colors,
                   parent_name: str = "",
                   ):
        """
        This method will set a config for a given a component using it's name to identify it.  The
        name must be unique!
        :param name: The name of your component
        :param details: Any further information about your component you wish to convey
        :param timeout_min: the number of minutes your status should remain valid for
        :param timeout_color: the color your status should change to once it times out, will never "improve" the
        color of your status
        :param parent_name: a key for your parent component, results in your
        :return:
        """
        if not parent_name:
            parent_id = 0
        else:
            parent_id = self.name_to_component_id(parent_name)

        component_id = self.name_to_component_id(name)
        return self.set_config_base(component_id, name, details, timeout_min, timeout_color, parent_id)

    @staticmethod
    def name_to_component_id(name: str) -> int:
        """
        creates a unique component id assuming a unique name
        :param name: the name you wish converted to a component id
        :return:
        """
        return int.from_bytes(hashlib.md5(name.encode('utf-8')).digest(), 'little')

    def set_status_base(self,
                        component_key: int,
                        color: Colors,
                        message: str,
                        date: datetime = False,
                        ):
        """
        Base methods have full capability, but there may be an easier implementation for you to use.
        Sets the status for a given component_key
        :param component_key:
        :param color: The color to use for the status
        :param message: Any information you wish accessible on the server about the status
        :param date: the date of the status, defaults to now
        :return:
        """
        if not date:
            date = datetime.now()
        status = StatusIn(color=color, date=date, message=message)
        url = self.url / "components" / str(component_key) / "status"
        response = self.send_it(status, url)
        return response

    def set_status(self,
                   name: str,
                   color: Colors,
                   message: str,
                   date: datetime = datetime.now(),
                   ):
        """
        Base methods have full capability, but there may be an easier implementation for you to use.
        Sets the status for a given component_key
        :param component_key:
        :param color: The color to use for the status
        :param message: Any information you wish accessible on the server about the status
        :param date: the date of the status, defaults to now
        :return:
        """
        return self.set_status_base(self.name_to_component_id(name), color, message, date)

    @staticmethod
    def send_it(post_content, url):
        response = requests.post(url, json=json.loads(post_content.json()))
        if response.status_code != 200:
            raise Exception(response.content)
        return response
