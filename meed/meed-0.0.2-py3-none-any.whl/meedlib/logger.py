import logging
from os import environ, path, makedirs

LOG_FILE = environ.get(
    "MEED_LOG_PATH",
    path.join(path.expanduser("~"), ".cache", "meed", "meed.log"),
)

makedirs(path.dirname(str(LOG_FILE)), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, filemode="a+", level=logging.WARN)
