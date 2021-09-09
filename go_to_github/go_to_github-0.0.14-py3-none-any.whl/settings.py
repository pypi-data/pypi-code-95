import os
from pathlib import Path

URL = "https://github.com.ipaddress.com/"
GITHUB_URL = "https://github.com"

CONFIG_DICT = {
    "github.global.ssl.fastly.net": "199.232.69.194",
    "ssets-cdn.github.com": [
        "185.199.108.153",
        "185.199.109.153",
        "185.199.110.153",
        "185.199.111.153",
    ],
}

CONFIG_LIST = [
    "199.232.69.194 github.global.ssl.fastly.net",
    "185.199.108.153 ssets-cdn.github.com",
    "185.199.109.153 ssets-cdn.github.com",
    "185.199.110.153 ssets-cdn.github.com",
    "185.199.111.153 ssets-cdn.github.com",
]

GITHUB_HOST_NAME = "github.com"
GLOBAL_HOST_NAME = "github.global.ssl.fastly.net"
CDN_HOST_NAME = "ssets-cdn.github.com"

HOSTS_PATH = "/private/etc/hosts"
LOCAL_DIR = Path(os.environ["HOME"]).absolute() / ".local" / "share" / "gotogithub"
BACKUP_FILE = os.path.join(LOCAL_DIR, "hosts")
