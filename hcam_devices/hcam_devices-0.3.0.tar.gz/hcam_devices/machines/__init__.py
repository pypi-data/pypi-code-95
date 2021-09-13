import pkg_resources
import os

from sismic.interpreter import Interpreter
from sismic.clock import UtcClock
from sismic.io import import_from_yaml


def get_yaml_file(machine_name):
    if not machine_name.endswith(".yaml"):
        machine_name += ".yaml"
    path = os.path.join('hcam_devices/machines', machine_name)
    full_path = pkg_resources.resource_filename(__name__, path)
    if not os.path.exists(full_path):
        full_path = os.path.join(os.path.dirname(__file__), machine_name)
    return full_path


def create_machine(name, **kwargs):
    full_path = get_yaml_file(name)
    return Interpreter(import_from_yaml(filepath=full_path), clock=UtcClock(),
                       **kwargs)
