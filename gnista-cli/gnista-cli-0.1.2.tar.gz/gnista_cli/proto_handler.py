# pylint:disable=E0401
import winreg
import ctypes
import os
import sys
import time
from elevate import elevate

from structlog import get_logger

log = get_logger()


class PyProtoHandler:
    url_protocol = "hgnista"
    start_path = '"{0}" "-m" "gnista_cli" "o" "%1"'.format(
        os.path.normpath(os.path.abspath(sys.executable))
    )

    @staticmethod
    def install_handler_user():
        log.info("Started Installing for User")
        PyProtoHandler._user_config_win()

    @staticmethod
    def install_handler_global():
        log.info("Started Installing for all users")
        if not ctypes.windll.shell32.IsUserAnAdmin():
            log.info("Not enough priviledge, restarting...")
            elevate()
        else:
            log.info("Running as Admin")
            PyProtoHandler._global_config_win()

    @staticmethod
    def _global_config_win():
        access_registry = winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT)
        try:
            log.info("Writing key to registry")
            key = winreg.CreateKey(access_registry, PyProtoHandler.url_protocol)
            winreg.SetValue(
                key, "", winreg.REG_SZ, "URL:" + PyProtoHandler.url_protocol
            )
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)

            key = winreg.CreateKey(
                access_registry, PyProtoHandler.url_protocol + "\\shell\\open\\command"
            )
            winreg.SetValue(key, "", winreg.REG_SZ, PyProtoHandler.start_path)
            winreg.CloseKey(key)
        except (OSError, ImportError):
            log.error("FAILED to setup registry link")
            time.sleep(10)

    @staticmethod
    def _user_config_win():
        try:
            log.info("Writing key to registry")
            access_registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.CreateKey(
                access_registry, "SOFTWARE\\Classes\\" + PyProtoHandler.url_protocol
            )

            winreg.SetValue(
                key, "", winreg.REG_SZ, "URL:" + PyProtoHandler.url_protocol
            )
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)

            key = winreg.CreateKey(
                access_registry,
                "SOFTWARE\\Classes\\"
                + PyProtoHandler.url_protocol
                + "\\shell\\open\\command",
            )
            winreg.SetValue(key, "", winreg.REG_SZ, PyProtoHandler.start_path)
            winreg.CloseKey(key)

        except (OSError, ImportError):
            log.error("FAILED to setup registry link")
            time.sleep(10)
