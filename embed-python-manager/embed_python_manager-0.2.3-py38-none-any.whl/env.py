from os import path
import platform

SYSTEM = platform.system().lower()  # e.g. 'windows'
# BITS = platform.architecture()[0]  # e.g. '64bits'
# MACHINE = platform.machine().lower()  # e.g. 'amd64'

_DEV_MODE = False  # change it to False when publish this project to pypi.
if _DEV_MODE:
    ASSETS_ENTRY = path.dirname(path.dirname(__file__))  # the proj dir
else:
    ASSETS_ENTRY = path.dirname(__file__)  # current dir
