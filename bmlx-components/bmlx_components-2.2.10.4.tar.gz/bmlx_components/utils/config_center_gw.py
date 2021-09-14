import requests
import json
import logging
from typing import Text, List

CONFIG_CENTER_OPEN_API_URL_PREFIX = (
    "http://config-sys.internal.bigo.sg/a/config"
)
LIST_KEY_HISTORY_SUFFIX = "listKeyHistory"
SERVICE_NAME = "bmlx"
SERVICE_KEY = "1591846975961"


class ConfigCenterGw(object):
    def __init__(
        self,
        url_prefix: Text = CONFIG_CENTER_OPEN_API_URL_PREFIX,
        service_name: Text = SERVICE_NAME,
        service_key: Text = SERVICE_KEY,
    ):
        self.url_prefix = url_prefix
        self.service_name = service_name
        self.service_key = service_key

    def get_published_configs(
        self, namespace: Text, group: Text, conf_name: Text, num: int = 1
    ) -> List[dict]:
        headers = {
            "A-KEY-A": self.service_key,
            "A-SERVICE-A": self.service_name,
        }
        try:
            resp = requests.get(
                url=f"{self.url_prefix}/{LIST_KEY_HISTORY_SUFFIX}",
                headers=headers,
                params={
                    "namespace_flag": namespace,
                    "group_name": group,
                    "conf_name": conf_name,
                    "num": num,
                },
            )
            if resp.status_code == 200:
                resp_obj = json.loads(resp.content)
                if resp_obj["retcode"] != 0:
                    raise RuntimeError("Invalid response %s" % resp.content)
                return resp_obj["result"]["data"]

        except Exception as e:
            logging.error(
                "Failed to request %s, error: %s",
                f"{self.url_prefix}/{LIST_KEY_HISTORY_SUFFIX}",
                e,
            )
            raise RuntimeError("Failed to request config center!")
