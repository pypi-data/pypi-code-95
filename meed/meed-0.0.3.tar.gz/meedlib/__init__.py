# Common
from .config import *
from .terminal import *

# Commands
from .cli import *
from .stat import *
from .base import *
from .command import *
from .log import *
from .graph import *

# TODO Meed GUI automatically check for updates and a command to manually check
# TODO Meed base command creates a GUI which can be used to customise config
# TODO Meed Graphs
# TODO Finish Meed Stats
# TODO Cleanup the way commands work using the cli.py file
# TODO Cron scheduling is performed in meed + GUI
# TODO Meed logging
# TODO Meed templating

# Logging
import logging
from os import environ, path, makedirs

LOG_FILE = environ.get(
    "MEED_LOG_PATH",
    path.join(path.expanduser("~"), ".cache", "meed", "meed.log"),
)

makedirs(path.dirname(str(LOG_FILE)), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    filemode="a+",
    level=logging.WARN,
    format="%(asctime)s :: %(levelname)s :: %(funcName)s-%(lineno)d :: %(message)s"
)


