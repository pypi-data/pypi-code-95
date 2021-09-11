try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata
__version__ = importlib_metadata.version(__name__)

from .main import app
from .mqtt_task import mqttc_setup, mqttc_publish, mqttc_close
